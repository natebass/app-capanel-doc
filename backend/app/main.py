import os
import subprocess
import sys
import threading
from pathlib import Path

import httpx
import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlalchemy import func, text
from sqlmodel import Session, select
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.database import engine
from app.model.academic_indicator import AcademicIndicator

IMPORT_LOCK_KEY = 580083315


def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _sync_resources(gcs_uri: str, destination: Path) -> int:
    from app.scripts.sync_gcs_resources import (
        download_objects,
        get_access_token,
        list_objects,
        parse_gs_uri,
    )

    destination.mkdir(parents=True, exist_ok=True)
    bucket, prefix = parse_gs_uri(gcs_uri)
    with httpx.Client(follow_redirects=True) as client:
        token = get_access_token(client)
        objects = list_objects(client, token, bucket, prefix)
        return download_objects(client, token, bucket, prefix, destination, objects)


def _academic_indicator_count() -> int:
    with Session(engine) as session:
        count = session.exec(select(func.count()).select_from(AcademicIndicator)).one()
        return int(count or 0)


def _parse_years(raw: str) -> set[str] | None:
    years = {y.strip() for y in raw.split(",") if y.strip()}
    return years or None


def _run_data_import_pipeline() -> None:
    if not _env_bool("RUN_DATA_IMPORTS", True):
        print("RUN_DATA_IMPORTS is disabled; skipping startup data import pipeline")
        return

    gcs_uri = os.getenv("IMPORT_GCS_URI", "gs://ca-panel-001-resources/resources")
    resources_dir = Path(os.getenv("IMPORT_RESOURCES_LOCAL_PATH", "/tmp/resources"))
    downloaded = _sync_resources(gcs_uri, resources_dir)
    print(f"Synced {downloaded} object(s) from {gcs_uri} to {resources_dir}")

    existing_count = _academic_indicator_count()
    if existing_count > 0:
        print(
            "academic_indicator already populated "
            f"({existing_count} rows); skipping import steps"
        )
        return

    from app.scripts.import_ela_data import import_ela_data

    ela_batch_size = int(os.getenv("IMPORT_ELA_BATCH_SIZE", "1000"))
    ela_files_env = os.getenv("IMPORT_ELA_FILES", "").strip()
    if ela_files_env:
        ela_files = [Path(p.strip()) for p in ela_files_env.split(",") if p.strip()]
    else:
        ela_file = Path(
            os.getenv(
                "IMPORT_ELA_DATA_FILE",
                str(resources_dir / "cde" / "eladownload2025.xlsx"),
            )
        )
        ela_files = [ela_file]

    for ela_path in ela_files:
        if ela_path.exists():
            print(f"Importing ELA data from {ela_path}")
            import_ela_data(str(ela_path), batch_size=ela_batch_size)
        else:
            print(f"ELA file not found at {ela_path}; skipping")

    source = os.getenv("IMPORT_INDICATORS_SOURCE", "cde").strip().lower()
    indicators_path = Path(
        os.getenv("IMPORT_INDICATORS_PATH", str(resources_dir / "cde"))
    ).expanduser()
    batch_size = int(os.getenv("IMPORT_INDICATORS_BATCH_SIZE", "1000"))
    years_filter = _parse_years(os.getenv("IMPORT_INDICATORS_YEARS", "2024,2025"))
    indicator = os.getenv("IMPORT_INDICATORS_INDICATOR", "").strip().upper()
    indicators = [indicator] if indicator else None

    if not indicators_path.exists():
        print(
            f"Indicators path not found at {indicators_path}; skipping indicators import"
        )
        return

    command = [
        sys.executable,
        "app/scripts/import_indicators.py",
        "--source",
        source,
        "--path",
        str(indicators_path),
        "--batch-size",
        str(batch_size),
        "--all-files",
    ]
    if indicators:
        command.extend(["--indicator", indicators[0]])
    if years_filter:
        command.extend(["--years", ",".join(sorted(years_filter))])

    subprocess.run(command, check=True)
    print("Indicators import completed")


def _run_data_import_pipeline_with_lock() -> None:
    db_uri = settings.SQLALCHEMY_DATABASE_URI.lower()
    if not db_uri.startswith("postgresql"):
        # Advisory locks are PostgreSQL-specific.
        _run_data_import_pipeline()
        return

    with engine.connect() as conn:
        acquired = bool(
            conn.execute(
                text("SELECT pg_try_advisory_lock(:lock_key)"),
                {"lock_key": IMPORT_LOCK_KEY},
            ).scalar_one()
        )
        if not acquired:
            print("Another instance is running startup data import; skipping this run")
            return

        try:
            _run_data_import_pipeline()
        finally:
            conn.execute(
                text("SELECT pg_advisory_unlock(:lock_key)"),
                {"lock_key": IMPORT_LOCK_KEY},
            )


@app.on_event("startup")
def startup_data_import() -> None:
    if not _env_bool("RUN_STARTUP_DATA_IMPORTS", False):
        print("RUN_STARTUP_DATA_IMPORTS is disabled; skipping startup data import")
        return

    if _env_bool("RUN_DATA_IMPORTS_BLOCKING", False):
        _run_data_import_pipeline_with_lock()
        return

    thread = threading.Thread(
        target=_run_data_import_pipeline_with_lock,
        name="startup-data-import",
        daemon=True,
    )
    thread.start()
