"""Command line entry point for importing CAASPP and ELPAC research files.

Examples:
    Load everything under the configured source::

        uv run app/scripts/ingest_research_files.py

    Load one administration from a bucket, ignoring the manifest::

        uv run app/scripts/ingest_research_files.py \\
            --source s3://ca-panel-resources/research-files \\
            --year 2025 --force

    Refresh only the reference tables::

        uv run app/scripts/ingest_research_files.py --seed-only
"""

from __future__ import annotations

import argparse
import logging
import sys

from sqlmodel import Session

from app.core.config import settings
from app.core.database import engine
from app.ingest.reference_data import seed_reference_data
from app.ingest.runner import ImportRunner
from app.model.ingest import IngestStatus

logger = logging.getLogger("app.ingest")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default=settings.RESEARCH_FILE_SOURCE_URI,
        help="Directory path or s3://bucket/prefix holding the research files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reload files even if their size and entity tag are unchanged.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=None,
        metavar="FRAGMENT",
        help="Only load files whose name contains this text. Repeatable.",
    )
    parser.add_argument(
        "--year",
        action="append",
        type=int,
        dest="years",
        default=None,
        help="Restrict to an administration year, e.g. --year 2025. Repeatable.",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Refresh the reference tables and exit without loading results.",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Only report warnings and errors."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
    )

    if args.seed_only:
        with Session(engine) as session:
            seed_reference_data(session)
        logger.info("reference data seeded")
        return 0

    if not args.source:
        print(
            "No research file source configured. Pass --source or set "
            "RESEARCH_FILE_SOURCE_URI.",
            file=sys.stderr,
        )
        return 2

    outcome = ImportRunner(engine).run(
        args.source, force=args.force, only=args.only, years=args.years
    )
    for file_outcome in outcome.files:
        logger.info(
            "%-9s %-34s %8s results %8s subscores %s",
            file_outcome.status.value,
            file_outcome.name,
            f"{file_outcome.results:,}",
            f"{file_outcome.subscores:,}",
            file_outcome.error or "",
        )
    logger.info(
        "run %s finished: %s (%s result rows, %s subscore rows)",
        outcome.run_id,
        outcome.status.value,
        f"{outcome.results:,}",
        f"{outcome.subscores:,}",
    )
    return 0 if outcome.status is IngestStatus.SUCCEEDED else 1


if __name__ == "__main__":
    raise SystemExit(main())
