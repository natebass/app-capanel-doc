"""Google Cloud specific script helpers.

The generic pieces — path discovery, ``.env`` parsing, subprocess handling —
live in :mod:`app.scripts.script_utils` and are re-exported here so that the
Cloud Run scripts can keep importing a single module.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from app.scripts.script_utils import (
    ScriptError,
    ScriptPaths,
    compute_paths,
    env_bool,
    env_or,
    env_required,
    load_env_file,
    load_repo_env_if_present,
    log,
    parse_env_lines,
    resolve_env_file,
    resolve_executable,
    run_command,
    strip_wrapping_quotes,
    timestamp,
)

__all__ = [
    "GcpDefaults",
    "ScriptError",
    "ScriptPaths",
    "compute_paths",
    "env_bool",
    "env_or",
    "env_required",
    "gcloud_candidates",
    "load_env_file",
    "load_gcp_defaults",
    "load_repo_env_if_present",
    "log",
    "parse_env_lines",
    "resolve_env_file",
    "resolve_executable",
    "run_command",
    "run_gcloud",
    "strip_wrapping_quotes",
    "timestamp",
    "yaml_escape",
]


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


def gcloud_candidates() -> Sequence[Path]:
    """Windows install locations to fall back on when ``gcloud`` is not on PATH."""
    if os.name != "nt":
        return ()

    candidates = [
        Path(r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"),
        Path(
            r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
        ),
    ]
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.insert(
            0,
            Path(local_app_data)
            / "Google"
            / "Cloud SDK"
            / "google-cloud-sdk"
            / "bin"
            / "gcloud.cmd",
        )
    return candidates


def run_gcloud(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = True,
    capture_output: bool = False,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run ``gcloud`` with the Windows install locations as a fallback."""
    return run_command(
        ["gcloud", *args],
        cwd=cwd,
        env=env,
        check=check,
        capture_output=capture_output,
        input_text=input_text,
        extra_candidates=gcloud_candidates(),
    )


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
