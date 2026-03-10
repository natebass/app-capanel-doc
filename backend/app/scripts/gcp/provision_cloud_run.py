from __future__ import annotations

import sys

from app.scripts.gcp.gcp_utils import (
    ScriptError,
    env_or,
    env_required,
    load_env_file,
    resolve_env_file,
    run_command,
)


def exists(cmd: list[str]) -> bool:
    result = run_command(cmd, capture_output=True, check=False)
    return result.returncode == 0


def main() -> int:
    env_path = resolve_env_file(__file__, sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"Loading environment from {env_path}")
    load_env_file(env_path)

    project_id = env_required("GCP_PROJECT_ID")
    region = env_required("GCP_REGION", "for example us-central1")
    ar_repo = env_required("GCP_AR_REPOSITORY")
    run_service_account = env_required("RUN_SERVICE_ACCOUNT")
    vpc_network = env_required("VPC_NETWORK", "for example default")
    private_range_name = env_required("PRIVATE_RANGE_NAME")
    private_range_prefix = env_required("PRIVATE_RANGE_PREFIX", "for example 16")
    cloud_sql_instance = env_required("CLOUD_SQL_INSTANCE")
    cloud_sql_db = env_required("CLOUD_SQL_DB")
    cloud_sql_user = env_required("CLOUD_SQL_USER")
    cloud_sql_password = env_required("CLOUD_SQL_PASSWORD")
    import_gcs_uri = env_required("IMPORT_GCS_URI")

    cloud_sql_version = env_or("CLOUD_SQL_VERSION", "POSTGRES_18")
    cloud_sql_edition = env_or("CLOUD_SQL_EDITION", "enterprise")
    run_sa_email = f"{run_service_account}@{project_id}.iam.gserviceaccount.com"

    run_command(["gcloud", "config", "set", "project", project_id])

    run_command(
        [
            "gcloud",
            "services",
            "enable",
            "run.googleapis.com",
            "cloudfunctions.googleapis.com",
            "eventarc.googleapis.com",
            "pubsub.googleapis.com",
            "artifactregistry.googleapis.com",
            "cloudbuild.googleapis.com",
            "sqladmin.googleapis.com",
            "secretmanager.googleapis.com",
            "storage.googleapis.com",
            "servicenetworking.googleapis.com",
            "compute.googleapis.com",
        ]
    )

    if not exists(
        [
            "gcloud",
            "artifacts",
            "repositories",
            "describe",
            ar_repo,
            f"--location={region}",
        ]
    ):
        run_command(
            [
                "gcloud",
                "artifacts",
                "repositories",
                "create",
                ar_repo,
                f"--location={region}",
                "--repository-format=docker",
                "--description=Container images for CAPanel services",
            ]
        )

    if not exists(["gcloud", "iam", "service-accounts", "describe", run_sa_email]):
        run_command(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "create",
                run_service_account,
                "--display-name=CAPanel Cloud Run runtime",
            ]
        )

    for role in [
        "roles/cloudsql.client",
        "roles/artifactregistry.reader",
        "roles/run.developer",
        "roles/storage.objectViewer",
    ]:
        run_command(
            [
                "gcloud",
                "projects",
                "add-iam-policy-binding",
                project_id,
                f"--member=serviceAccount:{run_sa_email}",
                f"--role={role}",
            ]
        )

    if not exists(
        ["gcloud", "compute", "addresses", "describe", private_range_name, "--global"]
    ):
        run_command(
            [
                "gcloud",
                "compute",
                "addresses",
                "create",
                private_range_name,
                "--global",
                "--purpose=VPC_PEERING",
                f"--prefix-length={private_range_prefix}",
                f"--network={vpc_network}",
            ]
        )

    peerings = run_command(
        [
            "gcloud",
            "services",
            "vpc-peerings",
            "list",
            f"--network={vpc_network}",
            "--format=value(service)",
        ],
        capture_output=True,
    )
    if "servicenetworking.googleapis.com" not in peerings.stdout.splitlines():
        run_command(
            [
                "gcloud",
                "services",
                "vpc-peerings",
                "connect",
                "--service=servicenetworking.googleapis.com",
                f"--network={vpc_network}",
                f"--ranges={private_range_name}",
            ]
        )

    if not exists(["gcloud", "sql", "instances", "describe", cloud_sql_instance]):
        run_command(
            [
                "gcloud",
                "sql",
                "instances",
                "create",
                cloud_sql_instance,
                f"--database-version={cloud_sql_version}",
                f"--edition={cloud_sql_edition}",
                "--cpu=1",
                "--memory=3840MiB",
                f"--region={region}",
                "--availability-type=zonal",
                "--storage-size=20GB",
                "--storage-type=SSD",
                f"--network={vpc_network}",
                "--no-assign-ip",
            ]
        )

    if not exists(
        [
            "gcloud",
            "sql",
            "databases",
            "describe",
            cloud_sql_db,
            f"--instance={cloud_sql_instance}",
        ]
    ):
        run_command(
            [
                "gcloud",
                "sql",
                "databases",
                "create",
                cloud_sql_db,
                f"--instance={cloud_sql_instance}",
            ]
        )

    users = run_command(
        [
            "gcloud",
            "sql",
            "users",
            "list",
            f"--instance={cloud_sql_instance}",
            "--format=value(name)",
        ],
        capture_output=True,
    )
    if cloud_sql_user not in users.stdout.splitlines():
        run_command(
            [
                "gcloud",
                "sql",
                "users",
                "create",
                cloud_sql_user,
                f"--instance={cloud_sql_instance}",
                f"--password={cloud_sql_password}",
            ]
        )

    # Ensure the resources bucket exists and is in the correct region
    if import_gcs_uri.startswith("gs://"):
        import_gcs_bucket = import_gcs_uri.split("/")[2]
        if not exists(
            ["gcloud", "storage", "buckets", "describe", f"gs://{import_gcs_bucket}"]
        ):
            print(f"Creating bucket gs://{import_gcs_bucket} in {region}")
            run_command(
                [
                    "gcloud",
                    "storage",
                    "buckets",
                    "create",
                    f"gs://{import_gcs_bucket}",
                    f"--location={region}",
                    "--uniform-bucket-level-access",
                ]
            )

    print("Provisioning complete.")
    print(f"Artifact Registry: {region}-docker.pkg.dev/{project_id}/{ar_repo}")
    print(f"Cloud SQL connection: {project_id}:{region}:{cloud_sql_instance}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
