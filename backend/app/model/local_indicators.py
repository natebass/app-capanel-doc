"""The LCFF Local Indicators -- the other half of the California Dashboard.

The Dashboard has two halves.  :mod:`app.model.dashboard` holds the state
half: seven indicators the state measures, each reduced to a performance
colour.  This module holds the local half, which works nothing like it.

Local Indicators are **self-assessments**.  Each local educational agency
rates itself against the LCFF state priorities, reports the result to its own
governing board at a public meeting, and the state records what it said.  There
is no colour, no five-by-five grid and no cut points; there is only ``Met``,
``Not Met``, or ``Not Met For Two or More Years``, plus whatever the LEA chose
to write.

Three consequences shape the schema:

``performance`` is a string, never a colour
    Nothing here is comparable to ``dashboard_indicator_results.color``, and
    joining the two would imply an equivalence the state does not make.

The grain is the LEA, not the school
    Districts, county offices and charter schools that are their own LEA.  A
    school inherits its district's answer; it does not have one.

The columns change almost every year
    Priority 3 has been published with 8, 21, 27 and 28 columns; Priority 6's
    single ``summary`` became ``summary1``/``summary2``/``summary3``; the key
    column has been spelled ``CDSCode``, ``cdsCode`` and ``cdscode``, and the
    priority ``PriorityNumber`` then ``priorityId``.  Only a small envelope is
    stable, so only that is given columns.  Everything else is kept verbatim in
    ``responses``, exactly as ``source_extras`` does on the state side.
"""

from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field

from app.model.reference import ApiModel

#: The three values the state publishes for a local indicator.
MET = "Met"
NOT_MET = "Not Met"
NOT_MET_TWO_YEARS = "Not Met For Two or More Years"

PERFORMANCE_VALUES = (MET, NOT_MET, NOT_MET_TWO_YEARS)


class LocalIndicatorPriority(ApiModel, table=True):
    """One of the seven LCFF state priorities reported as a local indicator."""

    __tablename__ = "local_indicator_priorities"

    priority_number: int = Field(primary_key=True)
    name: str = Field(max_length=120)
    short_name: str = Field(max_length=60)
    description: str | None = Field(default=None)
    #: Priorities 9 and 10 are reported only by county offices of education.
    county_office_only: bool = Field(default=False)
    sort_order: int = Field(default=0)


class LocalIndicatorResult(ApiModel, table=True):
    """One LEA's self-assessment against one priority, for one year."""

    __tablename__ = "local_indicator_results"
    __table_args__ = (
        # The primary key leads with the entity, which serves the LEA page.
        # This covers the other direction -- one priority across many LEAs --
        # for statewide summaries.
        Index(
            "ix_local_indicator_lookup",
            "reporting_year",
            "priority_number",
            "performance",
        ),
    )

    cds_code: str = Field(
        primary_key=True, max_length=14, foreign_key="entities.cds_code"
    )
    reporting_year: int = Field(primary_key=True)
    priority_number: int = Field(
        primary_key=True, foreign_key="local_indicator_priorities.priority_number"
    )

    #: The LEA's name as it appears in the file, which is not always the name
    #: the entity carries from the assessment files.
    lea_name: str | None = Field(default=None, max_length=200)

    performance: str | None = Field(default=None, max_length=40)

    #: When the governing board received the self-assessment at a public
    #: meeting.  This is the only provenance a reader has for the narratives,
    #: so it travels with them rather than being dropped as bookkeeping.
    meeting_date: datetime.date | None = Field(default=None)

    additional_info: str | None = Field(default=None)

    #: Every column outside the stable envelope, under the name the state gave
    #: it that year.  Ratings arrive as integers, narratives as text.
    responses: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False, default=dict)
    )
