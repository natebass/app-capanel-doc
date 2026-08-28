from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, col, delete

from app.api.routes.dashboard import reset_student_group_cache
from app.core.config import settings
from app.model.assessments import (
    CaasppStudentGroup,
    CaasppTest,
    CastResult,
    Entity,
    SbResult,
)

# Every fixture row in this module uses a CDS code in this reserved range.
TEST_CDS_PREFIX = "999999999999"
# A late-import student group; it must not leak into other tests, because it
# changes what "All Students" resolves to.
LATE_IMPORT_GROUP_ID = "900"


def _clear_assessment_fixtures(db: Session) -> None:
    db.rollback()
    for model in (SbResult, CastResult):
        db.exec(  # type: ignore[call-overload]
            delete(model).where(col(model.cds_code).like(f"{TEST_CDS_PREFIX}%"))
        )
    db.exec(  # type: ignore[call-overload]
        delete(Entity).where(col(Entity.cds_code).like(f"{TEST_CDS_PREFIX}%"))
    )
    db.exec(  # type: ignore[call-overload]
        delete(CaasppStudentGroup).where(
            col(CaasppStudentGroup.demographic_id) == LATE_IMPORT_GROUP_ID
        )
    )
    db.commit()


@pytest.fixture(autouse=True)
def dashboard_fixtures(db: Session) -> Generator[None]:
    """Reset the cached lookup tables and the rows each test seeds."""
    reset_student_group_cache()
    _clear_assessment_fixtures(db)
    yield
    _clear_assessment_fixtures(db)
    reset_student_group_cache()


def test_dashboard_summary_normalizes_all_students_and_preserves_zero_values(
    client: TestClient, db: Session
) -> None:
    cds_code = "99999999999999"

    db.merge(
        Entity(
            cds_code=cds_code,
            school_name="Dashboard Test School",
        )
    )
    db.merge(
        CaasppStudentGroup(
            demographic_id="1",
            demographic_id_num=1,
            student_group="All Students",
        )
    )
    db.merge(CaasppTest(test_id=1, test_name="ELA"))
    db.add(
        SbResult(
            cds_code=cds_code,
            test_year=2025,
            student_group_id="1",
            test_id=1,
            grade="03",
            total_students_enrolled=10,
            total_students_tested=0,
            mean_scale_score=Decimal("0.0"),
            percentage_standard_not_met=Decimal("0.0"),
            percentage_standard_nearly_met=Decimal("0.0"),
            percentage_standard_met=Decimal("0.0"),
            percentage_standard_exceeded=Decimal("0.0"),
            percentage_standard_met_and_above=Decimal("0.0"),
        )
    )
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/dashboard/summary",
        params={"cds": cds_code, "reportingYear": "2025", "studentGroup": "ALL"},
    )

    assert response.status_code == 200
    content = response.json()
    assert content["cds"] == cds_code
    assert len(content["indicators"]) == 1

    indicator = content["indicators"][0]
    assert indicator["studentsTested"] == "0"
    assert indicator["overallMeanScaleScore"] == "0.0"
    assert Decimal(indicator["overallMetAndAbovePct"]) == Decimal("0")
    assert indicator["levels"]["Standard Not Met (Level 1)"] == 0.0


def test_equity_report_weights_percentages_by_students_tested(
    client: TestClient, db: Session
) -> None:
    cds_code = "99999999999998"

    db.merge(Entity(cds_code=cds_code, school_name="Equity Test School"))
    db.merge(
        CaasppStudentGroup(
            demographic_id="1", demographic_id_num=1, student_group="All Students"
        )
    )
    db.merge(
        CaasppStudentGroup(
            demographic_id="128", demographic_id_num=128, student_group="Male"
        )
    )
    db.merge(CaasppTest(test_id=1, test_name="ELA"))
    # Two grades for All Students, plus a grade with no reported percentage: it
    # counts towards students tested but must not drag the average down.
    db.add(
        SbResult(
            cds_code=cds_code,
            test_year=2025,
            student_group_id="1",
            test_id=1,
            grade="03",
            total_students_tested=100,
            percentage_standard_met_and_above=Decimal("50.00"),
        )
    )
    db.add(
        SbResult(
            cds_code=cds_code,
            test_year=2025,
            student_group_id="1",
            test_id=1,
            grade="04",
            total_students_tested=100,
            percentage_standard_met_and_above=Decimal("70.00"),
        )
    )
    db.add(
        SbResult(
            cds_code=cds_code,
            test_year=2025,
            student_group_id="1",
            test_id=1,
            grade="05",
            total_students_tested=50,
            percentage_standard_met_and_above=None,
        )
    )
    db.add(
        SbResult(
            cds_code=cds_code,
            test_year=2025,
            student_group_id="128",
            test_id=1,
            grade="03",
            total_students_tested=20,
            percentage_standard_met_and_above=Decimal("40.00"),
        )
    )
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/dashboard/equity",
        params={"cds": cds_code, "testId": "1", "reportingYear": "2025"},
    )

    assert response.status_code == 200
    groups = {group["studentGroup"]: group for group in response.json()["groups"]}
    assert set(groups) == {"All Students", "Male"}
    assert groups["All Students"]["studentsTested"] == "250"
    assert Decimal(groups["All Students"]["overallMetAndAbovePct"]) == Decimal("60")
    assert Decimal(groups["Male"]["overallMetAndAbovePct"]) == Decimal("40")


def test_equity_report_reads_science_from_cast_results(
    client: TestClient, db: Session
) -> None:
    cds_code = "99999999999997"

    db.merge(Entity(cds_code=cds_code, school_name="Science Test School"))
    db.merge(
        CaasppStudentGroup(
            demographic_id="1", demographic_id_num=1, student_group="All Students"
        )
    )
    db.merge(CaasppTest(test_id=3, test_name="CAST"))
    db.add(
        CastResult(
            cds_code=cds_code,
            test_year=2025,
            student_group_id="1",
            test_id=3,
            grade="05",
            total_students_tested=80,
            percentage_standard_met_and_above=Decimal("25.00"),
        )
    )
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/dashboard/equity",
        params={"cds": cds_code, "testId": "3", "reportingYear": "2025"},
    )

    assert response.status_code == 200
    groups = response.json()["groups"]
    assert len(groups) == 1
    assert groups[0]["studentGroup"] == "All Students"
    assert groups[0]["studentsTested"] == "80"
    assert Decimal(groups[0]["overallMetAndAbovePct"]) == Decimal("25")


def test_dashboard_responses_are_cacheable(client: TestClient) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/dashboard/summary",
        params={"cds": "99999999999996", "reportingYear": "2025"},
    )

    assert response.status_code == 200
    assert "max-age=300" in response.headers["cache-control"]


def test_dashboard_rejects_a_non_numeric_reporting_year(client: TestClient) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/dashboard/summary",
        params={"cds": f"{TEST_CDS_PREFIX}96", "reportingYear": "not-a-year"},
    )

    assert response.status_code == 422


def test_summary_sees_a_group_imported_after_the_cache_warmed(
    client: TestClient, db: Session
) -> None:
    """A newly imported "All Students" group must not wait out the cache TTL."""
    cds_code = f"{TEST_CDS_PREFIX}95"

    db.merge(Entity(cds_code=cds_code, school_name="Late Import School"))
    db.merge(
        CaasppStudentGroup(
            demographic_id="1", demographic_id_num=1, student_group="All Students"
        )
    )
    db.merge(CaasppTest(test_id=1, test_name="ELA"))
    db.commit()

    # Warm the in-process name cache before the new group exists.
    assert (
        client.get(
            f"{settings.API_V1_STR}/dashboard/equity",
            params={"cds": cds_code, "testId": "1", "reportingYear": "2025"},
        ).status_code
        == 200
    )
    warmup = client.get(
        f"{settings.API_V1_STR}/dashboard/summary",
        params={"cds": cds_code, "reportingYear": "2025", "studentGroup": "ALL"},
    )
    assert warmup.status_code == 200
    assert warmup.json()["indicators"] == []

    # Import a second demographic id that also means "All Students".
    db.merge(
        CaasppStudentGroup(
            demographic_id=LATE_IMPORT_GROUP_ID,
            demographic_id_num=900,
            demographic_name="All Students",
        )
    )
    db.add(
        SbResult(
            cds_code=cds_code,
            test_year=2025,
            student_group_id=LATE_IMPORT_GROUP_ID,
            test_id=1,
            grade="06",
            total_students_tested=30,
            percentage_standard_met_and_above=Decimal("55.00"),
        )
    )
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/dashboard/summary",
        params={"cds": cds_code, "reportingYear": "2025", "studentGroup": "ALL"},
    )

    assert response.status_code == 200
    indicators = response.json()["indicators"]
    assert len(indicators) == 1
    assert indicators[0]["studentsTested"] == "30"
