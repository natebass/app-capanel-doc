"""The growth endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, col, select

from app.core.config import settings
from app.model.growth import GrowthResult

PREFIX = f"{settings.API_V1_STR}/dashboard/growth"
CATEGORIES = {
    1: "Minimal Growth",
    2: "Moderate Growth",
    3: "Average Growth",
    4: "Accelerated Growth",
    5: "Exceptional Growth",
}


@pytest.fixture(scope="module")
def an_entity(db: Session) -> str:
    row = db.exec(
        select(GrowthResult)
        .where(GrowthResult.student_group_code == "ALL")
        .where(col(GrowthResult.performance_category).is_not(None))
        .limit(1)
    ).first()
    if row is None:
        pytest.skip("no growth data imported")
    return row.cds_code


def test_growth_returns_both_subjects(client: TestClient, an_entity: str) -> None:
    body = client.get(PREFIX, params={"cds": an_entity}).json()
    assert {r["subject"] for r in body["results"]} <= {"ELA", "MATH"}
    assert body["results"]


def test_growth_is_always_flagged_informational(
    client: TestClient, an_entity: str
) -> None:
    """The State Board adopted growth for information only in July 2025."""
    body = client.get(PREFIX, params={"cds": an_entity}).json()
    assert body["isInformational"] is True


def test_no_growth_result_carries_a_performance_colour(
    client: TestClient, an_entity: str
) -> None:
    body = client.get(PREFIX, params={"cds": an_entity}).json()
    for result in body["results"]:
        assert "color" not in result


def test_each_category_carries_its_published_name(
    client: TestClient, an_entity: str
) -> None:
    body = client.get(PREFIX, params={"cds": an_entity}).json()
    for result in body["results"]:
        if result["performanceCategory"] is not None:
            assert (
                result["performanceCategoryName"]
                == CATEGORIES[result["performanceCategory"]]
            )


def test_the_statewide_row_does_not_exist(client: TestClient) -> None:
    """Growth files carry district and school rows only."""
    body = client.get(PREFIX, params={"cds": "00000000000000"}).json()
    assert body["results"] == []


def test_an_unknown_entity_is_a_404(client: TestClient) -> None:
    assert client.get(PREFIX, params={"cds": "99999999999999"}).status_code == 404
