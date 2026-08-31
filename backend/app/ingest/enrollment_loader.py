"""Read and load the Census Day enrolment files.

One file per year, 2018 onwards, in the tab-delimited envelope the other
Dashboard files use.  Columns are matched by name because the state has
reordered and re-capitalised them: 2021 puts the student group third and
capitalises every heading, and 2022 spells ``subgroupTotal`` with a capital T.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import Engine

from app.ingest.dashboard_parser import iter_rows
from app.ingest.parser import ParseError
from app.ingest.run_bookkeeping import FileOutcome, RunBookkeeper, RunOutcome
from app.ingest.sources import (
    DASHBOARD_BASE_URL,
    HttpSource,
    ResearchFileSource,
    SourceObject,
    source_from_uri,
)
from app.ingest.staged_load import analyze, replace_years
from app.model.ingest import IngestStatus

logger = logging.getLogger(__name__)

FIRST_YEAR = 2018
TABLE = "enrollment_rates"

_COLUMNS = (
    "cds_code",
    "reporting_year",
    "student_group_code",
    "total_enrollment",
    "subgroup_total",
    "rate",
)


def enrollment_file_names(years: Sequence[int] | None = None) -> list[str]:
    span = years or range(FIRST_YEAR, datetime.now(tz=UTC).year + 1)
    return [f"censusenrollratesdownload{year}.txt" for year in span]


def year_from_filename(name: str) -> int | None:
    digits = "".join(c for c in name if c.isdigit())
    return int(digits[-4:]) if len(digits) >= 4 else None


@dataclass(slots=True)
class EnrollmentRecord:
    cds_code: str
    reporting_year: int
    student_group_code: str
    total_enrollment: int | None = None
    subgroup_total: int | None = None
    rate: Decimal | None = None


def _int(raw: str | None) -> int | None:
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return int(float(value)) if "." in value else int(value)
    except ValueError:
        return None


def _decimal(raw: str | None) -> Decimal | None:
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


class EnrollmentRowParser:
    """Reads rows of one Census Day enrolment file."""

    REQUIRED = ("cds", "studentgroup", "totalenrollment")

    def __init__(self, header: Sequence[str]) -> None:
        self.header = [c.strip() for c in header]
        lowered = [c.lower() for c in self.header]
        missing = [n for n in self.REQUIRED if n not in lowered]
        if missing:
            raise ParseError(
                "Not a Census Day enrolment file; missing "
                f"{', '.join(missing)}. First columns seen: {self.header[:8]}"
            )
        self._index = {name: i for i, name in enumerate(lowered)}

    def _cell(self, row: Sequence[str], name: str) -> str | None:
        i = self._index.get(name)
        return row[i] if i is not None and i < len(row) else None

    def parse(
        self, row: Sequence[str], *, default_year: int | None = None
    ) -> EnrollmentRecord:
        cds = (self._cell(row, "cds") or "").strip()
        if len(cds) != 14 or not cds.isdigit():
            raise ParseError(f"malformed CDS code {cds!r}")
        year = _int(self._cell(row, "reportingyear")) or default_year
        if year is None:
            raise ParseError("no reporting year on the row or in the file name")
        group = (self._cell(row, "studentgroup") or "").strip().upper()
        if not group:
            raise ParseError("no student group on the row")
        return EnrollmentRecord(
            cds_code=cds,
            reporting_year=year,
            student_group_code=group,
            total_enrollment=_int(self._cell(row, "totalenrollment")),
            subgroup_total=_int(self._cell(row, "subgrouptotal")),
            rate=_decimal(self._cell(row, "rate")),
        )


def _values(record: EnrollmentRecord) -> tuple[Any, ...]:
    return (
        record.cds_code,
        record.reporting_year,
        record.student_group_code,
        record.total_enrollment,
        record.subgroup_total,
        record.rate,
    )


class EnrollmentLoader:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def load(self, records: Iterable[EnrollmentRecord]) -> int:
        return replace_years(
            self.engine,
            table=TABLE,
            columns=_COLUMNS,
            rows=(_values(record) for record in records),
        )


class EnrollmentImportRunner:
    """Runs Census Day enrolment imports."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.loader = EnrollmentLoader(engine)
        self.books = RunBookkeeper(engine)
        self.books.program = "ENROLL"

    def run(
        self,
        source_uri: str = DASHBOARD_BASE_URL,
        *,
        force: bool = False,
        years: Sequence[int] | None = None,
    ) -> RunOutcome:
        source = source_from_uri(source_uri)
        if isinstance(source, HttpSource):
            source.names = tuple(enrollment_file_names(years))

        run_id = self.books.start(source.uri)
        outcome = RunOutcome(
            run_id=str(run_id), source_uri=source.uri, status=IngestStatus.RUNNING
        )
        try:
            for obj in source.list_objects():
                if "censusenrollrates" not in obj.name.lower():
                    continue
                year = year_from_filename(obj.name)
                if years and year is not None and year not in years:
                    continue
                outcome.files.append(self._load(source, obj, run_id, force=force))
            outcome.settle()
        except Exception as error:  # noqa: BLE001 - recorded on the run row
            outcome.status = IngestStatus.FAILED
            self.books.finish(run_id, outcome, error=str(error))
            raise
        else:
            if outcome.rows:
                analyze(self.engine, TABLE)
            self.books.finish(run_id, outcome)
        return outcome

    def _load(
        self, source: ResearchFileSource, obj: SourceObject, run_id, *, force: bool
    ) -> FileOutcome:
        started = time.monotonic()
        year = year_from_filename(obj.name)
        if not force and self.books.already_loaded(obj):
            logger.info("skipping unchanged %s", obj.name)
            self.books.record_file(run_id, obj, IngestStatus.SKIPPED, started=started)
            return FileOutcome(name=obj.name, status=IngestStatus.SKIPPED)

        try:
            with source.open_text(obj) as lines:
                header_line = next(lines, "").rstrip("\r\n")
                if not header_line:
                    raise ParseError(f"{obj.name} is empty")
                parser = EnrollmentRowParser(header_line.split("\t"))
                loaded = self.loader.load(
                    parser.parse(row, default_year=year) for row in iter_rows(lines)
                )
        except (ParseError, ValueError) as error:
            logger.warning("skipping %s: %s", obj.name, error)
            self.books.record_file(
                run_id, obj, IngestStatus.FAILED, started=started, error=str(error)
            )
            return FileOutcome(
                name=obj.name, status=IngestStatus.FAILED, error=str(error)
            )

        self.books.record_file(
            run_id,
            obj,
            IngestStatus.SUCCEEDED,
            started=started,
            rows=loaded,
            label="ENROLL",
            year=year,
        )
        logger.info("loaded %s: %s rows", obj.name, f"{loaded:,}")
        return FileOutcome(
            name=obj.name,
            status=IngestStatus.SUCCEEDED,
            label="ENROLL",
            reporting_year=year,
            rows=loaded,
            duration_seconds=time.monotonic() - started,
        )
