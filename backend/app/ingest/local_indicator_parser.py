"""Read rows of an LCFF Local Indicator file.

These files change shape almost every year, so unlike the state indicator
files there is no fixed layout to match.  Instead a small stable envelope is
recognised by name -- case-insensitively, across every spelling the state has
used -- and every other column is kept verbatim under the name it was
published with.

Spellings seen across 2018 to 2025::

    CDSCode | cdsCode | cdscode
    PriorityNumber | priorityNumber | priorityId
    Performance | performance | countyPerformance

Priority 3 alone has been published with 8, 21, 27 and 28 columns.  Trying to
give those columns a schema would mean a migration every autumn; keeping them
in JSON means a new column simply appears.
"""

from __future__ import annotations

import datetime
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

from app.ingest.parser import ParseError

# Canonical field -> the header spellings that mean it, lower-cased.
_ENVELOPE: dict[str, tuple[str, ...]] = {
    "cds_code": ("cdscode", "cds"),
    "lea_name": ("lea", "leaname"),
    "priority_number": ("prioritynumber", "priorityid", "priority"),
    "performance": ("countyperformance", "performance"),
    "meeting_date": ("meetingdate",),
    "additional_info": ("additionalinfo",),
    "reporting_year": ("year", "reportingyear"),
}

# Without these a file is not a Local Indicator file.
REQUIRED_COLUMNS = ("cdscode", "lea")

# Pipe for 2018, 2019, 2021, 2024 and 2025; tab for 2022 and 2023.
PIPE = "|"
TAB = "\t"

_FILENAME = re.compile(r"^Pr(\d+)(\d{4})", re.IGNORECASE)


class LocalIndicatorLayoutError(RuntimeError):
    """Raised when a file is not a Local Indicator file."""


def parse_filename(name: str) -> tuple[int | None, int | None]:
    """Read the priority and year out of ``Pr32025.xlsx``."""
    match = _FILENAME.match(name.rsplit("/", 1)[-1])
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def detect_delimiter(header_line: str) -> str:
    """Pick the delimiter a Local Indicator file uses from its header row."""
    return PIPE if PIPE in header_line else TAB


@dataclass(slots=True)
class LocalIndicatorRecord:
    """One LEA's self-assessment against one priority."""

    cds_code: str
    reporting_year: int
    priority_number: int
    lea_name: str | None = None
    performance: str | None = None
    meeting_date: datetime.date | None = None
    additional_info: str | None = None
    responses: dict[str, Any] = field(default_factory=dict)


def _clean(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    return str(raw).strip()


def _parse_date(raw: Any) -> datetime.date | None:
    """Read a board meeting date.

    The text exports write ``2025-06-10``; the spreadsheets hand back a real
    datetime.  Anything else is left out rather than guessed at.
    """
    if isinstance(raw, datetime.datetime):
        return raw.date()
    if isinstance(raw, datetime.date):
        return raw
    value = _clean(raw)
    if not value:
        return None
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(value[:10], pattern).date()
        except ValueError:
            continue
    return None


def _coerce(raw: Any) -> Any:
    """Keep a response value as the kind of thing it is.

    Ratings are published as small integers and narratives as text; storing a
    rating as ``"4"`` would make it useless for anything but display.
    """
    if isinstance(raw, bool | int | float):
        return raw
    value = _clean(raw)
    if not value:
        return None
    if value.lstrip("-").isdigit():
        return int(value)
    return value


class LocalIndicatorRowParser:
    """Reads rows of one Local Indicator file."""

    def __init__(
        self,
        header: Sequence[Any],
        *,
        default_priority: int | None = None,
        default_year: int | None = None,
    ) -> None:
        self.default_priority = default_priority
        self.default_year = default_year
        self.header = [_clean(column) for column in header]
        lowered = [column.lower() for column in self.header]

        missing = [name for name in REQUIRED_COLUMNS if name not in lowered]
        if missing:
            raise LocalIndicatorLayoutError(
                "Not a Local Indicator file; missing "
                f"{', '.join(missing)}. First columns seen: {self.header[:6]}"
            )

        self._position: dict[str, int] = {}
        claimed: set[int] = set()
        for canonical, spellings in _ENVELOPE.items():
            for spelling in spellings:
                if spelling in lowered:
                    index = lowered.index(spelling)
                    self._position[canonical] = index
                    claimed.add(index)
                    break
        self._responses = [
            (index, self.header[index])
            for index in range(len(self.header))
            if index not in claimed
        ]

    def _cell(self, row: Sequence[Any], canonical: str) -> Any:
        index = self._position.get(canonical)
        if index is None or index >= len(row):
            return None
        return row[index]

    def parse(self, row: Sequence[Any]) -> LocalIndicatorRecord:
        cds_code = _clean(self._cell(row, "cds_code"))
        # A few LEAs are published without the trailing zeros.
        if cds_code.isdigit() and len(cds_code) < 14:
            cds_code = cds_code.ljust(14, "0")
        if len(cds_code) != 14 or not cds_code.isdigit():
            raise ParseError(f"malformed CDS code {cds_code!r}")

        year_cell = _clean(self._cell(row, "reporting_year"))
        year = int(year_cell[:4]) if year_cell[:4].isdigit() else self.default_year
        if year is None:
            raise ParseError("no reporting year on the row or in the file name")

        priority_cell = _clean(self._cell(row, "priority_number"))
        priority = (
            int(priority_cell) if priority_cell.isdigit() else self.default_priority
        )
        if priority is None:
            raise ParseError("no priority on the row or in the file name")

        responses = {}
        for index, name in self._responses:
            if index < len(row):
                value = _coerce(row[index])
                if value is not None and value != "":
                    responses[name] = value

        return LocalIndicatorRecord(
            cds_code=cds_code,
            reporting_year=year,
            priority_number=priority,
            lea_name=_clean(self._cell(row, "lea_name")) or None,
            performance=_clean(self._cell(row, "performance")) or None,
            meeting_date=_parse_date(self._cell(row, "meeting_date")),
            additional_info=_clean(self._cell(row, "additional_info")) or None,
            responses=responses,
        )


def iter_rows(lines: Iterator[str], delimiter: str) -> Iterator[list[str]]:
    """Split a Local Indicator text file's lines.  The files are not quoted."""
    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped:
            yield stripped.split(delimiter)
