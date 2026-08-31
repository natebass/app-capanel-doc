"""Import the Census Day enrolment files.

These give each entity's total enrolment and the size of every student group
inside it, which is the context the accountability pages otherwise lack: a
Dashboard result can say a group was not rated without saying whether that
group is eighteen students or eighteen thousand.

    uv run app/scripts/ingest_enrollment.py
"""

from __future__ import annotations

import argparse
import logging
import sys

from sqlalchemy import create_engine

from app.core.config import settings
from app.ingest.enrollment_loader import EnrollmentImportRunner
from app.ingest.sources import DASHBOARD_BASE_URL
from app.model.ingest import IngestStatus

logger = logging.getLogger("app.ingest.enrollment")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", default=None, help="Directory, s3:// or https:// base URL."
    )
    parser.add_argument(
        "--year",
        action="append",
        type=int,
        dest="years",
        help="Reporting year, repeatable.",
    )
    parser.add_argument("--force", action="store_true", help="Reload unchanged files.")
    parser.add_argument("--quiet", action="store_true", help="Log warnings only.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    source = args.source or getattr(
        settings, "DASHBOARD_FILE_SOURCE_URI", DASHBOARD_BASE_URL
    )
    runner = EnrollmentImportRunner(create_engine(str(settings.DATABASE_URL)))
    outcome = runner.run(source, force=args.force, years=args.years)
    for file_outcome in outcome.files:
        logger.info(
            "%-36s %-9s %8s rows %6.1fs %s",
            file_outcome.name,
            file_outcome.status.value,
            f"{file_outcome.rows:,}",
            file_outcome.duration_seconds,
            file_outcome.error or "",
        )
    logger.info(
        "run %s %s: %s rows", outcome.run_id, outcome.status.value, f"{outcome.rows:,}"
    )
    return 0 if outcome.status is not IngestStatus.FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
