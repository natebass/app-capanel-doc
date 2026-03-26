from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete, func
from sqlmodel import Session, col, select

from app.model.academic_indicator import AcademicIndicator

YEAR_PATTERN = re.compile(r"(20\d{2})")


@dataclass
class ImportCategory:
    source: str
    indicator: str
    reporting_year: str
    path: str
    existing_rows: int = 0
    action: str = "import"
    status: str = "pending"
    imported_rows: int = 0
    deleted_rows: int = 0
    message: str = ""


def detect_reporting_year(file_path: Path, fallback_year: str = "2025") -> str:
    candidates = [file_path.name, file_path.parent.name]
    for candidate in candidates:
        match = YEAR_PATTERN.search(candidate)
        if match:
            return match.group(1)
    return fallback_year


def count_existing_rows(
    session: Session, *, indicator: str, reporting_year: str
) -> int:
    result = session.exec(
        select(func.count())
        .select_from(AcademicIndicator)
        .where(AcademicIndicator.test_id == indicator)
        .where(AcademicIndicator.test_year == reporting_year)
    ).one()
    return int(result or 0)


def delete_category_rows(
    session: Session, *, indicator: str, reporting_year: str
) -> int:
    stmt = (
        delete(AcademicIndicator)
        .where(
            col(AcademicIndicator.test_id) == indicator
        )
        .where(
            col(AcademicIndicator.test_year) == reporting_year
        )
    )
    result = session.exec(stmt)
    session.commit()
    return int(result.rowcount or 0)


def render_ascii_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def _line(char: str) -> str:
        return "+" + "+".join(char * (w + 2) for w in widths) + "+"

    def _row(values: list[str]) -> str:
        cells = [f" {v.ljust(widths[i])} " for i, v in enumerate(values)]
        return "|" + "|".join(cells) + "|"

    output = [_line("-"), _row(headers), _line("=")]
    for row in rows:
        output.append(_row(row))
    output.append(_line("-"))
    return "\n".join(output)
