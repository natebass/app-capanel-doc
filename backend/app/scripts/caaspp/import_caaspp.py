"""
Import CAASPP TSV files into PostgreSQL `academic_indicators` table.

Reads all .txt (TSV) files in the script's directory. Each row's varying
domain-specific columns are packed into a JSONB `domain_data` column,
while the shared identifier/participation/overall columns stay flat.

Reads connection details from the project root .env file.

Usage:
                python import_caaspp.py                   # import from script dir
                python import_caaspp.py /path/to/folder   # import from custom folder
"""

import csv
import json
import os
import pathlib
import sys
import time

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

# ── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]  # backend/app/scripts/caaspp -> project root
ENV_PATH = PROJECT_ROOT / ".env"

BATCH_SIZE = 5_000  # rows per INSERT batch

# The 12 shared columns that map 1-to-1 to db columns (in TSV header order).
# TSV Header Name  →  DB column name
SHARED_COLUMN_MAP = {
    "County Code": "county_code",
    "District Code": "district_code",
    "School Code": "school_code",
    "Type ID": "record_type_id",
    "Charter Number": "charter_number",
    "Test Year": "test_year",
    "Test Type": "test_type",
    "Test ID": "test_id",
    "Student Group ID": "student_group_id",
    "Grade": "grade",
    "Total Students Enrolled": "students_enrolled",
    "Total Students Tested": "students_tested",
    "Total Students Tested with Scores": "students_tested_with_scores",
}

# Overall-level TSV columns → db column names.
# Different test types use different header names for equivalent data.
OVERALL_COLUMN_MAP = {
    # Smarter Balanced / CAST uses "Mean Scale Score"
    "Mean Scale Score": "overall_mean_scale_score",
    # CSA / ELPAC uses "Overall Mean Scale Score"
    "Overall Mean Scale Score": "overall_mean_scale_score",
    "Overall Total": "overall_total",
    # SB levels → mapped to generic level names
    "Percentage Standard Not Met": "overall_level_1_pct",
    "Count Standard Not Met": "overall_level_1_count",
    "Percentage Standard Nearly Met": "overall_level_2_pct",
    "Count Standard Nearly Met": "overall_level_2_count",
    "Percentage Standard Met and Above": "overall_level_3_pct",
    "Count Standard Met and Above": "overall_level_3_count",
    "Percentage Standard Exceeded": "overall_level_4_pct",
    "Count Standard Exceeded": "overall_level_4_count",
    "Percentage Standard Met": "overall_met_and_above_pct",
    "Count Standard Met": "overall_met_and_above_count",
    # CAA / CAAS / CSA levels (already labeled by level number)
    "Percentage Level 1": "overall_level_1_pct",
    "Count Level 1": "overall_level_1_count",
    "Percentage Level 2": "overall_level_2_pct",
    "Count Level 2": "overall_level_2_count",
    "Percentage Level 3": "overall_level_3_pct",
    "Count Level 3": "overall_level_3_count",
    # CSA variant names
    "Percent Level 1": "overall_level_1_pct",
    "Percent Level 2": "overall_level_2_pct",
    "Percent Level 3": "overall_level_3_pct",
}

# Columns to always skip (metadata not stored in db)
SKIP_COLUMNS = {"District Name", "School Name", "Filler"}

# All known non-domain column headers (shared + overall + skip).
# Anything NOT in this set for a given file is treated as domain data → JSONB.
KNOWN_NON_DOMAIN_HEADERS = (
    set(SHARED_COLUMN_MAP.keys()) | set(OVERALL_COLUMN_MAP.keys()) | SKIP_COLUMNS
)

# DB columns in INSERT order
DB_COLUMNS = [
    "county_code",
    "district_code",
    "school_code",
    "record_type_id",
    "charter_number",
    "test_year",
    "test_type",
    "test_id",
    "student_group_id",
    "grade",
    "students_enrolled",
    "students_tested",
    "students_tested_with_scores",
    "overall_mean_scale_score",
    "overall_total",
    "overall_level_1_pct",
    "overall_level_1_count",
    "overall_level_2_pct",
    "overall_level_2_count",
    "overall_level_3_pct",
    "overall_level_3_count",
    "overall_level_4_pct",
    "overall_level_4_count",
    "overall_met_and_above_pct",
    "overall_met_and_above_count",
    "domain_data",
]


# ── Helpers ──────────────────────────────────────────────────────────────────


def load_env() -> dict[str, str]:
    """Load .env and return db connection params."""
    load_dotenv(ENV_PATH)
    return {
        "host": os.getenv("POSTGRES_SERVER", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }


def normalize_header(header: str) -> str:
    """Normalize a TSV header to a snake_case key for JSONB storage."""
    return (
        header.strip()
        .lower()
        .replace(" ", "_")
        .replace("and_space_", "")  # "Earth and Space Sciences" → "earth_sciences"
    )


def parse_row(row: dict[str, str], domain_headers: list[str]) -> tuple:
    """Convert a single TSV row dict into a tuple matching DB_COLUMNS order."""
    values: dict[str, str | None] = {}

    # Shared columns
    for tsv_col, db_col in SHARED_COLUMN_MAP.items():
        val = row.get(tsv_col, "").strip()
        values[db_col] = val if val else None

    # Overall columns
    for tsv_col, db_col in OVERALL_COLUMN_MAP.items():
        if tsv_col in row:
            val = row[tsv_col].strip()
            if val and db_col not in values:
                values[db_col] = val
            elif val:
                # Don't overwrite if already set by a prior mapping
                values.setdefault(db_col, val)

    # Domain data → JSONB
    domain_data: dict[str, str] = {}
    for tsv_col in domain_headers:
        val = row.get(tsv_col, "").strip()
        if val:
            domain_data[normalize_header(tsv_col)] = val

    # Build final tuple in DB_COLUMNS order
    result = []
    for col in DB_COLUMNS:
        if col == "domain_data":
            result.append(json.dumps(domain_data) if domain_data else None)
        else:
            result.append(values.get(col))
    return tuple(result)


def import_file(filepath: pathlib.Path, cursor, conn) -> int:
    """
    Import a single TSV file. Returns number of rows imported.
    Note: Open the file as latin-1 instead of utf-8 because that is what the CAASPP files are encoded as.
    """
    print(f"\n{'─' * 60}")
    print(f"  Importing: {filepath.name}")
    print(f"  Size:      {filepath.stat().st_size / 1_000_000:.1f} MB")
    print(f"{'─' * 60}")

    start = time.time()
    total_rows = 0

    with open(filepath, encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter="^")

        # Determine which columns in this file are domain-specific
        assert reader.fieldnames is not None, f"No headers in {filepath.name}"
        domain_headers = [
            h for h in reader.fieldnames if h not in KNOWN_NON_DOMAIN_HEADERS
        ]
        if domain_headers:
            print(
                f"  Domain columns ({len(domain_headers)}): "
                f"{', '.join(domain_headers[:5])}{'…' if len(domain_headers) > 5 else ''}"
            )
        else:
            print("  No domain-specific columns detected")

        batch: list[tuple] = []
        for row in reader:
            batch.append(parse_row(row, domain_headers))
            if len(batch) >= BATCH_SIZE:
                _insert_batch(cursor, batch)
                conn.commit()
                total_rows += len(batch)
                print(f"  … {total_rows:>10,} rows", end="\r")
                batch = []

        # Final partial batch
        if batch:
            _insert_batch(cursor, batch)
            conn.commit()
            total_rows += len(batch)

    elapsed = time.time() - start
    rate = total_rows / elapsed if elapsed > 0 else 0
    print(f"  ✓ {total_rows:>10,} rows in {elapsed:.1f}s ({rate:,.0f} rows/s)")
    return total_rows


def _insert_batch(cursor, batch: list[tuple]):
    """Bulk-insert a batch of rows using execute_values for speed."""
    # placeholders = ", ".join(["%s"] * len(DB_COLUMNS))
    cols = ", ".join(f'"{c}"' for c in DB_COLUMNS)
    query = f'INSERT INTO "academic_indicators" ({cols}) VALUES %s'
    execute_values(cursor, query, batch, page_size=BATCH_SIZE)


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    """
    Run with python import_caaspp.py (reads from script dir) or python import_caaspp.py /path/to/folder
    """
    # Determine data folder
    if len(sys.argv) > 1:
        data_dir = pathlib.Path(sys.argv[1]).resolve()
    else:
        data_dir = SCRIPT_DIR

    if not data_dir.is_dir():
        print(f"Error: {data_dir} is not a directory")
        sys.exit(1)

    txt_files = sorted(data_dir.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {data_dir}")
        sys.exit(1)

    print(f"\nFound {len(txt_files)} file(s) in {data_dir}")

    # Connect
    db_params = load_env()
    print(
        f"Connecting to {db_params['user']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
    )

    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    grand_total = 0
    grand_start = time.time()

    try:
        for filepath in txt_files:
            grand_total += import_file(filepath, cursor, conn)
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    elapsed = time.time() - grand_start
    print(f"\n{'═' * 60}")
    print(f"  DONE — {grand_total:,} total rows in {elapsed:.1f}s")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()
