"""
State assessment TXT file parser for California assessment data.

Parses caret-delimited (^) text files from the California State assessment
data downloads. These contain raw assessment results rather than accountability
indicators.
"""

import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pandas as pd  # type: ignore[import-untyped]
from sqlmodel import Session

from .base import BaseIndicatorParser

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.model.academic_indicator import AcademicIndicator


class StateParser(BaseIndicatorParser):
    """Parser for state assessment caret-delimited TXT files."""

    CHUNK_SIZE = 50000  # Read large files in chunks

    # Mapping of Type ID to rtype
    TYPE_ID_MAP = {
        "4": "X",  # State aggregate
        "5": "C",  # County
        "6": "D",  # District
        "7": "S",  # School
    }

    def __init__(self, indicator: str):
        """Initialize parser for a specific indicator.

        Args:
            indicator: One of ELA, MATH, SCI
        """
        self.INDICATOR = indicator.upper()

    def get_extra_fields(self) -> dict[str, str]:
        """Return indicator-specific field mappings for state files."""
        # State files have different column names
        return {
            # Map state file columns to our model fields
            "County Code": "county_code_raw",
            "District Code": "district_code_raw",
            "School Code": "school_code_raw",
            "Type ID": "type_id_raw",
            "County Name": "countyname",
            "District Name": "districtname",
            "School Name": "schoolname",
            "Subgroup ID": "studentgroup",
            "Test Year": "reportingyear",
            "Students Tested": "currdenom",
            "Mean Scale Score": "currstatus",
            # Additional state-specific fields can be added here
        }

    def build_cds_code(
        self, county_code: str, district_code: str, school_code: str
    ) -> str:
        """Build 14-character CDS code from component codes.

        Args:
            county_code: 2-digit county code
            district_code: 5-digit district code
            school_code: 7-digit school code

        Returns:
            14-character CDS code
        """
        county = str(county_code or "").zfill(2)
        district = str(district_code or "").zfill(5)
        school = str(school_code or "").zfill(7)
        return f"{county}{district}{school}"

    def parse_row_state(
        self, row: pd.Series, columns: list[str]
    ) -> dict[str, Any] | None:
        """Parse a row from state assessment file.

        Args:
            row: pandas Series representing a row
            columns: list of column names

        Returns:
            dict suitable for AcademicIndicator model or None if invalid
        """
        try:
            # Build CDS code
            county_code = row.get("county code", "")
            district_code = row.get("district code", "")
            school_code = row.get("school code", "")

            # Handle statewide aggregate (Type ID = 4)
            type_id = str(row.get("type id", "7"))
            if type_id == "4":
                cds = "00000000000000"
                rtype = "X"
            else:
                cds = self.build_cds_code(county_code, district_code, school_code)
                rtype = self.TYPE_ID_MAP.get(type_id, "S")

            # Map studentgroup
            subgroup_id = str(row.get("subgroup id", "1"))
            studentgroup = self.map_subgroup(subgroup_id)

            record_data = {
                "cds": cds,
                "rtype": rtype,
                "countyname": self.clean_value(row.get("county name")),
                "districtname": self.clean_value(row.get("district name")),
                "schoolname": self.clean_value(row.get("school name")),
                "studentgroup": studentgroup,
                "indicator": self.INDICATOR,
                "reportingyear": self.clean_value(row.get("test year"), "str")
                or "2025",
                "currdenom": self.clean_value(row.get("students tested"), "int"),
                "currstatus": self.clean_value(row.get("mean scale score"), "float"),
            }

            # Validate required fields
            if not cds or not studentgroup:
                return None

            return record_data

        except Exception as e:
            print(f"Error parsing state row: {e}")
            return None

    def map_subgroup(self, subgroup_id: str) -> str:
        """Map state file subgroup ID to dashboard studentgroup code.

        Args:
            subgroup_id: Numeric subgroup ID from state file

        Returns:
            Dashboard studentgroup code (ALL, AA, AI, etc.)
        """
        # Common subgroup ID mappings (may need adjustment based on actual data)
        subgroup_map = {
            "1": "ALL",
            "74": "AA",  # African American
            "75": "AI",  # American Indian
            "76": "AS",  # Asian
            "77": "FI",  # Filipino
            "78": "HI",  # Hispanic
            "79": "PI",  # Pacific Islander
            "80": "WH",  # White
            "31": "MR",  # Two or More Races
            "111": "EL",  # English Learners
            "128": "SED",  # Socioeconomically Disadvantaged
            "99": "SWD",  # Students with Disabilities
            "121": "FOS",  # Foster
            "160": "HOM",  # Homeless
            "142": "MIG",  # Migrant
        }
        return subgroup_map.get(subgroup_id, f"SG{subgroup_id}")

    def parse_txt(
        self, file_path: str | Path
    ) -> Generator[AcademicIndicator, None, None]:
        """Parse a caret-delimited TXT file and yield AcademicIndicator records.

        Args:
            file_path: Path to the TXT file

        Yields:
            AcademicIndicator instances
        """
        file_path = Path(file_path)
        print(f"Reading TXT file: {file_path}")

        # Read in chunks for large files
        # Use latin-1 encoding to handle Spanish characters (ñ, accents, etc.)
        chunk_iter = pd.read_csv(
            file_path,
            sep="^",
            encoding="latin-1",
            dtype=str,
            chunksize=self.CHUNK_SIZE,
            on_bad_lines="skip",
        )

        total_rows = 0
        for chunk in chunk_iter:
            # Normalize column names to lowercase
            chunk.columns = chunk.columns.str.lower()
            columns = list(chunk.columns)

            for idx, row in chunk.iterrows():
                try:
                    record_data = self.parse_row_state(row, columns)
                    if record_data is None:
                        continue

                    yield AcademicIndicator(**record_data)
                    total_rows += 1

                except Exception as e:
                    print(f"Error processing row {idx}: {e}")
                    continue

            print(f"Processed chunk, total rows so far: {total_rows}")

        print(f"Total rows parsed: {total_rows}")

    def import_file(
        self, session: Session, file_path: str | Path, batch_size: int | None = None
    ) -> int:
        """Import a TXT file to the database.

        Args:
            session: SQLModel Session
            file_path: Path to the TXT file
            batch_size: Override default batch size

        Returns:
            Number of records imported
        """
        records = self.parse_txt(file_path)
        return self.import_to_session(session, records, batch_size)


# State file patterns
STATE_FILES = {
    "ELA": "sb_ca*_all_csv_ela_*.txt",
    "MATH": "sb_ca*_all_csv_math_*.txt",
    "SCI": "cast_ca*_all_csv_*.txt",
}


def get_parser(indicator: str) -> StateParser:
    """Get the appropriate parser for an indicator.

    Args:
        indicator: Indicator code (ELA, MATH, SCI)

    Returns:
        StateParser instance configured for the indicator
    """
    return StateParser(indicator)
