"""Loading Local Indicator files and reading them back."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text
from sqlmodel import Session

from app.core.database import engine
from app.ingest.local_indicator_loader import (
    LocalIndicatorImportRunner,
    LocalIndicatorLoader,
    local_indicator_names,
)
from app.ingest.local_indicator_parser import (
    LocalIndicatorRowParser,
    detect_delimiter,
    iter_rows,
    parse_filename,
)
from app.ingest.local_indicator_reference import seed_local_indicator_reference
from app.model.ingest import IngestStatus

FIXTURES = Path(__file__).parent.parent / "fixtures" / "local_indicators"
FIXTURE_YEAR = 2099


def load(name: str) -> int:
    priority, year = parse_filename(name)
    lines = (FIXTURES / name).read_text(encoding="utf-8").splitlines()
    delimiter = detect_delimiter(lines[0])
    parser = LocalIndicatorRowParser(
        lines[0].split(delimiter), default_priority=priority, default_year=year
    )
    records = [parser.parse(row) for row in iter_rows(iter(lines[1:]), delimiter)]
    return LocalIndicatorLoader(engine).load(records).rows


@pytest.fixture(scope="module", autouse=True)
def seeded(db: Session):
    seed_local_indicator_reference(db)
    db.commit()
    yield
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM local_indicator_results WHERE reporting_year = :y"),
            {"y": FIXTURE_YEAR},
        )


def count(where: str = "") -> int:
    clause = f" AND {where}" if where else ""
    with engine.connect() as connection:
        return connection.execute(
            text(
                "SELECT count(*) FROM local_indicator_results "
                f"WHERE reporting_year = :y{clause}"
            ),
            {"y": FIXTURE_YEAR},
        ).scalar_one()


def test_a_file_loads_its_rows() -> None:
    loaded = load("Pr12099.txt")
    assert loaded > 0
    assert count("priority_number = 1") == loaded


def test_loading_the_same_file_twice_does_not_duplicate() -> None:
    first = load("Pr62099.txt")
    assert count("priority_number = 6") == first
    assert load("Pr62099.txt") == first
    assert count("priority_number = 6") == first


def test_each_priority_replaces_only_its_own_rows() -> None:
    load("Pr12099.txt")
    load("Pr62099.txt")
    one = count("priority_number = 1")
    load("Pr62099.txt")
    assert count("priority_number = 1") == one


def test_narratives_keep_their_paragraph_breaks() -> None:
    """The whole reason the importer prefers spreadsheets."""
    load("Pr32099.txt")
    with engine.connect() as connection:
        longest = connection.execute(
            text(
                "SELECT max(length(value)) FROM local_indicator_results, "
                "jsonb_each_text(responses) WHERE reporting_year = :y "
                "AND priority_number = 3"
            ),
            {"y": FIXTURE_YEAR},
        ).scalar_one()
    assert longest and longest > 200, "expected substantial narrative text"


def test_rows_whose_lea_is_unknown_are_skipped_not_fatal() -> None:
    """Two of the ~2,300 LEAs are not in the entity dimension."""
    from app.ingest.local_indicator_parser import LocalIndicatorRecord

    records = [
        LocalIndicatorRecord(
            cds_code="99999999999999",
            reporting_year=FIXTURE_YEAR,
            priority_number=7,
            performance="Met",
        )
    ]
    assert LocalIndicatorLoader(engine).load(records).rows == 0


def test_a_run_over_a_directory_records_what_it_did() -> None:
    runner = LocalIndicatorImportRunner(engine)
    runner.suffix = ".txt"
    outcome = runner.run(str(FIXTURES), force=True, priorities=[9])
    assert outcome.status is IngestStatus.SUCCEEDED
    assert [f.name for f in outcome.files] == ["Pr92099.txt"]
    assert outcome.files[0].priority == 9


def test_an_unchanged_file_is_skipped_on_the_next_run() -> None:
    runner = LocalIndicatorImportRunner(engine)
    runner.suffix = ".txt"
    runner.run(str(FIXTURES), force=True, priorities=[1])
    again = runner.run(str(FIXTURES), priorities=[1])
    assert [f.status for f in again.files] == [IngestStatus.SKIPPED]


def test_the_published_file_names_skip_the_year_with_no_dashboard() -> None:
    names = local_indicator_names(priorities=[1])
    years = {int(n[3:7]) for n in names}
    assert 2020 not in years, "no local indicators were published for 2020"
    assert 2019 in years and 2021 in years
