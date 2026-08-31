"""Import the LCFF Local Indicators -- the local half of the Dashboard.

By default the spreadsheets are read straight from the state's web server::

    uv run app/scripts/ingest_local_indicators.py --year 2025

Spreadsheets rather than the text exports, because the text versions flatten
the paragraph breaks out of the narrative fields.  Pass ``--text`` to use them
anyway, or ``--source`` to read from a local directory or an ``s3://`` prefix.
"""

from __future__ import annotations

import argparse
import logging
import sys

from sqlalchemy import create_engine

from app.core.config import settings
from app.ingest.local_indicator_loader import LocalIndicatorImportRunner
from app.ingest.local_indicator_reference import PRIORITY_NUMBERS
from app.ingest.sources import DASHBOARD_BASE_URL
from app.model.ingest import IngestStatus

logger = logging.getLogger("app.ingest.local_indicators")


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
        "--year",
        action="append",
        type=int,
        dest="years",
        help="Reporting year to load, repeatable.  Defaults to every year.",
    )
    parser.add_argument(
        "--priority",
        action="append",
        type=int,
        dest="priorities",
        choices=PRIORITY_NUMBERS,
        help="LCFF priority to load, repeatable.  Defaults to all seven.",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Read the .txt exports instead of the spreadsheets.  Faster, but "
        "narrative paragraph breaks are lost.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reload files even when their fingerprint is unchanged.",
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
    runner = LocalIndicatorImportRunner(engine)
    if args.text:
        runner.suffix = ".txt"
    outcome = runner.run(
        source,
        force=args.force,
        years=args.years,
        priorities=args.priorities,
    )

    for file_outcome in outcome.files:
        logger.info(
            "%-18s %-9s %7s rows %6.1fs %s",
            file_outcome.name,
            file_outcome.status.value,
            f"{file_outcome.rows:,}",
            file_outcome.duration_seconds,
            file_outcome.error or "",
        )
    logger.info(
        "run %s %s: %s files, %s rows",
        outcome.run_id,
        outcome.status.value,
        len(outcome.files),
        f"{outcome.rows:,}",
    )
    return 0 if outcome.status is not IngestStatus.FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
