"""Loading Dashboard files into the database and reading them back.

The fixtures are real published rows stamped with a reporting year the state
has never used, so these tests can run against a database that also holds
really-imported data without colliding with it.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text
from sqlmodel import Session

from app.core.database import engine
from app.ingest.dashboard_loader import (
    DashboardImportRunner,
    DashboardLoader,
    year_from_filename,
)
from app.ingest.dashboard_parser import (
    DashboardRowParser,
    indicator_from_filename,
    iter_rows,
)
from app.ingest.dashboard_reference import seed_dashboard_reference
from app.ingest.sources import LocalSource
from app.model.ingest import IngestStatus

FIXTURES = Path(__file__).parent.parent / "fixtures" / "dashboard_files"
FIXTURE_YEAR = 2099


def load(name: str) -> int:
    """Load one fixture file the way the runner would."""
    path = FIXTURES / name
    with path.open(encoding="utf-8", newline="") as handle:
        lines = list(handle)
    parser = DashboardRowParser(
        lines[0].rstrip("\r\n").split("\t"),
        default_indicator=indicator_from_filename(name),
    )
    rows = (
        parser.parse(row, default_year=year_from_filename(name))
        for row in iter_rows(iter(lines[1:]))
    )
    return DashboardLoader(engine).load(rows).results


@pytest.fixture(scope="module", autouse=True)
def seeded(db: Session):
    seed_dashboard_reference(db)
    db.commit()
    yield
    with engine.begin() as connection:
        connection.execute(
            text(
                "DELETE FROM dashboard_indicator_results WHERE reporting_year = :year"
            ),
            {"year": FIXTURE_YEAR},
        )


def count(where: str = "", **params) -> int:
    clause = f" AND {where}" if where else ""
    with engine.connect() as connection:
        return connection.execute(
            text(
                "SELECT count(*) FROM dashboard_indicator_results "
                f"WHERE reporting_year = :year{clause}"
            ),
            {"year": FIXTURE_YEAR, **params},
        ).scalar_one()


def test_a_file_loads_its_rows() -> None:
    loaded = load("chronicdownload2099.txt")
    assert loaded > 0
    assert count("indicator_code = 'CHRO'") == loaded


def test_loading_the_same_file_twice_does_not_duplicate() -> None:
    first = load("graddownload2099.txt")
    assert count("indicator_code = 'GRAD'") == first
    second = load("graddownload2099.txt")
    assert second == first
    assert count("indicator_code = 'GRAD'") == first


def test_each_indicator_replaces_only_its_own_rows() -> None:
    load("chronicdownload2099.txt")
    load("suspdownload2099.txt")
    chronic = count("indicator_code = 'CHRO'")
    assert chronic > 0
    # Reloading suspension must leave chronic absenteeism untouched.
    load("suspdownload2099.txt")
    assert count("indicator_code = 'CHRO'") == chronic
    assert count("indicator_code = 'SUSP'") > 0


def test_published_rows_are_not_marked_projected() -> None:
    load("chronicdownload2099.txt")
    assert count("indicator_code = 'CHRO' AND is_projected") == 0


def test_indicator_specific_columns_survive_as_json() -> None:
    load("ccidownload2099.txt")
    with engine.connect() as connection:
        extras = connection.execute(
            text(
                "SELECT source_extras FROM dashboard_indicator_results "
                "WHERE reporting_year = :year AND indicator_code = 'CCI' "
                "AND source_extras ? 'curr_prep' LIMIT 1"
            ),
            {"year": FIXTURE_YEAR},
        ).scalar_one_or_none()
    assert extras is not None
    assert "curr_prep" in extras


def test_the_suspension_variant_is_part_of_the_key() -> None:
    load("suspdownload2099.txt")
    with engine.connect() as connection:
        variants = set(
            connection.execute(
                text(
                    "SELECT DISTINCT variant FROM dashboard_indicator_results "
                    "WHERE reporting_year = :year AND indicator_code = 'SUSP'"
                ),
                {"year": FIXTURE_YEAR},
            ).scalars()
        )
    assert variants <= {"ED", "HD", "UD", "ES", "MS", "HS"}
    assert len(variants) > 1


def test_a_run_over_a_directory_records_what_it_did() -> None:
    runner = DashboardImportRunner(engine)
    outcome = runner.run(str(FIXTURES), force=True, only=["elpi"])
    assert outcome.status is IngestStatus.SUCCEEDED
    assert outcome.results > 0
    assert [f.name for f in outcome.files] == ["elpidownload2099.txt"]
    assert outcome.files[0].indicator == "ELPI"


def test_an_unchanged_file_is_skipped_on_the_next_run() -> None:
    runner = DashboardImportRunner(engine)
    runner.run(str(FIXTURES), force=True, only=["science"])
    again = runner.run(str(FIXTURES), only=["science"])
    assert [f.status for f in again.files] == [IngestStatus.SKIPPED]


def test_english_learner_progress_needs_no_student_group_column() -> None:
    """Before 2024 the file had none; every row is English learners."""
    parser = DashboardRowParser(
        ["cds", "rtype", "reportingyear", "currstatus"],
        default_indicator="ELPI",
    )
    parsed = parser.parse(["00000000000000", "X", "2099", "46.4"])
    assert parsed.result.student_group_code == "EL"
    assert parsed.result.indicator_code == "ELPI"


def test_the_indicator_can_come_from_the_file_name() -> None:
    """The state only added an ``indicator`` column in 2023."""
    assert indicator_from_filename("chronicdownload2019.txt") == "CHRO"
    assert indicator_from_filename("sciencedownload2025.txt") == "SCIENCE"
    assert indicator_from_filename("something-else.txt") is None


def test_a_local_directory_is_read_as_utf8() -> None:
    """Dashboard files are UTF-8, unlike the cp1252 research files."""
    source = LocalSource(FIXTURES, encoding="utf-8")
    names = {obj.name for obj in source.list_objects()}
    assert "chronicdownload2099.txt" in names
