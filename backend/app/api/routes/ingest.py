"""Administrative endpoints for the research file importer.

A run walks the configured source, loads whatever has changed and records what
it did.  Runs happen in the background because a statewide administration takes
minutes to load, so the request returns the run identifier and the history
endpoints report progress.
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlmodel import col, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.config import settings
from app.core.database import engine
from app.ingest.runner import ImportRunner
from app.model.ingest import IngestFile, IngestRun, IngestStatus
from app.model.reference import ApiModel
from app.service.reference import reset_reference_cache

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ingest",
    tags=["ingest"],
    dependencies=[Depends(get_current_active_superuser)],
)


class IngestRequest(ApiModel):
    """What to import."""

    source_uri: str | None = None
    force: bool = False
    only: list[str] | None = None
    years: list[int] | None = None


class IngestRunPublic(ApiModel):
    """One import run."""

    id: UUID
    source_uri: str
    status: IngestStatus
    started_at: datetime
    finished_at: datetime | None = None
    files_seen: int
    files_loaded: int
    files_skipped: int
    result_rows: int
    subscore_rows: int
    error: str | None = None


class IngestFilePublic(ApiModel):
    """The outcome of one file within a run."""

    source_key: str
    program: str | None = None
    test_type: str | None = None
    test_year: int | None = None
    status: IngestStatus
    result_rows: int
    subscore_rows: int
    duration_seconds: float | None = None
    error: str | None = None
    loaded_at: datetime | None = None


class IngestRunDetail(ApiModel):
    """A run together with every file it touched."""

    run: IngestRunPublic
    files: list[IngestFilePublic]


class IngestRunList(ApiModel):
    """A page of import runs."""

    data: list[IngestRunPublic]
    count: int


def _run_import(
    source_uri: str, force: bool, only: list[str] | None, years: list[int] | None
) -> None:
    """Background worker: import, then drop the cached reference snapshot."""
    try:
        ImportRunner(engine).run(source_uri, force=force, only=only, years=years)
    except Exception:
        logger.exception("research file import failed")
    finally:
        reset_reference_cache()


@router.post("/runs", status_code=202)
def start_ingest(
    request: IngestRequest, background_tasks: BackgroundTasks
) -> IngestRunPublic:
    """Start an import in the background."""
    source_uri = request.source_uri or settings.RESEARCH_FILE_SOURCE_URI
    if not source_uri:
        raise HTTPException(
            status_code=422,
            detail=(
                "No source configured. Provide sourceUri or set "
                "RESEARCH_FILE_SOURCE_URI."
            ),
        )
    background_tasks.add_task(
        _run_import, source_uri, request.force, request.only, request.years
    )
    return IngestRunPublic(
        id=UUID(int=0),
        source_uri=source_uri,
        status=IngestStatus.RUNNING,
        started_at=datetime.now(tz=UTC),
        files_seen=0,
        files_loaded=0,
        files_skipped=0,
        result_rows=0,
        subscore_rows=0,
    )


@router.get("/runs")
def list_runs(
    session: SessionDep, limit: int = Query(default=20, ge=1, le=100)
) -> IngestRunList:
    """The most recent import runs, newest first."""
    rows = session.exec(
        select(IngestRun).order_by(col(IngestRun.started_at).desc()).limit(limit)
    ).all()
    return IngestRunList(
        data=[IngestRunPublic.model_validate(row) for row in rows], count=len(rows)
    )


@router.get("/runs/{run_id}")
def read_run(session: SessionDep, run_id: UUID) -> IngestRunDetail:
    """One run with the outcome of every file it touched."""
    run = session.get(IngestRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Unknown ingest run")
    files = session.exec(
        select(IngestFile)
        .where(IngestFile.run_id == run_id)
        .order_by(col(IngestFile.source_key))
    ).all()
    return IngestRunDetail(
        run=IngestRunPublic.model_validate(run),
        files=[IngestFilePublic.model_validate(file) for file in files],
    )
