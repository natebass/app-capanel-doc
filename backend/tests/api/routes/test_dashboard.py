from decimal import Decimal

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.model.assessments import CaasppStudentGroup, CaasppTest, Entity, SbResult


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
