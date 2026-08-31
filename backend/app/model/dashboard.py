"""Reference and fact tables for the California School Dashboard indicators.

The Dashboard is a different publication from the research files.  Where
:mod:`app.model.results` holds *what students scored*, this module holds *how
the state judged an entity* -- the accountability layer that
``caschooldashboard.org`` actually shows.  Five of its seven indicators
(chronic absenteeism, suspension, graduation, college/career and English
learner progress) have no assessment-file source at all.

Every indicator file the state publishes shares one record envelope::

    cds, rtype, schoolname, districtname, countyname, charter_flag, coe_flag,
    dass_flag, studentgroup, curr*/prior*, change, statuslevel, changelevel,
    color, box, currnsizemet, priornsizemet, accountabilitymet, indicator,
    reportingyear

so one fact table serves all of them.  Only the measure columns differ, and
those that do not fit the shared shape -- the twenty-odd ``curr_prep_*``
columns in the College/Career file, the ``currprogressed*`` columns in the
English Learner Progress file -- are kept verbatim in ``source_extras`` rather
than being flattened into columns that are null for six indicators out of
seven.

Two vocabularies are deliberately *not* unified with the assessment side:

``student_group_code``
    The Dashboard uses short strings (``ALL``, ``AA``, ``EL``, ``SED``) while
    the research files use numeric CAASPP/ELPAC group IDs.  They are different
    code sets from different publishers and only partly overlap.
``variant``
    The state publishes six suspension five-by-five tables keyed by school
    type and two academic ones split at grade 11, so a cut point is only
    meaningful together with the variant it belongs to.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, TypedDict

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field

from app.model.reference import ApiModel


class _Precision(TypedDict):
    """Column precision shared by rate fields."""

    max_digits: int
    decimal_places: int


# Precision matches app.model.results so the two layers round alike.
_RATE: _Precision = {"max_digits": 8, "decimal_places": 2}

# The variant used when an indicator publishes a single five-by-five table.
DEFAULT_VARIANT = "ALL"


class DashboardIndicator(ApiModel, table=True):
    """One of the seven state indicators shown on the Dashboard."""

    __tablename__ = "dashboard_indicators"

    # Wide enough for the longest published code; 8 was too tight for
    # ELPACPART.
    code: str = Field(primary_key=True, max_length=16)
    name: str = Field(max_length=120)
    short_name: str = Field(max_length=40)
    #: Chronic absenteeism and suspension are judged in reverse: a *low* rate
    #: is the good outcome, so the status scale runs the other way.
    lower_is_better: bool = Field(default=False)
    unit: str = Field(max_length=40, description="percent, dfs or points.")
    #: Published alongside the accountability indicators but not part of the
    #: accountability system: it carries no colour and cannot trigger support.
    is_informational: bool = Field(default=False)
    description: str | None = Field(default=None)
    sort_order: int = Field(default=0)


class DashboardStudentGroup(ApiModel, table=True):
    """A Dashboard student group code.

    Separate from :class:`app.model.reference.StudentGroup`, which holds the
    numeric CAASPP and ELPAC ids.  The Dashboard publishes short strings, and
    the two sets only partly overlap: the academic indicator files also report
    ``SBA``, ``CAA`` and ``CAST`` rows, which are assessment types rather than
    demographics.
    """

    __tablename__ = "dashboard_student_groups"

    # Wide enough for the longest published code; 8 was too tight for
    # ELPACPART.
    code: str = Field(primary_key=True, max_length=16)
    name: str = Field(max_length=120)
    category: str = Field(max_length=40)
    sort_order: int = Field(default=0)


class DashboardCutpoint(ApiModel, table=True):
    """One status or change band for an indicator, from the state's tables.

    Bounds are inclusive and either end may be open, which is how the
    published tables read ("+45.0 points or more", "-70.1 points or fewer").
    """

    __tablename__ = "dashboard_cutpoints"

    indicator_code: str = Field(
        primary_key=True, max_length=16, foreign_key="dashboard_indicators.code"
    )
    variant: str = Field(primary_key=True, max_length=16)
    kind: str = Field(primary_key=True, max_length=8, description="status or change.")
    level: int = Field(primary_key=True, description="1 (worst) to 5 (best).")

    lower_bound: Decimal | None = Field(default=None, **_RATE)
    upper_bound: Decimal | None = Field(default=None, **_RATE)
    label: str = Field(max_length=60)


class DashboardColorCell(ApiModel, table=True):
    """One cell of a five-by-five grid: status x change -> color.

    ``color`` is null for the handful of combinations the state marks N/A --
    an entity cannot be at the very highest graduation rate and also have
    declined significantly.

    Entities with fewer than 150 students are judged on a reduced grid, which
    is why ``small_denominator`` is part of the key.  For chronic absenteeism,
    suspension and college/career that grid is three change bands wide rather
    than five; graduation keeps five bands but assigns different colors.  The
    state does not publish these grids as tables, so they are derived from the
    published files and checked against them.
    """

    __tablename__ = "dashboard_color_cells"

    indicator_code: str = Field(
        primary_key=True, max_length=16, foreign_key="dashboard_indicators.code"
    )
    variant: str = Field(primary_key=True, max_length=16)
    small_denominator: bool = Field(primary_key=True)
    status_level: int = Field(primary_key=True)
    change_level: int = Field(primary_key=True)
    color: int | None = Field(
        default=None, description="1 red, 2 orange, 3 yellow, 4 green, 5 blue."
    )


class DashboardIndicatorResult(ApiModel, table=True):
    """One published (or projected) indicator result for one entity.

    The grain is the grain of a Dashboard file row: an entity, a reporting
    year, an indicator and a student group -- with ``variant`` joining the key
    because the suspension file reports a school under its school type.
    """

    __tablename__ = "dashboard_indicator_results"
    __table_args__ = (
        # Deliberately no foreign key onto ``dashboard_color_cells``: the
        # color on a published row is whatever the state printed, and it must
        # survive even when our transcription of the grid disagrees or has
        # not been seeded for a variant yet.
        #
        # The primary key already leads with ``cds_code``, which serves the
        # entity-scoped views.  This index covers the opposite direction --
        # one indicator across many entities -- for ranking and comparison.
        Index(
            "ix_dashboard_lookup",
            "reporting_year",
            "indicator_code",
            "student_group_code",
            "cds_code",
        ),
    )

    cds_code: str = Field(
        primary_key=True, max_length=14, foreign_key="entities.cds_code"
    )
    reporting_year: int = Field(primary_key=True)
    indicator_code: str = Field(
        primary_key=True, max_length=16, foreign_key="dashboard_indicators.code"
    )
    student_group_code: str = Field(primary_key=True, max_length=8)
    variant: str = Field(primary_key=True, max_length=16, default=DEFAULT_VARIANT)

    curr_numerator: int | None = Field(default=None)
    curr_denominator: int | None = Field(default=None)
    prior_numerator: int | None = Field(default=None)
    prior_denominator: int | None = Field(default=None)

    curr_status: Decimal | None = Field(default=None, **_RATE)
    prior_status: Decimal | None = Field(default=None, **_RATE)
    change: Decimal | None = Field(default=None, **_RATE)

    status_level: int | None = Field(default=None)
    change_level: int | None = Field(default=None)
    color: int | None = Field(default=None)
    box: int | None = Field(default=None)

    curr_nsize_met: bool = Field(default=False)
    prior_nsize_met: bool = Field(default=False)
    accountability_met: bool = Field(default=False)
    small_denominator: bool = Field(default=False)

    charter_flag: bool = Field(default=False)
    coe_flag: bool = Field(default=False)
    dass_flag: bool = Field(default=False)

    #: False for a figure the state published, True for one this application
    #: projected ahead of the Dashboard release.  Every read path must filter
    #: on this explicitly -- a projection must never be mistaken for a result.
    is_projected: bool = Field(default=False)
    #: How a projected row was produced, for display next to the figure.
    projection_basis: str | None = Field(default=None, max_length=200)

    #: Indicator-specific columns kept verbatim rather than flattened.
    source_extras: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False, default=dict)
    )
