#!/usr/bin/env python3
"""
Import California Dashboard ELA Academic Indicator data from Excel file.

Usage:
    cd backend
    source ../.venv/bin/activate
    python scripts/import_ela_data.py ~/Downloads/resources/eladownload2025.xlsx
"""

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd  # type: ignore[import-untyped]
from sqlmodel import Session

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from app.model.academic_indicator import AcademicIndicator
from app.scripts.cde.import_plan import (
    ImportCategory,
    count_existing_rows,
    delete_category_rows,
    detect_reporting_year,
    render_ascii_table,
)
from app.scripts.gcp.gcp_utils import load_repo_env_if_present

load_repo_env_if_present(__file__, scope="import_ela_data")

# Column mapping from Excel to model fields (lowercase)
COLUMN_MAPPING = {
    "cds": "cds",
    "rtype": "rtype",
    "schoolname": "schoolname",
    "districtname": "districtname",
    "countyname": "countyname",
    "charter_flag": "charter_flag",
    "coe_flag": "coe_flag",
    "dass_flag": "dass_flag",
    "studentgroup": "studentgroup",
    "currdenom": "currdenom",
    "currstatus": "currstatus",
    "priordenom": "priordenom",
    "priorstatus": "priorstatus",
    "change": "change",
    "statuslevel": "statuslevel",
    "changelevel": "changelevel",
    "color": "color",
    "box": "box",
    "currnsizemet": "currnsizemet",
    "priornsizemet": "priornsizemet",
    "accountabilitymet": "accountabilitymet",
    "hscutpoints": "hscutpoints",
    "pairshare_method": "pairshare_method",
    "currprate_enrolled": "currprate_enrolled",
    "currprate_tested": "currprate_tested",
    "currprate": "currprate",
    "currnumprloss": "currnumprloss",
    "currdenom_withoutprloss": "currdenom_withoutprloss",
    "currstatus_withoutprloss": "currstatus_withoutprloss",
    "priorprate_enrolled": "priorprate_enrolled",
    "priorprate_tested": "priorprate_tested",
    "priorprate": "priorprate",
    "priornumprloss": "priornumprloss",
    "priordenom_withoutprloss": "priordenom_withoutprloss",
    "priorstatus_withoutprloss": "priorstatus_withoutprloss",
    "indicator": "indicator",
    "reportingyear": "reportingyear",
}


def clean_value(value: Any, field_type: str = "str") -> Any:
    """Clean a value for database insertion."""
    if pd.isna(value) or value == "" or value == "*":
        return None

    if field_type == "int":
        try:
            return int(float(value))
        except ValueError, TypeError:
            return None
    elif field_type == "float":
        try:
            return float(value)
        except ValueError, TypeError:
            return None
    else:
        return str(value).strip() if value else None


def _print_report(title: str, category: ImportCategory) -> None:
    rows = [
        [
            category.source,
            category.indicator,
            category.reporting_year,
            str(category.existing_rows),
            category.action,
            category.status,
            str(category.imported_rows),
            str(category.deleted_rows),
            category.message,
            category.path,
        ]
    ]
    print(f"\n{title}")
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


def import_ela_data(
    file_path: str,
    batch_size: int = 1000,
    *,
    overwrite: bool = False,
    reporting_year: str | None = None,
) -> int:
    """Import ELA data from Excel file into the database."""
    resolved_path = Path(file_path).expanduser().resolve()
    if reporting_year:
        year = reporting_year
    else:
        year = detect_reporting_year(resolved_path)

    category = ImportCategory(
        source="cde",
        indicator="ELA",
        reporting_year=year,
        path=str(resolved_path),
    )

    with Session(engine) as session:
        category.existing_rows = count_existing_rows(
            session,
            indicator=category.indicator,
            reporting_year=category.reporting_year,
        )

    category.action = (
        "overwrite"
        if (category.existing_rows > 0 and overwrite)
        else ("skip_existing" if category.existing_rows > 0 else "import")
    )
    _print_report("ELA Import Plan", category)

    if category.existing_rows > 0 and not overwrite:
        category.status = "skipped"
        category.message = "existing data found; rerun with --overwrite"
        _print_report("ELA Import Result", category)
        return 0

    print(f"Reading Excel file: {resolved_path}")
    df = pd.read_excel(resolved_path)

    # Normalize column names to lowercase
    df.columns = df.columns.str.lower()

    print(f"Found {len(df)} rows in Excel file")
    print(f"Columns: {list(df.columns)}")

    # Define field types
    int_fields = {
        "currdenom",
        "priordenom",
        "statuslevel",
        "changelevel",
        "color",
        "box",
        "currprate_enrolled",
        "currprate_tested",
        "currnumprloss",
        "currdenom_withoutprloss",
        "priorprate_enrolled",
        "priorprate_tested",
        "priornumprloss",
        "priordenom_withoutprloss",
    }
    float_fields = {
        "currstatus",
        "priorstatus",
        "change",
        "currprate",
        "currstatus_withoutprloss",
        "priorprate",
        "priorstatus_withoutprloss",
    }

    records = []
    skipped = 0

    for idx, row in df.iterrows():
        try:
            record_data = {}

            for excel_col, model_field in COLUMN_MAPPING.items():
                if excel_col in df.columns:
                    if model_field in int_fields:
                        record_data[model_field] = clean_value(row[excel_col], "int")
                    elif model_field in float_fields:
                        record_data[model_field] = clean_value(row[excel_col], "float")
                    else:
                        record_data[model_field] = clean_value(row[excel_col], "str")

            # Ensure required fields are present
            # Handle statewide aggregate (rtype = 'X') where CDS might be missing/empty in Excel
            if not record_data.get("cds") and record_data.get("rtype") == "X":
                record_data["cds"] = "00000000000000"

            if not record_data.get("cds") or not record_data.get("studentgroup"):
                skipped += 1
                continue

            # Set defaults for required fields
            if not record_data.get("rtype"):
                record_data["rtype"] = "S"
            if not record_data.get("indicator"):
                record_data["indicator"] = "ELA"
            if not record_data.get("reportingyear"):
                record_data["reportingyear"] = category.reporting_year

            records.append(AcademicIndicator(**record_data))

        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            skipped += 1
            continue

    print(f"Prepared {len(records)} records for insertion ({skipped} skipped)")

    # Insert in batches
    with Session(engine) as session:
        if category.existing_rows > 0 and overwrite:
            category.deleted_rows = delete_category_rows(
                session,
                indicator=category.indicator,
                reporting_year=category.reporting_year,
            )

        total_inserted = 0
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            session.add_all(batch)
            session.commit()
            total_inserted += len(batch)
            print(
                f"Inserted batch {i // batch_size + 1}: {total_inserted} / {len(records)}"
            )

    category.imported_rows = total_inserted
    category.status = "imported"
    category.message = "completed"
    _print_report("ELA Import Result", category)
    print(f"Successfully imported {total_inserted} records")
    return total_inserted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import ELA indicator data")
    parser.add_argument("path", type=Path, help="Path to ELA Excel file")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Records per batch (default: 1000)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing ELA rows for the target reporting year.",
    )
    parser.add_argument(
        "--reporting-year",
        default=None,
        help="Optional reporting year override. Defaults to year in filename/folder.",
    )
    args = parser.parse_args()

    if args.batch_size <= 0:
        print("Error: --batch-size must be > 0")
        sys.exit(1)

    file_path = args.path.expanduser().resolve()
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    import_ela_data(
        str(file_path),
        batch_size=args.batch_size,
        overwrite=args.overwrite,
        reporting_year=args.reporting_year,
    )
