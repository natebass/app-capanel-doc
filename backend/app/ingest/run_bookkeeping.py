"""Shared bookkeeping for file imports.

Every importer in this package does the same three things around the part that
is actually specific to it: decide whether a file has already been loaded,
record what happened to each file, and close out the run.  Those are here so
that adding a new family of files -- growth, enrolment, participation -- means
writing a parser and a loader, not a fourth copy of this.

What each importer still owns is the interesting part: which files exist, how
to read one, and where its rows go.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import Engine
from sqlmodel import Session, col, select

from app.ingest.sources import SourceObject
from app.model.ingest import IngestFile, IngestRun, IngestStatus


@dataclass(slots=True)
class FileOutcome:
    """What happened to one file during a run."""

    name: str
    status: IngestStatus
    #: Whatever identifies the file within its family: an indicator code, a
    #: priority number, a subject.
    label: str | None = None
    reporting_year: int | None = None
    rows: int = 0
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
    def rows(self) -> int:
        return sum(outcome.rows for outcome in self.files)

    def settle(self) -> None:
        """Decide the run's status from its files."""
        self.status = (
            IngestStatus.FAILED
            if any(f.status is IngestStatus.FAILED for f in self.files)
            else IngestStatus.SUCCEEDED
        )


class RunBookkeeper:
    """Records what an import run did."""

    #: Stored on each file row so runs of different families can be told apart.
    program = "DASHBOARD"

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def start(self, source_uri: str) -> uuid.UUID:
        with Session(self.engine) as session:
            run = IngestRun(source_uri=source_uri, started_at=datetime.now(tz=UTC))
            session.add(run)
            session.commit()
            session.refresh(run)
            return run.id

    def already_loaded(self, obj: SourceObject) -> bool:
        """Whether this exact file has been loaded successfully before.

        The state revises files in place, so "the same file" means the same
        entity tag *and* the same size, not the same name.
        """
        with Session(self.engine) as session:
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

    def record_file(
        self,
        run_id: uuid.UUID,
        obj: SourceObject,
        status: IngestStatus,
        *,
        started: float,
        rows: int = 0,
        label: str | None = None,
        year: int | None = None,
        error: str | None = None,
    ) -> None:
        with Session(self.engine) as session:
            session.add(
                IngestFile(
                    run_id=run_id,
                    source_key=obj.key,
                    etag=obj.etag,
                    size_bytes=obj.size_bytes,
                    last_modified=obj.last_modified,
                    program=self.program,
                    test_type=label,
                    test_year=year,
                    status=status,
                    result_rows=rows,
                    subscore_rows=0,
                    duration_seconds=time.monotonic() - started,
                    error=error,
                    loaded_at=datetime.now(tz=UTC),
                )
            )
            session.commit()

    def finish(
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
            run.result_rows = outcome.rows
            run.subscore_rows = 0
            run.error = error
            session.add(run)
            session.commit()
