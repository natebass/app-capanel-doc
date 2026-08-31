"""California School Dashboard accountability endpoints.

These serve the layer ``caschooldashboard.org`` shows: one colour per
indicator per entity, the student groups beneath it, the history behind it and
the schools inside a district ranked on it.

Figures come back exactly as the state published them.  Where a figure is a
projection -- this application working out a provisional colour in the months
between the underlying data being certified and the Dashboard being released --
the result says so in ``isProjected`` and explains itself in
``projectionBasis``.  Clients must present the two differently.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from sqlmodel import Session

from app.api.deps import SessionDep
from app.api.routes.entities import load_entity
from app.model.dashboard_reports import (
    COLOR_NAMES,
    ChildIndicatorReport,
    ChildIndicatorResult,
    DashboardCatalog,
    EnrollmentGroupPublic,
    EnrollmentReport,
    GrowthReport,
    GrowthResultPublic,
    IndicatorGroupReport,
    IndicatorPublic,
    IndicatorReport,
    IndicatorTrendPoint,
    IndicatorTrendReport,
    StudentGroupCodePublic,
)
from app.model.growth import (
    ESTIMATE_METHODS,
    GROWTH_CATEGORY_NAMES,
)
from app.service import dashboard_reports as service
from app.service.dashboard_reports import ALL_STUDENTS, STATE_CDS
from app.service.reports import entity_public

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

CACHE_CONTROL = "public, max-age=300"


def _resolve_year(session: Session, year: int | None) -> int:
    years = service.available_years(session, include_projected=True)
    if not years:
        raise HTTPException(
            status_code=404,
            detail="No Dashboard indicator data has been imported yet.",
        )
    return year if year in years else years[0]


@router.get("/catalog")
def read_catalog(
    session: SessionDep, response: Response, year: int | None = None
) -> DashboardCatalog:
    """Everything needed to populate the accountability filters."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    reference = service.dashboard_reference(session)
    if not reference.indicators:
        raise HTTPException(
            status_code=404, detail="Dashboard reference data has not been seeded."
        )
    return DashboardCatalog(
        reporting_year=_resolve_year(session, year),
        years=service.available_years(session, include_projected=True),
        indicators=[
            IndicatorPublic.model_validate(indicator)
            for indicator in reference.indicators
        ],
        student_groups=[
            StudentGroupCodePublic(code=group.code, name=group.name)
            for group in reference.student_groups
        ],
        colors=COLOR_NAMES,
    )


@router.get("/indicators")
def read_indicators(
    session: SessionDep,
    response: Response,
    cds: str = Query(default=STATE_CDS, description="14-character CDS code."),
    year: int | None = None,
    student_group: str = Query(default=ALL_STUDENTS, alias="studentGroup"),
    include_projected: bool = Query(default=True, alias="includeProjected"),
) -> IndicatorReport:
    """Every indicator for one entity -- the Dashboard landing view."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    reporting_year = _resolve_year(session, year)
    reference = service.dashboard_reference(session)

    rows = service.fetch_indicators(
        session,
        cds_code=entity.cds_code,
        reporting_year=reporting_year,
        student_group_code=student_group.upper(),
        include_projected=include_projected,
    )
    results = [service.to_public(row, reference) for row in rows]
    results.sort(key=lambda result: service.sort_key(reference, result))

    return IndicatorReport(
        entity=entity_public(entity),
        reporting_year=reporting_year,
        student_group_code=student_group.upper(),
        results=results,
        available_years=service.entity_years(session, entity.cds_code),
        includes_projections=any(result.is_projected for result in results),
    )


@router.get("/indicator")
def read_indicator(
    session: SessionDep,
    response: Response,
    indicator: str = Query(description="Indicator code, e.g. CHRO."),
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
) -> IndicatorGroupReport:
    """One indicator for one entity, broken out by student group."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    reporting_year = _resolve_year(session, year)
    reference = service.dashboard_reference(session)
    code = indicator.upper()
    if reference.indicator(code) is None:
        raise HTTPException(status_code=404, detail=f"Unknown indicator {indicator!r}.")

    rows = service.fetch_groups(
        session,
        cds_code=entity.cds_code,
        reporting_year=reporting_year,
        indicator_code=code,
    )
    order = {group.code: group.sort_order for group in reference.student_groups}
    results = [service.to_public(row, reference) for row in rows]
    results.sort(key=lambda result: order.get(result.student_group_code, 99))

    all_students = next(
        (result for result in results if result.student_group_code == ALL_STUDENTS),
        None,
    )
    return IndicatorGroupReport(
        entity=entity_public(entity),
        reporting_year=reporting_year,
        indicator_code=code,
        indicator_name=reference.indicator_name(code),
        all_students=all_students,
        groups=[
            result for result in results if result.student_group_code != ALL_STUDENTS
        ],
    )


@router.get("/trend")
def read_trend(
    session: SessionDep,
    response: Response,
    indicator: str = Query(description="Indicator code, e.g. CHRO."),
    cds: str = Query(default=STATE_CDS),
    student_group: str = Query(default=ALL_STUDENTS, alias="studentGroup"),
    from_year: int | None = Query(default=None, alias="fromYear"),
    to_year: int | None = Query(default=None, alias="toYear"),
) -> IndicatorTrendReport:
    """One indicator over time for one entity."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    reference = service.dashboard_reference(session)
    code = indicator.upper()
    if reference.indicator(code) is None:
        raise HTTPException(status_code=404, detail=f"Unknown indicator {indicator!r}.")

    rows = service.fetch_trend(
        session,
        cds_code=entity.cds_code,
        indicator_code=code,
        student_group_code=student_group.upper(),
        from_year=from_year,
        to_year=to_year,
    )
    points = [
        IndicatorTrendPoint(
            reporting_year=row.reporting_year,
            curr_status=row.curr_status,
            change=row.change,
            status_level=row.status_level,
            change_level=row.change_level,
            color=row.color,
            color_name=COLOR_NAMES.get(row.color) if row.color else None,
            is_projected=row.is_projected,
        )
        for row in rows
    ]
    # The state published no Dashboard for 2020 or 2021, so a gap in the line
    # is expected rather than missing data.
    covered = {point.reporting_year for point in points}
    span = range(min(covered), max(covered) + 1) if covered else range(0)
    return IndicatorTrendReport(
        entity=entity_public(entity),
        indicator_code=code,
        indicator_name=reference.indicator_name(code),
        student_group_code=student_group.upper(),
        points=points,
        missing_years=[year for year in span if year not in covered],
    )


@router.get("/children")
def read_children(
    session: SessionDep,
    response: Response,
    indicator: str = Query(description="Indicator code, e.g. CHRO."),
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
    student_group: str = Query(default=ALL_STUDENTS, alias="studentGroup"),
    order_by: str = Query(default="curr_status", alias="orderBy"),
    descending: bool = True,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> ChildIndicatorReport:
    """The entities inside a district or county, ranked on one indicator."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    if not service.is_aggregate(entity):
        raise HTTPException(
            status_code=422, detail="A school has no entities inside it."
        )
    reporting_year = _resolve_year(session, year)
    reference = service.dashboard_reference(session)
    code = indicator.upper()
    if reference.indicator(code) is None:
        raise HTTPException(status_code=404, detail=f"Unknown indicator {indicator!r}.")

    rows, total = service.fetch_children(
        session,
        parent=entity,
        reporting_year=reporting_year,
        indicator_code=code,
        student_group_code=student_group.upper(),
        order_by=order_by,
        descending=descending,
        limit=limit,
        offset=offset,
    )
    return ChildIndicatorReport(
        entity=entity_public(entity),
        reporting_year=reporting_year,
        indicator_code=code,
        student_group_code=student_group.upper(),
        children=[
            ChildIndicatorResult(
                entity=entity_public(child),
                result=service.to_public(result, reference),
            )
            for child, result in rows
        ],
        count=total,
    )


@router.get("/growth")
def read_growth(
    session: SessionDep,
    response: Response,
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
    student_group: str = Query(default=ALL_STUDENTS, alias="studentGroup"),
) -> GrowthReport:
    """Growth in ELA and mathematics -- how far students moved.

    Reported for information only.  Growth is not an accountability result and
    carries no performance colour.
    """
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    years = service.growth_years(session)
    if not years:
        raise HTTPException(
            status_code=404, detail="No growth data has been imported yet."
        )
    reporting_year = year if year in years else years[0]

    rows = service.fetch_growth(
        session,
        cds_code=entity.cds_code,
        reporting_year=reporting_year,
        student_group_code=student_group.upper(),
    )
    return GrowthReport(
        entity=entity_public(entity),
        reporting_year=reporting_year,
        student_group_code=student_group.upper(),
        results=[
            GrowthResultPublic(
                subject=row.subject,
                denominator=row.denominator,
                growth=row.growth,
                estimate_method=row.estimate_method,
                estimate_method_name=ESTIMATE_METHODS.get(row.estimate_method or ""),
                performance_category=row.performance_category,
                performance_category_name=GROWTH_CATEGORY_NAMES.get(
                    row.performance_category or 0
                ),
                number_improved=row.number_improved,
                percent_improved=row.percent_improved,
            )
            for row in rows
        ],
        available_years=years,
    )


@router.get("/enrollment")
def read_enrollment(
    session: SessionDep,
    response: Response,
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
) -> EnrollmentReport:
    """Who attends: every student group's share of Census Day enrolment."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    years = service.enrollment_years(session)
    if not years:
        raise HTTPException(
            status_code=404, detail="No enrolment data has been imported yet."
        )
    reporting_year = year if year in years else years[0]

    reference = service.dashboard_reference(session)
    names = {group.code: group.name for group in reference.student_groups}
    rows = service.fetch_enrollment(
        session, cds_code=entity.cds_code, reporting_year=reporting_year
    )
    total = next(
        (row.total_enrollment for row in rows if row.total_enrollment is not None), None
    )
    return EnrollmentReport(
        entity=entity_public(entity),
        reporting_year=reporting_year,
        total_enrollment=total,
        groups=[
            EnrollmentGroupPublic(
                student_group_code=row.student_group_code,
                name=names.get(row.student_group_code, row.student_group_code),
                subgroup_total=row.subgroup_total,
                rate=row.rate,
            )
            for row in rows
        ],
        available_years=years,
    )
