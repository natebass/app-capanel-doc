"""Orchestrates an import of research files from a source location.

A run walks every object under the source, matches each one to a published
research file layout, and loads the ones that have changed since the last
successful run.  What "changed" means is the object's size and entity tag, so
pointing the importer at an S3 prefix and running it on a schedule loads only
newly uploaded administrations.

Reference data is seeded first, because result rows reference the assessment
catalogue and the parser needs the county names.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import Engine
from sqlmodel import Session, col, select

from app.ingest.layouts import (
    LayoutError,
    ResearchFileLayout,
    resolve_layout,
    year_from_filename,
)
from app.ingest.loader import ResearchFileLoader, analyze
from app.ingest.parser import ParsedRows, ParseError, RowParser, iter_rows
from app.ingest.reference_data import seed_reference_data
from app.ingest.sources import ResearchFileSource, SourceObject, source_from_uri
from app.model.ingest import IngestFile, IngestRun, IngestStatus

logger = logging.getLogger(__name__)

# Statewide files use a caret; administrations through 2018-19 used a comma.
CARET = "^"
COMMA = ","


@dataclass(slots=True)
class FileOutcome:
    """What happened to one object during a run."""

    name: str
    status: IngestStatus
    layout_key: str | None = None
    test_year: int | None = None
    results: int = 0
    subscores: int = 0
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

    @property
    def subscores(self) -> int:
        return sum(outcome.subscores for outcome in self.files)


def detect_delimiter(header_line: str) -> str:
    """Pick the delimiter a research file uses from its header row."""
    return CARET if CARET in header_line else COMMA


def _parsed_rows(
    rows: Iterator[Sequence[str]],
    layout: ResearchFileLayout,
    header: Sequence[str],
    year: int | None,
) -> Iterator[ParsedRows]:
    parser = RowParser(layout, header)
    for index, row in enumerate(rows, start=2):
        try:
            yield parser.parse(row, default_year=year)
        except ParseError as error:
            raise ParseError(f"line {index}: {error}") from error


class ImportRunner:
    """Runs imports and records what it did."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.loader = ResearchFileLoader(engine)

    def run(
        self,
        source_uri: str,
        *,
        force: bool = False,
        only: Sequence[str] | None = None,
        years: Sequence[int] | None = None,
    ) -> RunOutcome:
        """Import every changed research file under ``source_uri``.

        Args:
            source_uri: A local directory or an ``s3://bucket/prefix`` URI.
            force: Reload files even when their fingerprint is unchanged.
            only: Substrings; when given, only matching file names are loaded.
            years: Administration years to restrict the run to.
        """
        source = source_from_uri(source_uri)
        with Session(self.engine) as session:
            seed_reference_data(session)
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

        try:
            with source.open_text(obj) as lines:
                header_line = next(lines, "").rstrip("\r\n")
                if not header_line:
                    raise LayoutError(f"{obj.name} is empty")
                delimiter = detect_delimiter(header_line)
                header = [column.strip() for column in header_line.split(delimiter)]
                file_year = year_from_filename(obj.name)
                layout = resolve_layout(obj.name, header, test_year=file_year)
                logger.info("loading %s using layout %s", obj.name, layout.key)
                counts = self.loader.load(
                    _parsed_rows(iter_rows(lines, delimiter), layout, header, file_year)
                )
        except (LayoutError, ParseError, ValueError) as error:
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
                layout=layout,
                test_year=next(iter(sorted(counts.test_years or {})), file_year),
                results=counts.results,
                subscores=counts.subscores,
            )
        logger.info(
            "loaded %s: %s results, %s subscores, %s entities in %.1fs",
            obj.name,
            f"{counts.results:,}",
            f"{counts.subscores:,}",
            f"{counts.entities:,}",
            duration,
        )
        return FileOutcome(
            name=obj.name,
            status=IngestStatus.SUCCEEDED,
            layout_key=layout.key,
            test_year=next(iter(sorted(counts.test_years or {})), file_year),
            results=counts.results,
            subscores=counts.subscores,
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
        layout: ResearchFileLayout | None = None,
        test_year: int | None = None,
        results: int = 0,
        subscores: int = 0,
        error: str | None = None,
    ) -> None:
        session.add(
            IngestFile(
                run_id=run_id,
                source_key=obj.key,
                etag=obj.etag,
                size_bytes=obj.size_bytes,
                last_modified=obj.last_modified,
                program=layout.program.value if layout else None,
                test_type=layout.test_type if layout else None,
                test_year=test_year,
                status=status,
                result_rows=results,
                subscore_rows=subscores,
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
            run.subscore_rows = outcome.subscores
            run.error = error
            session.add(run)
            session.commit()
