"""LCFF Local Indicator endpoints -- the local half of the Dashboard.

Where ``/dashboard`` reports how the state judged a school, these report what
the local educational agency said about itself and told its governing board.
There is no performance colour here, only ``Met``, ``Not Met`` or ``Not Met
For Two or More Years``, so nothing in these responses should be rendered in
the Dashboard's five colours.

Local indicators are reported by the LEA.  Asking about a school returns its
district's report, and ``reportedBy`` says so.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from sqlmodel import Session

from app.api.deps import SessionDep
from app.api.routes.entities import load_entity
from app.model.local_indicator_reports import (
    LocalIndicatorCatalog,
    LocalIndicatorDetail,
    LocalIndicatorReport,
    LocalIndicatorSummary,
    LocalIndicatorTrendPoint,
    LocalIndicatorTrendReport,
    PriorityPublic,
)
from app.service import local_indicator_reports as service
from app.service.reports import STATE_CDS, entity_public

router = APIRouter(prefix="/local-indicators", tags=["local-indicators"])

CACHE_CONTROL = "public, max-age=300"


def _resolve_year(session: Session, year: int | None) -> int:
    years = service.available_years(session)
    if not years:
        raise HTTPException(
            status_code=404,
            detail="No local indicator data has been imported yet.",
        )
    return year if year in years else years[0]


@router.get("/catalog")
def read_catalog(
    session: SessionDep, response: Response, year: int | None = None
) -> LocalIndicatorCatalog:
    """Everything needed to populate the local indicator filters."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    found = service.priorities(session)
    if not found:
        raise HTTPException(
            status_code=404, detail="Local indicator reference data is not seeded."
        )
    return LocalIndicatorCatalog(
        reporting_year=_resolve_year(session, year),
        years=service.available_years(session),
        priorities=[PriorityPublic.model_validate(p) for p in found],
        performance_values=service.performance_values(),
    )


@router.get("/")
def read_local_indicators(
    session: SessionDep,
    response: Response,
    cds: str = Query(default=STATE_CDS, description="14-character CDS code."),
    year: int | None = None,
) -> LocalIndicatorReport:
    """Every priority one LEA reported, for one year."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    reporter = service.resolve_reporter(session, entity)
    reporting_year = _resolve_year(session, year)

    by_priority = {
        row.priority_number: row
        for row in service.fetch_year(
            session, cds_code=reporter.cds_code, reporting_year=reporting_year
        )
    }
    summaries = []
    for priority in service.priorities(session):
        row = by_priority.get(priority.priority_number)
        ratings, narratives = (
            service.split_responses(row.responses) if row else ({}, [])
        )
        summaries.append(
            LocalIndicatorSummary(
                priority_number=priority.priority_number,
                name=priority.name,
                short_name=priority.short_name,
                county_office_only=priority.county_office_only,
                performance=row.performance if row else None,
                meeting_date=row.meeting_date if row else None,
                response_count=len(ratings) + len(narratives),
                has_narrative=bool(narratives),
            )
        )

    return LocalIndicatorReport(
        entity=entity_public(entity),
        reported_by=entity_public(reporter),
        reporting_year=reporting_year,
        priorities=summaries,
        available_years=service.entity_years(session, reporter.cds_code),
    )


@router.get("/priority")
def read_priority(
    session: SessionDep,
    response: Response,
    priority: int = Query(description="LCFF priority number, e.g. 3."),
    cds: str = Query(default=STATE_CDS),
    year: int | None = None,
) -> LocalIndicatorDetail:
    """One priority in full, including everything the LEA wrote."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    reporter = service.resolve_reporter(session, entity)
    reporting_year = _resolve_year(session, year)

    known = {p.priority_number: p for p in service.priorities(session)}
    meta = known.get(priority)
    if meta is None:
        raise HTTPException(status_code=404, detail=f"Unknown priority {priority!r}.")

    row = service.fetch_one(
        session,
        cds_code=reporter.cds_code,
        reporting_year=reporting_year,
        priority_number=priority,
    )
    ratings, narratives = service.split_responses(row.responses) if row else ({}, [])
    return LocalIndicatorDetail(
        priority_number=meta.priority_number,
        name=meta.name,
        short_name=meta.short_name,
        description=meta.description,
        county_office_only=meta.county_office_only,
        performance=row.performance if row else None,
        meeting_date=row.meeting_date if row else None,
        additional_info=row.additional_info if row else None,
        ratings=ratings,
        narratives=narratives,
    )


@router.get("/trend")
def read_trend(
    session: SessionDep,
    response: Response,
    priority: int = Query(description="LCFF priority number, e.g. 3."),
    cds: str = Query(default=STATE_CDS),
) -> LocalIndicatorTrendReport:
    """One priority across every year the LEA has reported."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds)
    reporter = service.resolve_reporter(session, entity)

    known = {p.priority_number: p for p in service.priorities(session)}
    meta = known.get(priority)
    if meta is None:
        raise HTTPException(status_code=404, detail=f"Unknown priority {priority!r}.")

    rows = service.fetch_trend(
        session, cds_code=reporter.cds_code, priority_number=priority
    )
    return LocalIndicatorTrendReport(
        entity=entity_public(entity),
        reported_by=entity_public(reporter),
        priority_number=priority,
        name=meta.name,
        points=[
            LocalIndicatorTrendPoint(
                reporting_year=row.reporting_year,
                performance=row.performance,
                meeting_date=row.meeting_date,
            )
            for row in rows
        ],
    )
