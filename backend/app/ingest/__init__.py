"""Import CAASPP and ELPAC research files into the application database.

The pipeline has four pieces:

:mod:`app.ingest.sources`
    Where files come from -- a local directory or an S3 prefix.
:mod:`app.ingest.layouts`
    Which columns each published research file has, keyed by test type and
    administration year.
:mod:`app.ingest.parser`
    Row-level conversion, including the state's two kinds of missing value.
:mod:`app.ingest.loader`
    Bulk ``COPY`` into staging tables and an atomic swap into place.

:class:`app.ingest.runner.ImportRunner` ties them together and records what was
loaded so repeated runs only do new work.
"""

from app.ingest.runner import FileOutcome, ImportRunner, RunOutcome
from app.ingest.sources import LocalSource, S3Source, source_from_uri

__all__ = [
    "FileOutcome",
    "ImportRunner",
    "LocalSource",
    "RunOutcome",
    "S3Source",
    "source_from_uri",
]
