"""Bulk-load parsed research file rows into PostgreSQL.

A statewide research file is a few million rows, so rows go in through
``COPY`` into an unlogged staging table and are then swapped into place in one
transaction.  Loading a file is idempotent: everything already stored for the
test years and test IDs the file covers is deleted and replaced, so re-running
the importer over an unchanged bucket converges rather than duplicating.

Entities are collected as a side effect of reading the rows.  Names arrive
piecemeal -- a school row carries only the school and district names, a
district row only the district name -- so entity columns are merged rather than
overwritten, and the years an entity appears in are widened, never narrowed.
"""

from __future__ import annotations

import csv
import logging
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from functools import cache
from typing import Any

from psycopg import Cursor
from sqlalchemy import Engine, text

from app.ingest.parser import EntityRecord, ParsedRows, ResultRecord, SubscoreRecord
from app.ingest.reference_data import proficient_from_level
from app.model.reference import MetOrAboveSource

logger = logging.getLogger(__name__)

# Rows are handed to COPY one at a time; this only bounds how often progress is
# logged.
LOG_EVERY_ROWS = 500_000

# Subscore rows are spooled while the result stream is copying.  A statewide
# Smarter Balanced file produces several million of them, so the spool falls
# back to disk once it outgrows this.
SPOOL_MAX_MEMORY_BYTES = 64 * 1024 * 1024
SPOOL_CHUNK_CHARS = 1 << 20

_RESULT_COLUMNS = (
    "cds_code",
    "test_year",
    "test_id",
    "student_group_id",
    "grade",
    "students_enrolled",
    "students_tested",
    "students_tested_with_scores",
    "mean_scale_score",
    "level1_count",
    "level1_pct",
    "level2_count",
    "level2_pct",
    "level3_count",
    "level3_pct",
    "level4_count",
    "level4_pct",
    "met_or_above_count",
    "met_or_above_pct",
    "met_or_above_source",
    "overall_total",
    "suppressed",
)

_SUBSCORE_COLUMNS = (
    "cds_code",
    "test_year",
    "test_id",
    "student_group_id",
    "grade",
    "subscore_code",
    "mean_scale_score",
    "band1_count",
    "band1_pct",
    "band2_count",
    "band2_pct",
    "band3_count",
    "band3_pct",
    "band4_count",
    "band4_pct",
    "subscore_total",
)

_ENTITY_COLUMNS = (
    "cds_code",
    "county_code",
    "district_code",
    "school_code",
    "entity_level",
    "type_id",
    "is_charter",
    "charter_funding",
    "county_name",
    "district_name",
    "school_name",
    "zip_code",
    "display_name",
    "parent_cds_code",
    "first_test_year",
    "last_test_year",
)


@dataclass(slots=True)
class LoadCounts:
    """How much a single file contributed."""

    results: int = 0
    subscores: int = 0
    entities: int = 0
    test_years: set[int] | None = None
    test_ids: set[int] | None = None


def _pad(values: list[Any], width: int) -> list[Any]:
    """Right-pad a list of level values to the fixed column count."""
    return [*values, *([None] * (width - len(values)))][:width]


@cache
def _proficiency_cut(test_id: int, test_year: int) -> int | None:
    """Memoised proficiency cut; a file holds at most a handful of pairs."""
    return proficient_from_level(test_id, test_year)


def _derive_met_or_above(record: ResultRecord) -> None:
    """Fill in "met or above" for tests whose files do not publish it.

    Smarter Balanced and CAST print the figure; the alternate assessments, the
    CSA and the ELPAC do not, so it is summed from the levels at or above the
    state's proficiency cut.  ``met_or_above_source`` records which happened.
    """
    if record.met_or_above_source is not None:
        return
    cut = _proficiency_cut(record.test_id, record.test_year)
    if cut is None:
        return
    counts = record.level_counts[cut - 1 :]
    pcts = record.level_pcts[cut - 1 :]
    if counts and all(value is not None for value in counts):
        record.met_or_above_count = sum(value for value in counts if value is not None)
        record.met_or_above_source = MetOrAboveSource.DERIVED
    if pcts and all(value is not None for value in pcts):
        record.met_or_above_pct = sum(
            (value for value in pcts if value is not None), Decimal(0)
        )
        record.met_or_above_source = MetOrAboveSource.DERIVED


def _result_row(record: ResultRecord) -> tuple[Any, ...]:
    _derive_met_or_above(record)
    counts = _pad(list(record.level_counts), 4)
    pcts = _pad(list(record.level_pcts), 4)
    return (
        record.cds_code,
        record.test_year,
        record.test_id,
        record.student_group_id,
        record.grade,
        record.students_enrolled,
        record.students_tested,
        record.students_tested_with_scores,
        record.mean_scale_score,
        counts[0],
        pcts[0],
        counts[1],
        pcts[1],
        counts[2],
        pcts[2],
        counts[3],
        pcts[3],
        record.met_or_above_count,
        record.met_or_above_pct,
        record.met_or_above_source.value if record.met_or_above_source else None,
        record.overall_total,
        record.suppressed,
    )


def _subscore_row(record: SubscoreRecord) -> tuple[Any, ...]:
    counts = _pad(list(record.band_counts), 4)
    pcts = _pad(list(record.band_pcts), 4)
    return (
        record.cds_code,
        record.test_year,
        record.test_id,
        record.student_group_id,
        record.grade,
        record.subscore_code,
        record.mean_scale_score,
        counts[0],
        pcts[0],
        counts[1],
        pcts[1],
        counts[2],
        pcts[2],
        counts[3],
        pcts[3],
        record.subscore_total,
    )


def _csv_values(row: tuple[Any, ...]) -> list[str]:
    """Render a row for a CSV-format COPY, where an empty field means NULL."""
    return ["" if value is None else str(value) for value in row]


def _entity_row(record: EntityRecord) -> tuple[Any, ...]:
    return (
        record.cds_code,
        record.county_code,
        record.district_code,
        record.school_code,
        record.entity_level.value,
        record.type_id,
        record.is_charter,
        record.charter_funding.value if record.charter_funding else None,
        record.county_name,
        record.district_name,
        record.school_name,
        record.zip_code,
        record.display_name,
        record.parent_cds_code,
        record.first_test_year,
        record.last_test_year,
    )


def _merge_entity(existing: EntityRecord, incoming: EntityRecord) -> None:
    """Widen an entity with anything the incoming row knows and it does not."""
    existing.county_name = existing.county_name or incoming.county_name
    existing.district_name = existing.district_name or incoming.district_name
    existing.school_name = existing.school_name or incoming.school_name
    existing.zip_code = existing.zip_code or incoming.zip_code
    if existing.display_name == existing.cds_code:
        existing.display_name = incoming.display_name
    existing.is_charter = existing.is_charter or incoming.is_charter
    existing.charter_funding = existing.charter_funding or incoming.charter_funding
    existing.first_test_year = min(existing.first_test_year, incoming.first_test_year)
    existing.last_test_year = max(existing.last_test_year, incoming.last_test_year)


# Temporary tables keep the staged copy out of the WAL, scope it to this
# connection so two importers cannot collide, and drop it when the swap
# commits.
_CREATE_STAGING = (
    "CREATE TEMP TABLE {staging} (LIKE {target} INCLUDING DEFAULTS) ON COMMIT DROP"
)

_MERGE_ENTITIES = """
                  INSERT INTO entities AS target ({columns})
                  SELECT {columns}
                  FROM {staging}
                  ON CONFLICT (cds_code) DO
                  UPDATE SET
                      entity_level = EXCLUDED.entity_level,
                      type_id = EXCLUDED.type_id,
                      is_charter = target.is_charter OR EXCLUDED.is_charter,
                      charter_funding = COALESCE (EXCLUDED.charter_funding, target.charter_funding),
                      county_name = COALESCE (EXCLUDED.county_name, target.county_name),
                      district_name = COALESCE (EXCLUDED.district_name, target.district_name),
                      school_name = COALESCE (EXCLUDED.school_name, target.school_name),
                      zip_code = COALESCE (EXCLUDED.zip_code, target.zip_code),
                      display_name = CASE
                      WHEN target.display_name = target.cds_code THEN EXCLUDED.display_name
                      ELSE target.display_name
                  END
                  ,
    parent_cds_code = COALESCE(EXCLUDED.parent_cds_code, target.parent_cds_code),
    first_test_year = LEAST(target.first_test_year, EXCLUDED.first_test_year),
    last_test_year = GREATEST(target.last_test_year, EXCLUDED.last_test_year) \
                  """


class ResearchFileLoader:
    """Loads one research file's parsed rows into the database."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def load(self, rows: Iterable[ParsedRows]) -> LoadCounts:
        """Stage, then atomically replace, everything a file covers."""
        counts = LoadCounts(test_years=set(), test_ids=set())
        entities: dict[str, EntityRecord] = {}

        with self.engine.begin() as connection:
            driver = connection.connection.driver_connection
            if driver is None:
                raise RuntimeError("no DBAPI connection behind the engine")
            with driver.cursor() as cursor:
                self._prepare_staging(cursor)
                self._copy(cursor, rows, counts, entities)
                self._flush_entities(cursor, entities)
                counts.entities = len(entities)
                self._swap(cursor, counts)
        return counts

    def _prepare_staging(self, cursor: Cursor[Any]) -> None:
        for staging, target in (
            ("stg_assessment_results", "assessment_results"),
            ("stg_assessment_subscores", "assessment_subscores"),
            ("stg_entities", "entities"),
        ):
            cursor.execute(_CREATE_STAGING.format(staging=staging, target=target))

    def _copy(
        self,
        cursor: Cursor[Any],
        rows: Iterable[ParsedRows],
        counts: LoadCounts,
        entities: dict[str, EntityRecord],
    ) -> None:
        """Stream results straight into COPY and spool subscores alongside.

        A connection can only run one COPY at a time, and a research file row
        produces both a result and up to six subscores.  Rather than read the
        file twice, subscore rows are written to a spool as they are found --
        in memory until it grows past `SPOOL_MAX_MEMORY_BYTES`, then on disk --
        and copied in once the result stream has finished.
        """
        result_sql = (
            f"COPY stg_assessment_results ({', '.join(_RESULT_COLUMNS)}) FROM STDIN"
        )
        assert counts.test_years is not None and counts.test_ids is not None

        with tempfile.SpooledTemporaryFile(
            max_size=SPOOL_MAX_MEMORY_BYTES, mode="w+", newline="", encoding="utf-8"
        ) as spool:
            writer = csv.writer(spool)
            with cursor.copy(result_sql) as results:
                for parsed in rows:
                    record = parsed.result
                    counts.test_years.add(record.test_year)
                    counts.test_ids.add(record.test_id)
                    results.write_row(_result_row(record))
                    counts.results += 1
                    for subscore in parsed.subscores:
                        writer.writerow(_csv_values(_subscore_row(subscore)))
                        counts.subscores += 1
                    if parsed.entity is not None:
                        known = entities.get(parsed.entity.cds_code)
                        if known is None:
                            entities[parsed.entity.cds_code] = parsed.entity
                        else:
                            _merge_entity(known, parsed.entity)
                    if counts.results % LOG_EVERY_ROWS == 0:
                        logger.info("staged %s result rows", f"{counts.results:,}")

            if counts.subscores:
                spool.seek(0)
                subscore_sql = (
                    f"COPY stg_assessment_subscores ({', '.join(_SUBSCORE_COLUMNS)}) "
                    "FROM STDIN WITH (FORMAT csv)"
                )
                with cursor.copy(subscore_sql) as subscores:
                    while chunk := spool.read(SPOOL_CHUNK_CHARS):
                        subscores.write(chunk)

    def _flush_entities(
        self, cursor: Cursor[Any], entities: dict[str, EntityRecord]
    ) -> None:
        if not entities:
            return
        columns = ", ".join(_ENTITY_COLUMNS)
        with cursor.copy(f"COPY stg_entities ({columns}) FROM STDIN") as copy:
            for record in entities.values():
                copy.write_row(_entity_row(record))
        cursor.execute(_MERGE_ENTITIES.format(columns=columns, staging="stg_entities"))

    def _swap(self, cursor: Cursor[Any], counts: LoadCounts) -> None:
        assert counts.test_years is not None and counts.test_ids is not None
        if not counts.test_years or not counts.test_ids:
            return
        years = sorted(counts.test_years)
        test_ids = sorted(counts.test_ids)
        for target in ("assessment_subscores", "assessment_results"):
            cursor.execute(
                f"DELETE FROM {target} WHERE test_year = ANY(%s) AND test_id = ANY(%s)",
                (years, test_ids),
            )
        cursor.execute(
            f"INSERT INTO assessment_results ({', '.join(_RESULT_COLUMNS)}) "
            f"SELECT {', '.join(_RESULT_COLUMNS)} FROM stg_assessment_results"
        )
        cursor.execute(
            f"INSERT INTO assessment_subscores ({', '.join(_SUBSCORE_COLUMNS)}) "
            f"SELECT {', '.join(_SUBSCORE_COLUMNS)} FROM stg_assessment_subscores"
        )


def analyze(engine: Engine) -> None:
    """Refresh planner statistics after a load."""
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        for table in ("entities", "assessment_results", "assessment_subscores"):
            connection.execute(text(f"ANALYZE {table}"))
