from __future__ import annotations

import argparse
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.scripts.gcp.gcp_utils import (
    GcpDefaults,
    ScriptError,
    compute_paths,
    env_bool,
    env_or,
    env_required,
    load_env_file,
    load_gcp_defaults,
    resolve_env_file,
    run_command,
    yaml_escape,
)


@dataclass(frozen=True)
class DeployConfig:
    project_id: str
    region: str
    ar_repository: str
    backend_service: str
    frontend_service: str
    run_service_account: str
    vpc_network: str
    vpc_subnet: str
    cloud_sql_instance: str
    cloud_sql_db: str
    cloud_sql_user: str
    full_service: str
    tag: str
    api_v1_str: str
    project_name: str
    cloud_sql_connection_name: str
    run_service_account_email: str
    run_data_imports: str
    run_startup_data_imports: str
    import_gcs_uri: str
    import_resources_local_path: str
    sync_local_imports_to_bucket: bool
    backend_init_job: str
    init_trigger_function_name: str
    backend_init_job_task_timeout: str
    backend_init_job_parallelism: str
    backend_init_job_max_retries: str
    backend_init_job_cpu: str
    backend_init_job_memory: str
    init_trigger_function_timeout: str
    job_step_timeout_seconds: str
    job_poll_interval_seconds: str
    init_trigger_function_source_dir: Path
    environment: str
    frontend_host: str
    backend_cors_origins: str
    backend_image: str
    frontend_image: str


def cmd_exists(cmd: list[str]) -> bool:
    return run_command(cmd, capture_output=True, check=False).returncode == 0


def current_git_tag(repo_dir: Path) -> str:
    result = run_command(
        ["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir, capture_output=True
    )
    return result.stdout.strip()


def load_and_apply_env(defaults: GcpDefaults) -> None:
    os.environ["RUN_SERVICE_ACCOUNT"] = env_or(
        "RUN_SERVICE_ACCOUNT", defaults.run_service_account
    )
    os.environ["VPC_NETWORK"] = env_or("VPC_NETWORK", defaults.vpc_network)
    os.environ["VPC_SUBNET"] = env_or("VPC_SUBNET", defaults.vpc_subnet)
    os.environ["CLOUD_SQL_INSTANCE"] = env_or(
        "CLOUD_SQL_INSTANCE", defaults.cloud_sql_instance
    )
    os.environ["CLOUD_SQL_DB"] = env_or("CLOUD_SQL_DB", defaults.cloud_sql_db)
    os.environ["CLOUD_SQL_USER"] = env_or("CLOUD_SQL_USER", defaults.cloud_sql_user)
    os.environ["FULL_SERVICE"] = env_or("FULL_SERVICE", defaults.full_service)


def build_config(defaults: GcpDefaults) -> DeployConfig:
    paths = compute_paths(__file__)
    project_id = env_required("GCP_PROJECT_ID")
    region = env_required("GCP_REGION", "for example us-central1")
    ar_repository = env_required("GCP_AR_REPOSITORY")
    backend_service = env_required("BACKEND_SERVICE")
    frontend_service = env_required("FRONTEND_SERVICE")
    run_service_account = env_required("RUN_SERVICE_ACCOUNT")
    vpc_network = env_required("VPC_NETWORK", "for example default")
    vpc_subnet = env_required("VPC_SUBNET", "for example default")
    cloud_sql_instance = env_required("CLOUD_SQL_INSTANCE")
    cloud_sql_db = env_required("CLOUD_SQL_DB")
    cloud_sql_user = env_required("CLOUD_SQL_USER")
    full_service = env_required("FULL_SERVICE")

    tag = env_or("TAG", current_git_tag(paths.repo_dir))
    api_v1_str = env_or("API_V1_STR", "/api/v1")
    project_name = env_or("PROJECT_NAME", defaults.project_name)
    cloud_sql_connection_name = f"{project_id}:{region}:{cloud_sql_instance}"
    run_sa_email = f"{run_service_account}@{project_id}.iam.gserviceaccount.com"
    run_data_imports = env_or("RUN_DATA_IMPORTS", "false")
    run_startup_data_imports = env_or("RUN_STARTUP_DATA_IMPORTS", "false")
    import_gcs_uri = env_or("IMPORT_GCS_URI", defaults.import_gcs_uri)
    import_resources_local_path = env_or(
        "IMPORT_RESOURCES_LOCAL_PATH", defaults.import_resources_local_path
    )
    sync_local_imports_to_bucket = env_bool("SYNC_LOCAL_IMPORTS_TO_BUCKET", False)
    backend_init_job = env_or("BACKEND_INIT_JOB", f"{full_service}-init")
    init_trigger_function_name = env_or(
        "INIT_TRIGGER_FUNCTION_NAME", f"{full_service}-init-trigger"
    )
    backend_init_job_task_timeout = env_or("BACKEND_INIT_JOB_TASK_TIMEOUT", "7200s")
    backend_init_job_parallelism = env_or("BACKEND_INIT_JOB_PARALLELISM", "1")
    backend_init_job_max_retries = env_or("BACKEND_INIT_JOB_MAX_RETRIES", "0")
    backend_init_job_cpu = env_or("BACKEND_INIT_JOB_CPU", "4")
    backend_init_job_memory = env_or("BACKEND_INIT_JOB_MEMORY", "8Gi")
    init_trigger_function_timeout = env_or("INIT_TRIGGER_FUNCTION_TIMEOUT", "3600s")
    job_step_timeout_seconds = env_or("JOB_STEP_TIMEOUT_SECONDS", "7200")
    job_poll_interval_seconds = env_or("JOB_POLL_INTERVAL_SECONDS", "10")
    source_dir = paths.backend_dir / "app/scripts/gcp/functions/manual_backend_init"
    environment = "production"
    frontend_host = env_or(
        "FRONTEND_HOST_PRODUCTION", defaults.frontend_host_production
    )
    backend_cors_origins = env_or(
        "BACKEND_CORS_ORIGINS_PRODUCTION", env_or("BACKEND_CORS_ORIGINS", frontend_host)
    )

    backend_image = (
        f"{region}-docker.pkg.dev/{project_id}/{ar_repository}/{backend_service}:{tag}"
    )
    frontend_image = (
        f"{region}-docker.pkg.dev/{project_id}/{ar_repository}/{frontend_service}:{tag}"
    )

    return DeployConfig(
        project_id=project_id,
        region=region,
        ar_repository=ar_repository,
        backend_service=backend_service,
        frontend_service=frontend_service,
        run_service_account=run_service_account,
        vpc_network=vpc_network,
        vpc_subnet=vpc_subnet,
        cloud_sql_instance=cloud_sql_instance,
        cloud_sql_db=cloud_sql_db,
        cloud_sql_user=cloud_sql_user,
        full_service=full_service,
        tag=tag,
        api_v1_str=api_v1_str,
        project_name=project_name,
        cloud_sql_connection_name=cloud_sql_connection_name,
        run_service_account_email=run_sa_email,
        run_data_imports=run_data_imports,
        run_startup_data_imports=run_startup_data_imports,
        import_gcs_uri=import_gcs_uri,
        import_resources_local_path=import_resources_local_path,
        sync_local_imports_to_bucket=sync_local_imports_to_bucket,
        backend_init_job=backend_init_job,
        init_trigger_function_name=init_trigger_function_name,
        backend_init_job_task_timeout=backend_init_job_task_timeout,
        backend_init_job_parallelism=backend_init_job_parallelism,
        backend_init_job_max_retries=backend_init_job_max_retries,
        backend_init_job_cpu=backend_init_job_cpu,
        backend_init_job_memory=backend_init_job_memory,
        init_trigger_function_timeout=init_trigger_function_timeout,
        job_step_timeout_seconds=job_step_timeout_seconds,
        job_poll_interval_seconds=job_poll_interval_seconds,
        init_trigger_function_source_dir=source_dir,
        environment=environment,
        frontend_host=frontend_host,
        backend_cors_origins=backend_cors_origins,
        backend_image=backend_image,
        frontend_image=frontend_image,
    )


def ensure_bucket_exists(import_gcs_uri: str, region: str) -> None:
    bucket = import_gcs_uri.removeprefix("gs://").split("/", 1)[0]
    if not cmd_exists(["gcloud", "storage", "buckets", "describe", f"gs://{bucket}"]):
        print(f"Creating bucket gs://{bucket} in {region}")
        run_command(
            [
                "gcloud",
                "storage",
                "buckets",
                "create",
                f"gs://{bucket}",
                f"--location={region}",
                "--uniform-bucket-level-access",
            ]
        )


def maybe_sync_local_resources(cfg: DeployConfig) -> None:
    if not cfg.sync_local_imports_to_bucket:
        print("SYNC_LOCAL_IMPORTS_TO_BUCKET=false; skipping local->bucket sync.")
        return

    local_path = Path(cfg.import_resources_local_path).expanduser()
    if not local_path.is_dir():
        msg = f"Local resources path not found: {local_path}"
        raise ScriptError(msg)

    print(
        f"Merging local resources {local_path} -> {cfg.import_gcs_uri} "
        "(new files only; no overwrite/delete)"
    )
    run_command(
        [
            "gcloud",
            "storage",
            "cp",
            "--recursive",
            "--no-clobber",
            f"{local_path}/.",
            cfg.import_gcs_uri,
        ]
    )


def render_build_config(dockerfile: str, image_subst: str) -> str:
    return (
        "steps:\n"
        "  - name: gcr.io/cloud-builders/docker\n"
        "    env:\n"
        "      - DOCKER_BUILDKIT=1\n"
        "    args:\n"
        "      - build\n"
        f"      - -f\n      - {dockerfile}\n"
        "      - -t\n"
        f"      - {image_subst}\n"
        "      - .\n"
        "images:\n"
        f"  - {image_subst}\n"
    )


def build_backend_image(cfg: DeployConfig) -> None:
    print(f"Building backend image {cfg.backend_image}")
    content = render_build_config("backend/Dockerfile", "${_IMAGE}")
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        tmp.write(content)
        config_path = Path(tmp.name)

    try:
        run_command(
            [
                "gcloud",
                "builds",
                "submit",
                "--substitutions",
                f"_IMAGE={cfg.backend_image}",
                "--config",
                str(config_path),
                ".",
            ]
        )
    finally:
        config_path.unlink(missing_ok=True)


def deploy_init_job(cfg: DeployConfig) -> None:
    print(f"Deploying backend init job {cfg.backend_init_job}")
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        env_file = Path(tmp.name)
        tmp.write(f"ENVIRONMENT: '{yaml_escape(cfg.environment)}'\n")
        tmp.write(f"PROJECT_NAME: '{yaml_escape(cfg.project_name)}'\n")
        tmp.write(f"API_V1_STR: '{yaml_escape(cfg.api_v1_str)}'\n")
        tmp.write(f"BACKEND_CORS_ORIGINS: '{yaml_escape(cfg.backend_cors_origins)}'\n")
        tmp.write(f"FRONTEND_HOST: '{yaml_escape(cfg.frontend_host)}'\n")
        tmp.write(
            "CLOUD_SQL_INSTANCE_CONNECTION_NAME: "
            f"'{yaml_escape(cfg.cloud_sql_connection_name)}'\n"
        )
        tmp.write(f"POSTGRES_DB: '{yaml_escape(cfg.cloud_sql_db)}'\n")
        tmp.write(f"POSTGRES_USER: '{yaml_escape(cfg.cloud_sql_user)}'\n")
        tmp.write("POSTGRES_SERVER: 'localhost'\n")
        tmp.write("RUN_DATA_IMPORTS: 'false'\n")
        tmp.write("RUN_STARTUP_DATA_IMPORTS: 'false'\n")
        tmp.write(f"IMPORT_GCS_URI: '{yaml_escape(cfg.import_gcs_uri)}'\n")
        tmp.write(
            "IMPORT_RESOURCES_LOCAL_PATH: "
            f"'{yaml_escape(cfg.import_resources_local_path)}'\n"
        )

    try:
        run_command(
            [
                "gcloud",
                "run",
                "jobs",
                "deploy",
                cfg.backend_init_job,
                "--image",
                cfg.backend_image,
                "--region",
                cfg.region,
                "--service-account",
                cfg.run_service_account_email,
                "--task-timeout",
                cfg.backend_init_job_task_timeout,
                "--parallelism",
                cfg.backend_init_job_parallelism,
                "--max-retries",
                cfg.backend_init_job_max_retries,
                "--cpu",
                cfg.backend_init_job_cpu,
                "--memory",
                cfg.backend_init_job_memory,
                "--network",
                cfg.vpc_network,
                "--subnet",
                cfg.vpc_subnet,
                "--vpc-egress",
                "private-ranges-only",
                "--set-cloudsql-instances",
                cfg.cloud_sql_connection_name,
                "--command",
                "python",
                "--args",
                "app/scripts/cde/run_import_pipeline.py",
                "--env-vars-file",
                str(env_file),
                "--set-secrets",
                "POSTGRES_PASSWORD=capanel-postgres-password:latest,"
                "SECRET_KEY=capanel-secret-key:latest",
            ]
        )
    finally:
        env_file.unlink(missing_ok=True)

    run_command(
        [
            "gcloud",
            "run",
            "jobs",
            "add-iam-policy-binding",
            cfg.backend_init_job,
            "--region",
            cfg.region,
            "--member",
            f"serviceAccount:{cfg.run_service_account_email}",
            "--role",
            "roles/run.invoker",
        ]
    )


def deploy_trigger_function(cfg: DeployConfig) -> str:
    if not cfg.init_trigger_function_source_dir.is_dir():
        msg = f"Function source directory not found: {cfg.init_trigger_function_source_dir}"
        raise ScriptError(msg)

    run_command(
        [
            "gcloud",
            "functions",
            "deploy",
            cfg.init_trigger_function_name,
            "--gen2",
            "--runtime",
            "python314",
            "--region",
            cfg.region,
            "--timeout",
            cfg.init_trigger_function_timeout,
            "--source",
            str(cfg.init_trigger_function_source_dir),
            "--entry-point",
            "trigger_backend_init",
            "--trigger-http",
            "--no-allow-unauthenticated",
            "--service-account",
            cfg.run_service_account_email,
            "--set-env-vars",
            "GCP_PROJECT_ID="
            f"{cfg.project_id},"
            f"GCP_REGION={cfg.region},"
            f"BACKEND_INIT_JOB={cfg.backend_init_job},"
            f"JOB_STEP_TIMEOUT_SECONDS={cfg.job_step_timeout_seconds},"
            f"JOB_POLL_INTERVAL_SECONDS={cfg.job_poll_interval_seconds}",
        ]
    )

    return run_command(
        [
            "gcloud",
            "functions",
            "describe",
            cfg.init_trigger_function_name,
            "--region",
            cfg.region,
            "--gen2",
            "--format=value(serviceConfig.uri)",
        ],
        capture_output=True,
    ).stdout.strip()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build and deploy California Accountability Panel Cloud Run resources. "
            "Default deploys all resources."
        )
    )
    parser.add_argument(
        "env_file",
        nargs="?",
        help="Optional path to environment file (defaults to script resolution).",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--init-trigger-only",
        action="store_true",
        help=(
            "Deploy only backend init resources "
            "(backend image + init job + init trigger function)."
        ),
    )
    mode_group.add_argument(
        "--full-only",
        action="store_true",
        help=(
            "Deploy only full service resources "
            "(backend image + frontend image + combined Cloud Run service)."
        ),
    )
    return parser.parse_args(argv)


def build_frontend_image(cfg: DeployConfig) -> None:
    print(
        f"Building frontend image {cfg.frontend_image} with VITE_API_URL={cfg.api_v1_str}"
    )
    content = (
        "steps:\n"
        "  - name: gcr.io/cloud-builders/docker\n"
        "    env:\n"
        "      - DOCKER_BUILDKIT=1\n"
        "    args:\n"
        "      - build\n"
        "      - -f\n"
        "      - frontend/Dockerfile\n"
        "      - -t\n"
        "      - ${_IMAGE}\n"
        "      - --build-arg\n"
        "      - VITE_API_URL=${_VITE_API_URL}\n"
        "      - .\n"
        "images:\n"
        "  - ${_IMAGE}\n"
    )
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        tmp.write(content)
        config_path = Path(tmp.name)

    try:
        run_command(
            [
                "gcloud",
                "builds",
                "submit",
                "--substitutions",
                f"_IMAGE={cfg.frontend_image},_VITE_API_URL={cfg.api_v1_str}",
                "--config",
                str(config_path),
                ".",
            ]
        )
    finally:
        config_path.unlink(missing_ok=True)


def deploy_combined_service(cfg: DeployConfig) -> tuple[str, str]:
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        rendered_path = Path(tmp.name)
    render_script = Path(__file__).resolve().parent / "render_cloud_run_service.py"

    try:
        env = os.environ.copy()
        env.update(
            {
                "FULL_SERVICE": cfg.full_service,
                "GCP_REGION": cfg.region,
                "RUN_SERVICE_ACCOUNT_EMAIL": cfg.run_service_account_email,
                "FRONTEND_IMAGE": cfg.frontend_image,
                "BACKEND_IMAGE": cfg.backend_image,
                "CLOUD_SQL_CONNECTION_NAME": cfg.cloud_sql_connection_name,
                "ENVIRONMENT": cfg.environment,
                "PROJECT_NAME": cfg.project_name,
                "API_V1_STR": cfg.api_v1_str,
                "BACKEND_CORS_ORIGINS": cfg.backend_cors_origins,
                "FRONTEND_HOST": cfg.frontend_host,
                "CLOUD_SQL_DB": cfg.cloud_sql_db,
                "CLOUD_SQL_USER": cfg.cloud_sql_user,
                "RUN_DATA_IMPORTS": cfg.run_data_imports,
                "RUN_STARTUP_DATA_IMPORTS": cfg.run_startup_data_imports,
                "IMPORT_GCS_URI": cfg.import_gcs_uri,
                "IMPORT_RESOURCES_LOCAL_PATH": cfg.import_resources_local_path,
                "VPC_NETWORK": cfg.vpc_network,
                "VPC_SUBNET": cfg.vpc_subnet,
            }
        )

        rendered = run_command(
            ["python", str(render_script)],
            env=env,
            capture_output=True,
            check=False,
        )
        if rendered.returncode != 0:
            details = (rendered.stderr or rendered.stdout or "").strip()
            msg = (
                "Failed to render Cloud Run service YAML via "
                f"{render_script} (exit {rendered.returncode})."
            )
            if details:
                msg = f"{msg}\n{details}"
            raise ScriptError(msg)
        rendered_path.write_text(rendered.stdout)

        run_command(
            [
                "gcloud",
                "run",
                "services",
                "replace",
                str(rendered_path),
                "--region",
                cfg.region,
            ]
        )
        run_command(
            [
                "gcloud",
                "run",
                "services",
                "add-iam-policy-binding",
                cfg.full_service,
                "--region",
                cfg.region,
                "--member",
                "allUsers",
                "--role",
                "roles/run.invoker",
            ]
        )

        service_url = run_command(
            [
                "gcloud",
                "run",
                "services",
                "describe",
                cfg.full_service,
                "--region",
                cfg.region,
                "--format=value(status.url)",
            ],
            capture_output=True,
        ).stdout.strip()

        function_url = run_command(
            [
                "gcloud",
                "functions",
                "describe",
                cfg.init_trigger_function_name,
                "--region",
                cfg.region,
                "--gen2",
                "--format=value(serviceConfig.uri)",
            ],
            capture_output=True,
        ).stdout.strip()
        return service_url, function_url
    finally:
        rendered_path.unlink(missing_ok=True)


def main() -> int:
    args = parse_args(sys.argv[1:])
    env_path = resolve_env_file(__file__, args.env_file)
    print(f"Loading environment from {env_path}")
    load_env_file(env_path)
    defaults = load_gcp_defaults(__file__)
    load_and_apply_env(defaults)

    original_environment = os.environ.get("ENVIRONMENT", "<unset>")
    cfg = build_config(defaults)

    print(f"Using project={cfg.project_id}, region={cfg.region}, tag={cfg.tag}")
    print(f"Using FRONTEND_HOST={cfg.frontend_host}")
    if original_environment != "production":
        print(
            f"Forcing ENVIRONMENT=production for Cloud Run deploy (was: {original_environment})"
        )

    run_command(["gcloud", "config", "set", "project", cfg.project_id])
    run_command(
        [
            "gcloud",
            "services",
            "enable",
            "run.googleapis.com",
            "cloudfunctions.googleapis.com",
            "eventarc.googleapis.com",
            "artifactregistry.googleapis.com",
            "cloudbuild.googleapis.com",
            "sqladmin.googleapis.com",
            "storage.googleapis.com",
        ]
    )

    ensure_bucket_exists(cfg.import_gcs_uri, cfg.region)
    maybe_sync_local_resources(cfg)

    if not cmd_exists(
        [
            "gcloud",
            "artifacts",
            "repositories",
            "describe",
            cfg.ar_repository,
            f"--location={cfg.region}",
        ]
    ):
        run_command(
            [
                "gcloud",
                "artifacts",
                "repositories",
                "create",
                cfg.ar_repository,
                f"--location={cfg.region}",
                "--repository-format=docker",
                "--description=Container images for California Accountability Panel services",
            ]
        )

    deploy_init_only = args.init_trigger_only
    deploy_full_only = args.full_only

    if deploy_init_only:
        print("Deploy mode: init-trigger-only")
        build_backend_image(cfg)
        deploy_init_job(cfg)
        function_url = deploy_trigger_function(cfg)
        print(f"Manual init trigger URL: {function_url}")
        print("Invoke with:")
        print(
            'curl -X POST -H "Authorization: Bearer '
            '$(gcloud auth print-identity-token)" '
            f'"{function_url}"'
        )
        print("Done.")
        return 0

    if deploy_full_only:
        print("Deploy mode: full-only")
        build_backend_image(cfg)
        build_frontend_image(cfg)
        full_service_url, function_url = deploy_combined_service(cfg)
        print(f"Full service URL: {full_service_url}")
        print(f"Manual init trigger URL (existing): {function_url}")
        print("Done.")
        return 0

    print("Deploy mode: all")
    build_backend_image(cfg)
    deploy_init_job(cfg)
    deploy_trigger_function(cfg)
    build_frontend_image(cfg)
    full_service_url, function_url = deploy_combined_service(cfg)

    print(f"Full service URL: {full_service_url}")
    print(f"Manual init trigger URL: {function_url}")
    print("Invoke with:")
    print(
        'curl -X POST -H "Authorization: Bearer '
        '$(gcloud auth print-identity-token)" '
        f'"{function_url}"'
    )
    print("Done.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
