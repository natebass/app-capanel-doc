"""Queries behind the accountability endpoints.

Every query filters on ``is_projected`` explicitly.  A caller asking for
published results gets only published results; a caller that wants the
provisional figure has to say so, and gets it labelled.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func
from sqlmodel import Session, col, or_, select

from app.model.dashboard import (
    DashboardIndicator,
    DashboardIndicatorResult,
    DashboardStudentGroup,
)
from app.model.dashboard_reports import COLOR_NAMES, IndicatorResult
from app.model.growth import GrowthResult
from app.model.reference import Entity, EntityLevel

STATE_CDS = "00000000000000"
ALL_STUDENTS = "ALL"

#: Indicators that report a single population and never an "all students" row.
#: English learner progress is only ever about English learners, so asking for
#: all students must still return it -- the Dashboard shows all seven
#: indicators side by side.
SOLE_GROUP_INDICATORS = {"ELPI": "EL"}

# The Dashboard is released in the autumn following the school year it covers.
DASHBOARD_RELEASE_MONTH = 11


@dataclass(frozen=True, slots=True)
class DashboardReference:
    """The indicator and student-group vocabularies, read once per request."""

    indicators: tuple[DashboardIndicator, ...]
    student_groups: tuple[DashboardStudentGroup, ...]

    def indicator(self, code: str) -> DashboardIndicator | None:
        return next((i for i in self.indicators if i.code == code), None)

    def indicator_name(self, code: str) -> str:
        found = self.indicator(code)
        return found.name if found else code


def dashboard_reference(session: Session) -> DashboardReference:
    return DashboardReference(
        indicators=tuple(
            session.exec(
                select(DashboardIndicator).order_by(col(DashboardIndicator.sort_order))
            ).all()
        ),
        student_groups=tuple(
            session.exec(
                select(DashboardStudentGroup).order_by(
                    col(DashboardStudentGroup.sort_order)
                )
            ).all()
        ),
    )


def available_years(session: Session, *, include_projected: bool = False) -> list[int]:
    """Every reporting year with data, newest first."""
    statement = select(DashboardIndicatorResult.reporting_year).distinct()
    if not include_projected:
        statement = statement.where(
            col(DashboardIndicatorResult.is_projected).is_(False)
        )
    years = session.exec(statement).all()
    return sorted(years, reverse=True)


def entity_years(session: Session, cds_code: str) -> list[int]:
    """The years one entity has any indicator data for, newest first."""
    years = session.exec(
        select(DashboardIndicatorResult.reporting_year)
        .where(DashboardIndicatorResult.cds_code == cds_code)
        .distinct()
    ).all()
    return sorted(years, reverse=True)


def fetch_indicators(
    session: Session,
    *,
    cds_code: str,
    reporting_year: int,
    student_group_code: str = ALL_STUDENTS,
    indicator_codes: list[str] | None = None,
    include_projected: bool = True,
) -> list[DashboardIndicatorResult]:
    """Every indicator result for one entity, year and student group.

    An indicator that only reports one population is returned under that
    population rather than being silently dropped.
    """
    wanted = {student_group_code}
    if student_group_code == ALL_STUDENTS:
        wanted |= set(SOLE_GROUP_INDICATORS.values())
    statement = (
        select(DashboardIndicatorResult)
        .where(DashboardIndicatorResult.cds_code == cds_code)
        .where(DashboardIndicatorResult.reporting_year == reporting_year)
        .where(col(DashboardIndicatorResult.student_group_code).in_(wanted))
    )
    if student_group_code == ALL_STUDENTS:
        # Only the sole-group indicators may come back under another group.
        statement = statement.where(
            or_(
                col(DashboardIndicatorResult.student_group_code) == ALL_STUDENTS,
                col(DashboardIndicatorResult.indicator_code).in_(SOLE_GROUP_INDICATORS),
            )
        )
    if indicator_codes:
        statement = statement.where(
            col(DashboardIndicatorResult.indicator_code).in_(indicator_codes)
        )
    if not include_projected:
        statement = statement.where(
            col(DashboardIndicatorResult.is_projected).is_(False)
        )
    return list(session.exec(statement).all())


def fetch_groups(
    session: Session,
    *,
    cds_code: str,
    reporting_year: int,
    indicator_code: str,
) -> list[DashboardIndicatorResult]:
    """One indicator for one entity, every student group."""
    return list(
        session.exec(
            select(DashboardIndicatorResult)
            .where(DashboardIndicatorResult.cds_code == cds_code)
            .where(DashboardIndicatorResult.reporting_year == reporting_year)
            .where(DashboardIndicatorResult.indicator_code == indicator_code)
        ).all()
    )


def fetch_trend(
    session: Session,
    *,
    cds_code: str,
    indicator_code: str,
    student_group_code: str = ALL_STUDENTS,
    from_year: int | None = None,
    to_year: int | None = None,
) -> list[DashboardIndicatorResult]:
    """One indicator's history for one entity, oldest first."""
    statement = (
        select(DashboardIndicatorResult)
        .where(DashboardIndicatorResult.cds_code == cds_code)
        .where(DashboardIndicatorResult.indicator_code == indicator_code)
        .where(DashboardIndicatorResult.student_group_code == student_group_code)
        .order_by(col(DashboardIndicatorResult.reporting_year))
    )
    if from_year is not None:
        statement = statement.where(
            DashboardIndicatorResult.reporting_year >= from_year
        )
    if to_year is not None:
        statement = statement.where(DashboardIndicatorResult.reporting_year <= to_year)
    return list(session.exec(statement).all())


def fetch_children(
    session: Session,
    *,
    parent: Entity,
    reporting_year: int,
    indicator_code: str,
    student_group_code: str = ALL_STUDENTS,
    order_by: str = "curr_status",
    descending: bool = True,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[tuple[Entity, DashboardIndicatorResult]], int]:
    """The entities directly inside a district or county, ranked."""
    column = {
        "curr_status": col(DashboardIndicatorResult.curr_status),
        "change": col(DashboardIndicatorResult.change),
        "color": col(DashboardIndicatorResult.color),
    }.get(order_by, col(DashboardIndicatorResult.curr_status))

    base = (
        select(Entity, DashboardIndicatorResult)
        .join(
            DashboardIndicatorResult,
            col(DashboardIndicatorResult.cds_code) == col(Entity.cds_code),
        )
        .where(Entity.parent_cds_code == parent.cds_code)
        .where(DashboardIndicatorResult.reporting_year == reporting_year)
        .where(DashboardIndicatorResult.indicator_code == indicator_code)
        .where(DashboardIndicatorResult.student_group_code == student_group_code)
    )
    total = session.exec(select(func.count()).select_from(base.subquery())).one()
    ordered = base.order_by(
        column.desc().nullslast() if descending else column.asc().nullslast()
    )
    rows = session.exec(ordered.offset(offset).limit(limit)).all()
    return [(entity, result) for entity, result in rows], total


def to_public(
    result: DashboardIndicatorResult,
    reference: DashboardReference,
    *,
    status_label: str | None = None,
    change_label: str | None = None,
) -> IndicatorResult:
    """Present one stored row, with the published names attached."""
    return IndicatorResult(
        indicator_code=result.indicator_code,
        indicator_name=reference.indicator_name(result.indicator_code),
        student_group_code=result.student_group_code,
        variant=result.variant,
        curr_numerator=result.curr_numerator,
        curr_denominator=result.curr_denominator,
        curr_status=result.curr_status,
        prior_status=result.prior_status,
        change=result.change,
        status_level=result.status_level,
        status_label=status_label,
        change_level=result.change_level,
        change_label=change_label,
        color=result.color,
        color_name=COLOR_NAMES.get(result.color) if result.color else None,
        box=result.box,
        accountability_met=result.accountability_met,
        small_denominator=result.small_denominator,
        dass_flag=result.dass_flag,
        is_projected=result.is_projected,
        projection_basis=result.projection_basis,
    )


def sort_key(reference: DashboardReference, result: IndicatorResult) -> int:
    indicator = reference.indicator(result.indicator_code)
    return indicator.sort_order if indicator else 99


def is_aggregate(entity: Entity) -> bool:
    """Whether an entity has children worth ranking."""
    return entity.entity_level is not EntityLevel.SCHOOL


def growth_years(session: Session) -> list[int]:
    """Every reporting year with growth data, newest first."""
    years = session.exec(select(GrowthResult.reporting_year).distinct()).all()
    return sorted(years, reverse=True)


def fetch_growth(
    session: Session,
    *,
    cds_code: str,
    reporting_year: int,
    student_group_code: str = ALL_STUDENTS,
) -> list[GrowthResult]:
    """Growth for one entity, year and student group, ELA then mathematics."""
    return list(
        session.exec(
            select(GrowthResult)
            .where(GrowthResult.cds_code == cds_code)
            .where(GrowthResult.reporting_year == reporting_year)
            .where(GrowthResult.student_group_code == student_group_code)
            .order_by(col(GrowthResult.subject))
        ).all()
    )
