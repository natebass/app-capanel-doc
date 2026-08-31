"""The local indicator endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app.core.config import settings
from app.ingest.local_indicator_reference import seed_local_indicator_reference
from app.service.local_indicator_reports import available_years

PREFIX = f"{settings.API_V1_STR}/local-indicators"
PERFORMANCE = {"Met", "Not Met", "Not Met For Two or More Years"}


@pytest.fixture(scope="module", autouse=True)
def seeded(db: Session) -> None:
    seed_local_indicator_reference(db)
    db.commit()


@pytest.fixture(scope="module")
def year(db: Session) -> int:
    years = available_years(db)
    if not years:
        pytest.skip("no local indicator data imported")
    return years[0]


@pytest.fixture(scope="module")
def an_lea(db: Session) -> str:
    row = (
        db.connection()
        .execute(
            text(
                "SELECT cds_code FROM local_indicator_results "
                "WHERE performance IS NOT NULL LIMIT 1"
            )
        )
        .scalar_one_or_none()
    )
    if row is None:
        pytest.skip("no local indicator data imported")
    return row


def test_the_catalog_lists_the_seven_priorities(client: TestClient) -> None:
    body = client.get(f"{PREFIX}/catalog").json()
    numbers = {p["priorityNumber"] for p in body["priorities"]}
    assert numbers == {1, 2, 3, 6, 7, 9, 10}
    assert set(body["performanceValues"]) == PERFORMANCE


def test_the_catalog_marks_the_county_office_only_priorities(
    client: TestClient,
) -> None:
    body = client.get(f"{PREFIX}/catalog").json()
    coe_only = {
        p["priorityNumber"] for p in body["priorities"] if p["countyOfficeOnly"]
    }
    assert coe_only == {9, 10}


def test_an_lea_returns_all_seven_priorities(
    client: TestClient, an_lea: str, year: int
) -> None:
    response = client.get(f"{PREFIX}/", params={"cds": an_lea, "year": year})
    assert response.status_code == 200
    body = response.json()
    assert len(body["priorities"]) == 7
    assert body["reportingYear"] == year


def test_performance_is_only_ever_a_published_value(
    client: TestClient, an_lea: str, year: int
) -> None:
    body = client.get(f"{PREFIX}/", params={"cds": an_lea, "year": year}).json()
    for priority in body["priorities"]:
        assert priority["performance"] in PERFORMANCE | {None}


def test_no_response_carries_a_dashboard_colour(
    client: TestClient, an_lea: str, year: int
) -> None:
    """Local indicators have no five-by-five grid and must not imply one."""
    body = client.get(f"{PREFIX}/", params={"cds": an_lea, "year": year}).json()
    assert "color" not in body
    for priority in body["priorities"]:
        assert "color" not in priority


def test_a_school_inherits_its_district_report(
    client: TestClient, db: Session, year: int
) -> None:
    # A charter school is its own LEA and reports directly, so the school
    # picked here must be one that does *not* report for itself.
    school = (
        db.connection()
        .execute(
            text(
                "SELECT e.cds_code FROM entities e "
                "JOIN local_indicator_results r ON r.cds_code = e.parent_cds_code "
                "WHERE e.entity_level = 'school' "
                "AND NOT EXISTS (SELECT 1 FROM local_indicator_results own "
                "                WHERE own.cds_code = e.cds_code) LIMIT 1"
            )
        )
        .scalar_one_or_none()
    )
    if school is None:
        pytest.skip("no school under a reporting LEA")
    body = client.get(f"{PREFIX}/", params={"cds": school, "year": year}).json()
    assert body["entity"]["cdsCode"] == school
    assert body["entity"]["entityLevel"] == "school"
    # The report belongs to the LEA, and the response says so.
    assert body["reportedBy"]["cdsCode"] != school


def test_a_charter_school_reports_for_itself(
    client: TestClient, db: Session, year: int
) -> None:
    """A charter school is its own LEA, so it does not inherit anything."""
    charter = (
        db.connection()
        .execute(
            text(
                "SELECT e.cds_code FROM entities e "
                "JOIN local_indicator_results r ON r.cds_code = e.cds_code "
                "WHERE e.entity_level = 'school' LIMIT 1"
            )
        )
        .scalar_one_or_none()
    )
    if charter is None:
        pytest.skip("no self-reporting school imported")
    body = client.get(f"{PREFIX}/", params={"cds": charter, "year": year}).json()
    assert body["reportedBy"]["cdsCode"] == charter


def test_one_priority_comes_back_in_full(
    client: TestClient, an_lea: str, year: int
) -> None:
    response = client.get(
        f"{PREFIX}/priority", params={"cds": an_lea, "year": year, "priority": 3}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["priorityNumber"] == 3
    assert isinstance(body["ratings"], dict)
    assert isinstance(body["narratives"], list)


def test_ratings_are_numbers_and_narratives_are_text(
    client: TestClient, db: Session, year: int
) -> None:
    lea = (
        db.connection()
        .execute(
            text(
                "SELECT cds_code FROM local_indicator_results "
                "WHERE priority_number = 3 AND jsonb_typeof(responses) = 'object' "
                "AND responses <> '{}'::jsonb LIMIT 1"
            )
        )
        .scalar_one_or_none()
    )
    if lea is None:
        pytest.skip("no priority 3 responses imported")
    body = client.get(
        f"{PREFIX}/priority", params={"cds": lea, "year": year, "priority": 3}
    ).json()
    assert all(isinstance(v, int) for v in body["ratings"].values())
    for narrative in body["narratives"]:
        assert set(narrative) == {"field", "text"}
        assert len(narrative["text"]) >= 40


def test_an_unknown_priority_is_a_404(
    client: TestClient, an_lea: str, year: int
) -> None:
    response = client.get(
        f"{PREFIX}/priority", params={"cds": an_lea, "year": year, "priority": 4}
    )
    assert response.status_code == 404


def test_an_unknown_entity_is_a_404(client: TestClient, year: int) -> None:
    response = client.get(f"{PREFIX}/", params={"cds": "99999999999999", "year": year})
    assert response.status_code == 404


def test_the_trend_runs_oldest_first(client: TestClient, an_lea: str) -> None:
    body = client.get(f"{PREFIX}/trend", params={"cds": an_lea, "priority": 1}).json()
    years = [p["reportingYear"] for p in body["points"]]
    assert years == sorted(years)


def test_responses_are_cacheable(client: TestClient, an_lea: str, year: int) -> None:
    response = client.get(f"{PREFIX}/", params={"cds": an_lea, "year": year})
    assert response.headers["Cache-Control"] == "public, max-age=300"
