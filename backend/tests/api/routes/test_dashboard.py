"""The accountability endpoints.

These run against whatever the importer has loaded, so they assert on shape
and on the invariants that must hold for any year, not on particular figures.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, col, select

from app.core.config import settings
from app.ingest.dashboard_reference import seed_dashboard_reference
from app.model.dashboard import DashboardIndicatorResult
from app.model.reference import Entity, EntityLevel
from app.service.dashboard_reports import available_years

PREFIX = f"{settings.API_V1_STR}/dashboard"
STATE_CDS = "00000000000000"


@pytest.fixture(scope="module", autouse=True)
def seeded(db: Session) -> None:
    seed_dashboard_reference(db)
    db.commit()


@pytest.fixture(scope="module")
def year(db: Session) -> int:
    years = available_years(db, include_projected=True)
    if not years:
        pytest.skip("no Dashboard data imported")
    return years[0]


def test_the_catalog_lists_the_seven_indicators(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/catalog")
    assert response.status_code == 200
    body = response.json()
    codes = {indicator["code"] for indicator in body["indicators"]}
    assert {"ELA", "MATH", "CHRO", "SUSP", "GRAD", "CCI", "ELPI"} <= codes
    assert body["colors"]["1"] == "Red"
    assert body["colors"]["5"] == "Blue"


def test_the_catalog_marks_the_inverted_indicators(client: TestClient) -> None:
    body = client.get(f"{PREFIX}/catalog").json()
    inverted = {i["code"] for i in body["indicators"] if i["lowerIsBetter"]}
    assert inverted == {"CHRO", "SUSP"}


def test_the_statewide_view_returns_every_indicator(
    client: TestClient, year: int
) -> None:
    response = client.get(
        f"{PREFIX}/indicators", params={"cds": STATE_CDS, "year": year}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["entity"]["cdsCode"] == STATE_CDS
    assert body["reportingYear"] == year
    assert body["results"]


def test_english_learner_progress_survives_the_all_students_view(
    client: TestClient, year: int
) -> None:
    """It only ever reports English learners, and must not be dropped."""
    body = client.get(
        f"{PREFIX}/indicators", params={"cds": STATE_CDS, "year": year}
    ).json()
    elpi = [r for r in body["results"] if r["indicatorCode"] == "ELPI"]
    if not elpi:
        pytest.skip("no English learner progress data for this year")
    assert elpi[0]["studentGroupCode"] == "EL"


def test_asking_for_one_group_does_not_return_another(
    client: TestClient, year: int
) -> None:
    body = client.get(
        f"{PREFIX}/indicators",
        params={"cds": STATE_CDS, "year": year, "studentGroup": "SED"},
    ).json()
    assert {r["studentGroupCode"] for r in body["results"]} <= {"SED"}


def test_every_colour_carries_its_published_name(client: TestClient, year: int) -> None:
    body = client.get(
        f"{PREFIX}/indicators", params={"cds": STATE_CDS, "year": year}
    ).json()
    names = {1: "Red", 2: "Orange", 3: "Yellow", 4: "Green", 5: "Blue"}
    for result in body["results"]:
        if result["color"] is not None:
            assert result["colorName"] == names[result["color"]]


def test_published_results_are_not_labelled_projections(
    client: TestClient, year: int
) -> None:
    body = client.get(
        f"{PREFIX}/indicators", params={"cds": STATE_CDS, "year": year}
    ).json()
    assert all(result["isProjected"] is False for result in body["results"])
    assert body["includesProjections"] is False


def test_one_indicator_breaks_out_by_student_group(
    client: TestClient, year: int
) -> None:
    response = client.get(
        f"{PREFIX}/indicator",
        params={"cds": STATE_CDS, "year": year, "indicator": "CHRO"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["indicatorCode"] == "CHRO"
    assert body["allStudents"] is not None
    assert body["allStudents"]["studentGroupCode"] == "ALL"
    assert all(g["studentGroupCode"] != "ALL" for g in body["groups"])
    assert len(body["groups"]) > 1


def test_an_unknown_indicator_is_a_404(client: TestClient, year: int) -> None:
    response = client.get(
        f"{PREFIX}/indicator",
        params={"cds": STATE_CDS, "year": year, "indicator": "NOPE"},
    )
    assert response.status_code == 404


def test_an_unknown_entity_is_a_404(client: TestClient, year: int) -> None:
    response = client.get(
        f"{PREFIX}/indicators", params={"cds": "99999999999999", "year": year}
    )
    assert response.status_code == 404


def test_the_trend_runs_oldest_first(client: TestClient) -> None:
    response = client.get(
        f"{PREFIX}/trend", params={"cds": STATE_CDS, "indicator": "CHRO"}
    )
    assert response.status_code == 200
    years = [point["reportingYear"] for point in response.json()["points"]]
    assert years == sorted(years)


def test_the_trend_names_the_years_the_state_skipped(client: TestClient) -> None:
    """No Dashboard was published for 2020 or 2021."""
    body = client.get(
        f"{PREFIX}/trend", params={"cds": STATE_CDS, "indicator": "CHRO"}
    ).json()
    covered = {point["reportingYear"] for point in body["points"]}
    if 2019 in covered and 2022 in covered:
        assert {2020, 2021} <= set(body["missingYears"])


def test_the_trend_can_be_bounded(client: TestClient) -> None:
    body = client.get(
        f"{PREFIX}/trend",
        params={
            "cds": STATE_CDS,
            "indicator": "CHRO",
            "fromYear": 2023,
            "toYear": 2024,
        },
    ).json()
    assert {p["reportingYear"] for p in body["points"]} <= {2023, 2024}


def test_children_rank_the_entities_inside_a_county(
    client: TestClient, year: int
) -> None:
    response = client.get(
        f"{PREFIX}/children",
        params={"cds": STATE_CDS, "year": year, "indicator": "CHRO", "limit": 5},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["children"]) <= 5
    assert body["count"] >= len(body["children"])
    statuses = [
        float(child["result"]["currStatus"])
        for child in body["children"]
        if child["result"]["currStatus"] is not None
    ]
    assert statuses == sorted(statuses, reverse=True)


def test_children_can_be_ranked_the_other_way(client: TestClient, year: int) -> None:
    body = client.get(
        f"{PREFIX}/children",
        params={
            "cds": STATE_CDS,
            "year": year,
            "indicator": "CHRO",
            "limit": 5,
            "descending": False,
        },
    ).json()
    statuses = [
        float(child["result"]["currStatus"])
        for child in body["children"]
        if child["result"]["currStatus"] is not None
    ]
    assert statuses == sorted(statuses)


def test_a_school_has_no_children(client: TestClient, db: Session, year: int) -> None:
    school = db.exec(
        select(Entity.cds_code)
        .where(Entity.entity_level == EntityLevel.SCHOOL)
        .where(col(Entity.cds_code).in_(select(DashboardIndicatorResult.cds_code)))
        .limit(1)
    ).first()
    if school is None:
        pytest.skip("no school with Dashboard data")
    response = client.get(
        f"{PREFIX}/children",
        params={"cds": school, "year": year, "indicator": "CHRO"},
    )
    assert response.status_code == 422


def test_responses_are_cacheable(client: TestClient, year: int) -> None:
    response = client.get(
        f"{PREFIX}/indicators", params={"cds": STATE_CDS, "year": year}
    )
    assert response.headers["Cache-Control"] == "public, max-age=300"


def test_the_catalog_separates_informational_indicators(client: TestClient) -> None:
    """Participation is published alongside the seven but is not one of them."""
    body = client.get(f"{PREFIX}/catalog").json()
    informational = {i["code"] for i in body["indicators"] if i["isInformational"]}
    accountability = {i["code"] for i in body["indicators"] if not i["isInformational"]}
    assert "ELPACPART" in informational
    assert {"ELA", "MATH", "CHRO", "SUSP", "GRAD", "CCI", "ELPI"} <= accountability
    assert not informational & accountability


def test_the_alternative_school_graduation_rate_is_a_separate_variant(
    db: Session,
) -> None:
    """A one-year rate is not the four-year rate and must not overwrite it."""
    from sqlmodel import col, select

    from app.model.dashboard import DashboardIndicatorResult

    variants = set(
        db.exec(
            select(DashboardIndicatorResult.variant)
            .where(DashboardIndicatorResult.indicator_code == "GRAD")
            .distinct()
        ).all()
    )
    if "DASS1YR" not in variants:
        pytest.skip("no DASS graduation data imported")
    assert "ALL" in variants, "the four-year rate must still be there"
    # The one-year rate is not coloured.
    coloured = db.exec(
        select(DashboardIndicatorResult)
        .where(DashboardIndicatorResult.variant == "DASS1YR")
        .where(col(DashboardIndicatorResult.color).is_not(None))
        .limit(1)
    ).first()
    assert coloured is None
