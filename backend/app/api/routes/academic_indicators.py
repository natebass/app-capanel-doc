import uuid
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.model.academic_indicator import (
    AcademicIndicator,
    AcademicIndicatorCreate,
    AcademicIndicatorPublic,
    AcademicIndicatorsPublic,
    AcademicIndicatorUpdate,
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
from app.service.color_calculator import calculate_all

router = APIRouter(prefix="/academic-indicators", tags=["academic-indicators"])


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
    # Build base query
    statement = select(AcademicIndicator)
    count_statement = select(func.count()).select_from(AcademicIndicator)

    # Apply filters
    if cds:
        statement = statement.where(AcademicIndicator.cds == cds)
        count_statement = count_statement.where(AcademicIndicator.cds == cds)
    if studentgroup:
        statement = statement.where(AcademicIndicator.studentgroup == studentgroup)
        count_statement = count_statement.where(
            AcademicIndicator.studentgroup == studentgroup
        )
    if reportingyear:
        statement = statement.where(AcademicIndicator.reportingyear == reportingyear)
        count_statement = count_statement.where(
            AcademicIndicator.reportingyear == reportingyear
        )

    count = session.exec(count_statement).one()
    statement = (
        statement.order_by(col(AcademicIndicator.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    indicators = session.exec(statement).all()

    return AcademicIndicatorsPublic(data=indicators, count=count)


@router.get("/dashboard", response_model=DashboardAggregation)
def get_dashboard_data(
    session: SessionDep,
    q: str = Query(..., description="CDS code to query"),
) -> Any:
    """
    Get aggregated dashboard data for a specific CDS code.
    Returns the 'ALL' student group data for the most recent reporting year.
    """
    # Query for the 'ALL' student group for the given CDS code
    statement = (
        select(AcademicIndicator)
        .where(AcademicIndicator.cds == q)
        .where(AcademicIndicator.studentgroup == "ALL")
        .order_by(col(AcademicIndicator.reportingyear).desc())
        .limit(1)
    )
    indicator = session.exec(statement).first()

    if not indicator:
        raise HTTPException(
            status_code=404,
            detail=f"No academic indicator data found for CDS code: {q}",
        )

    return DashboardAggregation(
        cds=indicator.cds,
        schoolname=indicator.schoolname,
        districtname=indicator.districtname,
        countyname=indicator.countyname,
        studentgroup=indicator.studentgroup,
        currstatus=_currstatus(indicator),
        priorstatus=indicator.priorstatus,
        change=indicator.change,
        statuslevel=indicator.statuslevel,
        changelevel=indicator.changelevel,
        color=indicator.color,
        indicator=indicator.indicator,
        reportingyear=indicator.reportingyear,
    )


# List of all accountability indicators
ALL_INDICATORS = ["ELA", "MATH", "SCI", "CHRONIC", "SUSP", "GRAD", "ELPI", "CCI"]

# Map color levels to color names
COLOR_NAMES = {1: "red", 2: "orange", 3: "yellow", 4: "green", 5: "blue", 0: "none"}


def _currstatus(indicator: AcademicIndicator) -> float | None:
    return getattr(indicator, "currstatus", None)


def _currdenom(indicator: AcademicIndicator) -> int | None:
    return getattr(indicator, "currdenom", None)


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
    Get all indicator summaries for a school/district/state.

    Returns summary data for all 8 accountability indicators for the specified
    CDS code, reporting year, and student group.
    """
    # Query all indicators for the given cds, year, studentgroup
    statement = (
        select(AcademicIndicator)
        .where(AcademicIndicator.cds == cds)
        .where(AcademicIndicator.reportingyear == reportingyear)
        .where(AcademicIndicator.studentgroup == studentgroup)
    )
    indicators = session.exec(statement).all()

    if not indicators:
        raise HTTPException(
            status_code=404,
            detail=f"No indicator data found for CDS code: {cds}, year: {reportingyear}",
        )

    # Get basic info from the first indicator
    first = indicators[0]

    # Build indicator summaries
    indicator_summaries = []
    indicators_by_code = {ind.indicator: ind for ind in indicators}

    for code in ALL_INDICATORS:
        ind = indicators_by_code.get(code)
        if ind:
            currstatus = _currstatus(ind)
            currdenom = _currdenom(ind)
            # Calculate colors on-the-fly if missing (for legacy/state data)
            statuslevel = ind.statuslevel
            changelevel = ind.changelevel
            color = ind.color
            change = ind.change

            if color is None and currstatus is not None:
                # State assessment data has Mean Scale Score - convert to DFS
                is_mean_scale = (
                    code in ("ELA", "MATH")
                    and currstatus > 1000  # Mean scale scores are ~2400-2700
                )
                color_data = calculate_all(
                    indicator=code,
                    currstatus=currstatus,
                    priorstatus=ind.priorstatus,
                    is_mean_scale_score=is_mean_scale,
                )
                statuslevel = cast(int | None, color_data["statuslevel"])
                changelevel = cast(int | None, color_data["changelevel"])
                color = cast(int | None, color_data["color"])
                change = cast(float | None, color_data["change"])

            indicator_summaries.append(
                IndicatorSummary(
                    indicator=code,
                    currstatus=currstatus,
                    priorstatus=ind.priorstatus,
                    change=change,
                    statuslevel=statuslevel,
                    changelevel=changelevel,
                    color=color,
                    currdenom=currdenom,
                )
            )
        else:
            # Return empty summary for missing indicators
            indicator_summaries.append(IndicatorSummary(indicator=code))

    return DashboardSummaryResponse(
        cds=cds,
        rtype=first.rtype,
        schoolname=first.schoolname,
        districtname=first.districtname,
        countyname=first.countyname,
        charter_flag=first.charter_flag,
        reportingyear=reportingyear,
        indicators=indicator_summaries,
    )


@router.get("/dashboard/equity", response_model=EquityReportResponse)
def get_equity_report(
    session: SessionDep,
    cds: str = Query(..., description="14-char CDS code"),
    indicator: str = Query(..., description="Indicator code (ELA, MATH, etc.)"),
    reportingyear: str = Query(default="2025", description="Reporting year"),
) -> Any:
    """
    Get student group breakdown for an indicator.

    Returns color-coded performance data for all student groups within a
    school/district/state for a specific indicator.
    """
    # Query all studentgroups for given cds/indicator/year
    statement = (
        select(AcademicIndicator)
        .where(AcademicIndicator.cds == cds)
        .where(AcademicIndicator.indicator == indicator)
        .where(AcademicIndicator.reportingyear == reportingyear)
        .where(AcademicIndicator.studentgroup != "ALL")  # Exclude ALL group
    )
    indicators = session.exec(statement).all()

    # Count groups by color level
    color_counts = {
        "red": 0,
        "orange": 0,
        "yellow": 0,
        "green": 0,
        "blue": 0,
        "none": 0,
    }
    groups = []

    for ind in indicators:
        color_name = COLOR_NAMES.get(ind.color or 0, "none")
        color_counts[color_name] += 1

        groups.append(
            EquityGroupSummary(
                studentgroup=ind.studentgroup,
                statuslevel=ind.statuslevel,
                color=ind.color,
                currdenom=_currdenom(ind),
            )
        )

    return EquityReportResponse(
        cds=cds,
        indicator=indicator,
        reportingyear=reportingyear,
        color_counts=color_counts,
        groups=groups,
    )


@router.put("/users/me/preferences", response_model=UserPublic)
def update_user_preferences(
    session: SessionDep,
    current_user: CurrentUser,
    preferences: UserPreferencesUpdate,
) -> Any:
    """
    Update user preferences including last viewed school.
    """
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
    """
    Get the user's last viewed CDS code.
    """
    return {"last_viewed_cds": current_user.last_viewed_cds}


@router.get("/{id}", response_model=AcademicIndicatorPublic)
def read_academic_indicator(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get academic indicator by ID.
    """
    indicator = session.get(AcademicIndicator, id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Academic indicator not found")
    return indicator


@router.post("/", response_model=AcademicIndicatorPublic)
def create_academic_indicator(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    indicator_in: AcademicIndicatorCreate,
) -> Any:
    """
    Create new academic indicator. Superuser only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    indicator = AcademicIndicator.model_validate(indicator_in)
    session.add(indicator)
    session.commit()
    session.refresh(indicator)
    return indicator


@router.put("/{id}", response_model=AcademicIndicatorPublic)
def update_academic_indicator(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    indicator_in: AcademicIndicatorUpdate,
) -> Any:
    """
    Update an academic indicator. Superuser only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    indicator = session.get(AcademicIndicator, id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Academic indicator not found")

    update_dict = indicator_in.model_dump(exclude_unset=True)
    indicator.sqlmodel_update(update_dict)
    session.add(indicator)
    session.commit()
    session.refresh(indicator)
    return indicator


@router.delete("/{id}")
def delete_academic_indicator(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an academic indicator. Superuser only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    indicator = session.get(AcademicIndicator, id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Academic indicator not found")

    session.delete(indicator)
    session.commit()
    return Message(message="Academic indicator deleted successfully")
