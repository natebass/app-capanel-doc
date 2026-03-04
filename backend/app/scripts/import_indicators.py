#!/usr/bin/env python3
"""
Import California Dashboard indicator data from various sources.

Supports both CDE Excel files and state assessment TXT files.

Usage:
    # Import a single indicator from CDE Excel file
    python app/scripts/import_indicators.py --indicator ELA --path ~/Downloads/resources/cde/eladownload2025.xlsx

    # Import all indicators from a CDE directory
    python app/scripts/import_indicators.py --source cde --path ~/Downloads/resources/cde/

    # Import from state assessment files
    python app/scripts/import_indicators.py --source state --indicator ELA --path ~/Desktop/resources/california-state/sb_ca2025_all_csv_ela_v1.txt

    # List available indicators
    python app/scripts/import_indicators.py --list
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from importers.cde_parser import INDICATOR_FILES, CDEParser  # type: ignore
from importers.state_parser import STATE_FILES, StateParser  # type: ignore
from sqlmodel import Session

from app.core.database import engine

INDICATORS = ["ELA", "MATH", "SCI", "CHRONIC", "SUSP", "GRAD", "ELPI", "CCI"]


def _matches_year_filter(file_path: Path, years: set[str] | None) -> bool:
    if not years:
        return True
    name = file_path.name.lower()
    return any(year in name for year in years)


def import_single_file(
    file_path: Path, indicator: str, source: str = "cde", batch_size: int = 1000
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
    results = {}

    for indicator, pattern in INDICATOR_FILES.items():
        # Find matching files
        files = sorted(dir_path.glob(pattern))
        files = [f for f in files if _matches_year_filter(f, years)]
        if not files:
            print(f"\nNo files found for {indicator} (pattern: {pattern})")
            continue

        selected_files = files if all_files else [files[-1]]
        imported_count = 0
        for file_path in selected_files:
            try:
                count = import_single_file(file_path, indicator, "cde", batch_size)
                imported_count += count
            except Exception as e:
                print(f"Error importing {indicator} from {file_path.name}: {e}")
        results[indicator] = imported_count

    return results


def import_state_directory(
    dir_path: Path, indicators: list[str] | None = None, batch_size: int = 1000
) -> dict[str, int]:
    """Import state assessment files from a directory.

    Args:
        dir_path: Directory containing state TXT files
        indicators: List of indicators to import (default: all)
        batch_size: Records per batch

    Returns:
        dict mapping indicator to record count
    """
    results = {}
    indicators = indicators or list(STATE_FILES.keys())

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
        try:
            count = import_single_file(file_path, indicator, "state", batch_size)
            results[indicator] = count
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
        default=1000,
        help="Records per batch (default: 1000)",
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

    if path.is_file():
        # Import single file
        if not args.indicator:
            parser.error("--indicator is required when importing a single file")
        import_single_file(path, args.indicator, args.source, args.batch_size)

    elif path.is_dir():
        # Import directory
        print(f"Importing from directory: {path}")
        if args.source == "cde":
            results = import_cde_directory(
                path,
                args.batch_size,
                all_files=args.all_files,
                years=years_filter,
            )
        else:
            indicators = [args.indicator] if args.indicator else None
            results = import_state_directory(path, indicators, args.batch_size)

        print("\n" + "=" * 50)
        print("Import Summary:")
        print("=" * 50)
        total = 0
        for indicator, count in sorted(results.items()):
            print(f"  {indicator}: {count:,} records")
            total += count
        print("-" * 50)
        print(f"  TOTAL: {total:,} records")

    else:
        print(f"Error: Invalid path: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
