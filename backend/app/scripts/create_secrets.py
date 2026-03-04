from __future__ import annotations

import sys

from app.scripts.script_utils import (
    ScriptError,
    env_required,
    load_env_file,
    log,
    resolve_env_file,
    run_command,
)


def main() -> int:
    env_path = resolve_env_file(__file__, sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"Loading environment from {env_path}")
    load_env_file(env_path)

    project_id = env_required("GCP_PROJECT_ID")
    run_service_account = env_required("RUN_SERVICE_ACCOUNT")
    cloud_sql_password = env_required("CLOUD_SQL_PASSWORD")
    secret_key = env_required("SECRET_KEY")
    first_superuser = env_required("FIRST_SUPERUSER")
    first_superuser_password = env_required("FIRST_SUPERUSER_PASSWORD")

    run_sa_email = f"{run_service_account}@{project_id}.iam.gserviceaccount.com"

    secrets = {
        "capanel-postgres-password": cloud_sql_password,
        "capanel-secret-key": secret_key,
        "capanel-superuser-email": first_superuser,
        "capanel-superuser-password": first_superuser_password,
    }

    log("create-secrets", "Enabling Secret Manager API")
    run_command(
        [
            "gcloud",
            "services",
            "enable",
            "secretmanager.googleapis.com",
            f"--project={project_id}",
        ]
    )

    for secret_name, secret_value in secrets.items():
        describe = run_command(
            ["gcloud", "secrets", "describe", secret_name, f"--project={project_id}"],
            capture_output=True,
            check=False,
        )
        if describe.returncode != 0:
            log("create-secrets", f"Creating secret {secret_name}")
            run_command(
                [
                    "gcloud",
                    "secrets",
                    "create",
                    secret_name,
                    f"--project={project_id}",
                    "--replication-policy=automatic",
                ]
            )
        else:
            log("create-secrets", f"Secret {secret_name} already exists")

        log("create-secrets", f"Adding latest version for {secret_name}")
        run_command(
            [
                "gcloud",
                "secrets",
                "versions",
                "add",
                secret_name,
                f"--project={project_id}",
                "--data-file=-",
            ],
            input_text=secret_value,
        )

        log("create-secrets", f"Granting accessor role on {secret_name}")
        run_command(
            [
                "gcloud",
                "secrets",
                "add-iam-policy-binding",
                secret_name,
                f"--project={project_id}",
                f"--member=serviceAccount:{run_sa_email}",
                "--role=roles/secretmanager.secretAccessor",
                "--quiet",
            ]
        )

    print("\nAll secrets created/updated and IAM bindings applied.")
    print(
        "Verify with:\n"
        f"  gcloud secrets list --project={project_id} --filter='name:capanel-'"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
