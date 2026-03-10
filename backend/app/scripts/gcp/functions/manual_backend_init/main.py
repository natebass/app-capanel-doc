import json
import os
import time
from typing import Any, TypedDict, cast

import google.auth
from google.auth.transport.requests import (
    AuthorizedSession,
)

MODES = {
    "full",
    "migrate_only",
    "initial_data",
    "import_ela_data",
    "import_indicators",
    "both_imports",
}


class Step(TypedDict):
    name: str
    args: list[str]


def _normalize_indicators_source(source: str) -> str:
    normalized = source.strip().lower().replace("_", "-")
    if normalized in {"state", "california-state", "california state"}:
        return "state"
    return "cde"


def _is_year_folder(name: str, year: str, source: str) -> bool:
    lowered = name.lower()
    if year not in lowered:
        return False
    if source == "cde":
        return "cde" in lowered
    return (
        "california-state" in lowered
        or "california_state" in lowered
        or ("california" in lowered and "state" in lowered)
    )


def _discover_indicator_paths(
    resources_path: str, years: list[str], source: str, indicators_path: str
) -> list[str]:
    base_path = (indicators_path or resources_path).strip()
    base_path = base_path.rstrip("/") or base_path
    discovered: list[str] = []

    def _get_year_folders(base: str, src: str) -> list[str]:
        found: list[str] = []
        if os.path.isdir(base):
            try:
                for entry in sorted(os.listdir(base)):
                    child = os.path.join(base, entry)
                    if not os.path.isdir(child):
                        continue
                    if any(_is_year_folder(entry, year, src) for year in years):
                        found.append(child)
            except OSError:
                pass
        return found

    # If a specific year folder is already provided, keep it.
    base_name = os.path.basename(base_path)
    if any(_is_year_folder(base_name, year, source) for year in years):
        discovered = [base_path]
    elif os.path.isdir(base_path):
        # Discover for primary source
        discovered.extend(_get_year_folders(base_path, source))

        # If source is 'state', also discover 'cde' folders
        if source == "state":
            discovered.extend(_get_year_folders(base_path, "cde"))

    # If nothing was found, fallback to expected year-folder names under resources_path.
    if not discovered:
        root = resources_path.rstrip("/") or resources_path
        sources = [source]
        if source == "state":
            sources.append("cde")

        for s in sources:
            prefix = "cde" if s == "cde" else "california-state"
            for year in years:
                discovered.append(f"{root}/{prefix}-{year}")

    # Deduplicate while preserving order.
    deduped: list[str] = []
    seen: set[str] = set()
    for path in discovered:
        if path in seen:
            continue
        seen.add(path)
        deduped.append(path)
    return deduped


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _parse_bool(name: str, raw: Any, *, default: bool) -> bool:
    if raw is None:
        return default
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        normalized = raw.strip().lower()
        if normalized in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "f", "no", "n", "off"}:
            return False
    if isinstance(raw, (int, float)):
        return bool(raw)
    raise ValueError(f"{name} must be a boolean.")


def _parse_positive_int(name: str, raw: Any, *, default: int) -> int:
    value = default if raw is None else int(raw)
    if value <= 0:
        raise ValueError(f"{name} must be > 0.")
    return value


DEFAULT_STEP_TIMEOUT_SECONDS = _env_int("JOB_STEP_TIMEOUT_SECONDS", 7200)
DEFAULT_POLL_INTERVAL_SECONDS = max(1, _env_int("JOB_POLL_INTERVAL_SECONDS", 10))


def _response(status: int, payload: dict[str, Any]) -> tuple[str, int, dict[str, str]]:
    return json.dumps(payload), status, {"Content-Type": "application/json"}


def _poll_operation(
    session: AuthorizedSession,
    operation_name: str,
    *,
    timeout_seconds: int,
    poll_interval_seconds: int,
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
            raise TimeoutError(f"Timed out waiting for operation {operation_name}")
        time.sleep(poll_interval_seconds)


def _poll_execution(
    session: AuthorizedSession,
    execution_name: str,
    *,
    timeout_seconds: int,
    poll_interval_seconds: int,
) -> dict[str, Any]:
    execution_url = f"https://run.googleapis.com/v2/{execution_name}"
    deadline = time.time() + timeout_seconds

    while True:
        response = session.get(execution_url)
        response.raise_for_status()
        execution = cast(dict[str, Any], response.json())
        conditions = execution.get("conditions", [])
        completed = next((c for c in conditions if c.get("type") == "Completed"), None)
        if completed and completed.get("status") == "True":
            return execution
        if completed and completed.get("status") == "False":
            msg = completed.get("message") or "Cloud Run job execution failed"
            raise RuntimeError(msg)
        if time.time() >= deadline:
            raise TimeoutError(f"Timed out waiting for execution {execution_name}")
        time.sleep(poll_interval_seconds)


def _start_job(
    session: AuthorizedSession,
    *,
    project_id: str,
    region: str,
    job_name: str,
    args: list[str],
) -> str:
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
    operation_name = cast(dict[str, Any], run_response.json()).get("name")
    if not operation_name:
        raise RuntimeError("Missing operation name when running job")
    return str(operation_name)


# Modes that run alembic migrations (and possibly seed initial data) require
# explicit confirmation to prevent accidental schema changes in production.
_DESTRUCTIVE_MODES = {"full", "initial_data", "migrate_only"}


def _build_pipeline_args(
    request_json: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    mode = str(request_json.get("mode", "both_imports")).strip()
    if mode not in MODES:
        raise ValueError(f"Invalid mode: {mode}. Allowed: {sorted(MODES)}")

    # Destructive modes (alembic + seed) require an explicit opt-in flag.
    if mode in _DESTRUCTIVE_MODES:
        confirm = _parse_bool(
            "confirm_destructive",
            request_json.get("confirm_destructive"),
            default=False,
        )
        if not confirm:
            raise ValueError(
                f"mode='{mode}' runs database migrations. "
                'Set "confirm_destructive": true to proceed.'
            )

    # overwrite=true permanently replaces existing DB rows — require explicit opt-in.
    overwrite_raw = request_json.get("overwrite")
    if overwrite_raw is not None:
        overwrite = _parse_bool("overwrite", overwrite_raw, default=False)
        if overwrite:
            confirm_overwrite = _parse_bool(
                "confirm_overwrite",
                request_json.get("confirm_overwrite"),
                default=False,
            )
            if not confirm_overwrite:
                raise ValueError(
                    "overwrite=true will permanently replace existing DB rows. "
                    'Set "confirm_overwrite": true to proceed.'
                )
    else:
        overwrite = False

    gcs_uri = str(
        request_json.get("gcs_uri", "gs://ca-panel-001-resources/resources")
    ).strip()
    resources_path = str(request_json.get("resources_path", "/tmp/resources")).strip()

    years_raw = request_json.get("years")
    if years_raw is None:
        years = ["2024", "2025"]
    elif isinstance(years_raw, list):
        years = [str(y).strip() for y in years_raw if str(y).strip()]
    else:
        years = [y.strip() for y in str(years_raw).split(",") if y.strip()]
    if not years:
        years = ["2024", "2025"]

    default_ela_year = years[-1] if years else "2025"
    default_ela_file = (
        f"{resources_path}/cde-{default_ela_year}/eladownload{default_ela_year}.xlsx"
    )
    ela_file = str(request_json.get("ela_file", default_ela_file)).strip()

    ela_files_raw = request_json.get("ela_files")
    if isinstance(ela_files_raw, list):
        ela_files = [str(p).strip() for p in ela_files_raw if str(p).strip()]
    elif isinstance(ela_files_raw, str) and ela_files_raw.strip():
        ela_files = [ela_files_raw.strip()]
    else:
        # Let run_import_pipeline discover year-specific ELA files after sync.
        ela_files = []

    indicators_source = _normalize_indicators_source(
        str(request_json.get("indicators_source", "state"))
    )
    indicators_path = str(request_json.get("indicators_path", resources_path)).strip()
    indicators_paths = _discover_indicator_paths(
        resources_path=resources_path,
        years=years,
        source=indicators_source,
        indicators_path=indicators_path,
    )
    batch_size = _parse_positive_int(
        "batch_size", request_json.get("batch_size"), default=5000
    )
    indicator = str(request_json.get("indicator", "")).strip()
    # overwrite already parsed and validated above.
    skip_sync = _parse_bool("skip_sync", request_json.get("skip_sync"), default=False)

    args: list[str] = [
        "app/scripts/cde/run_import_pipeline.py",
        "--mode",
        mode,
        "--gcs-uri",
        gcs_uri,
        "--resources-path",
        resources_path,
        "--ela-file",
        ela_file,
        "--years",
        ",".join(years),
        "--indicators-source",
        indicators_source,
        "--indicators-path",
        indicators_path,
        "--indicators-paths",
        ",".join(indicators_paths),
        "--batch-size",
        str(batch_size),
    ]
    if overwrite:
        args.append("--overwrite")
    if skip_sync:
        args.append("--skip-sync")
    if ela_files:
        args.extend(["--ela-files", ",".join(ela_files)])
    if indicator:
        args.extend(["--indicator", indicator])

    request_summary: dict[str, Any] = {
        "mode": mode,
        "gcs_uri": gcs_uri,
        "resources_path": resources_path,
        "ela_file": ela_file,
        "ela_files": ela_files,
        "years": years,
        "indicators_source": indicators_source,
        "indicators_path": indicators_path,
        "indicators_paths": indicators_paths,
        "batch_size": batch_size,
        "overwrite": overwrite,
        "skip_sync": skip_sync,
        # Echo confirmation flags so callers can audit what was acknowledged.
        "confirm_destructive": mode in _DESTRUCTIVE_MODES,
        "confirm_overwrite": overwrite,
    }
    if indicator:
        request_summary["indicator"] = indicator

    return args, request_summary


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

    try:
        pipeline_args, summary = _build_pipeline_args(request_json)
    except ValueError as exc:
        return _response(400, {"error": str(exc), "allowed_modes": sorted(MODES)})
    except Exception as exc:
        return _response(400, {"error": f"Invalid request: {exc}"})

    try:
        wait_for_completion = _parse_bool(
            "wait_for_completion",
            request_json.get("wait_for_completion"),
            default=False,
        )
        step_timeout_seconds = _parse_positive_int(
            "step_timeout_seconds",
            request_json.get("step_timeout_seconds"),
            default=DEFAULT_STEP_TIMEOUT_SECONDS,
        )
        poll_interval_seconds = _parse_positive_int(
            "poll_interval_seconds",
            request_json.get("poll_interval_seconds"),
            default=DEFAULT_POLL_INTERVAL_SECONDS,
        )
    except ValueError as exc:
        return _response(400, {"error": str(exc)})

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    session = AuthorizedSession(credentials)  # type: ignore[no-untyped-call]

    try:
        operation_name = _start_job(
            session,
            project_id=project_id,
            region=region,
            job_name=job_name,
            args=pipeline_args,
        )

        if not wait_for_completion:
            return _response(
                202,
                {
                    "job": job_name,
                    "status": "started",
                    "operation": operation_name,
                    "wait_for_completion": False,
                    "request": summary,
                    "args": pipeline_args,
                },
            )

        operation = _poll_operation(
            session,
            operation_name,
            timeout_seconds=step_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        operation_error = operation.get("error")
        if operation_error:
            return _response(
                500,
                {
                    "error": operation_error.get("message")
                    or "Job run operation failed",
                    "operation": operation_name,
                },
            )

        execution_name = operation.get("response", {}).get("name")
        if not execution_name:
            return _response(
                500,
                {
                    "error": "Missing execution name from operation response",
                    "operation": operation_name,
                },
            )

        execution = _poll_execution(
            session,
            str(execution_name),
            timeout_seconds=step_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        return _response(
            200,
            {
                "job": job_name,
                "status": "completed",
                "operation": operation_name,
                "execution": execution_name,
                "succeeded": int(execution.get("succeededCount", 0)),
                "failed": int(execution.get("failedCount", 0)),
                "request": summary,
                "args": pipeline_args,
            },
        )
    except Exception as exc:
        return _response(
            500,
            {
                "error": "Failed to start backend import pipeline",
                "message": str(exc),
                "job": job_name,
            },
        )
