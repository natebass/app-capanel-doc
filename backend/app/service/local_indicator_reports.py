"""Queries behind the local indicator endpoints.

The one piece of real logic here is resolving the reporting entity.  Local
indicators are reported by the LEA, so a school has no report of its own; it
inherits its district's.  Rather than returning a 404 for two thirds of the
entities in the database, a school walks up its ancestry until it finds one
that reported, and the response says which entity answered.
"""

from __future__ import annotations

from sqlmodel import Session, col, select

from app.model.local_indicators import (
    PERFORMANCE_VALUES,
    LocalIndicatorPriority,
    LocalIndicatorResult,
)
from app.model.reference import Entity

#: Fields that are prose rather than a rating, by how they read.
_MIN_NARRATIVE_LENGTH = 40


def priorities(session: Session) -> list[LocalIndicatorPriority]:
    return list(
        session.exec(
            select(LocalIndicatorPriority).order_by(
                col(LocalIndicatorPriority.sort_order)
            )
        ).all()
    )


def available_years(session: Session) -> list[int]:
    """Every reporting year with local indicator data, newest first."""
    years = session.exec(select(LocalIndicatorResult.reporting_year).distinct()).all()
    return sorted(years, reverse=True)


def resolve_reporter(session: Session, entity: Entity) -> Entity:
    """The nearest entity at or above ``entity`` that reports local indicators.

    Charter schools are their own LEA and report directly; a school inside a
    district does not, and inherits its district's report.
    """
    cursor: Entity | None = entity
    seen = 0
    while cursor is not None and seen < 5:
        has_any = session.exec(
            select(LocalIndicatorResult.cds_code)
            .where(LocalIndicatorResult.cds_code == cursor.cds_code)
            .limit(1)
        ).first()
        if has_any is not None:
            return cursor
        if not cursor.parent_cds_code:
            break
        cursor = session.get(Entity, cursor.parent_cds_code)
        seen += 1
    return entity


def entity_years(session: Session, cds_code: str) -> list[int]:
    years = session.exec(
        select(LocalIndicatorResult.reporting_year)
        .where(LocalIndicatorResult.cds_code == cds_code)
        .distinct()
    ).all()
    return sorted(years, reverse=True)


def fetch_year(
    session: Session, *, cds_code: str, reporting_year: int
) -> list[LocalIndicatorResult]:
    """Every priority one LEA reported for one year."""
    return list(
        session.exec(
            select(LocalIndicatorResult)
            .where(LocalIndicatorResult.cds_code == cds_code)
            .where(LocalIndicatorResult.reporting_year == reporting_year)
            .order_by(col(LocalIndicatorResult.priority_number))
        ).all()
    )


def fetch_one(
    session: Session, *, cds_code: str, reporting_year: int, priority_number: int
) -> LocalIndicatorResult | None:
    return session.exec(
        select(LocalIndicatorResult)
        .where(LocalIndicatorResult.cds_code == cds_code)
        .where(LocalIndicatorResult.reporting_year == reporting_year)
        .where(LocalIndicatorResult.priority_number == priority_number)
    ).first()


def fetch_trend(
    session: Session, *, cds_code: str, priority_number: int
) -> list[LocalIndicatorResult]:
    return list(
        session.exec(
            select(LocalIndicatorResult)
            .where(LocalIndicatorResult.cds_code == cds_code)
            .where(LocalIndicatorResult.priority_number == priority_number)
            .order_by(col(LocalIndicatorResult.reporting_year))
        ).all()
    )


def split_responses(
    responses: dict[str, object],
) -> tuple[dict[str, int], list[dict[str, str]]]:
    """Separate the numeric self-ratings from the free text.

    The state gives both the same kind of column name, so they are told apart
    by what they hold: an integer is a rating on the published 1-5 scale, and
    anything long enough to be a sentence is a narrative.  Order is preserved,
    because the narratives are written to be read in sequence.
    """
    ratings: dict[str, int] = {}
    narratives: list[dict[str, str]] = []
    for name, value in responses.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            ratings[name] = value
            continue
        text = str(value).strip()
        if not text:
            continue
        if text.isdigit():
            ratings[name] = int(text)
        elif len(text) >= _MIN_NARRATIVE_LENGTH:
            narratives.append({"field": name, "text": text})
    return ratings, narratives


def performance_values() -> list[str]:
    return list(PERFORMANCE_VALUES)
