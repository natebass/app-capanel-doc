"""Reporting endpoints against the fixture administrations.

The fixtures loaded by ``tests/ingest/test_import_roundtrip.py`` cover the
2015-16 Smarter Balanced and 2016-17 alternate assessment years; these tests
reuse them so the reporting routes are exercised against real imported rows.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, col, delete

from app.core.database import engine
from app.ingest.runner import ImportRunner
from app.model.reference import Entity
from app.model.results import AssessmentResult, AssessmentSubscore
from app.service.reference import reset_reference_cache

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "research_files"
FIXTURE_YEARS = (2016, 2017)
STATE = "00000000000000"
COUNTY = "58000000000000"
DISTRICT = "58999990000000"
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


def test_catalog_lists_the_tests_reported_in_a_year(client: TestClient) -> None:
    payload = client.get("/api/v1/reference/catalog", params={"year": 2016}).json()
    assert payload["testYear"] == 2016
    smarter_balanced = next(
        item for item in payload["assessments"] if item["testId"] == 1
    )
    assert smarter_balanced["program"] == "CAASPP"
    assert smarter_balanced["levelScheme"]["proficientFromLevel"] == 3
    assert "03" in smarter_balanced["grades"]
    assert {"AREA_1", "COMPOSITE_AREA_1"} <= {
        item["code"] for item in smarter_balanced["subscores"]
    }
    assert any(group["name"] == "All Students" for group in payload["studentGroups"])


def test_entity_search_matches_names_and_cds_codes(client: TestClient) -> None:
    by_name = client.get(
        "/api/v1/entities/search", params={"q": "Fixture Element", "level": "school"}
    ).json()
    assert by_name["count"] >= 1
    assert by_name["data"][0]["cdsCode"] == SCHOOL

    by_code = client.get("/api/v1/entities/search", params={"q": SCHOOL}).json()
    assert by_code["data"][0]["displayName"] == "Fixture Elementary"


def test_an_entity_reports_the_entities_it_rolls_up_into(client: TestClient) -> None:
    payload = client.get(f"/api/v1/entities/{SCHOOL}").json()
    assert payload["entity"]["entityLevel"] == "school"
    assert [item["cdsCode"] for item in payload["ancestors"]] == [
        DISTRICT,
        COUNTY,
        STATE,
    ]


def test_children_of_a_district_are_its_schools(client: TestClient) -> None:
    payload = client.get(f"/api/v1/entities/{DISTRICT}/children").json()
    assert {item["cdsCode"] for item in payload["data"]} == {SCHOOL, CHARTER}


def test_overview_includes_the_comparison_entities(client: TestClient) -> None:
    payload = client.get(
        "/api/v1/reports/overview",
        params={"cds": SCHOOL, "year": 2016, "grade": "13"},
    ).json()
    assert [item["entity"]["cdsCode"] for item in payload["comparisons"]] == [
        DISTRICT,
        COUNTY,
        STATE,
    ]


def test_grade_report_orders_grades_with_the_aggregate_last(
    client: TestClient,
) -> None:
    payload = client.get(
        "/api/v1/reports/grades", params={"cds": STATE, "year": 2016, "testId": 1}
    ).json()
    assert [item["grade"] for item in payload["grades"]] == ["03", "13"]
    assert payload["grades"][0]["label"] == "Grade 3"


def test_student_group_report_separates_all_students(client: TestClient) -> None:
    payload = client.get(
        "/api/v1/reports/student-groups",
        params={"cds": SCHOOL, "year": 2016, "testId": 1, "grade": "13"},
    ).json()
    assert payload["allStudents"]["name"] == "All Students"
    withheld = next(item for item in payload["groups"] if item["studentGroupId"] == 160)
    assert withheld["suppressed"] is True


def test_child_results_can_be_ordered_and_filtered_to_charters(
    client: TestClient,
) -> None:
    payload = client.get(
        "/api/v1/reports/children",
        params={
            "cds": DISTRICT,
            "year": 2016,
            "testId": 1,
            "grade": "13",
            "schoolType": "charter",
        },
    ).json()
    assert payload["childLevel"] == "school"
    assert [item["entity"]["cdsCode"] for item in payload["data"]] == [CHARTER]


def test_compare_returns_one_entry_per_requested_entity(client: TestClient) -> None:
    payload = client.get(
        "/api/v1/reports/compare",
        params={
            "cdsCodes": f"{SCHOOL},{CHARTER},{DISTRICT}",
            "year": 2016,
            "testId": 1,
            "grade": "13",
        },
    ).json()
    assert [item["entity"]["cdsCode"] for item in payload["entries"]] == [
        SCHOOL,
        CHARTER,
        DISTRICT,
    ]


def test_trend_returns_one_point_per_reported_year(client: TestClient) -> None:
    """Bounded to the fixture year so real imported years do not change it."""
    payload = client.get(
        "/api/v1/reports/trend",
        params={
            "cds": STATE,
            "testId": 1,
            "grade": "13",
            "fromYear": 2016,
            "toYear": 2016,
        },
    ).json()
    assert [point["testYear"] for point in payload["points"]] == [2016]
    assert payload["points"][0]["metOrAbovePct"] == "45.00"


def test_a_missing_entity_is_a_404(client: TestClient) -> None:
    assert (
        client.get("/api/v1/reports/overview", params={"cds": "x" * 14}).status_code
        == 404
    )


def test_starting_an_import_requires_a_superuser(client: TestClient) -> None:
    assert client.post("/api/v1/ingest/runs", json={}).status_code == 401
