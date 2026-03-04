from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from string import Template
from typing import Mapping


class ScriptError(RuntimeError):
    """Raised when script preconditions are not met."""


@dataclass(frozen=True)
class ScriptPaths:
    script_dir: Path
    backend_dir: Path
    repo_dir: Path


@dataclass(frozen=True)
class GcpDefaults:
    full_service: str = "capanel-full"
    run_service_account: str = "capanel-runner"
    cloud_sql_instance: str = "capanel-pg"
    cloud_sql_db: str = "capanel"
    cloud_sql_user: str = "capanel_app"
    project_name: str = "California Accountability Panel"
    import_gcs_uri: str = "gs://ca-panel-001-resources/resources"
    import_resources_local_path: str = "$HOME/Downloads/resources"
    vpc_network: str = "default"
    vpc_subnet: str = "default"
    frontend_host_production: str = "https://localhost"


def compute_paths(current_file: str) -> ScriptPaths:
    script_dir = Path(current_file).resolve().parent
    backend_dir = script_dir.parents[1]
    repo_dir = script_dir.parents[2]
    return ScriptPaths(
        script_dir=script_dir, backend_dir=backend_dir, repo_dir=repo_dir
    )


def timestamp() -> str:
    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(scope: str, message: str) -> None:
    print(f"[{timestamp()}] [{scope}] {message}", flush=True)


def run_command(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = True,
    capture_output: bool = False,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    print(f"+ {shlex.join(cmd)}", flush=True)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        env=dict(env) if env is not None else None,
        check=check,
        text=True,
        capture_output=capture_output,
        input=input_text,
    )


def strip_wrapping_quotes(raw: str) -> str:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
        return raw[1:-1]
    return raw


def parse_env_lines(content: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        normalized_key = key.strip()
        normalized_value = strip_wrapping_quotes(value.strip())
        expanded = Template(normalized_value).safe_substitute(os.environ | parsed)
        parsed[normalized_key] = os.path.expanduser(expanded)
    return parsed


def load_env_file(path: Path, *, override: bool = True) -> dict[str, str]:
    values = parse_env_lines(path.read_text())
    for key, value in values.items():
        if override or key not in os.environ:
            os.environ[key] = value
    return values


def resolve_env_file(current_file: str, explicit_env_file: str | None) -> Path:
    if explicit_env_file:
        explicit_path = Path(explicit_env_file).expanduser().resolve()
        if explicit_path.is_file():
            return explicit_path
        msg = f"Environment file not found: {explicit_env_file}"
        raise ScriptError(msg)

    repo_env = compute_paths(current_file).repo_dir / ".env"
    if repo_env.is_file():
        return repo_env

    msg = (
        f"Environment file not found. Checked: {repo_env}. "
        "Pass an env file path as the first argument or create .env in the repo root."
    )
    raise ScriptError(msg)


def env_required(name: str, hint: str | None = None) -> str:
    value = os.environ.get(name, "")
    if value:
        return value
    suffix = f", {hint}" if hint else ""
    msg = f"Set {name}{suffix}"
    raise ScriptError(msg)


def env_or(name: str, default: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def yaml_escape(value: str) -> str:
    return value.replace("'", "''")


def load_gcp_defaults(current_file: str) -> GcpDefaults:
    defaults_file = Path(current_file).resolve().parent / "gcp.defaults.env"
    if defaults_file.is_file():
        defaults = parse_env_lines(defaults_file.read_text())
    else:
        defaults = {}

    return GcpDefaults(
        full_service=defaults.get("DEFAULT_FULL_SERVICE", GcpDefaults.full_service),
        run_service_account=defaults.get(
            "DEFAULT_RUN_SERVICE_ACCOUNT", GcpDefaults.run_service_account
        ),
        cloud_sql_instance=defaults.get(
            "DEFAULT_CLOUD_SQL_INSTANCE", GcpDefaults.cloud_sql_instance
        ),
        cloud_sql_db=defaults.get("DEFAULT_CLOUD_SQL_DB", GcpDefaults.cloud_sql_db),
        cloud_sql_user=defaults.get(
            "DEFAULT_CLOUD_SQL_USER", GcpDefaults.cloud_sql_user
        ),
        project_name=defaults.get("DEFAULT_PROJECT_NAME", GcpDefaults.project_name),
        import_gcs_uri=defaults.get(
            "DEFAULT_IMPORT_GCS_URI", GcpDefaults.import_gcs_uri
        ),
        import_resources_local_path=defaults.get(
            "DEFAULT_IMPORT_RESOURCES_LOCAL_PATH",
            GcpDefaults.import_resources_local_path,
        ),
        vpc_network=defaults.get("DEFAULT_VPC_NETWORK", GcpDefaults.vpc_network),
        vpc_subnet=defaults.get("DEFAULT_VPC_SUBNET", GcpDefaults.vpc_subnet),
        frontend_host_production=defaults.get(
            "DEFAULT_FRONTEND_HOST_PRODUCTION", GcpDefaults.frontend_host_production
        ),
    )
