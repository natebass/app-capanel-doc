"""Bookkeeping for research-file imports.

The importer is expected to run repeatedly against the same object store
prefix, so it records what it has already loaded.  A source object is skipped
when its size and entity tag still match the row written by the last successful
load, which is what lets a scheduled run in AWS re-read the whole bucket and do
work only for the files that actually changed.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Index
from sqlmodel import Field

from app.model.reference import ApiModel, enum_type


class IngestStatus(StrEnum):
    """Lifecycle of an ingest run or of one file within it."""

    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class IngestRun(ApiModel, table=True):
    """One invocation of the importer over a source location."""

    __tablename__ = "ingest_runs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source_uri: str = Field(max_length=500)
    status: IngestStatus = Field(
        default=IngestStatus.RUNNING, sa_type=enum_type(IngestStatus)
    )
    started_at: datetime
    finished_at: datetime | None = Field(default=None)
    files_seen: int = Field(default=0)
    files_loaded: int = Field(default=0)
    files_skipped: int = Field(default=0)
    result_rows: int = Field(default=0)
    subscore_rows: int = Field(default=0)
    error: str | None = Field(default=None)


class IngestFile(ApiModel, table=True):
    """The outcome of loading a single research file."""

    __tablename__ = "ingest_files"
    __table_args__ = (Index("ix_ingest_files_key", "source_key"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_id: uuid.UUID = Field(foreign_key="ingest_runs.id", index=True)
    source_key: str = Field(max_length=500)
    etag: str | None = Field(default=None, max_length=200)
    size_bytes: int | None = Field(default=None)
    last_modified: datetime | None = Field(default=None)
    program: str | None = Field(default=None, max_length=10)
    test_type: str | None = Field(default=None, max_length=5)
    test_year: int | None = Field(default=None)
    status: IngestStatus = Field(
        default=IngestStatus.RUNNING, sa_type=enum_type(IngestStatus)
    )
    result_rows: int = Field(default=0)
    subscore_rows: int = Field(default=0)
    duration_seconds: float | None = Field(default=None)
    error: str | None = Field(default=None)
    loaded_at: datetime | None = Field(default=None)
