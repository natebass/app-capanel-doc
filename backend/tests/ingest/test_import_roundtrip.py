"""End-to-end import of fixture research files, then read back through the API.

The fixtures use administration years the state never published research files
for (2015-16 for Smarter Balanced, 2016-17 for the alternate assessments), so
this exercises the real loader against the real database without touching rows
imported from actual files.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, col, delete, select

from app.core.database import engine
from app.ingest.runner import ImportRunner
from app.model.reference import Entity
from app.model.results import AssessmentResult, AssessmentSubscore
from app.service.reference import reset_reference_cache

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "research_files"
FIXTURE_YEARS = (2016, 2017)
STATE = "00000000000000"
SCHOOL = "58999999900001"
CHARTER = "58999999900002"


@pytest.fixture(scope="module", autouse=True)
def imported() -> Iterator[None]:
    ImportRunner(engine).run(str(FIXTURES), force=True)
    reset_reference_cache()
    yield
    with Session(engine) as session:
        for model in (AssessmentSubscore, AssessmentResult):
            session.exec(delete(model).where(col(model.test_year).in_(FIXTURE_YEARS)))
        session.exec(delete(Entity).where(col(Entity.cds_code).in_((SCHOOL, CHARTER))))
        session.commit()
    reset_reference_cache()


def read(
    cds_code: str, test_id: int, grade: str = "13", year: int = 2016
) -> AssessmentResult:
    with Session(engine) as session:
        row = session.exec(
            select(AssessmentResult)
            .where(AssessmentResult.cds_code == cds_code)
            .where(AssessmentResult.test_year == year)
            .where(AssessmentResult.test_id == test_id)
            .where(AssessmentResult.student_group_id == 1)
            .where(AssessmentResult.grade == grade)
        ).one()
    return row


def test_published_percentages_are_stored_unchanged() -> None:
    row = read(STATE, 1)
    assert float(row.met_or_above_pct or 0) == 45.00
    assert row.met_or_above_source == "published"
    assert float(row.level4_pct or 0) == 20.00
    assert row.students_tested == 110


def test_met_or_above_is_derived_where_the_state_does_not_publish_it() -> None:
    """The alternate assessments print levels but no proficiency figure."""
    row = read(STATE, 3, year=2017)
    assert row.met_or_above_source == "derived"
    assert row.met_or_above_count == 26
    assert float(row.met_or_above_pct or 0) == 15.00


def test_subscores_land_lowest_band_first() -> None:
    with Session(engine) as session:
        area = session.exec(
            select(AssessmentSubscore)
            .where(AssessmentSubscore.cds_code == STATE)
            .where(AssessmentSubscore.test_year == 2016)
            .where(AssessmentSubscore.subscore_code == "AREA_1")
            .where(AssessmentSubscore.grade == "13")
        ).one()
    assert float(area.band1_pct or 0) == 30.00  # Below Standard
    assert float(area.band3_pct or 0) == 20.00  # Above Standard


def test_entities_are_created_with_their_parents_and_charter_status() -> None:
    with Session(engine) as session:
        charter = session.get(Entity, CHARTER)
        school = session.get(Entity, SCHOOL)
    assert charter is not None and charter.is_charter is True
    assert charter.parent_cds_code == "58999990000000"
    assert school is not None and school.is_charter is False
    assert school.display_name == "Fixture Elementary"


def test_reloading_the_same_files_does_not_duplicate_rows() -> None:
    before = _count_rows()
    ImportRunner(engine).run(str(FIXTURES), force=True)
    assert _count_rows() == before


def test_an_unchanged_file_is_skipped_on_the_next_run() -> None:
    outcome = ImportRunner(engine).run(str(FIXTURES))
    assert outcome.files
    assert all(file.status == "skipped" for file in outcome.files)


def _count_rows() -> int:
    with Session(engine) as session:
        return len(
            session.exec(
                select(AssessmentResult).where(
                    col(AssessmentResult.test_year).in_(FIXTURE_YEARS)
                )
            ).all()
        )


def test_the_overview_endpoint_labels_every_level(client: TestClient) -> None:
    response = client.get(
        "/api/v1/reports/overview",
        params={"cds": STATE, "year": 2016, "grade": "13", "compare": "false"},
    )
    assert response.status_code == 200
    payload = response.json()
    result = next(item for item in payload["results"] if item["testId"] == 1)
    names = [level["name"] for level in result["levels"]]
    assert names == [
        "Standard Not Met",
        "Standard Nearly Met",
        "Standard Met",
        "Standard Exceeded",
    ]
    assert result["metOrAbovePct"] == "45.00"


def test_a_withheld_group_is_reported_as_suppressed(client: TestClient) -> None:
    response = client.get(
        "/api/v1/reports/overview",
        params={
            "cds": SCHOOL,
            "year": 2016,
            "grade": "13",
            "studentGroup": 160,
            "compare": "false",
        },
    )
    result = response.json()["results"][0]
    assert result["suppressed"] is True
    assert result["metOrAbovePct"] is None


def test_the_charter_filter_aggregates_over_schools(client: TestClient) -> None:
    """The files publish one district aggregate, so this is rebuilt."""
    response = client.get(
        "/api/v1/reports/overview",
        params={
            "cds": "58999990000000",
            "year": 2016,
            "grade": "13",
            "schoolType": "charter",
            "compare": "false",
        },
    )
    result = next(item for item in response.json()["results"] if item["testId"] == 1)
    assert result["derivedFromChildren"] is True
    assert result["studentsTested"] == 16


def test_subscores_are_returned_with_their_published_names(client: TestClient) -> None:
    response = client.get(
        "/api/v1/reports/subscores",
        params={"cds": STATE, "year": 2016, "testId": 1, "grade": "13"},
    )
    names = {item["code"]: item["name"] for item in response.json()["subscores"]}
    assert names["AREA_1"] == "Reading"
    assert names["AREA_3"] == "Speaking/Listening"
    assert names["COMPOSITE_AREA_2"] == "Writing and Research"
