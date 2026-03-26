from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.model.academic_indicator import (
    AcademicIndicator,
    AcademicIndicatorCreate,
    AcademicIndicatorPublic,
    AcademicIndicatorsPublic,
)
from app.model.dashboard import (
    DashboardAggregation,
    DashboardSummaryResponse,
    EquityGroupSummary,
    EquityReportResponse,
    IndicatorSummary,
)
from app.model.models import (
    Message,
)
from app.model.user import UserPreferencesUpdate, UserPublic

router = APIRouter(prefix="/academic-indicators", tags=["academic-indicators"])


def parse_cds(cds_string: str) -> tuple[str, str, str]:
    if len(cds_string) != 14:
        # Default to state if not 14 chars
        return "00", "00000", "0000000"
    return cds_string[:2], cds_string[2:7], cds_string[7:]


@router.get("/", response_model=AcademicIndicatorsPublic)
def read_academic_indicators(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    cds: str | None = Query(default=None, description="Filter by CDS code"),
    studentgroup: str | None = Query(
        default=None, description="Filter by student group"
    ),
    reportingyear: str | None = Query(
        default=None, description="Filter by reporting year"
    ),
) -> Any:
    """
    Retrieve academic indicators with optional filters.
    """
    statement = select(AcademicIndicator)
    count_statement = select(func.count()).select_from(AcademicIndicator)

    if cds:
        county, district, school = parse_cds(cds)
        statement = statement.where(
            AcademicIndicator.county_code == county,
            AcademicIndicator.district_code == district,
            AcademicIndicator.school_code == school,
        )
        count_statement = count_statement.where(
            AcademicIndicator.county_code == county,
            AcademicIndicator.district_code == district,
            AcademicIndicator.school_code == school,
        )
    if studentgroup:
        statement = statement.where(AcademicIndicator.student_group_id == studentgroup)
        count_statement = count_statement.where(
            AcademicIndicator.student_group_id == studentgroup
        )
    if reportingyear:
        statement = statement.where(AcademicIndicator.test_year == reportingyear)
        count_statement = count_statement.where(
            AcademicIndicator.test_year == reportingyear
        )

    count = session.exec(count_statement).one()
    statement = statement.offset(skip).limit(limit)
    indicators = session.exec(statement).all()

    return AcademicIndicatorsPublic(data=indicators, count=count)


@router.get("/dashboard", response_model=DashboardAggregation)
def get_dashboard_data(
    session: SessionDep,
    q: str = Query(..., description="CDS code to query"),
) -> Any:
    """
    Get aggregated dashboard data for a specific CDS code.
    """
    county, district, school = parse_cds(q)
    statement = (
        select(AcademicIndicator)
        .where(
            AcademicIndicator.county_code == county,
            AcademicIndicator.district_code == district,
            AcademicIndicator.school_code == school,
            AcademicIndicator.student_group_id == "1",
        )
        .order_by(col(AcademicIndicator.test_year).desc())
        .limit(1)
    )
    indicator = session.exec(statement).first()

    if not indicator:
        # Return empty record with 200 OK so frontend doesn't crash
        return DashboardAggregation(
            cds=q,
            student_group_id="1",
            test_year="N/A",
            overall_met_and_above_pct=None,
            overall_mean_scale_score=None,
        )

    return DashboardAggregation(
        cds=q,
        student_group_id=indicator.student_group_id,
        test_year=indicator.test_year,
        overall_met_and_above_pct=indicator.overall_met_and_above_pct,
        overall_mean_scale_score=indicator.overall_mean_scale_score,
    )


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    session: SessionDep,
    cds: str = Query(
        ..., description="14-char CDS code or '00000000000000' for statewide"
    ),
    reportingyear: str = Query(default="2025", description="Reporting year"),
    studentgroup: str = Query(default="ALL", description="Student group code"),
) -> Any:
    """
    Get all test summaries for a school/district/state.
    """
    county, district, school = parse_cds(cds)

    # Translate ALL to 1 for CAASPP as discovered in the database
    group_id = "1" if studentgroup == "ALL" else studentgroup

    statement = select(AcademicIndicator).where(
        AcademicIndicator.county_code == county,
        AcademicIndicator.district_code == district,
        AcademicIndicator.school_code == school,
        AcademicIndicator.test_year == reportingyear,
        AcademicIndicator.student_group_id == group_id,
    )
    indicators = session.exec(statement).all()

    if not indicators:
        # Return metadata but empty indicators list to prevent UI crash
        return DashboardSummaryResponse(
            cds=cds,
            test_year=reportingyear,
            indicators=[],
        )

    indicator_summaries = []

    # Aggregate CAASPP tests: CAASPP has ELA (1), Math (2), etc.
    for ind in indicators:
        indicator_summaries.append(
            IndicatorSummary(
                test_id=ind.test_id,
                test_type=ind.test_type,
                grade=ind.grade,
                students_enrolled=ind.students_enrolled,
                students_tested=ind.students_tested,
                overall_mean_scale_score=ind.overall_mean_scale_score,
                overall_met_and_above_pct=ind.overall_met_and_above_pct,
            )
        )

    return DashboardSummaryResponse(
        cds=cds,
        test_year=reportingyear,
        indicators=indicator_summaries,
    )


@router.get("/dashboard/equity", response_model=EquityReportResponse)
def get_equity_report(
    session: SessionDep,
    cds: str = Query(..., description="14-char CDS code"),
    indicator: str = Query(
        ..., description="Test ID code (1 for ELA, 2 for MATH, etc.)"
    ),
    reportingyear: str = Query(default="2025", description="Reporting year"),
) -> Any:
    """
    Get student group breakdown for a test.
    """
    county, district, school = parse_cds(cds)
    statement = select(AcademicIndicator).where(
        AcademicIndicator.county_code == county,
        AcademicIndicator.district_code == district,
        AcademicIndicator.school_code == school,
        AcademicIndicator.test_id == indicator,
        AcademicIndicator.test_year == reportingyear,
        AcademicIndicator.student_group_id.notin_(["ALL", "001"]),
    )
    indicators = session.exec(statement).all()

    groups = []
    for ind in indicators:
        groups.append(
            EquityGroupSummary(
                studentgroup=ind.student_group_id,
                overall_met_and_above_pct=ind.overall_met_and_above_pct,
                students_tested=ind.students_tested,
            )
        )

    return EquityReportResponse(
        cds=cds,
        test_id=indicator,
        test_year=reportingyear,
        groups=groups,
    )


@router.put("/users/me/preferences", response_model=UserPublic)
def update_user_preferences(
    session: SessionDep,
    current_user: CurrentUser,
    preferences: UserPreferencesUpdate,
) -> Any:
    if preferences.last_viewed_cds is not None:
        current_user.last_viewed_cds = preferences.last_viewed_cds
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/users/me/preferences/last-viewed-cds")
def get_last_viewed_cds(
    current_user: CurrentUser,
) -> dict[str, str | None]:
    return {"last_viewed_cds": current_user.last_viewed_cds}


@router.get("/{id}", response_model=AcademicIndicatorPublic)
def read_academic_indicator() -> Any:
    # Since our CAASPP schema doesn't have UUIDs, this endpoint might be invalid.
    # We will raise 404 to be safe.
    raise HTTPException(status_code=404, detail="Not supported with new CAASPP schema.")


@router.post("/", response_model=AcademicIndicatorPublic)
def create_academic_indicator(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    indicator_in: AcademicIndicatorCreate,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    indicator = AcademicIndicator.model_validate(indicator_in)
    session.add(indicator)
    session.commit()
    session.refresh(indicator)
    return indicator


@router.put("/{id}", response_model=AcademicIndicatorPublic)
def update_academic_indicator() -> Any:
    raise HTTPException(
        status_code=501, detail="Update not implemented for CAASPP composite keys."
    )


@router.delete("/{id}")
def delete_academic_indicator() -> Message:
    raise HTTPException(
        status_code=501, detail="Delete not implemented for CAASPP composite keys."
    )
