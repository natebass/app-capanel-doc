"""Where research files are read from.

Two sources are supported and they present the same interface, so the importer
does not care which one it is given:

``LocalSource``
    A directory tree, used for development and for one-off loads from a
    downloaded copy of the files.
``S3Source``
    An S3 bucket and prefix, which is how the deployed application gets its
    data.  New administrations are published by uploading them to the bucket;
    nothing has to be parsed or pushed from a workstation.

Both yield objects with the size, entity tag and modification time the
importer records so it can skip files it has already loaded.

Research files are distributed as ZIP archives and are sometimes stored
compressed, so ``.zip`` and ``.gz`` are unwrapped transparently.  ZIP archives
need random access, which an S3 response body cannot provide, so those are
staged to a temporary file first.
"""

from __future__ import annotations

import gzip
import io
import shutil
import tempfile
import zipfile
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Protocol, runtime_checkable
from urllib.parse import urlparse

# The state publishes research files in Windows code page 1252; district and
# school names contain characters that are not valid UTF-8.
FILE_ENCODING = "cp1252"

# Extensions that can contain a research file.
_DATA_SUFFIXES = frozenset({".txt", ".csv", ".dat"})
_ARCHIVE_SUFFIXES = frozenset({".zip", ".gz"})


@dataclass(frozen=True, slots=True)
class SourceObject:
    """One candidate research file in a source location."""

    key: str
    name: str
    size_bytes: int | None = None
    etag: str | None = None
    last_modified: datetime | None = None

    @property
    def fingerprint(self) -> str:
        """A value that changes whenever the object's contents change."""
        return f"{self.etag or ''}:{self.size_bytes or 0}"


@runtime_checkable
class ResearchFileSource(Protocol):
    """A place research files can be read from."""

    uri: str

    def list_objects(self) -> Iterator[SourceObject]:
        """Yield every candidate research file, in a stable order."""

    def open_text(self, obj: SourceObject) -> AbstractContextManager[Iterator[str]]:
        """Open an object as decoded text lines."""


def _is_candidate(name: str) -> bool:
    suffixes = Path(name).suffixes
    if not suffixes:
        return False
    if suffixes[-1].lower() in _ARCHIVE_SUFFIXES:
        return True
    return suffixes[-1].lower() in _DATA_SUFFIXES


@contextmanager
def _decode(binary: IO[bytes]) -> Iterator[Iterator[str]]:
    wrapper = io.TextIOWrapper(
        binary, encoding=FILE_ENCODING, errors="replace", newline=""
    )
    try:
        yield wrapper
    finally:
        wrapper.detach()


@contextmanager
def _open_archive_member(path: Path) -> Iterator[Iterator[str]]:
    """Open the single data member of a ZIP archive as text."""
    with zipfile.ZipFile(path) as archive:
        members = [
            info
            for info in archive.infolist()
            if not info.is_dir()
            and _is_candidate(info.filename)
            and Path(info.filename).suffix.lower() in _DATA_SUFFIXES
        ]
        if not members:
            raise FileNotFoundError(f"{path} contains no research file")
        if len(members) > 1:
            raise ValueError(
                f"{path} contains {len(members)} data files; extract it and load "
                "each research file separately"
            )
        with archive.open(members[0]) as member, _decode(member) as lines:
            yield lines


class LocalSource:
    """Reads research files from a directory tree."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser()
        self.uri = str(self.root)

    def list_objects(self) -> Iterator[SourceObject]:
        if not self.root.exists():
            raise FileNotFoundError(f"Research file directory not found: {self.root}")
        paths = [self.root] if self.root.is_file() else sorted(self.root.rglob("*"))
        for path in paths:
            if not path.is_file() or not _is_candidate(path.name):
                continue
            stat = path.stat()
            yield SourceObject(
                key=str(path),
                name=path.name,
                size_bytes=stat.st_size,
                # Local files have no entity tag; the modification time stands
                # in, which is enough to notice a replaced file.
                etag=str(int(stat.st_mtime)),
                last_modified=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
            )

    @contextmanager
    def open_text(self, obj: SourceObject) -> Iterator[Iterator[str]]:
        path = Path(obj.key)
        suffix = path.suffix.lower()
        if suffix == ".zip":
            with _open_archive_member(path) as lines:
                yield lines
        elif suffix == ".gz":
            with gzip.open(path, "rb") as binary, _decode(binary) as lines:
                yield lines
        else:
            with path.open("rb") as binary, _decode(binary) as lines:
                yield lines


class S3Source:
    """Reads research files from an S3 bucket prefix."""

    def __init__(
        self, bucket: str, prefix: str = "", *, client: object | None = None
    ) -> None:
        self.bucket = bucket
        self.prefix = prefix.lstrip("/")
        self.uri = f"s3://{bucket}/{self.prefix}".rstrip("/")
        self._client = client

    @property
    def client(self) -> object:
        if self._client is None:
            import boto3  # imported lazily so local runs need no AWS SDK

            self._client = boto3.client("s3")
        return self._client

    def list_objects(self) -> Iterator[SourceObject]:
        paginator = self.client.get_paginator("list_objects_v2")  # type: ignore[attr-defined]
        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for item in page.get("Contents", ()):
                key = item["Key"]
                name = key.rsplit("/", 1)[-1]
                if not _is_candidate(name):
                    continue
                yield SourceObject(
                    key=key,
                    name=name,
                    size_bytes=item.get("Size"),
                    etag=(item.get("ETag") or "").strip('"') or None,
                    last_modified=item.get("LastModified"),
                )

    @contextmanager
    def open_text(self, obj: SourceObject) -> Iterator[Iterator[str]]:
        suffix = Path(obj.name).suffix.lower()
        response = self.client.get_object(Bucket=self.bucket, Key=obj.key)  # type: ignore[attr-defined]
        body = response["Body"]
        if suffix == ".zip":
            # ZipFile seeks, so the archive is staged locally first.
            with tempfile.NamedTemporaryFile(suffix=".zip") as staged:
                shutil.copyfileobj(body, staged)
                staged.flush()
                with _open_archive_member(Path(staged.name)) as lines:
                    yield lines
        elif suffix == ".gz":
            with gzip.GzipFile(fileobj=body) as binary, _decode(binary) as lines:
                yield lines
        else:
            with _decode(body) as lines:
                yield lines


def source_from_uri(uri: str) -> ResearchFileSource:
    """Build a source from a local path or an ``s3://bucket/prefix`` URI."""
    parsed = urlparse(uri)
    if parsed.scheme == "s3":
        return S3Source(parsed.netloc, parsed.path)
    if parsed.scheme in {"", "file"}:
        return LocalSource(parsed.path if parsed.scheme == "file" else uri)
    raise ValueError(f"Unsupported research file source: {uri!r}")
