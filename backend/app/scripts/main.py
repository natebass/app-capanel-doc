import json
import os
import time
from typing import Any, TypedDict, cast

import google.auth  # type: ignore[import-not-found]
from google.auth.transport.requests import (  # type: ignore[import-not-found]
    AuthorizedSession,
)


MODES = {
    "full",
    "initial_data",
    "import_ela_data",
    "import_indicators",
    "both_imports",
}


class Step(TypedDict):
    name: str
    args: list[str]


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


DEFAULT_STEP_TIMEOUT_SECONDS = _env_int("JOB_STEP_TIMEOUT_SECONDS", 7200)
DEFAULT_POLL_INTERVAL_SECONDS = max(1, _env_int("JOB_POLL_INTERVAL_SECONDS", 10))


def _response(status: int, payload: dict[str, Any]) -> tuple[str, int, dict[str, str]]:
    return json.dumps(payload), status, {"Content-Type": "application/json"}


def _poll_operation(
    session: AuthorizedSession,
    operation_name: str,
    *,
    timeout_seconds: int = 1800,
    poll_interval_seconds: int = 5,
) -> dict[str, Any]:
    operation_url = f"https://run.googleapis.com/v2/{operation_name}"
    deadline = time.time() + timeout_seconds

    while True:
        response = session.get(operation_url)
        response.raise_for_status()
        payload = cast(dict[str, Any], response.json())
        if payload.get("done"):
            return payload
        if time.time() >= deadline:
            msg = f"Timed out waiting for operation {operation_name}"
            raise TimeoutError(msg)
        time.sleep(poll_interval_seconds)


def _poll_execution(
    session: AuthorizedSession,
    execution_name: str,
    *,
    timeout_seconds: int = 1800,
    poll_interval_seconds: int = 5,
) -> dict[str, Any]:
    execution_url = f"https://run.googleapis.com/v2/{execution_name}"
    deadline = time.time() + timeout_seconds

    while True:
        response = session.get(execution_url)
        response.raise_for_status()
        execution = cast(dict[str, Any], response.json())
        conditions = execution.get("conditions", [])
        completed = next(
            (c for c in conditions if c.get("type") == "Completed"),
            None,
        )
        if completed and completed.get("status") == "True":
            return execution
        if completed and completed.get("status") == "False":
            msg = completed.get("message") or "Cloud Run job execution failed"
            raise RuntimeError(msg)
        if time.time() >= deadline:
            msg = f"Timed out waiting for execution {execution_name}"
            raise TimeoutError(msg)
        time.sleep(poll_interval_seconds)


def _run_job_step(
    session: AuthorizedSession,
    *,
    project_id: str,
    region: str,
    job_name: str,
    step_name: str,
    args: list[str],
    step_timeout_seconds: int,
    poll_interval_seconds: int,
) -> dict[str, Any]:
    endpoint = (
        "https://run.googleapis.com/v2/projects/"
        f"{project_id}/locations/{region}/jobs/{job_name}:run"
    )
    run_payload = {
        "overrides": {
            "containerOverrides": [
                {
                    "args": args,
                }
            ]
        }
    }

    run_response = session.post(endpoint, json=run_payload)
    run_response.raise_for_status()
    run_body = cast(dict[str, Any], run_response.json())
    operation_name = run_body.get("name")
    if not operation_name:
        msg = f"Missing operation name when running step '{step_name}'"
        raise RuntimeError(msg)

    operation = _poll_operation(
        session,
        operation_name,
        timeout_seconds=step_timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
    )
    operation_error = operation.get("error")
    if operation_error:
        msg = operation_error.get("message") or f"Step '{step_name}' failed"
        raise RuntimeError(msg)

    execution_name = operation.get("response", {}).get("name")
    if not execution_name:
        msg = f"Missing execution name when running step '{step_name}'"
        raise RuntimeError(msg)

    execution = _poll_execution(
        session,
        execution_name,
        timeout_seconds=step_timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
    )
    return {
        "step": step_name,
        "args": args,
        "execution": execution_name,
        "succeeded": int(execution.get("succeededCount", 0)),
        "failed": int(execution.get("failedCount", 0)),
    }


def _build_steps(
    *,
    mode: str,
    gcs_uri: str,
    resources_path: str,
    ela_file: str,
    ela_files: list[str],
    indicators_source: str,
    indicators_path: str,
    batch_size: int,
    indicator: str,
    years: list[str],
) -> list[Step]:
    migrate_step: Step = {
        "name": "migrate",
        "args": ["-m", "alembic", "upgrade", "head"],
    }
    initial_data_step: Step = {
        "name": "initial_data",
        "args": ["app/scripts/initial_data.py"],
    }
    sync_step: Step = {
        "name": "sync_gcs_resources",
        "args": [
            "app/scripts/sync_gcs_resources.py",
            "--uri",
            gcs_uri,
            "--dest",
            resources_path,
        ],
    }
    import_ela_step: Step = {
        "name": "import_ela_data",
        "args": ["app/scripts/import_ela_data.py", ela_file],
    }
    import_indicators_step: Step = {
        "name": "import_indicators",
        "args": [
            "app/scripts/import_indicators.py",
            "--source",
            indicators_source,
            "--path",
            indicators_path,
            "--batch-size",
            str(batch_size),
        ],
    }
    if indicator:
        import_indicators_step["args"].extend(["--indicator", indicator])
    if years:
        import_indicators_step["args"].extend(["--years", ",".join(years)])

    if mode == "initial_data":
        return [migrate_step, initial_data_step]
    if mode == "import_ela_data":
        return [sync_step, import_ela_step]
    if mode == "import_indicators":
        return [sync_step, import_indicators_step]
    if mode == "both_imports":
        ela_steps: list[Step] = []
        for i, current_ela_file in enumerate(ela_files):
            ela_steps.append(
                {
                    "name": f"import_ela_data_{i + 1}",
                    "args": ["app/scripts/import_ela_data.py", current_ela_file],
                }
            )
        import_indicators_all_step: Step = {
            "name": "import_indicators_all_files",
            "args": [
                "app/scripts/import_indicators.py",
                "--source",
                indicators_source,
                "--path",
                indicators_path,
                "--batch-size",
                str(batch_size),
                "--all-files",
            ],
        }
        if indicator:
            import_indicators_all_step["args"].extend(["--indicator", indicator])
        if years:
            import_indicators_all_step["args"].extend(["--years", ",".join(years)])
        return [sync_step, *ela_steps, import_indicators_all_step]
    return [
        migrate_step,
        initial_data_step,
        sync_step,
        import_ela_step,
        import_indicators_step,
    ]


def trigger_backend_init(request: Any) -> tuple[str, int, dict[str, str]]:
    if request.method != "POST":
        return _response(405, {"error": "Method not allowed. Use POST."})

    project_id = os.environ.get("GCP_PROJECT_ID")
    region = os.environ.get("GCP_REGION")
    job_name = os.environ.get("BACKEND_INIT_JOB")

    if not project_id or not region or not job_name:
        return _response(
            500,
            {
                "error": "Missing required env vars",
                "required": ["GCP_PROJECT_ID", "GCP_REGION", "BACKEND_INIT_JOB"],
            },
        )

    request_json = request.get_json(silent=True) or {}
    if not isinstance(request_json, dict):
        return _response(400, {"error": "Request body must be a JSON object."})
    mode = str(request_json.get("mode", "full")).strip()
    if mode not in MODES:
        return _response(
            400,
            {
                "error": "Invalid mode.",
                "allowed_modes": sorted(MODES),
            },
        )
    gcs_uri = str(
        request_json.get("gcs_uri", "gs://ca-panel-001-resources/resources")
    ).strip()
    resources_path = str(request_json.get("resources_path", "/tmp/resources")).strip()
    ela_file = str(
        request_json.get("ela_file", f"{resources_path}/cde/eladownload2025.xlsx")
    ).strip()
    years_raw = request_json.get("years")
    years: list[str]
    if years_raw is None:
        years = ["2024", "2025"]
    elif isinstance(years_raw, list):
        years = [str(y).strip() for y in years_raw if str(y).strip()]
    else:
        years = [y.strip() for y in str(years_raw).split(",") if y.strip()]

    ela_files_raw = request_json.get("ela_files")
    if isinstance(ela_files_raw, list):
        ela_files = [str(p).strip() for p in ela_files_raw if str(p).strip()]
    elif isinstance(ela_files_raw, str) and ela_files_raw.strip():
        ela_files = [ela_files_raw.strip()]
    else:
        ela_files = [f"{resources_path}/cde/eladownload{year}.xlsx" for year in years]
        if not ela_files:
            ela_files = [ela_file]
    indicators_source = str(request_json.get("indicators_source", "cde")).strip()
    indicators_path = str(
        request_json.get("indicators_path", f"{resources_path}/cde")
    ).strip()
    try:
        batch_size = int(request_json.get("batch_size", 1000))
    except (TypeError, ValueError):
        return _response(400, {"error": "batch_size must be an integer."})
    if batch_size <= 0:
        return _response(400, {"error": "batch_size must be > 0."})
    try:
        step_timeout_seconds = int(
            request_json.get("step_timeout_seconds", DEFAULT_STEP_TIMEOUT_SECONDS)
        )
    except (TypeError, ValueError):
        return _response(400, {"error": "step_timeout_seconds must be an integer."})
    if step_timeout_seconds <= 0:
        return _response(400, {"error": "step_timeout_seconds must be > 0."})
    try:
        poll_interval_seconds = int(
            request_json.get("poll_interval_seconds", DEFAULT_POLL_INTERVAL_SECONDS)
        )
    except (TypeError, ValueError):
        return _response(400, {"error": "poll_interval_seconds must be an integer."})
    if poll_interval_seconds <= 0:
        return _response(400, {"error": "poll_interval_seconds must be > 0."})
    indicator = str(request_json.get("indicator", "")).strip()

    if not gcs_uri.startswith("gs://"):
        return _response(400, {"error": "gcs_uri must start with gs://"})

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    session = AuthorizedSession(credentials)

    steps = _build_steps(
        mode=mode,
        gcs_uri=gcs_uri,
        resources_path=resources_path,
        ela_file=ela_file,
        ela_files=ela_files,
        indicators_source=indicators_source,
        indicators_path=indicators_path,
        batch_size=batch_size,
        indicator=indicator,
        years=years,
    )

    completed_steps: list[dict[str, Any]] = []
    for step in steps:
        try:
            result = _run_job_step(
                session,
                project_id=project_id,
                region=region,
                job_name=job_name,
                step_name=step["name"],
                args=step["args"],
                step_timeout_seconds=step_timeout_seconds,
                poll_interval_seconds=poll_interval_seconds,
            )
            completed_steps.append(result)
        except Exception as exc:
            return _response(
                500,
                {
                    "error": "Backend import pipeline failed",
                    "job": job_name,
                    "failed_step": step["name"],
                    "message": str(exc),
                    "completed_steps": completed_steps,
                },
            )

    return _response(
        200,
        {
            "job": job_name,
            "mode": mode,
            "gcs_uri": gcs_uri,
            "resources_path": resources_path,
            "years": years,
            "ela_files": ela_files,
            "step_timeout_seconds": step_timeout_seconds,
            "poll_interval_seconds": poll_interval_seconds,
            "status": "completed",
            "steps": completed_steps,
        },
    )
