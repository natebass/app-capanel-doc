"""API shapes for the LCFF Local Indicators.

Every response says plainly that this is an LEA's own account of itself.  The
state half of the Dashboard is measured; this half is self-reported to a
governing board, and a reader who does not know the difference will misread
the page.
"""

from __future__ import annotations

import datetime

from app.model.reference import ApiModel
from app.model.reports import EntityPublic


class PriorityPublic(ApiModel):
    """One of the seven LCFF priorities reported as a local indicator."""

    priority_number: int
    name: str
    short_name: str
    description: str | None = None
    county_office_only: bool = False
    sort_order: int = 0


class LocalIndicatorSummary(ApiModel):
    """One priority's headline result for one LEA."""

    priority_number: int
    name: str
    short_name: str
    county_office_only: bool = False
    performance: str | None = None
    #: When the governing board received this at a public meeting.
    meeting_date: datetime.date | None = None
    #: How many narrative and rating fields the LEA filled in.
    response_count: int = 0
    has_narrative: bool = False


class LocalIndicatorDetail(ApiModel):
    """One priority in full, including everything the LEA wrote."""

    priority_number: int
    name: str
    short_name: str
    description: str | None = None
    county_office_only: bool = False
    performance: str | None = None
    meeting_date: datetime.date | None = None
    additional_info: str | None = None
    #: Numeric self-ratings, under the state's own column names.
    ratings: dict[str, int] = {}
    #: Free text, under the state's own column names, in file order.
    narratives: list[dict[str, str]] = []


class LocalIndicatorReport(ApiModel):
    """Every priority for one LEA and year."""

    #: The entity the reader asked about.
    entity: EntityPublic
    #: The entity that actually answered.  Local indicators are reported by
    #: the LEA, so a school's report is its district's.
    reported_by: EntityPublic
    reporting_year: int
    priorities: list[LocalIndicatorSummary]
    available_years: list[int]


class LocalIndicatorTrendPoint(ApiModel):
    reporting_year: int
    performance: str | None = None
    meeting_date: datetime.date | None = None


class LocalIndicatorTrendReport(ApiModel):
    """One priority across every year the LEA has reported."""

    entity: EntityPublic
    reported_by: EntityPublic
    priority_number: int
    name: str
    points: list[LocalIndicatorTrendPoint]


class LocalIndicatorCatalog(ApiModel):
    """Everything needed to populate the local indicator filters."""

    reporting_year: int
    years: list[int]
    priorities: list[PriorityPublic]
    performance_values: list[str]
