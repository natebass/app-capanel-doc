"""Startup data-import pipeline.

Orchestrates syncing resources from Google Cloud Storage and importing
academic-indicator data (ELA scores, CDE indicators) into the database.
The pipeline is designed to run once on application startup, optionally
guarded by a PostgreSQL advisory lock to prevent concurrent imports
across multiple instances.
"""

import os
import subprocess
import sys
import threading
from pathlib import Path

import httpx
from sqlalchemy import func, text
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import engine
from app.core.utils import env_bool, parse_csv_set
from app.model.academic_indicator import AcademicIndicator

IMPORT_LOCK_KEY = 580083315
"""PostgreSQL advisory-lock key used to serialise concurrent imports."""


def sync_resources(gcs_uri: str, destination: Path) -> int:
    """Download objects from a Google Cloud Storage URI to a local directory.

    The *destination* directory is created if it does not already exist.
    Uses :mod:`app.scripts.gcp.sync_gcs_resources` for the actual GCS
    interaction.

    Args:
        gcs_uri: A ``gs://`` URI pointing to the source bucket/prefix.
        destination: Local directory to write the downloaded objects into.

    Returns:
        The number of objects downloaded.
    """
    from app.scripts.gcp.sync_gcs_resources import (
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


def academic_indicator_count() -> int:
    """Return the number of rows currently in the ``academic_indicator`` table.

    Returns:
        Row count as an integer (``0`` if the table is empty).
    """
    with Session(engine) as session:
        count = session.exec(select(func.count()).select_from(AcademicIndicator)).one()
        return int(count or 0)


def run_data_import_pipeline() -> None:
    """Execute the full data-import pipeline.

    Steps performed (in order):

    1. Sync resources from GCS to a local directory.
    2. Skip remaining steps if the ``academic_indicator`` table is already
       populated.
    3. Import ELA data from Excel files.
    4. Import CDE indicator data via a subprocess.

    The pipeline can be disabled entirely by setting the
    ``RUN_DATA_IMPORTS`` environment variable to a falsy value.
    """
    if not env_bool("RUN_DATA_IMPORTS", True):
        print("RUN_DATA_IMPORTS is disabled; skipping startup data import pipeline")
        return

    gcs_uri = os.getenv("IMPORT_GCS_URI", "")
    resources_dir = Path(os.getenv("IMPORT_RESOURCES_LOCAL_PATH", "/tmp/resources"))
    downloaded = sync_resources(gcs_uri, resources_dir)
    print(f"Synced {downloaded} object(s) from {gcs_uri} to {resources_dir}")

    existing_count = academic_indicator_count()
    if existing_count > 0:
        print(
            "academic_indicator already populated "
            f"({existing_count} rows); skipping import steps"
        )
        return

    _import_ela_data(resources_dir)
    _import_indicators(resources_dir)


def _import_ela_data(resources_dir: Path) -> None:
    """Import ELA data from one or more Excel files.

    File paths are resolved from the ``IMPORT_ELA_FILES`` or
    ``IMPORT_ELA_DATA_FILE`` environment variables.  Falls back to
    ``<resources_dir>/cde/eladownload2025.xlsx``.

    Args:
        resources_dir: Base directory where synced resources are stored.
    """
    from app.scripts.cde.import_ela_data import import_ela_data

    ela_batch_size = int(os.getenv("IMPORT_ELA_BATCH_SIZE", "5000"))
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


def _import_indicators(resources_dir: Path) -> None:
    """Import CDE indicator data by invoking the import script as a subprocess.

    Configuration is read from environment variables prefixed with
    ``IMPORT_INDICATORS_``.

    Args:
        resources_dir: Base directory where synced resources are stored.
    """
    source = os.getenv("IMPORT_INDICATORS_SOURCE", "cde").strip().lower()
    indicators_path = Path(
        os.getenv("IMPORT_INDICATORS_PATH", str(resources_dir / "cde"))
    ).expanduser()
    batch_size = int(os.getenv("IMPORT_INDICATORS_BATCH_SIZE", "5000"))
    years_filter = parse_csv_set(os.getenv("IMPORT_INDICATORS_YEARS", "2024,2025"))
    indicator = os.getenv("IMPORT_INDICATORS_INDICATOR", "").strip().upper()
    indicators = [indicator] if indicator else None

    if not indicators_path.exists():
        print(
            f"Indicators path not found at {indicators_path}; "
            "skipping indicators import"
        )
        return

    command = [
        sys.executable,
        "app/scripts/cde/import_indicators.py",
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


def run_data_import_pipeline_with_lock() -> None:
    """Run the data-import pipeline with a PostgreSQL advisory lock.

    On non-PostgreSQL databases the pipeline is executed directly without
    locking.  On PostgreSQL, ``pg_try_advisory_lock`` is used so that
    only one application instance performs the import at a time.
    """
    db_uri = settings.SQLALCHEMY_DATABASE_URI.lower()
    if not db_uri.startswith("postgresql"):
        run_data_import_pipeline()
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
            run_data_import_pipeline()
        finally:
            conn.execute(
                text("SELECT pg_advisory_unlock(:lock_key)"),
                {"lock_key": IMPORT_LOCK_KEY},
            )


def startup_data_import() -> None:
    """Entry point called from the application lifespan to trigger data imports.

    Behaviour is controlled by two environment variables:

    * ``RUN_STARTUP_DATA_IMPORTS`` — master switch (default ``False``).
    * ``RUN_DATA_IMPORTS_BLOCKING`` — when ``True``, the import runs
      synchronously on the main thread; otherwise it runs in a daemon
      thread so the application can start accepting requests immediately.
    """
    if not env_bool("RUN_STARTUP_DATA_IMPORTS", False):
        print("RUN_STARTUP_DATA_IMPORTS is disabled; skipping startup data import")
        return

    if env_bool("RUN_DATA_IMPORTS_BLOCKING", False):
        run_data_import_pipeline_with_lock()
        return

    thread = threading.Thread(
        target=run_data_import_pipeline_with_lock,
        name="startup-data-import",
        daemon=True,
    )
    thread.start()
