"""
Base class for indicator data parsers.

Provides common functionality for parsing and importing California Dashboard
accountability indicator data.
"""

import sys
from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pandas as pd  # type: ignore[import-untyped]
from sqlmodel import Session

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.model.academic_indicator import AcademicIndicator


class BaseIndicatorParser(ABC):
    """Abstract base class for indicator parsers."""

    INDICATOR: str = ""
    BATCH_SIZE: int = 1000

    # Maps raw indicator values from source files to canonical names.
    INDICATOR_NORMALIZE: dict[str, str] = {
        "CHRO": "CHRONIC",
    }

    # Common fields across all indicators
    COMMON_MAPPING = {
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

    # Integer fields
    INT_FIELDS = {
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
        "currnumer",
        "priornumer",
        "fiveyrnumer",
        "currprogressed",
        "currmaintainpl4",
        "currmaintainoth",
        "currdeclined",
        "currprogressed_alternate",
        "currmaintainpl3_alternate",
        "currnotprognotmain_alternate",
        "curr95",
        "priorprogressed",
        "priormaintainpl4",
        "priormaintainoth",
        "priordeclined",
        "priorprogressed_alternate",
        "priormaintainpl3_alternate",
        "priornotprognotmain_alternate",
        "prior95",
    }

    # Float fields
    FLOAT_FIELDS = {
        "currstatus",
        "priorstatus",
        "change",
        "currprate",
        "currstatus_withoutprloss",
        "priorprate",
        "priorstatus_withoutprloss",
        "studentgroup_pct",
    }

    @abstractmethod
    def get_extra_fields(self) -> dict[str, str]:
        """Return indicator-specific field mappings.

        Returns:
            dict mapping source column names to model field names
        """
        pass

    def get_all_fields(self) -> dict[str, str]:
        """Get combined common and extra field mappings."""
        return {**self.COMMON_MAPPING, **self.get_extra_fields()}

    @staticmethod
    def clean_value(value: Any, field_type: str = "str") -> Any:
        """Clean a value for database insertion.

        Args:
            value: The value to clean
            field_type: One of 'str', 'int', or 'float'

        Returns:
            Cleaned value or None if invalid
        """
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

    def parse_row(self, row: pd.Series, columns: list[str]) -> dict[str, Any] | None:
        """Parse a single row into a model data dictionary.

        Args:
            row: pandas Series representing a row
            columns: list of column names in the DataFrame

        Returns:
            dict suitable for AcademicIndicator model or None if invalid
        """
        record_data = {}
        field_mapping = self.get_all_fields()

        for source_col, model_field in field_mapping.items():
            source_col_lower = source_col.lower()
            if source_col_lower in columns:
                if model_field in self.INT_FIELDS:
                    record_data[model_field] = self.clean_value(
                        row[source_col_lower], "int"
                    )
                elif model_field in self.FLOAT_FIELDS:
                    record_data[model_field] = self.clean_value(
                        row[source_col_lower], "float"
                    )
                else:
                    record_data[model_field] = self.clean_value(
                        row[source_col_lower], "str"
                    )

        # Ensure CDS code is padded to 14 characters
        # Handle statewide aggregate (rtype = 'X') where CDS might be missing/empty in Excel
        if not record_data.get("cds") and record_data.get("rtype") == "X":
            record_data["cds"] = "00000000000000"

        if record_data.get("cds"):
            cds = str(record_data["cds"]).strip()
            # Remove any decimal points (e.g., "0.0" -> "0")
            if "." in cds:
                cds = cds.split(".")[0]
            record_data["cds"] = cds.zfill(14)

        # Ensure required fields are present
        if not record_data.get("cds") or not record_data.get("studentgroup"):
            return None

        # Set defaults for required fields
        if not record_data.get("rtype"):
            record_data["rtype"] = "S"
        if not record_data.get("indicator"):
            record_data["indicator"] = self.INDICATOR
        else:
            record_data["indicator"] = self.INDICATOR_NORMALIZE.get(
                record_data["indicator"], record_data["indicator"]
            )
        if not record_data.get("reportingyear"):
            record_data["reportingyear"] = "2025"

        return record_data

    def parse_cci_details(
        self, row: pd.Series, columns: list[str]
    ) -> dict[str, Any] | None:
        """Parse CCI-specific breakdown fields into a JSON object.

        Args:
            row: pandas Series representing a row
            columns: list of column names in the DataFrame

        Returns:
            dict containing CCI detail fields
        """
        cci_details = {}
        # CCI fields start with curr_prep_, curr_aprep_, prior_prep_, prior_aprep_
        cci_prefixes = ("curr_prep_", "curr_aprep_", "prior_prep_", "prior_aprep_")

        for col in columns:
            col_lower = col.lower()
            if any(col_lower.startswith(prefix) for prefix in cci_prefixes):
                value = self.clean_value(row[col_lower], "int")
                if value is not None:
                    cci_details[col_lower] = value

        return cci_details if cci_details else None

    def parse_dataframe(
        self, df: pd.DataFrame
    ) -> Generator[AcademicIndicator, None, None]:
        """Parse a DataFrame into AcademicIndicator records.

        Args:
            df: pandas DataFrame with indicator data

        Yields:
            AcademicIndicator instances
        """
        # Normalize column names to lowercase
        df.columns = df.columns.str.lower()
        columns = list(df.columns)

        for idx, row in df.iterrows():
            try:
                record_data = self.parse_row(row, columns)
                if record_data is None:
                    continue

                # Handle CCI-specific JSON details
                if self.INDICATOR == "CCI":
                    cci_details = self.parse_cci_details(row, columns)
                    if cci_details:
                        record_data["cci_details"] = cci_details

                yield AcademicIndicator(**record_data)

            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue

    def import_to_session(
        self,
        session: Session,
        records: Generator[AcademicIndicator, None, None],
        batch_size: int | None = None,
    ) -> int:
        """Import records to the database in batches.

        Args:
            session: SQLModel Session
            records: Generator of AcademicIndicator instances
            batch_size: Override default batch size

        Returns:
            Number of records imported
        """
        batch_size = batch_size or self.BATCH_SIZE
        batch = []
        total_inserted = 0

        for record in records:
            batch.append(record)
            if len(batch) >= batch_size:
                session.add_all(batch)
                session.commit()
                total_inserted += len(batch)
                print(f"Inserted batch: {total_inserted} records")
                batch = []

        # Insert remaining records
        if batch:
            session.add_all(batch)
            session.commit()
            total_inserted += len(batch)
            print(f"Inserted final batch: {total_inserted} records")

        return total_inserted
