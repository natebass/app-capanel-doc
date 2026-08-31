"""Replace a year's rows in one transaction.

Several of the Dashboard file families load the same way: stream rows into a
temporary staging table with ``COPY``, delete everything already stored for
the years the file covers, and move the staged rows across -- all inside one
transaction, so a reload converges rather than duplicating and a failure
leaves the previous load intact.

Rows whose entity is unknown are dropped rather than failing the file.  These
files reach schools that never sat an assessment, and a handful in every
family are not in the entity dimension; losing a whole year over them helps
nobody.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable, Sequence
from typing import Any

from sqlalchemy import Engine, text

logger = logging.getLogger(__name__)

_CREATE_STAGING = (
    "CREATE TEMP TABLE {staging} (LIKE {target} INCLUDING DEFAULTS) ON COMMIT DROP"
)


def replace_years(
    engine: Engine,
    *,
    table: str,
    columns: Sequence[str],
    rows: Iterable[tuple[Any, ...]],
    year_column: str = "reporting_year",
    year_index: int = 1,
    require_known_entity: bool = True,
) -> int:
    """Stage ``rows`` and swap them in, replacing the years they cover.

    ``year_index`` is the position of the reporting year within each row
    tuple, used to work out which years to clear.
    """
    staging = f"stg_{table}"
    column_list = ", ".join(columns)
    staged = 0
    years: set[int] = set()

    with engine.begin() as connection:
        driver = connection.connection.driver_connection
        if driver is None:
            raise RuntimeError("no DBAPI connection behind the engine")
        with driver.cursor() as cursor:
            cursor.execute(_CREATE_STAGING.format(staging=staging, target=table))
            with cursor.copy(f"COPY {staging} ({column_list}) FROM STDIN") as copy:
                for row in rows:
                    years.add(row[year_index])
                    copy.write_row(row)
                    staged += 1
            if not staged:
                return 0

            cursor.execute(
                f"DELETE FROM {table} WHERE {year_column} = ANY(%s)", (sorted(years),)
            )
            where = (
                " WHERE cds_code IN (SELECT cds_code FROM entities)"
                if require_known_entity
                else ""
            )
            cursor.execute(
                f"INSERT INTO {table} ({column_list}) "
                f"SELECT {column_list} FROM {staging}{where}"
            )
            loaded = cursor.rowcount
    if loaded < staged:
        logger.info("skipped %s rows with no matching entity", staged - loaded)
    return loaded


def analyze(engine: Engine, table: str) -> None:
    """Refresh planner statistics after a load."""
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        connection.execute(text(f"ANALYZE {table}"))
