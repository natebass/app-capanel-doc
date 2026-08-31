"""Import California School Dashboard indicator files.

By default the files are read straight from the state's web server, so a fresh
database can be filled without downloading anything by hand::

    uv run app/scripts/ingest_dashboard_files.py --year 2025

Point ``--source`` at a directory or an ``s3://`` prefix to load from a local
copy instead.  Files already loaded are skipped unless their entity tag or
size has changed, which is how the state's in-place revisions are picked up.
"""

from __future__ import annotations

import argparse
import logging
import sys

from sqlalchemy import create_engine

from app.core.config import settings
from app.ingest.dashboard_loader import DashboardImportRunner
from app.ingest.sources import DASHBOARD_BASE_URL, DASHBOARD_FILE_STEMS
from app.model.ingest import IngestStatus

logger = logging.getLogger("app.ingest.dashboard")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default=None,
        help=(
            "Where to read from: a directory, an s3:// prefix or an https:// "
            f"base URL.  Defaults to {DASHBOARD_BASE_URL}"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reload files even when their fingerprint is unchanged.",
    )
    parser.add_argument(
        "--only",
        action="append",
        metavar="INDICATOR",
        help=(
            "Load only files whose name contains this, repeatable.  "
            f"Known indicators: {', '.join(DASHBOARD_FILE_STEMS)}"
        ),
    )
    parser.add_argument(
        "--year",
        action="append",
        type=int,
        dest="years",
        help="Reporting year to load, repeatable.  Defaults to every year.",
    )
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
    engine = create_engine(str(settings.DATABASE_URL))
    runner = DashboardImportRunner(engine)
    outcome = runner.run(source, force=args.force, only=args.only, years=args.years)

    for file_outcome in outcome.files:
        logger.info(
            "%-28s %-9s %8s rows %6.1fs %s",
            file_outcome.name,
            file_outcome.status.value,
            f"{file_outcome.results:,}",
            file_outcome.duration_seconds,
            file_outcome.error or "",
        )
    logger.info(
        "run %s %s: %s files, %s rows",
        outcome.run_id,
        outcome.status.value,
        len(outcome.files),
        f"{outcome.results:,}",
    )
    return 0 if outcome.status is not IngestStatus.FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
