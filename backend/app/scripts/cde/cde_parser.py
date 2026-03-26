"""
CDE Excel file parser for California Dashboard indicator data.

Parses Excel files downloaded from the California Department of Education
Dashboard download site.
"""

import sys
from collections.abc import Generator
from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]
from sqlmodel import Session

from .base import BaseIndicatorParser

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.model.academic_indicator import AcademicIndicator


class CDEParser(BaseIndicatorParser):
    """Parser for CDE Excel download files."""

    def __init__(self, indicator: str) -> None:
        """Initialize parser for a specific indicator.

        Args:
            indicator: One of ELA, MATH, SCI, CHRONIC, SUSP, GRAD, ELPI, CCI
        """
        self.INDICATOR = indicator.upper()

    def get_extra_fields(self) -> dict[str, str]:
        """Return indicator-specific field mappings."""
        extra = {}

        if self.INDICATOR in ("CHRONIC", "SUSP", "GRAD", "ELPI"):
            # Common extended fields
            extra.update(
                {
                    "currnumer": "currnumer",
                    "priornumer": "priornumer",
                    "smalldenom": "smalldenom",
                    "certifyflag": "certifyflag",
                    "priorcertifyflag": "priorcertifyflag",
                    "dataerrorflag": "dataerrorflag",
                }
            )

        if self.INDICATOR == "SUSP":
            # Suspension has a 'type' column
            extra["type"] = "school_type"

        if self.INDICATOR == "GRAD":
            extra["fiveyrnumer"] = "fiveyrnumer"

        if self.INDICATOR == "ELPI":
            # ELPI-specific fields
            extra.update(
                {
                    "currprogressed": "currprogressed",
                    "currmaintainpl4": "currmaintainpl4",
                    "currmaintainoth": "currmaintainoth",
                    "currdeclined": "currdeclined",
                    "currprogressed_alternate": "currprogressed_alternate",
                    "currmaintainpl3_alternate": "currmaintainpl3_alternate",
                    "currnotprognotmain_alternate": "currnotprognotmain_alternate",
                    "curr95": "curr95",
                    "priorprogressed": "priorprogressed",
                    "priormaintainpl4": "priormaintainpl4",
                    "priormaintainoth": "priormaintainoth",
                    "priordeclined": "priordeclined",
                    "priorprogressed_alternate": "priorprogressed_alternate",
                    "priormaintainpl3_alternate": "priormaintainpl3_alternate",
                    "priornotprognotmain_alternate": "priornotprognotmain_alternate",
                    "prior95": "prior95",
                }
            )

        if self.INDICATOR == "CCI":
            extra["studentgroup_pct"] = "studentgroup_pct"
            # Note: CCI has many additional fields stored in cci_details JSON

        return extra

    def parse_excel(self, file_path: str | Path) -> Generator[AcademicIndicator]:
        """Parse an Excel file and yield AcademicIndicator records.

        Args:
            file_path: Path to the Excel file

        Yields:
            AcademicIndicator instances
        """
        file_path = Path(file_path)
        print(f"Reading Excel file: {file_path}")

        df = pd.read_excel(file_path)
        print(f"Found {len(df)} rows in Excel file")
        print(f"Columns: {list(df.columns)}")

        yield from self.parse_dataframe(df)

    def import_file(
        self, session: Session, file_path: str | Path, batch_size: int | None = None
    ) -> int:
        """Import an Excel file to the database.

        Args:
            session: SQLModel Session
            file_path: Path to the Excel file
            batch_size: Override default batch size

        Returns:
            Number of records imported
        """
        records = self.parse_excel(file_path)
        return self.import_to_session(session, records, batch_size)


# Indicator-specific parser classes for convenience
class ELAParser(CDEParser):
    def __init__(self) -> None:
        super().__init__("ELA")


class MATHParser(CDEParser):
    def __init__(self) -> None:
        super().__init__("MATH")


class SCIParser(CDEParser):
    def __init__(self) -> None:
        super().__init__("SCI")


class CHRONICParser(CDEParser):
    def __init__(self) -> None:
        super().__init__("CHRONIC")


class SUSPParser(CDEParser):
    def __init__(self) -> None:
        super().__init__("SUSP")


class GRADParser(CDEParser):
    def __init__(self) -> None:
        super().__init__("GRAD")


class ELPIParser(CDEParser):
    def __init__(self) -> None:
        super().__init__("ELPI")


class CCIParser(CDEParser):
    def __init__(self) -> None:
        super().__init__("CCI")


# Mapping of indicator codes to file patterns
INDICATOR_FILES = {
    "ELA": "eladownload*.xlsx",
    "MATH": "mathdownload*.xlsx",
    "SCI": "sciencedownload*.xlsx",
    "CHRONIC": "chronicdownload*.xlsx",
    "SUSP": "suspdownload*.xlsx",
    "GRAD": "graddownload*.xlsx",
    "ELPI": "elpidownload*.xlsx",
    "CCI": "ccidownload*.xlsx",
}


def get_parser(indicator: str) -> CDEParser:
    """Get the appropriate parser for an indicator.

    Args:
        indicator: Indicator code (ELA, MATH, etc.)

    Returns:
        CDEParser instance configured for the indicator
    """
    return CDEParser(indicator)
