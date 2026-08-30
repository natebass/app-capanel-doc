"""Reporting endpoints.

These mirror the reports the state publishes: an overall achievement
distribution for a chosen entity, the reporting categories beneath it, the same
figure over time, by grade, by student group, and across the entities inside a
county or district.

Percentages come back exactly as the state published them.  The one exception
is the charter filter on aggregate reports, which the research files cannot
answer directly -- they publish a single aggregate covering every school -- so
those responses set ``derivedFromChildren`` and recompute the mean scale score
as a weighted mean.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from sqlmodel import Session

from app.api.deps import SessionDep
from app.api.routes.entities import load_entity
from app.model.reference import Entity, EntityLevel, Program
from app.model.reports import (
    ChildEntityReport,
    CompareReport,
    EntityResults,
    GradeReport,
    OverviewReport,
    ResultSummary,
    StudentGroupReport,
    SubscoreReport,
    TrendReport,
)
from app.service import reports as report_service
from app.service.reference import ReferenceData, reference_data
from app.service.reports import (
    ALL_GRADES,
    ALL_STUDENTS_GROUP_ID,
    STATE_CDS,
    SchoolType,
    entity_public,
)

router = APIRouter(prefix="/reports", tags=["reports"])

CACHE_CONTROL = "public, max-age=300"


def _resolve_year(session: Session, year: int | None) -> int:
    years = report_service.available_years(session)
    if not years:
        raise HTTPException(
            status_code=404, detail="No assessment results have been imported yet."
        )
    return year if year in years else years[0]


def _parse_test_ids(tests: str | None) -> list[int] | None:
    if not tests:
        return None
    try:
        return [int(part) for part in tests.split(",") if part.strip()]
    except ValueError:
        raise HTTPException(
            status_code=422, detail="tests must be a comma-separated list of test ids"
        )


def _summaries(
    data: ReferenceData,
    rows: list,
    *,
    derived_from_children: bool = False,
) -> list[ResultSummary]:
    summaries = []
    for row in rows:
        assessment = data.assessment(row.test_id)
        if assessment is None:
            continue
        summaries.append(
            report_service.result_summary(
                data, assessment, row, derived_from_children=derived_from_children
            )
        )
    summaries.sort(key=lambda summary: summary.test_id)
    return summaries


def _program_for(data: ReferenceData, test_id: int) -> Program:
    assessment = data.assessment(test_id)
    return assessment.program if assessment else Program.CAASPP


@router.get("/overview")
def read_overview(
    session: SessionDep,
    response: Response,
    cds: str = Query(default=STATE_CDS, description="14-character CDS code."),
    year: int | None = None,
    student_group: int = Query(default=ALL_STUDENTS_GROUP_ID, alias="studentGroup"),
    grade: str = Query(default=ALL_GRADES),
    tests: str | None = Query(
        default=None, description="Comma-separated test ids; defaults to all."
    ),
    school_type: SchoolType = Query(default=SchoolType.ALL, alias="schoolType"),
    compare: bool = Query(
        default=True, description="Include the district, county and state alongside."
    ),
) -> OverviewReport:
    """Overall results for one entity, year, student group and grade."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    data = reference_data(session)
    entity = load_entity(session, cds)
    test_year = _resolve_year(session, year)
    test_ids = _parse_test_ids(tests)

    if school_type is SchoolType.ALL or entity.entity_level is EntityLevel.SCHOOL:
        rows = report_service.fetch_results(
            session,
            cds_code=entity.cds_code,
            test_year=test_year,
            student_group_id=student_group,
            grade=grade,
            test_ids=test_ids,
        )
        results = _summaries(data, rows)
    else:
        rows = report_service.aggregate_over_children(
            session,
            parent=entity,
            test_year=test_year,
            student_group_id=student_group,
            grade=grade,
            school_type=school_type,
            test_ids=test_ids,
        )
        results = _summaries(data, rows, derived_from_children=True)

    comparisons: list[EntityResults] = []
    if compare:
        cursor: Entity | None = entity
        while cursor is not None and cursor.parent_cds_code:
            parent = session.get(Entity, cursor.parent_cds_code)
            if parent is None:
                break
            parent_rows = report_service.fetch_results(
                session,
                cds_code=parent.cds_code,
                test_year=test_year,
                student_group_id=student_group,
                grade=grade,
                test_ids=test_ids,
            )
            comparisons.append(
                EntityResults(
                    entity=entity_public(parent),
                    results=_summaries(data, parent_rows),
                )
            )
            cursor = parent

    return OverviewReport(
        entity=entity_public(entity),
        test_year=test_year,
        student_group_id=student_group,
        grade=grade,
        school_type=school_type.value,
        results=results,
        comparisons=comparisons,
    )


@router.get("/subscores")
def read_subscores(
    session: SessionDep,
    response: Response,
    test_id: int = Query(alias="testId"),
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
    student_group: int = Query(default=ALL_STUDENTS_GROUP_ID, alias="studentGroup"),
    grade: str = Query(default=ALL_GRADES),
) -> SubscoreReport:
    """The areas, domains and composites reported beneath one test."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    data = reference_data(session)
    entity = load_entity(session, cds)
    test_year = _resolve_year(session, year)
    return SubscoreReport(
        entity=entity_public(entity),
        test_year=test_year,
        test_id=test_id,
        student_group_id=student_group,
        grade=grade,
        subscores=report_service.subscore_results(
            session,
            data,
            cds_code=entity.cds_code,
            test_year=test_year,
            test_id=test_id,
            student_group_id=student_group,
            grade=grade,
        ),
    )


@router.get("/trend")
def read_trend(
    session: SessionDep,
    response: Response,
    test_id: int = Query(alias="testId"),
    cds: str = Query(default=STATE_CDS),
    student_group: int = Query(default=ALL_STUDENTS_GROUP_ID, alias="studentGroup"),
    grade: str = Query(default=ALL_GRADES),
    from_year: int | None = Query(default=None, alias="fromYear"),
    to_year: int | None = Query(default=None, alias="toYear"),
) -> TrendReport:
    """One cell's results across every year the state reported them."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    data = reference_data(session)
    entity = load_entity(session, cds)
    points = report_service.trend_points(
        session,
        data,
        cds_code=entity.cds_code,
        test_id=test_id,
        student_group_id=student_group,
        grade=grade,
        from_year=from_year,
        to_year=to_year,
    )
    return TrendReport(
        entity=entity_public(entity),
        test_id=test_id,
        student_group_id=student_group,
        grade=grade,
        points=points,
        scale_break_note=report_service.scale_break_note(
            test_id, [point.test_year for point in points]
        ),
    )


@router.get("/student-groups")
def read_student_groups(
    session: SessionDep,
    response: Response,
    test_id: int = Query(alias="testId"),
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
    grade: str = Query(default=ALL_GRADES),
    category: list[str] | None = Query(default=None),
) -> StudentGroupReport:
    """Every student group's result for one entity, test and grade."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    data = reference_data(session)
    entity = load_entity(session, cds)
    test_year = _resolve_year(session, year)
    groups = report_service.student_group_results(
        session,
        data,
        _program_for(data, test_id),
        cds_code=entity.cds_code,
        test_year=test_year,
        test_id=test_id,
        grade=grade,
        categories=category,
    )
    all_students = next(
        (group for group in groups if group.student_group_id == ALL_STUDENTS_GROUP_ID),
        None,
    )
    return StudentGroupReport(
        entity=entity_public(entity),
        test_year=test_year,
        test_id=test_id,
        grade=grade,
        all_students=all_students,
        groups=groups,
    )


@router.get("/grades")
def read_grades(
    session: SessionDep,
    response: Response,
    test_id: int = Query(alias="testId"),
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
    student_group: int = Query(default=ALL_STUDENTS_GROUP_ID, alias="studentGroup"),
) -> GradeReport:
    """One entity's result for every grade a test reports."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    data = reference_data(session)
    entity = load_entity(session, cds)
    test_year = _resolve_year(session, year)
    return GradeReport(
        entity=entity_public(entity),
        test_year=test_year,
        test_id=test_id,
        student_group_id=student_group,
        grades=report_service.grade_results(
            session,
            data,
            cds_code=entity.cds_code,
            test_year=test_year,
            test_id=test_id,
            student_group_id=student_group,
        ),
    )


@router.get("/children")
def read_child_results(
    session: SessionDep,
    response: Response,
    test_id: int = Query(alias="testId"),
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
    student_group: int = Query(default=ALL_STUDENTS_GROUP_ID, alias="studentGroup"),
    grade: str = Query(default=ALL_GRADES),
    school_type: SchoolType = Query(default=SchoolType.ALL, alias="schoolType"),
    order_by: str = Query(default="met_or_above_pct", alias="orderBy"),
    descending: bool = True,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> ChildEntityReport:
    """Results for the counties, districts or schools inside one entity."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    test_year = _resolve_year(session, year)
    child_level = report_service.child_level_of(entity)
    if child_level is None:
        raise HTTPException(
            status_code=422, detail="A school has no entities inside it."
        )
    count, rows = report_service.child_results(
        session,
        parent=entity,
        test_year=test_year,
        test_id=test_id,
        student_group_id=student_group,
        grade=grade,
        school_type=school_type,
        order_by=order_by,
        descending=descending,
        limit=limit,
        offset=offset,
    )
    return ChildEntityReport(
        entity=entity_public(entity),
        test_year=test_year,
        test_id=test_id,
        student_group_id=student_group,
        grade=grade,
        child_level=child_level,
        count=count,
        data=rows,
    )


@router.get("/compare")
def read_comparison(
    session: SessionDep,
    response: Response,
    cds_codes: str = Query(
        alias="cdsCodes", description="Comma-separated CDS codes, at most 10."
    ),
    test_id: int | None = Query(default=None, alias="testId"),
    year: int | None = None,
    student_group: int = Query(default=ALL_STUDENTS_GROUP_ID, alias="studentGroup"),
    grade: str = Query(default=ALL_GRADES),
) -> CompareReport:
    """Side-by-side results for an explicit list of entities."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    data = reference_data(session)
    test_year = _resolve_year(session, year)
    codes = [code.strip() for code in cds_codes.split(",") if code.strip()][:10]
    if not codes:
        raise HTTPException(status_code=422, detail="cdsCodes must not be empty")

    entries: list[EntityResults] = []
    for code in codes:
        entity = session.get(Entity, code)
        if entity is None:
            continue
        rows = report_service.fetch_results(
            session,
            cds_code=code,
            test_year=test_year,
            student_group_id=student_group,
            grade=grade,
            test_ids=[test_id] if test_id else None,
        )
        entries.append(
            EntityResults(entity=entity_public(entity), results=_summaries(data, rows))
        )

    return CompareReport(
        test_year=test_year,
        test_id=test_id or 0,
        student_group_id=student_group,
        grade=grade,
        entries=entries,
    )
