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
import logging
import shutil
import tempfile
import zipfile
from collections.abc import Iterator, Sequence
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import IO, Any, Protocol, cast, runtime_checkable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# The state publishes research files in Windows code page 1252; district and
# school names contain characters that are not valid UTF-8.
FILE_ENCODING = "cp1252"

# Extensions that can contain a research file.
_DATA_SUFFIXES = frozenset({".txt", ".csv", ".dat", ".xlsx"})
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
    encoding: str

    def list_objects(self) -> Iterator[SourceObject]:
        """Yield every candidate research file, in a stable order."""

    def open_text(self, obj: SourceObject) -> AbstractContextManager[Iterator[str]]:
        """Open an object as decoded text lines."""

    def open_file(self, obj: SourceObject) -> AbstractContextManager[Path]:
        """Make an object available as a real file on disk.

        Needed by readers that seek -- a spreadsheet, for instance -- which a
        streamed HTTP or S3 response body cannot support.
        """


def _is_candidate(name: str) -> bool:
    suffixes = Path(name).suffixes
    if not suffixes:
        return False
    if suffixes[-1].lower() in _ARCHIVE_SUFFIXES:
        return True
    return suffixes[-1].lower() in _DATA_SUFFIXES


@contextmanager
def _decode(
    binary: IO[bytes], encoding: str = FILE_ENCODING
) -> Iterator[Iterator[str]]:
    wrapper = io.TextIOWrapper(binary, encoding=encoding, errors="replace", newline="")
    try:
        yield wrapper
    finally:
        wrapper.detach()


@contextmanager
def _open_archive_member(
    path: Path, encoding: str = FILE_ENCODING
) -> Iterator[Iterator[str]]:
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
        with archive.open(members[0]) as member, _decode(member, encoding) as lines:
            yield lines


@contextmanager
def _staged(body: IO[bytes], suffix: str) -> Iterator[Path]:
    """Copy a non-seekable stream to a temporary file and yield its path."""
    with tempfile.NamedTemporaryFile(suffix=suffix) as staged:
        shutil.copyfileobj(body, staged)
        staged.flush()
        yield Path(staged.name)


class LocalSource:
    """Reads research files from a directory tree."""

    def __init__(self, root: str | Path, *, encoding: str = FILE_ENCODING) -> None:
        self.root = Path(root).expanduser()
        self.uri = str(self.root)
        self.encoding = encoding

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
            with _open_archive_member(path, self.encoding) as lines:
                yield lines
        elif suffix == ".gz":
            with gzip.open(path, "rb") as gzipped:
                # GzipFile reads like a binary file without declaring so.
                with _decode(cast(IO[bytes], gzipped), self.encoding) as lines:
                    yield lines
        else:
            with path.open("rb") as binary, _decode(binary, self.encoding) as lines:
                yield lines

    @contextmanager
    def open_file(self, obj: SourceObject) -> Iterator[Path]:
        yield Path(obj.key)


class S3Source:
    """Reads research files from an S3 bucket prefix."""

    def __init__(
        self,
        bucket: str,
        prefix: str = "",
        *,
        client: Any | None = None,
        encoding: str = FILE_ENCODING,
    ) -> None:
        self.bucket = bucket
        self.prefix = prefix.lstrip("/")
        self.uri = f"s3://{bucket}/{self.prefix}".rstrip("/")
        self._client = client
        self.encoding = encoding

    @property
    def client(self) -> Any:
        if self._client is None:
            import boto3  # imported lazily so local runs need no AWS SDK

            self._client = boto3.client("s3")
        return self._client

    def list_objects(self) -> Iterator[SourceObject]:
        paginator = self.client.get_paginator("list_objects_v2")
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
    def open_file(self, obj: SourceObject) -> Iterator[Path]:
        response = self.client.get_object(Bucket=self.bucket, Key=obj.key)
        with _staged(response["Body"], Path(obj.name).suffix) as path:
            yield path

    @contextmanager
    def open_text(self, obj: SourceObject) -> Iterator[Iterator[str]]:
        suffix = Path(obj.name).suffix.lower()
        response = self.client.get_object(Bucket=self.bucket, Key=obj.key)
        body = response["Body"]
        if suffix == ".zip":
            # ZipFile seeks, so the archive is staged locally first.
            with tempfile.NamedTemporaryFile(suffix=".zip") as staged:
                shutil.copyfileobj(body, staged)
                staged.flush()
                with _open_archive_member(Path(staged.name), self.encoding) as lines:
                    yield lines
        elif suffix == ".gz":
            with gzip.GzipFile(fileobj=body) as gzipped:
                with _decode(cast(IO[bytes], gzipped), self.encoding) as lines:
                    yield lines
        else:
            with _decode(body, self.encoding) as lines:
                yield lines


# The state publishes Dashboard files as UTF-8 rather than the code page the
# research files use.
DASHBOARD_ENCODING = "utf-8"

# Where the Dashboard indicator files live, and the indicators available.
DASHBOARD_BASE_URL = "https://www3.cde.ca.gov/researchfiles/cadashboard/"
DASHBOARD_FILE_STEMS = (
    "ela",
    "math",
    "chronic",
    "susp",
    "grad",
    "elpi",
    "cci",
    "science",
)

# Files in the same family that do not follow the ``{stem}download{year}``
# naming: the alternative-school graduation rate and ELPAC participation.
DASHBOARD_EXTRA_STEMS = ("dass1yeargraduationrate", "elpacpart")


class HttpSource:
    """Reads Dashboard indicator files straight from the state's web server.

    Unlike a bucket or a directory there is nothing to list, so the candidate
    file names are generated from the published naming convention --
    ``{indicator}download{year}.txt`` -- and a HEAD request decides whether
    each one exists and whether it has changed.  The state revises these files
    in place after release, which is exactly what the entity tag catches.
    """

    def __init__(
        self,
        base_url: str = DASHBOARD_BASE_URL,
        *,
        years: Sequence[int] | None = None,
        stems: Sequence[str] = DASHBOARD_FILE_STEMS,
        extra_stems: Sequence[str] = DASHBOARD_EXTRA_STEMS,
        encoding: str = DASHBOARD_ENCODING,
        names: Sequence[str] | None = None,
        opener: Any | None = None,
    ) -> None:
        self.base_url = base_url if base_url.endswith("/") else f"{base_url}/"
        self.uri = self.base_url
        self.years = tuple(years) if years else ()
        self.stems = tuple(stems)
        # An explicit file list, for families that do not follow the
        # ``{stem}download{year}`` convention -- the Local Indicators are
        # published as ``Pr32025``.
        self.names = tuple(names) if names is not None else None
        self.extra_stems = tuple(extra_stems)
        self.encoding = encoding
        self._opener = opener or urlopen

    def _candidates(self) -> Iterator[str]:
        if self.names is not None:
            yield from self.names
            return
        years = self.years or range(_FIRST_DASHBOARD_YEAR, _latest_dashboard_year() + 1)
        for year in years:
            for stem in self.stems:
                yield f"{stem}download{year}.txt"
            for stem in self.extra_stems:
                yield f"{stem}{year}.txt"

    def list_objects(self) -> Iterator[SourceObject]:
        # The state's server answers HEAD with a 303 redirect loop, so
        # existence and fingerprint are probed with a ranged GET whose body is
        # never read.
        probe = _HTTP_HEADERS | {"Range": "bytes=0-0"}
        for name in self._candidates():
            url = f"{self.base_url}{name}"
            request = Request(url, headers=probe)
            try:
                with self._opener(request, timeout=_HTTP_TIMEOUT) as response:
                    headers = response.headers
            except (HTTPError, URLError) as error:
                # A year the state has not published is a 404, not a failure.
                logger.debug("skipping %s: %s", url, error)
                continue
            size = headers.get("Content-Length")
            yield SourceObject(
                key=url,
                name=name,
                size_bytes=int(size) if size and size.isdigit() else None,
                etag=(headers.get("ETag") or "").strip('"') or None,
                last_modified=_parse_http_date(headers.get("Last-Modified")),
            )

    @contextmanager
    def open_file(self, obj: SourceObject) -> Iterator[Path]:
        request = Request(obj.key, headers=_HTTP_HEADERS)
        with self._opener(request, timeout=_HTTP_TIMEOUT) as response:
            with _staged(cast(IO[bytes], response), Path(obj.name).suffix) as path:
                yield path

    @contextmanager
    def open_text(self, obj: SourceObject) -> Iterator[Iterator[str]]:
        request = Request(obj.key, headers=_HTTP_HEADERS)
        with self._opener(request, timeout=_HTTP_TIMEOUT) as response:
            with _decode(cast(IO[bytes], response), self.encoding) as lines:
                yield lines


_HTTP_TIMEOUT = 120
_HTTP_HEADERS = {"User-Agent": "app-capanel/1.0 (+https://github.com/opensacorg)"}
# The first Dashboard with downloadable indicator files.
_FIRST_DASHBOARD_YEAR = 2017


def _latest_dashboard_year() -> int:
    """The newest year that could plausibly have been published.

    The Dashboard is released in the autumn, so the file for a spring year is
    available from roughly November of that same calendar year.
    """
    today = datetime.now(tz=UTC)
    return today.year if today.month >= 11 else today.year - 1


def _parse_http_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw)
    except TypeError, ValueError:
        return None


def source_from_uri(uri: str) -> ResearchFileSource:
    """Build a source from a path, an ``s3://`` prefix or an ``https://`` URL."""
    parsed = urlparse(uri)
    if parsed.scheme == "s3":
        return S3Source(parsed.netloc, parsed.path)
    if parsed.scheme in {"http", "https"}:
        return HttpSource(uri)
    if parsed.scheme in {"", "file"}:
        return LocalSource(parsed.path if parsed.scheme == "file" else uri)
    raise ValueError(f"Unsupported research file source: {uri!r}")
