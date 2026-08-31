"""Bulk-load Dashboard indicator rows, and run an import over a source.

The mechanics mirror :mod:`app.ingest.loader`: rows go in through ``COPY``
into a temporary staging table and are then swapped into place inside one
transaction, so re-running over an unchanged source converges rather than
duplicating.  What a file covers is its ``(reporting_year, indicator_code)``
pairs, and exactly those are replaced.

That idempotence matters more here than on the assessment side.  The state
revises indicator files in place after release -- the 2024-25 academic files
were reissued four months later -- so a load is expected to happen again over
the same year and to win.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from psycopg import Cursor
from psycopg.types.json import Json
from sqlalchemy import Engine, text
from sqlmodel import Session, col, select

from app.ingest.dashboard_parser import (
    DashboardLayoutError,
    DashboardParsedRow,
    DashboardResultRecord,
    DashboardRowParser,
    indicator_from_filename,
    iter_rows,
    variant_from_filename,
)
from app.ingest.dashboard_reference import seed_dashboard_reference
from app.ingest.loader import _ENTITY_COLUMNS, _entity_row, _merge_entity
from app.ingest.parser import EntityRecord, ParseError
from app.ingest.sources import (
    HttpSource,
    ResearchFileSource,
    SourceObject,
    source_from_uri,
)
from app.model.ingest import IngestFile, IngestRun, IngestStatus

logger = logging.getLogger(__name__)

LOG_EVERY_ROWS = 250_000

_RESULT_COLUMNS = (
    "cds_code",
    "reporting_year",
    "indicator_code",
    "student_group_code",
    "variant",
    "curr_numerator",
    "curr_denominator",
    "prior_numerator",
    "prior_denominator",
    "curr_status",
    "prior_status",
    "change",
    "status_level",
    "change_level",
    "color",
    "box",
    "curr_nsize_met",
    "prior_nsize_met",
    "accountability_met",
    "small_denominator",
    "charter_flag",
    "coe_flag",
    "dass_flag",
    "is_projected",
    "projection_basis",
    "source_extras",
)

_CREATE_STAGING = (
    "CREATE TEMP TABLE {staging} (LIKE {target} INCLUDING DEFAULTS) ON COMMIT DROP"
)


def _result_row(record: DashboardResultRecord) -> tuple[Any, ...]:
    return (
        record.cds_code,
        record.reporting_year,
        record.indicator_code,
        record.student_group_code,
        record.variant,
        record.curr_numerator,
        record.curr_denominator,
        record.prior_numerator,
        record.prior_denominator,
        record.curr_status,
        record.prior_status,
        record.change,
        record.status_level,
        record.change_level,
        record.color,
        record.box,
        record.curr_nsize_met,
        record.prior_nsize_met,
        record.accountability_met,
        record.small_denominator,
        record.charter_flag,
        record.coe_flag,
        record.dass_flag,
        record.is_projected,
        record.projection_basis,
        Json(record.source_extras),
    )


@dataclass(slots=True)
class DashboardLoadCounts:
    """How much one file contributed."""

    results: int = 0
    entities: int = 0
    keys: set[tuple[int, str]] = field(default_factory=set)


class DashboardLoader:
    """Loads one Dashboard indicator file's parsed rows."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def load(self, rows: Iterable[DashboardParsedRow]) -> DashboardLoadCounts:
        counts = DashboardLoadCounts()
        entities: dict[str, EntityRecord] = {}

        with self.engine.begin() as connection:
            driver = connection.connection.driver_connection
            if driver is None:
                raise RuntimeError("no DBAPI connection behind the engine")
            with driver.cursor() as cursor:
                for staging, target in (
                    ("stg_dashboard_results", "dashboard_indicator_results"),
                    ("stg_dashboard_entities", "entities"),
                ):
                    cursor.execute(
                        _CREATE_STAGING.format(staging=staging, target=target)
                    )
                self._copy(cursor, rows, counts, entities)
                self._flush_entities(cursor, entities)
                counts.entities = len(entities)
                self._swap(cursor, counts)
        return counts

    def _copy(
        self,
        cursor: Cursor[Any],
        rows: Iterable[DashboardParsedRow],
        counts: DashboardLoadCounts,
        entities: dict[str, EntityRecord],
    ) -> None:
        sql = f"COPY stg_dashboard_results ({', '.join(_RESULT_COLUMNS)}) FROM STDIN"
        with cursor.copy(sql) as copy:
            for parsed in rows:
                record = parsed.result
                counts.keys.add((record.reporting_year, record.indicator_code))
                copy.write_row(_result_row(record))
                counts.results += 1
                if parsed.entity is not None:
                    known = entities.get(parsed.entity.cds_code)
                    if known is None:
                        entities[parsed.entity.cds_code] = parsed.entity
                    else:
                        _merge_entity(known, parsed.entity)
                if counts.results % LOG_EVERY_ROWS == 0:
                    logger.info("staged %s indicator rows", f"{counts.results:,}")

    def _flush_entities(
        self, cursor: Cursor[Any], entities: dict[str, EntityRecord]
    ) -> None:
        """Add entities the assessment files have never seen.

        A Dashboard file knows about schools that never sat a test, so their
        names are worth keeping -- but the Dashboard is not an administration,
        so an entity that already exists is left exactly as it is rather than
        having its test years or charter status rewritten.
        """
        if not entities:
            return
        columns = ", ".join(_ENTITY_COLUMNS)
        with cursor.copy(f"COPY stg_dashboard_entities ({columns}) FROM STDIN") as copy:
            for record in entities.values():
                copy.write_row(_entity_row(record))
        cursor.execute(
            f"INSERT INTO entities ({columns}) SELECT {columns} "
            "FROM stg_dashboard_entities ON CONFLICT (cds_code) DO NOTHING"
        )

    def _swap(self, cursor: Cursor[Any], counts: DashboardLoadCounts) -> None:
        if not counts.keys:
            return
        years = sorted({year for year, _ in counts.keys})
        indicators = sorted({indicator for _, indicator in counts.keys})
        cursor.execute(
            "DELETE FROM dashboard_indicator_results "
            "WHERE reporting_year = ANY(%s) AND indicator_code = ANY(%s)",
            (years, indicators),
        )
        cursor.execute(
            f"INSERT INTO dashboard_indicator_results ({', '.join(_RESULT_COLUMNS)}) "
            f"SELECT {', '.join(_RESULT_COLUMNS)} FROM stg_dashboard_results"
        )


def analyze(engine: Engine) -> None:
    """Refresh planner statistics after a load."""
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        for table in ("entities", "dashboard_indicator_results"):
            connection.execute(text(f"ANALYZE {table}"))


@dataclass(slots=True)
class FileOutcome:
    """What happened to one file during a run."""

    name: str
    status: IngestStatus
    indicator: str | None = None
    reporting_year: int | None = None
    results: int = 0
    duration_seconds: float = 0.0
    error: str | None = None


@dataclass(slots=True)
class RunOutcome:
    """The result of a whole run."""

    run_id: str
    source_uri: str
    status: IngestStatus
    files: list[FileOutcome] = field(default_factory=list)

    @property
    def results(self) -> int:
        return sum(outcome.results for outcome in self.files)


def _parsed_rows(
    rows: Iterator[list[str]], parser: DashboardRowParser, year: int | None
) -> Iterator[DashboardParsedRow]:
    for index, row in enumerate(rows, start=2):
        try:
            yield parser.parse(row, default_year=year)
        except ParseError as error:
            raise ParseError(f"line {index}: {error}") from error


def year_from_filename(name: str) -> int | None:
    """Pull the reporting year out of ``chronicdownload2025.txt``."""
    digits = "".join(character for character in name if character.isdigit())
    return int(digits[-4:]) if len(digits) >= 4 else None


class DashboardImportRunner:
    """Runs Dashboard imports and records what it did."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.loader = DashboardLoader(engine)

    def run(
        self,
        source_uri: str,
        *,
        force: bool = False,
        only: Sequence[str] | None = None,
        years: Sequence[int] | None = None,
    ) -> RunOutcome:
        """Import every changed Dashboard file under ``source_uri``."""
        source = source_from_uri(source_uri)
        if isinstance(source, HttpSource) and years and not source.years:
            # An HTTP source generates its own candidates, so tell it which
            # years to ask for rather than probing every one.
            source.years = tuple(years)

        with Session(self.engine) as session:
            seed_dashboard_reference(session)
            session.commit()
            run = IngestRun(source_uri=source.uri, started_at=datetime.now(tz=UTC))
            session.add(run)
            session.commit()
            session.refresh(run)
            run_id = run.id

        outcome = RunOutcome(
            run_id=str(run_id), source_uri=source.uri, status=IngestStatus.RUNNING
        )
        try:
            for obj in source.list_objects():
                if only and not any(fragment in obj.name for fragment in only):
                    continue
                file_year = year_from_filename(obj.name)
                if years and file_year is not None and file_year not in years:
                    continue
                outcome.files.append(
                    self._load_object(source, obj, run_id, force=force)
                )
            outcome.status = (
                IngestStatus.FAILED
                if any(f.status is IngestStatus.FAILED for f in outcome.files)
                else IngestStatus.SUCCEEDED
            )
        except Exception as error:  # noqa: BLE001 - recorded on the run row
            outcome.status = IngestStatus.FAILED
            self._finish_run(run_id, outcome, error=str(error))
            raise
        else:
            if outcome.results:
                analyze(self.engine)
            self._finish_run(run_id, outcome)
        return outcome

    def _already_loaded(self, session: Session, obj: SourceObject) -> bool:
        previous = session.exec(
            select(IngestFile)
            .where(IngestFile.source_key == obj.key)
            .where(IngestFile.status == IngestStatus.SUCCEEDED)
            .order_by(col(IngestFile.loaded_at).desc())
            .limit(1)
        ).first()
        if previous is None:
            return False
        return (
            previous.etag == obj.etag
            and previous.size_bytes == obj.size_bytes
            and previous.result_rows > 0
        )

    def _load_object(
        self,
        source: ResearchFileSource,
        obj: SourceObject,
        run_id: uuid.UUID,
        *,
        force: bool,
    ) -> FileOutcome:
        started = time.monotonic()
        with Session(self.engine) as session:
            if not force and self._already_loaded(session, obj):
                logger.info("skipping unchanged %s", obj.name)
                self._record_file(
                    session, run_id, obj, IngestStatus.SKIPPED, started=started
                )
                return FileOutcome(name=obj.name, status=IngestStatus.SKIPPED)

        indicator: str | None = None
        file_year = year_from_filename(obj.name)
        try:
            with source.open_text(obj) as lines:
                header_line = next(lines, "").rstrip("\r\n")
                if not header_line:
                    raise DashboardLayoutError(f"{obj.name} is empty")
                indicator = indicator_from_filename(obj.name)
                parser = DashboardRowParser(
                    header_line.split("\t"),
                    default_indicator=indicator,
                    default_variant=variant_from_filename(obj.name),
                    # Participation files name their columns after the year.
                    year_suffixed=indicator == "ELPACPART",
                    reporting_year=file_year,
                )
                logger.info("loading %s", obj.name)
                counts = self.loader.load(
                    _parsed_rows(iter_rows(lines), parser, file_year)
                )
            indicator = next((code for _, code in sorted(counts.keys)), None)
        except (DashboardLayoutError, ParseError, ValueError) as error:
            logger.warning("skipping %s: %s", obj.name, error)
            with Session(self.engine) as session:
                self._record_file(
                    session,
                    run_id,
                    obj,
                    IngestStatus.FAILED,
                    started=started,
                    error=str(error),
                )
            return FileOutcome(
                name=obj.name, status=IngestStatus.FAILED, error=str(error)
            )

        duration = time.monotonic() - started
        with Session(self.engine) as session:
            self._record_file(
                session,
                run_id,
                obj,
                IngestStatus.SUCCEEDED,
                started=started,
                results=counts.results,
                indicator=indicator,
                year=file_year,
            )
        return FileOutcome(
            name=obj.name,
            status=IngestStatus.SUCCEEDED,
            indicator=indicator,
            reporting_year=file_year,
            results=counts.results,
            duration_seconds=duration,
        )

    def _record_file(
        self,
        session: Session,
        run_id: uuid.UUID,
        obj: SourceObject,
        status: IngestStatus,
        *,
        started: float,
        results: int = 0,
        indicator: str | None = None,
        year: int | None = None,
        error: str | None = None,
    ) -> None:
        session.add(
            IngestFile(
                run_id=run_id,
                source_key=obj.key,
                etag=obj.etag,
                size_bytes=obj.size_bytes,
                last_modified=obj.last_modified,
                program="DASHBOARD",
                test_type=indicator,
                test_year=year,
                status=status,
                result_rows=results,
                subscore_rows=0,
                duration_seconds=time.monotonic() - started,
                error=error,
                loaded_at=datetime.now(tz=UTC),
            )
        )
        session.commit()

    def _finish_run(
        self, run_id: uuid.UUID, outcome: RunOutcome, *, error: str | None = None
    ) -> None:
        with Session(self.engine) as session:
            run = session.get(IngestRun, run_id)
            if run is None:
                return
            run.status = outcome.status
            run.finished_at = datetime.now(tz=UTC)
            run.files_seen = len(outcome.files)
            run.files_loaded = sum(
                1 for f in outcome.files if f.status is IngestStatus.SUCCEEDED
            )
            run.files_skipped = sum(
                1 for f in outcome.files if f.status is IngestStatus.SKIPPED
            )
            run.result_rows = outcome.results
            run.subscore_rows = 0
            run.error = error
            session.add(run)
            session.commit()
