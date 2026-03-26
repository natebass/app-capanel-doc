import argparse
import csv
import os
import pathlib
import sys
import time
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

# ── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]  # backend/app/scripts/caaspp -> project root
ENV_PATH = PROJECT_ROOT / ".env"

BATCH_SIZE = 5_000  # rows per COPY batch

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
    # CSA variant names (2025+)
    "Percent Level 1": "overall_level_1_pct",
    "Percent Level 2": "overall_level_2_pct",
    "Percent Level 3": "overall_level_3_pct",
    # 2024 CSA specific "Range" mappings (to comply with 2025 schema)
    "Percent Range 1": "overall_level_1_pct",
    "Count Range 1": "overall_level_1_count",
    "Percent Range 2": "overall_level_2_pct",
    "Count Range 2": "overall_level_2_count",
    "Percent Range 3": "overall_level_3_pct",
    "Count Range 3": "overall_level_3_count",
}

# Columns to always skip (metadata not stored in db)
SKIP_COLUMNS = {"District Name", "School Name", "Filler"}

# All known non-domain column headers (shared + overall + skip).
# Anything NOT in this set for a given file is treated as domain data → JSONB.
KNOWN_NON_DOMAIN_HEADERS = (
    set(SHARED_COLUMN_MAP.keys()) | set(OVERALL_COLUMN_MAP.keys()) | SKIP_COLUMNS
)

# DB columns in COPY order
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


def load_env() -> dict[str, Any]:
    """Load .env and return db connection params."""
    load_dotenv(ENV_PATH)
    return {
        "host": os.getenv("POSTGRES_SERVER", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }


def build_conninfo(params: dict[str, Any]) -> str:
    """Build a psycopg conninfo string from a params dict."""
    return " ".join(f"{k}={v}" for k, v in params.items() if v is not None)


def normalize_header(header: str) -> str:
    """Normalize a TSV header to a snake_case key for JSONB storage."""
    return (
        header.strip()
        .lower()
        .replace(" ", "_")
        .replace("and_space_", "")  # "Earth and Space Sciences" → "earth_sciences"
    )


def parse_row(row: dict[str, str], domain_headers: list[str]) -> tuple[Any, ...]:
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
                values.setdefault(db_col, val)

    # Domain data → JSONB
    domain_data: dict[str, str] = {}
    for tsv_col in domain_headers:
        val = row.get(tsv_col, "").strip()
        if val:
            domain_data[normalize_header(tsv_col)] = val

    # Build final tuple in DB_COLUMNS order.
    # Wrap domain_data in Jsonb so psycopg3 sends it correctly via COPY.
    result: list[Any] = []
    for col in DB_COLUMNS:
        if col == "domain_data":
            result.append(Jsonb(domain_data) if domain_data else None)
        else:
            result.append(values.get(col))
    return tuple(result)


def import_file(
    filepath: pathlib.Path, conn: psycopg.Connection | None, dry_run: bool = False
) -> int:
    """
    Import a single TSV file via COPY protocol. Returns number of rows imported.
    Note: Open the file as latin-1 instead of utf-8 because that is what the CAASPP files are encoded as.
    """
    print(f"\n{'─' * 60}")
    print(f"  {'DRY RUN: ' if dry_run else ''}Importing: {filepath.name}")
    print(f"  Size:      {filepath.stat().st_size / 1_000_000:.1f} MB")
    print(f"{'─' * 60}")

    start = time.time()
    total_rows = 0

    if not dry_run:
        assert conn is not None, "Connection must be provided for non-dry-run imports"
        cols = ", ".join(f'"{c}"' for c in DB_COLUMNS)
        copy_sql = f'COPY "academic_indicators" ({cols}) FROM STDIN (FORMAT BINARY)'

    with open(filepath, encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter="^")

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

        batch: list[tuple[Any, ...]] = []

        if dry_run:
            for i, row in enumerate(reader):
                parsed = parse_row(row, domain_headers)
                if i < 3:
                    print(f"  [Sample Row {i + 1}]: {parsed}")
                total_rows += 1
                if total_rows % 10000 == 0:
                    print(f"  … {total_rows:>10,} rows processed", end="\r")
        else:
            assert conn is not None
            with conn.cursor() as cursor:
                with cursor.copy(copy_sql) as copy:
                    for row in reader:
                        batch.append(parse_row(row, domain_headers))

                        if len(batch) >= BATCH_SIZE:
                            for record in batch:
                                copy.write_row(record)
                            total_rows += len(batch)
                            print(f"  … {total_rows:>10,} rows", end="\r")
                            batch = []

                    # Final partial batch
                    if batch:
                        for record in batch:
                            copy.write_row(record)
                        total_rows += len(batch)

            assert conn is not None
            conn.commit()

    elapsed = time.time() - start
    rate = total_rows / elapsed if elapsed > 0 else 0
    print(f"  ✓ {total_rows:>10,} rows in {elapsed:.1f}s ({rate:,.0f} rows/s)")
    return total_rows


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    """
    Run with python import_caaspp.py (reads from script dir) or python import_caaspp.py /path/to/folder
    """
    parser = argparse.ArgumentParser(
        description="Import CAASPP TSV files into PostgreSQL."
    )
    parser.add_argument(
        "data_dir",
        nargs="?",
        default=str(SCRIPT_DIR),
        help="Path to the directory containing .txt files.",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2025,
        help="The test year to target (default: 2025).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse files without inserting into the database.",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.data_dir).resolve()

    if path.is_file():
        txt_files = [path]
        print(f"\nProcessing single file: {path}")
    elif path.is_dir():
        txt_files = sorted(path.glob("*.txt"))
        if not txt_files:
            print(f"No .txt files found in {path}")
            sys.exit(1)
        print(f"\nFound {len(txt_files)} file(s) in {path}")
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)
    print(f"Target Year: {args.year}")

    grand_total = 0
    grand_start = time.time()

    if args.dry_run:
        for filepath in txt_files:
            grand_total += import_file(filepath, None, dry_run=True)
    else:
        db_params = load_env()
        print(
            f"Connecting to {db_params['user']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
        )
        conninfo = build_conninfo(db_params)
        with psycopg.connect(conninfo) as conn:
            try:
                for filepath in txt_files:
                    grand_total += import_file(filepath, conn)
            except Exception:
                conn.rollback()
                raise

    elapsed = time.time() - grand_start
    print(f"\n{'═' * 60}")
    print(f"  DONE — {grand_total:,} total rows in {elapsed:.1f}s")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()
