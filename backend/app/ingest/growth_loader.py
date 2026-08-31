"""Read and load the Growth Model files.

One file per year covering both subjects, in the same tab-delimited envelope
the state indicator files use.  Unlike those, growth carries no colour and no
prior year, so it goes to its own table; see :mod:`app.model.growth`.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import Engine, text

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
from app.model.growth import SUBJECTS
from app.model.ingest import IngestStatus

logger = logging.getLogger(__name__)

#: The first year the state published growth.
FIRST_YEAR = 2025

_COLUMNS = (
    "cds_code",
    "reporting_year",
    "subject",
    "student_group_code",
    "denominator",
    "growth",
    "estimate_method",
    "performance_category",
    "number_improved",
    "percent_improved",
    "charter_flag",
    "coe_flag",
    "dass_flag",
)


def growth_file_names(years: Sequence[int] | None = None) -> list[str]:
    from datetime import UTC, datetime

    span = years or range(FIRST_YEAR, datetime.now(tz=UTC).year + 1)
    return [f"growthmodeldownload{year}.txt" for year in span]


def year_from_filename(name: str) -> int | None:
    digits = "".join(c for c in name if c.isdigit())
    return int(digits[-4:]) if len(digits) >= 4 else None


@dataclass(slots=True)
class GrowthRecord:
    """One growth figure, ready to load."""

    cds_code: str
    reporting_year: int
    subject: str
    student_group_code: str
    denominator: int | None = None
    growth: Decimal | None = None
    estimate_method: str | None = None
    performance_category: int | None = None
    number_improved: int | None = None
    percent_improved: Decimal | None = None
    charter_flag: bool = False
    coe_flag: bool = False
    dass_flag: bool = False


def _flag(raw: str | None) -> bool:
    return (raw or "").strip().upper() == "Y"


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


class GrowthRowParser:
    """Reads rows of one Growth Model file, matching columns by name."""

    REQUIRED = ("cds", "subject", "studentgroup", "performancecategory")

    def __init__(self, header: Sequence[str]) -> None:
        self.header = [c.strip() for c in header]
        lowered = [c.lower() for c in self.header]
        missing = [n for n in self.REQUIRED if n not in lowered]
        if missing:
            raise ParseError(
                "Not a Growth Model file; missing "
                f"{', '.join(missing)}. First columns seen: {self.header[:8]}"
            )
        self._index = {name: i for i, name in enumerate(lowered)}

    def _cell(self, row: Sequence[str], name: str) -> str | None:
        i = self._index.get(name)
        return row[i] if i is not None and i < len(row) else None

    def parse(
        self, row: Sequence[str], *, default_year: int | None = None
    ) -> GrowthRecord:
        cds = (self._cell(row, "cds") or "").strip()
        if len(cds) != 14 or not cds.isdigit():
            raise ParseError(f"malformed CDS code {cds!r}")
        year = _int(self._cell(row, "reportingyear")) or default_year
        if year is None:
            raise ParseError("no reporting year on the row or in the file name")
        subject = (self._cell(row, "subject") or "").strip().upper()
        if subject not in SUBJECTS:
            raise ParseError(f"unexpected subject {subject!r}")
        group = (self._cell(row, "studentgroup") or "").strip().upper()
        if not group:
            raise ParseError("no student group on the row")

        category = _int(self._cell(row, "performancecategory"))
        return GrowthRecord(
            cds_code=cds,
            reporting_year=year,
            subject=subject,
            student_group_code=group,
            denominator=_int(self._cell(row, "denom")),
            growth=_decimal(self._cell(row, "status")),
            estimate_method=(self._cell(row, "estimate") or "").strip().upper() or None,
            # The state writes 0 where it assigned no category, which is not a
            # category zero.
            performance_category=None if category in (None, 0) else category,
            number_improved=_int(self._cell(row, "numberimprove")),
            percent_improved=_decimal(self._cell(row, "percentimprove")),
            charter_flag=_flag(self._cell(row, "charter_flag")),
            coe_flag=_flag(self._cell(row, "coe_flag")),
            dass_flag=_flag(self._cell(row, "dass_flag")),
        )


def _values(record: GrowthRecord) -> tuple[Any, ...]:
    return (
        record.cds_code,
        record.reporting_year,
        record.subject,
        record.student_group_code,
        record.denominator,
        record.growth,
        record.estimate_method,
        record.performance_category,
        record.number_improved,
        record.percent_improved,
        record.charter_flag,
        record.coe_flag,
        record.dass_flag,
    )


class GrowthLoader:
    """Loads one Growth Model file's parsed rows."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def load(self, records: Iterable[GrowthRecord]) -> int:
        columns = ", ".join(_COLUMNS)
        staging = (
            "CREATE TEMP TABLE stg_growth (LIKE growth_results INCLUDING DEFAULTS) "
            "ON COMMIT DROP"
        )
        loaded = 0
        years: set[int] = set()
        with self.engine.begin() as connection:
            driver = connection.connection.driver_connection
            if driver is None:
                raise RuntimeError("no DBAPI connection behind the engine")
            with driver.cursor() as cursor:
                cursor.execute(staging)
                with cursor.copy(f"COPY stg_growth ({columns}) FROM STDIN") as copy:
                    for record in records:
                        years.add(record.reporting_year)
                        copy.write_row(_values(record))
                        loaded += 1
                if not loaded:
                    return 0
                cursor.execute(
                    "DELETE FROM growth_results WHERE reporting_year = ANY(%s)",
                    (sorted(years),),
                )
                # Growth reaches schools that never appear in an assessment
                # file, so unknown entities are dropped rather than fatal.
                cursor.execute(
                    f"INSERT INTO growth_results ({columns}) SELECT {columns} "
                    "FROM stg_growth WHERE cds_code IN (SELECT cds_code FROM entities)"
                )
                cursor.execute("SELECT count(*) FROM growth_results")
        return loaded


def analyze(engine: Engine) -> None:
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        connection.execute(text("ANALYZE growth_results"))


class GrowthImportRunner:
    """Runs Growth Model imports."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.loader = GrowthLoader(engine)
        self.books = RunBookkeeper(engine)
        self.books.program = "GROWTH"

    def run(
        self,
        source_uri: str = DASHBOARD_BASE_URL,
        *,
        force: bool = False,
        years: Sequence[int] | None = None,
    ) -> RunOutcome:
        source = source_from_uri(source_uri)
        if isinstance(source, HttpSource):
            source.names = tuple(growth_file_names(years))

        run_id = self.books.start(source.uri)
        outcome = RunOutcome(
            run_id=str(run_id), source_uri=source.uri, status=IngestStatus.RUNNING
        )
        try:
            for obj in source.list_objects():
                if "growthmodel" not in obj.name.lower():
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
                analyze(self.engine)
            self.books.finish(run_id, outcome)
        return outcome

    def _load(
        self,
        source: ResearchFileSource,
        obj: SourceObject,
        run_id,
        *,
        force: bool,
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
                parser = GrowthRowParser(header_line.split("\t"))
                rows = (
                    parser.parse(row, default_year=year) for row in iter_rows(lines)
                )
                loaded = self.loader.load(rows)
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
            label="GROWTH",
            year=year,
        )
        logger.info("loaded %s: %s rows", obj.name, f"{loaded:,}")
        return FileOutcome(
            name=obj.name,
            status=IngestStatus.SUCCEEDED,
            label="GROWTH",
            reporting_year=year,
            rows=loaded,
            duration_seconds=time.monotonic() - started,
        )
