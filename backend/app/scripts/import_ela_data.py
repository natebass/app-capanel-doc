#!/usr/bin/env python3
"""
Import California Dashboard ELA Academic Indicator data from Excel file.

Usage:
    cd backend
    source ../.venv/bin/activate
    python scripts/import_ela_data.py ~/Downloads/resources/eladownload2025.xlsx
"""

import sys
from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]
from sqlmodel import Session

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from app.model.academic_indicator import AcademicIndicator

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


from typing import Any


def clean_value(value: Any, field_type: str = "str") -> Any:
    """Clean a value for database insertion."""
    if pd.isna(value) or value == "" or value == "*":
        return None

    if field_type == "int":
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    elif field_type == "float":
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    else:
        return str(value).strip() if value else None


def import_ela_data(file_path: str, batch_size: int = 1000) -> None:
    """Import ELA data from Excel file into the database."""
    print(f"Reading Excel file: {file_path}")
    df = pd.read_excel(file_path)

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
            if not record_data.get("cds") or not record_data.get("studentgroup"):
                skipped += 1
                continue

            # Set defaults for required fields
            if not record_data.get("rtype"):
                record_data["rtype"] = "S"
            if not record_data.get("indicator"):
                record_data["indicator"] = "ELA"
            if not record_data.get("reportingyear"):
                record_data["reportingyear"] = "2025"

            records.append(AcademicIndicator(**record_data))

        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            skipped += 1
            continue

    print(f"Prepared {len(records)} records for insertion ({skipped} skipped)")

    # Insert in batches
    with Session(engine) as session:
        total_inserted = 0
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            session.add_all(batch)
            session.commit()
            total_inserted += len(batch)
            print(
                f"Inserted batch {i // batch_size + 1}: {total_inserted} / {len(records)}"
            )

    print(f"Successfully imported {total_inserted} records")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_ela_data.py <path_to_excel_file>")
        print(
            "Example: python scripts/import_ela_data.py ~/Desktop/resources/eladownload2025.xlsx"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    import_ela_data(file_path)
