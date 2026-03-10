from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

from app.scripts.gcp.gcp_utils import (
    ScriptError,
    env_or,
    env_required,
    load_env_file,
    log,
    resolve_env_file,
    run_command,
)

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rotate Cloud SQL app password and service account keys, "
            "and update runtime references."
        )
    )
    parser.add_argument(
        "env_file",
        nargs="?",
        default=None,
        help="Optional env file path. Defaults to repo root .env.",
    )
    parser.add_argument(
        "--project-id",
        default=None,
        help="GCP project id (default: GCP_PROJECT_ID from env).",
    )
    parser.add_argument(
        "--instance",
        default=None,
        help="Cloud SQL instance id (default: CLOUD_SQL_INSTANCE from env).",
    )
    parser.add_argument(
        "--db-user",
        default=None,
        help="Cloud SQL database user (default: CLOUD_SQL_USER from env).",
    )
    parser.add_argument(
        "--new-db-password",
        default=None,
        help="New DB password (default: CLOUD_SQL_PASSWORD from env).",
    )
    parser.add_argument(
        "--secret-name",
        default="capanel-postgres-password",
        help="Secret Manager secret name for DB password.",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="Cloud Run region (default: GCP_REGION from env).",
    )
    parser.add_argument(
        "--restart-service",
        action="append",
        default=[],
        help=(
            "Cloud Run service to restart via update command. "
            "Repeat flag for multiple services."
        ),
    )
    parser.add_argument(
        "--service-account-email",
        default=None,
        help=(
            "Service account email. Defaults to "
            "RUN_SERVICE_ACCOUNT@GCP_PROJECT_ID.iam.gserviceaccount.com."
        ),
    )
    parser.add_argument(
        "--create-sa-key",
        default=None,
        help="Create a new service-account JSON key at this output path.",
    )
    parser.add_argument(
        "--delete-sa-key",
        action="append",
        default=[],
        help="Delete a service-account key id. Repeat for multiple key ids.",
    )
    parser.add_argument(
        "--rotate-cloud-sql-password",
        action="store_true",
        help="Run gcloud sql users set-password with the selected password.",
    )
    parser.add_argument(
        "--update-secret-manager",
        action="store_true",
        help="Add new version to Secret Manager for DB password.",
    )
    parser.add_argument(
        "--list-sa-keys",
        action="store_true",
        help="List current service-account keys.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "Run common rotation flow: rotate DB password, update secret manager, "
            "restart backend service, and list service-account keys."
        ),
    )
    return parser.parse_args()


def run_sensitive_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    masked_cmd = []
    for item in cmd:
        if item.startswith("--password="):
            masked_cmd.append("--password=***")
            continue
        masked_cmd.append(item)
    print(f"+ {shlex.join(masked_cmd)}", flush=True)
    return subprocess.run(cmd, check=True, text=True, capture_output=False)


def normalize_sa_email(project_id: str, provided: str | None) -> str:
    if provided:
        return provided
    run_service_account = env_required("RUN_SERVICE_ACCOUNT")
    return f"{run_service_account}@{project_id}.iam.gserviceaccount.com"


def ensure_actions_selected(args: argparse.Namespace) -> None:
    if args.all:
        return
    if args.rotate_cloud_sql_password:
        return
    if args.update_secret_manager:
        return
    if args.restart_service:
        return
    if args.list_sa_keys:
        return
    if args.create_sa_key:
        return
    if args.delete_sa_key:
        return
    msg = (
        "No actions selected. Pass one or more action flags, "
        "for example --rotate-cloud-sql-password --update-secret-manager."
    )
    raise ScriptError(msg)


def main() -> int:
    args = parse_args()
    env_path = resolve_env_file(__file__, args.env_file)
    print(f"Loading environment from {env_path}")
    load_env_file(env_path)

    ensure_actions_selected(args)

    project_id = args.project_id or env_required("GCP_PROJECT_ID")
    instance = args.instance or env_required("CLOUD_SQL_INSTANCE")
    db_user = args.db_user or env_required("CLOUD_SQL_USER")
    new_db_password = args.new_db_password or env_required("CLOUD_SQL_PASSWORD")
    region = args.region or env_required("GCP_REGION")
    default_backend_service = env_or("BACKEND_SERVICE", "capanel-backend")

    rotate_cloud_sql_password = args.rotate_cloud_sql_password or args.all
    update_secret_manager = args.update_secret_manager or args.all
    list_sa_keys = args.list_sa_keys or args.all

    restart_services = list(args.restart_service)
    if args.all and not restart_services:
        restart_services = [default_backend_service]

    sa_email = normalize_sa_email(project_id, args.service_account_email)

    if rotate_cloud_sql_password:
        log("rotate-gcp-credentials", "Rotating Cloud SQL user password")
        run_sensitive_command(
            [
                "gcloud",
                "sql",
                "users",
                "set-password",
                db_user,
                f"--instance={instance}",
                f"--project={project_id}",
                f"--password={new_db_password}",
            ]
        )

    if update_secret_manager:
        log("rotate-gcp-credentials", f"Updating secret {args.secret_name}")
        run_command(
            [
                "gcloud",
                "secrets",
                "versions",
                "add",
                args.secret_name,
                f"--project={project_id}",
                "--data-file=-",
            ],
            input_text=new_db_password,
        )

    for service in restart_services:
        log("rotate-gcp-credentials", f"Restarting Cloud Run service {service}")
        run_command(
            [
                "gcloud",
                "run",
                "services",
                "update",
                service,
                f"--project={project_id}",
                f"--region={region}",
            ]
        )

    if list_sa_keys:
        log("rotate-gcp-credentials", f"Listing keys for {sa_email}")
        run_command(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "keys",
                "list",
                f"--iam-account={sa_email}",
                f"--project={project_id}",
            ]
        )

    if args.create_sa_key:
        key_path = Path(args.create_sa_key).expanduser().resolve()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        log("rotate-gcp-credentials", f"Creating new key at {key_path}")
        run_command(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "keys",
                "create",
                str(key_path),
                f"--iam-account={sa_email}",
                f"--project={project_id}",
            ]
        )

    for key_id in args.delete_sa_key:
        log("rotate-gcp-credentials", f"Deleting service-account key {key_id}")
        run_command(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "keys",
                "delete",
                key_id,
                f"--iam-account={sa_email}",
                f"--project={project_id}",
                "--quiet",
            ]
        )

    log("rotate-gcp-credentials", "Rotation actions complete")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
