#!/usr/bin/env python3
"""
Import California Dashboard indicator data from various sources.

Supports both CDE Excel files and state assessment TXT files.

Usage:
    # Import a single indicator from CDE Excel file
    python app/scripts/cde/import_indicators.py --indicator ELA --path ~/Downloads/resources/cde/eladownload2025.xlsx

    # Import all indicators from a CDE directory
    python app/scripts/cde/import_indicators.py --source cde --path ~/Downloads/resources/cde/

    # Import from state assessment files
    python app/scripts/cde/import_indicators.py --source state --indicator ELA --path ~/Desktop/resources/california-state/sb_ca2025_all_csv_ela_v1.txt

    # List available indicators
    python app/scripts/cde/import_indicators.py --list
"""

import argparse
import fnmatch
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session

from app.core.database import engine
from app.scripts.cde.base import BaseIndicatorParser
from app.scripts.cde.cde_parser import INDICATOR_FILES, CDEParser
from app.scripts.cde.import_plan import (
    ImportCategory,
    count_existing_rows,
    delete_category_rows,
    detect_reporting_year,
    render_ascii_table,
)
from app.scripts.cde.state_parser import STATE_FILES, StateParser
from app.scripts.gcp.gcp_utils import load_repo_env_if_present

load_repo_env_if_present(__file__, scope="import_indicators")


INDICATORS = ["ELA", "MATH", "SCI", "CHRONIC", "SUSP", "GRAD", "ELPI", "CCI"]


def _matches_year_filter(file_path: Path, years: set[str] | None) -> bool:
    if not years:
        return True
    name = file_path.name.lower()
    return any(year in name for year in years)


def _resolve_indicator_from_name(file_path: Path, source: str) -> str | None:
    file_name = file_path.name.lower()
    patterns = INDICATOR_FILES if source == "cde" else STATE_FILES
    for indicator, pattern in patterns.items():
        if fnmatch.fnmatch(file_name, pattern.lower()):
            return indicator
    return None


def _collect_categories(
    *,
    path: Path,
    source: str,
    indicator: str | None,
    all_files: bool,
    years: set[str] | None,
) -> list[ImportCategory]:
    categories: list[ImportCategory] = []

    def _append(file_path: Path, resolved_indicator: str) -> None:
        year = detect_reporting_year(file_path)
        categories.append(
            ImportCategory(
                source=source,
                indicator=resolved_indicator,
                reporting_year=year,
                path=str(file_path),
            )
        )

    if path.is_file():
        if not indicator:
            raise ValueError("--indicator is required when importing a single file")
        _append(path, indicator)
        return categories

    if source == "cde":
        selected_indicators = [indicator] if indicator else list(INDICATOR_FILES.keys())
        for indicator_code in selected_indicators:
            pattern = INDICATOR_FILES[indicator_code]
            files = sorted(path.glob(pattern))
            files = [f for f in files if _matches_year_filter(f, years)]
            if not files:
                continue
            selected_files = files if all_files else [files[-1]]
            for file_path in selected_files:
                _append(file_path, indicator_code)
        return categories

    selected_indicators = [indicator] if indicator else list(STATE_FILES.keys())
    for indicator_code in selected_indicators:
        pattern = STATE_FILES[indicator_code]
        files = sorted(path.glob(pattern))
        files = [f for f in files if _matches_year_filter(f, years)]
        if not files:
            continue
        selected_files = files if all_files else [files[-1]]
        for file_path in selected_files:
            _append(file_path, indicator_code)

    return categories


def _print_categories_report(title: str, categories: list[ImportCategory]) -> None:
    rows = [
        [
            c.source,
            c.indicator,
            c.reporting_year,
            str(c.existing_rows),
            c.action,
            c.status,
            str(c.imported_rows),
            str(c.deleted_rows),
            c.message,
            c.path,
        ]
        for c in categories
    ]
    print(f"\n{title}")
    if not rows:
        print("No matching files/categories found.")
        return
    print(
        render_ascii_table(
            [
                "source",
                "indicator",
                "year",
                "existing_rows",
                "action",
                "status",
                "imported_rows",
                "deleted_rows",
                "message",
                "path",
            ],
            rows,
        )
    )


def import_single_file(
    file_path: Path, indicator: str, source: str = "cde", batch_size: int = 5000
) -> int:
    """Import a single file.

    Args:
        file_path: Path to the file
        indicator: Indicator code
        source: 'cde' or 'state'
        batch_size: Records per batch

    Returns:
        Number of records imported
    """
    parser: BaseIndicatorParser
    if source == "cde":
        parser = CDEParser(indicator)
        parse_method = parser.parse_excel
    else:
        parser = StateParser(indicator)
        parse_method = parser.parse_txt

    print(f"\nImporting {indicator} from {file_path}")
    print(f"Source: {source.upper()}")

    with Session(engine) as session:
        records = parse_method(file_path)
        count = parser.import_to_session(session, records, batch_size)

    print(f"Successfully imported {count} records for {indicator}")
    return int(count)


def import_cde_directory(
    dir_path: Path,
    batch_size: int = 1000,
    workers: int = 4,
    *,
    all_files: bool = False,
    years: set[str] | None = None,
) -> dict[str, int]:
    """Import all CDE files from a directory.

    Args:
        dir_path: Directory containing CDE Excel files
        batch_size: Records per batch

    Returns:
        dict mapping indicator to record count
    """
    results: dict[str, int] = {}

    jobs: list[tuple[str, Path]] = []
    for indicator, pattern in INDICATOR_FILES.items():
        # Find matching files
        files = sorted(dir_path.glob(pattern))
        files = [f for f in files if _matches_year_filter(f, years)]
        if not files:
            print(f"\nNo files found for {indicator} (pattern: {pattern})")
            continue

        selected_files = files if all_files else [files[-1]]
        for file_path in selected_files:
            jobs.append((indicator, file_path))

    if not jobs:
        return results

    imported_totals = dict.fromkeys(INDICATOR_FILES, 0)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_to_job = {
            executor.submit(
                import_single_file, file_path, indicator, "cde", batch_size
            ): (indicator, file_path)
            for indicator, file_path in jobs
        }
        for future in as_completed(future_to_job):
            indicator, file_path = future_to_job[future]
            try:
                count = future.result()
                imported_totals[indicator] = imported_totals.get(indicator, 0) + count
            except Exception as e:
                print(f"Error importing {indicator} from {file_path.name}: {e}")

    results.update({k: v for k, v in imported_totals.items() if v > 0})

    return results


def import_state_directory(
    dir_path: Path,
    indicators: list[str] | None = None,
    batch_size: int = 1000,
    workers: int = 4,
) -> dict[str, int]:
    """Import state assessment files from a directory.

    Args:
        dir_path: Directory containing state TXT files
        indicators: List of indicators to import (default: all)
        batch_size: Records per batch

    Returns:
        dict mapping indicator to record count
    """
    results: dict[str, int] = {}
    indicators = indicators or list(STATE_FILES.keys())

    jobs: list[tuple[str, Path]] = []
    for indicator in indicators:
        if indicator not in STATE_FILES:
            print(f"\nNo state file pattern for {indicator}")
            continue

        pattern = STATE_FILES[indicator]
        files = list(dir_path.glob(pattern))
        if not files:
            print(f"\nNo files found for {indicator} (pattern: {pattern})")
            continue

        # Use the most recent file if multiple exist
        file_path = sorted(files)[-1]
        jobs.append((indicator, file_path))

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_to_indicator = {
            executor.submit(
                import_single_file, file_path, indicator, "state", batch_size
            ): indicator
            for indicator, file_path in jobs
        }
        for future in as_completed(future_to_indicator):
            indicator = future_to_indicator[future]
            try:
                results[indicator] = future.result()
            except Exception as e:
                print(f"Error importing {indicator}: {e}")
                results[indicator] = 0

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import California Dashboard indicator data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--indicator",
        "-i",
        choices=INDICATORS,
        help="Specific indicator to import",
    )
    parser.add_argument(
        "--source",
        "-s",
        choices=["cde", "state"],
        default="cde",
        help="Data source type (default: cde)",
    )
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        help="Path to file or directory",
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=5000,
        help="Records per batch (default: 5000)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Thread workers for parallel file imports (default: 4).",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available indicators",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Import all matching files in a directory (default imports only latest).",
    )
    parser.add_argument(
        "--years",
        help="Comma-separated year filters for file names, e.g. 2024,2025.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing rows for each category (indicator + reporting year).",
    )

    args = parser.parse_args()

    if args.list:
        print("Available indicators:")
        print("\nCDE Excel files (--source cde):")
        for ind, pattern in INDICATOR_FILES.items():
            print(f"  {ind}: {pattern}")
        print("\nState assessment files (--source state):")
        for ind, pattern in STATE_FILES.items():
            print(f"  {ind}: {pattern}")
        return

    if not args.path:
        parser.error("--path is required")

    path = args.path.expanduser().resolve()
    if not path.exists():
        print(f"Error: Path not found: {path}")
        sys.exit(1)

    years_filter: set[str] | None = None
    if args.years:
        years_filter = {y.strip() for y in args.years.split(",") if y.strip()}

    if not path.is_file() and not path.is_dir():
        print(f"Error: Invalid path: {path}")
        sys.exit(1)

    try:
        categories = _collect_categories(
            path=path,
            source=args.source,
            indicator=args.indicator,
            all_files=args.all_files,
            years=years_filter,
        )
    except ValueError as exc:
        parser.error(str(exc))

    if not categories and path.is_file():
        # Fallback for explicit file names that do not match known glob patterns.
        resolved_indicator = args.indicator or _resolve_indicator_from_name(
            path, args.source
        )
        if not resolved_indicator:
            parser.error(
                "--indicator is required when indicator cannot be inferred from filename"
            )
        categories = [
            ImportCategory(
                source=args.source,
                indicator=resolved_indicator,
                reporting_year=detect_reporting_year(path),
                path=str(path),
            )
        ]

    with Session(engine) as session:
        for category in categories:
            category.existing_rows = count_existing_rows(
                session,
                indicator=category.indicator,
                reporting_year=category.reporting_year,
            )
            if category.existing_rows > 0:
                category.action = "overwrite" if args.overwrite else "skip_existing"
            else:
                category.action = "import"

    _print_categories_report("Import Plan", categories)

    total_imported = 0
    to_import: list[ImportCategory] = []
    try:
        with Session(engine) as session:
            for category in categories:
                file_path = Path(category.path)
                if not file_path.exists():
                    category.status = "missing"
                    category.message = "file not found"
                    continue

                if category.existing_rows > 0 and not args.overwrite:
                    category.status = "skipped"
                    category.message = "existing data found; rerun with --overwrite"
                    continue

                if category.existing_rows > 0 and args.overwrite:
                    category.deleted_rows = delete_category_rows(
                        session,
                        indicator=category.indicator,
                        reporting_year=category.reporting_year,
                    )

                category.status = "queued"
                category.message = "waiting for worker"
                to_import.append(category)

        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            future_to_category = {
                executor.submit(
                    import_single_file,
                    Path(category.path),
                    category.indicator,
                    args.source,
                    args.batch_size,
                ): category
                for category in to_import
            }
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                category.status = "running"
                try:
                    imported = future.result()
                    category.imported_rows = imported
                    category.status = "imported"
                    category.message = "completed"
                    total_imported += imported
                except Exception as exc:
                    category.status = "failed"
                    category.message = str(exc)
    finally:
        _print_categories_report("Import Result", categories)

    print(f"\nTotal imported rows: {total_imported:,}")


if __name__ == "__main__":
    main()
