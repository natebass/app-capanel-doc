"""The enrolment endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.service.dashboard_reports import enrollment_years

PREFIX = f"{settings.API_V1_STR}/dashboard/enrollment"
STATE_CDS = "00000000000000"


@pytest.fixture(scope="module")
def year(db: Session) -> int:
    years = enrollment_years(db)
    if not years:
        pytest.skip("no enrolment data imported")
    return years[0]


def test_enrolment_returns_a_total_and_its_groups(
    client: TestClient, year: int
) -> None:
    body = client.get(PREFIX, params={"cds": STATE_CDS, "year": year}).json()
    assert body["totalEnrollment"] and body["totalEnrollment"] > 0
    assert body["groups"]


def test_groups_are_largest_first(client: TestClient, year: int) -> None:
    body = client.get(PREFIX, params={"cds": STATE_CDS, "year": year}).json()
    totals = [
        g["subgroupTotal"] for g in body["groups"] if g["subgroupTotal"] is not None
    ]
    assert totals == sorted(totals, reverse=True)


def test_every_group_carries_its_published_name(client: TestClient, year: int) -> None:
    body = client.get(PREFIX, params={"cds": STATE_CDS, "year": year}).json()
    for group in body["groups"]:
        assert group["name"] and group["name"] != group["studentGroupCode"]


def test_no_group_exceeds_the_total(client: TestClient, year: int) -> None:
    body = client.get(PREFIX, params={"cds": STATE_CDS, "year": year}).json()
    total = body["totalEnrollment"]
    for group in body["groups"]:
        if group["subgroupTotal"] is not None:
            assert group["subgroupTotal"] <= total


def test_the_groups_overlap_so_rates_need_not_sum_to_a_hundred(
    client: TestClient, year: int
) -> None:
    """A student can be Hispanic, an English learner and disadvantaged at once."""
    body = client.get(PREFIX, params={"cds": STATE_CDS, "year": year}).json()
    total = sum(float(g["rate"]) for g in body["groups"] if g["rate"] is not None)
    assert total > 100


def test_an_unknown_entity_is_a_404(client: TestClient, year: int) -> None:
    assert (
        client.get(PREFIX, params={"cds": "99999999999999", "year": year}).status_code
        == 404
    )
