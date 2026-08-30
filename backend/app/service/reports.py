"""Queries behind the reporting API.

Two conventions keep these queries small.  The statewide row -- CDS code
``00000000000000`` -- carries every year, test and grade the database holds, so
"what data exists?" questions are answered from that one entity's slice of the
primary key rather than by scanning the fact table.  And percentages are read
back exactly as the state published them; nothing is recomputed except where a
report explicitly aggregates over child entities, which is flagged on the
response.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, col, select
from sqlmodel.sql.expression import Select

from app.model.reference import Assessment, Entity, EntityLevel, Program
from app.model.reports import (
    ChildEntityResult,
    EntityPublic,
    GradeResult,
    LevelResult,
    ResultSummary,
    StudentGroupResult,
    SubscoreResult,
    TrendPoint,
)
from app.model.results import AssessmentResult, AssessmentSubscore
from app.service.reference import ReferenceData

STATE_CDS = "00" + "0" * 12
ALL_STUDENTS_GROUP_ID = 1
ALL_GRADES = "13"

# The Smarter Balanced and CAST scales were set in 2014-15 and have not
# changed; these tests reset theirs, so a trend line across the break is not a
# like-for-like comparison.
SCALE_BREAKS: dict[int, tuple[int, str]] = {
    39: (
        2025,
        "The California Spanish Assessment blueprint changed for 2024-25. "
        "Scores from 2024-25 onward are not comparable with earlier years.",
    ),
}


class SchoolType(StrEnum):
    """The state's charter filter on aggregate reports."""

    ALL = "all"
    CHARTER = "charter"
    NON_CHARTER = "non-charter"


def entity_public(entity: Entity) -> EntityPublic:
    return EntityPublic.model_validate(entity)


def _level_results(
    data: ReferenceData,
    test_id: int,
    test_year: int,
    counts: Sequence[int | None],
    pcts: Sequence[Decimal | None],
) -> list[LevelResult]:
    """Attach the published level names to a distribution."""
    scheme = data.scheme_for(test_id, test_year)
    if scheme is None:
        return []
    return [
        LevelResult(
            level_number=level.level_number,
            name=level.name,
            short_name=level.short_name,
            count=counts[level.level_number - 1]
            if level.level_number <= len(counts)
            else None,
            pct=pcts[level.level_number - 1]
            if level.level_number <= len(pcts)
            else None,
        )
        for level in scheme.levels
    ]


def _result_levels(data: ReferenceData, row: AssessmentResult) -> list[LevelResult]:
    return _level_results(
        data,
        row.test_id,
        row.test_year,
        (row.level1_count, row.level2_count, row.level3_count, row.level4_count),
        (row.level1_pct, row.level2_pct, row.level3_pct, row.level4_pct),
    )


def _participation(row: AssessmentResult) -> Decimal | None:
    if not row.students_enrolled or row.students_tested is None:
        return None
    return round(Decimal(row.students_tested) * 100 / Decimal(row.students_enrolled), 2)


def result_summary(
    data: ReferenceData,
    assessment: Assessment,
    row: AssessmentResult,
    *,
    derived_from_children: bool = False,
) -> ResultSummary:
    """Turn one stored row into the labelled shape the API returns."""
    scheme = data.scheme_for(row.test_id, row.test_year)
    return ResultSummary(
        test_id=assessment.test_id,
        test_code=assessment.code,
        test_name=assessment.name,
        short_name=assessment.short_name,
        program=assessment.program,
        subject=assessment.subject,
        grade=row.grade,
        students_enrolled=row.students_enrolled,
        students_tested=row.students_tested,
        students_tested_with_scores=row.students_tested_with_scores,
        participation_rate=_participation(row),
        mean_scale_score=row.mean_scale_score,
        met_or_above_count=row.met_or_above_count,
        met_or_above_pct=row.met_or_above_pct,
        met_or_above_source=row.met_or_above_source,
        overall_total=row.overall_total,
        suppressed=row.suppressed,
        level_scheme_code=scheme.code if scheme else "",
        levels=_result_levels(data, row),
        derived_from_children=derived_from_children,
    )


def fetch_results(
    session: Session,
    *,
    cds_code: str,
    test_year: int,
    student_group_id: int,
    grade: str,
    test_ids: Sequence[int] | None = None,
) -> list[AssessmentResult]:
    """Read the stored rows for one reporting cell."""
    statement = (
        select(AssessmentResult)
        .where(AssessmentResult.cds_code == cds_code)
        .where(AssessmentResult.test_year == test_year)
        .where(AssessmentResult.student_group_id == student_group_id)
        .where(AssessmentResult.grade == grade)
    )
    if test_ids:
        statement = statement.where(col(AssessmentResult.test_id).in_(test_ids))
    return list(session.exec(statement).all())


def aggregate_over_children(
    session: Session,
    *,
    parent: Entity,
    test_year: int,
    student_group_id: int,
    grade: str,
    school_type: SchoolType,
    test_ids: Sequence[int] | None = None,
) -> list[AssessmentResult]:
    """Sum school-level rows to answer a charter-filtered request.

    The research files publish one aggregate per entity, covering every school
    in it, so a charter-only or non-charter-only figure has to be rebuilt from
    the schools underneath.  Counts add up exactly; the mean scale score does
    not, so it is recomputed as a mean weighted by the number of tests with
    scores and the response marks the row as derived.
    """
    weighted_mean = func.sum(
        AssessmentResult.mean_scale_score
        * func.coalesce(AssessmentResult.students_tested_with_scores, 0)
    ) / func.nullif(func.sum(AssessmentResult.students_tested_with_scores), 0)

    # SQLModel's ``select`` helper is typed for at most four entities, so this
    # wide aggregate is built from the ``Select`` class it returns instead.
    statement: Select[Any] = (
        Select(
            col(AssessmentResult.test_id),
            func.sum(AssessmentResult.students_enrolled),
            func.sum(AssessmentResult.students_tested),
            func.sum(AssessmentResult.students_tested_with_scores),
            weighted_mean,
            func.sum(AssessmentResult.level1_count),
            func.sum(AssessmentResult.level2_count),
            func.sum(AssessmentResult.level3_count),
            func.sum(AssessmentResult.level4_count),
            func.sum(AssessmentResult.met_or_above_count),
            func.sum(AssessmentResult.overall_total),
        )
        .join(Entity, col(Entity.cds_code) == col(AssessmentResult.cds_code))
        .where(Entity.entity_level == EntityLevel.SCHOOL)
        .where(AssessmentResult.test_year == test_year)
        .where(AssessmentResult.student_group_id == student_group_id)
        .where(AssessmentResult.grade == grade)
        .group_by(col(AssessmentResult.test_id))
    )
    statement = _restrict_to_descendants(statement, parent)
    if school_type is SchoolType.CHARTER:
        statement = statement.where(col(Entity.is_charter).is_(True))
    elif school_type is SchoolType.NON_CHARTER:
        statement = statement.where(col(Entity.is_charter).is_(False))
    if test_ids:
        statement = statement.where(col(AssessmentResult.test_id).in_(test_ids))

    rows: list[AssessmentResult] = []
    for record in session.exec(statement).all():
        (
            test_id,
            enrolled,
            tested,
            with_scores,
            mean,
            level1,
            level2,
            level3,
            level4,
            met,
            total,
        ) = record
        rows.append(
            AssessmentResult(
                cds_code=parent.cds_code,
                test_year=test_year,
                test_id=test_id,
                student_group_id=student_group_id,
                grade=grade,
                students_enrolled=enrolled,
                students_tested=tested,
                students_tested_with_scores=with_scores,
                mean_scale_score=(
                    round(Decimal(mean), 1) if mean is not None else None
                ),
                level1_count=level1,
                level1_pct=_share(level1, total),
                level2_count=level2,
                level2_pct=_share(level2, total),
                level3_count=level3,
                level3_pct=_share(level3, total),
                level4_count=level4,
                level4_pct=_share(level4, total),
                met_or_above_count=met,
                met_or_above_pct=_share(met, total),
                overall_total=total,
                suppressed=False,
            )
        )
    return rows


def _share(part: int | None, whole: int | None) -> Decimal | None:
    if part is None or not whole:
        return None
    return round(Decimal(part) * 100 / Decimal(whole), 2)


def _restrict_to_descendants(statement, parent: Entity):  # type: ignore[no-untyped-def]
    """Narrow a query to the entities inside ``parent``."""
    match parent.entity_level:
        case EntityLevel.STATE:
            return statement
        case EntityLevel.COUNTY:
            return statement.where(Entity.county_code == parent.county_code)
        case EntityLevel.DISTRICT:
            return statement.where(Entity.county_code == parent.county_code).where(
                Entity.district_code == parent.district_code
            )
        case _:
            return statement.where(Entity.cds_code == parent.cds_code)


def child_level_of(entity: Entity) -> EntityLevel | None:
    """The level of the entities directly inside this one."""
    match entity.entity_level:
        case EntityLevel.STATE:
            return EntityLevel.COUNTY
        case EntityLevel.COUNTY:
            return EntityLevel.DISTRICT
        case EntityLevel.DISTRICT:
            return EntityLevel.SCHOOL
        case _:
            return None


def child_results(
    session: Session,
    *,
    parent: Entity,
    test_year: int,
    test_id: int,
    student_group_id: int,
    grade: str,
    school_type: SchoolType = SchoolType.ALL,
    order_by: str = "met_or_above_pct",
    descending: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> tuple[int, list[ChildEntityResult]]:
    """List the entities inside ``parent`` with their result for one test."""
    child_level = child_level_of(parent)
    if child_level is None:
        return 0, []

    base = (
        select(Entity, AssessmentResult)
        .join(AssessmentResult, col(AssessmentResult.cds_code) == col(Entity.cds_code))
        .where(Entity.entity_level == child_level)
        .where(AssessmentResult.test_year == test_year)
        .where(AssessmentResult.test_id == test_id)
        .where(AssessmentResult.student_group_id == student_group_id)
        .where(AssessmentResult.grade == grade)
    )
    base = _restrict_to_descendants(base, parent)
    if school_type is SchoolType.CHARTER:
        base = base.where(col(Entity.is_charter).is_(True))
    elif school_type is SchoolType.NON_CHARTER:
        base = base.where(col(Entity.is_charter).is_(False))

    count = session.exec(select(func.count()).select_from(base.subquery())).one()

    sort_column = {
        "met_or_above_pct": col(AssessmentResult.met_or_above_pct),
        "mean_scale_score": col(AssessmentResult.mean_scale_score),
        "students_tested": col(AssessmentResult.students_tested),
        "name": col(Entity.display_name),
    }.get(order_by, col(AssessmentResult.met_or_above_pct))
    ordering = (
        sort_column.desc().nulls_last()
        if descending
        else sort_column.asc().nulls_last()
    )

    rows = session.exec(base.order_by(ordering).offset(offset).limit(limit)).all()
    return count, [
        ChildEntityResult(
            entity=entity_public(entity),
            students_tested=result.students_tested,
            mean_scale_score=result.mean_scale_score,
            met_or_above_pct=result.met_or_above_pct,
            suppressed=result.suppressed,
        )
        for entity, result in rows
    ]


def subscore_results(
    session: Session,
    data: ReferenceData,
    *,
    cds_code: str,
    test_year: int,
    test_id: int,
    student_group_id: int,
    grade: str,
) -> list[SubscoreResult]:
    """Read the area, domain and composite breakdown for one cell."""
    stored = {
        row.subscore_code: row
        for row in session.exec(
            select(AssessmentSubscore)
            .where(AssessmentSubscore.cds_code == cds_code)
            .where(AssessmentSubscore.test_year == test_year)
            .where(AssessmentSubscore.test_id == test_id)
            .where(AssessmentSubscore.student_group_id == student_group_id)
            .where(AssessmentSubscore.grade == grade)
        ).all()
    }

    results: list[SubscoreResult] = []
    for definition in data.subscores_for(test_id, test_year):
        row = stored.get(definition.code)
        if row is None:
            continue
        counts = (row.band1_count, row.band2_count, row.band3_count, row.band4_count)
        pcts = (row.band1_pct, row.band2_pct, row.band3_pct, row.band4_pct)
        results.append(
            SubscoreResult(
                code=definition.code,
                kind=definition.kind,
                name=definition.name,
                sort_order=definition.sort_order,
                mean_scale_score=row.mean_scale_score,
                total=row.subscore_total,
                band_scheme_code=definition.band_scheme.code,
                bands=[
                    LevelResult(
                        level_number=level.level_number,
                        name=level.name,
                        short_name=level.short_name,
                        count=counts[level.level_number - 1],
                        pct=pcts[level.level_number - 1],
                    )
                    for level in definition.band_scheme.levels
                    if level.level_number <= len(counts)
                ],
            )
        )
    return results


def trend_points(
    session: Session,
    data: ReferenceData,
    *,
    cds_code: str,
    test_id: int,
    student_group_id: int,
    grade: str,
    from_year: int | None = None,
    to_year: int | None = None,
) -> list[TrendPoint]:
    """Read one cell across every year it was reported."""
    statement = (
        select(AssessmentResult)
        .where(AssessmentResult.cds_code == cds_code)
        .where(AssessmentResult.test_id == test_id)
        .where(AssessmentResult.student_group_id == student_group_id)
        .where(AssessmentResult.grade == grade)
        .order_by(col(AssessmentResult.test_year))
    )
    if from_year is not None:
        statement = statement.where(AssessmentResult.test_year >= from_year)
    if to_year is not None:
        statement = statement.where(AssessmentResult.test_year <= to_year)

    return [
        TrendPoint(
            test_year=row.test_year,
            students_tested=row.students_tested,
            mean_scale_score=row.mean_scale_score,
            met_or_above_pct=row.met_or_above_pct,
            suppressed=row.suppressed,
            levels=_result_levels(data, row),
        )
        for row in session.exec(statement).all()
    ]


def student_group_results(
    session: Session,
    data: ReferenceData,
    program: Program,
    *,
    cds_code: str,
    test_year: int,
    test_id: int,
    grade: str,
    categories: Sequence[str] | None = None,
) -> list[StudentGroupResult]:
    """Read every student group's result for one entity, test and grade."""
    rows = session.exec(
        select(AssessmentResult)
        .where(AssessmentResult.cds_code == cds_code)
        .where(AssessmentResult.test_year == test_year)
        .where(AssessmentResult.test_id == test_id)
        .where(AssessmentResult.grade == grade)
    ).all()

    results: list[StudentGroupResult] = []
    for row in rows:
        group = data.student_groups.get((program, row.student_group_id))
        if group is None:
            continue
        if categories and group.category not in categories:
            continue
        results.append(
            StudentGroupResult(
                student_group_id=group.student_group_id,
                name=group.name,
                category=group.category,
                sort_order=group.sort_order,
                students_enrolled=row.students_enrolled,
                students_tested=row.students_tested,
                mean_scale_score=row.mean_scale_score,
                met_or_above_pct=row.met_or_above_pct,
                suppressed=row.suppressed,
                levels=_result_levels(data, row),
            )
        )
    results.sort(key=lambda group: group.sort_order)
    return results


def grade_results(
    session: Session,
    data: ReferenceData,
    *,
    cds_code: str,
    test_year: int,
    test_id: int,
    student_group_id: int,
) -> list[GradeResult]:
    """Read one entity's result for every grade the test reports."""
    rows = session.exec(
        select(AssessmentResult)
        .where(AssessmentResult.cds_code == cds_code)
        .where(AssessmentResult.test_year == test_year)
        .where(AssessmentResult.test_id == test_id)
        .where(AssessmentResult.student_group_id == student_group_id)
    ).all()

    results: list[GradeResult] = []
    for row in rows:
        grade = data.grades.get(row.grade)
        results.append(
            GradeResult(
                grade=row.grade,
                label=grade.label if grade else row.grade,
                sort_order=grade.sort_order if grade else 999,
                students_tested=row.students_tested,
                mean_scale_score=row.mean_scale_score,
                met_or_above_pct=row.met_or_above_pct,
                suppressed=row.suppressed,
                levels=_result_levels(data, row),
            )
        )
    results.sort(key=lambda grade: grade.sort_order)
    return results


def available_years(
    session: Session, test_ids: Iterable[int] | None = None
) -> list[int]:
    """Years that hold data, read from the statewide rows."""
    statement = (
        select(AssessmentResult.test_year)
        .where(AssessmentResult.cds_code == STATE_CDS)
        .distinct()
        .order_by(col(AssessmentResult.test_year).desc())
    )
    if test_ids:
        statement = statement.where(col(AssessmentResult.test_id).in_(list(test_ids)))
    return list(session.exec(statement).all())


def available_tests(session: Session, test_year: int) -> list[int]:
    """Tests reported in a year, read from the statewide rows."""
    return list(
        session.exec(
            select(AssessmentResult.test_id)
            .where(AssessmentResult.cds_code == STATE_CDS)
            .where(AssessmentResult.test_year == test_year)
            .distinct()
        ).all()
    )


def available_grades(session: Session, test_year: int, test_id: int) -> list[str]:
    """Grades a test reported in a year, read from the statewide rows."""
    return list(
        session.exec(
            select(col(AssessmentResult.grade))
            .where(AssessmentResult.cds_code == STATE_CDS)
            .where(AssessmentResult.test_year == test_year)
            .where(AssessmentResult.test_id == test_id)
            .distinct()
        ).all()
    )


def scale_break_note(test_id: int, years: Sequence[int]) -> str | None:
    """Warn when a trend line crosses a change in the test's scale."""
    entry = SCALE_BREAKS.get(test_id)
    if entry is None or not years:
        return None
    break_year, note = entry
    return note if min(years) < break_year <= max(years) else None
