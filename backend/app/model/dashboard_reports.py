"""API shapes for the accountability layer.

Like :mod:`app.model.reports`, these carry the published *names* alongside the
numbers -- "Very High", "Declined Significantly", "Yellow" -- so a client never
has to know that colour 3 means yellow or that status level 5 means the best
outcome for one indicator and the worst for another.

Every result says whether it was published by the state or projected by this
application.  That distinction is the most important thing on the page and is
never left for the client to infer.
"""

from __future__ import annotations

from decimal import Decimal

from app.model.reference import ApiModel
from app.model.reports import EntityPublic

#: Colour numbers as the Dashboard names them.
COLOR_NAMES = {1: "Red", 2: "Orange", 3: "Yellow", 4: "Green", 5: "Blue"}


class IndicatorPublic(ApiModel):
    """One of the seven state indicators."""

    code: str
    name: str
    short_name: str
    lower_is_better: bool
    unit: str
    sort_order: int


class StudentGroupCodePublic(ApiModel):
    """A Dashboard student group.

    These are the state's short codes, which are not the numeric CAASPP and
    ELPAC group ids used by the assessment reports.
    """

    code: str
    name: str


class IndicatorResult(ApiModel):
    """One indicator's result for one entity."""

    indicator_code: str
    indicator_name: str
    student_group_code: str
    variant: str

    curr_numerator: int | None = None
    curr_denominator: int | None = None
    curr_status: Decimal | None = None
    prior_status: Decimal | None = None
    change: Decimal | None = None

    status_level: int | None = None
    status_label: str | None = None
    change_level: int | None = None
    change_label: str | None = None
    color: int | None = None
    color_name: str | None = None
    box: int | None = None

    accountability_met: bool = False
    small_denominator: bool = False
    dass_flag: bool = False

    #: True when this application worked the figure out ahead of the state.
    is_projected: bool = False
    projection_basis: str | None = None


class IndicatorReport(ApiModel):
    """Every indicator for one entity and year."""

    entity: EntityPublic
    reporting_year: int
    student_group_code: str
    results: list[IndicatorResult]
    #: Years the entity has any indicator data for, newest first.
    available_years: list[int]
    #: True when any result in this report is a projection.
    includes_projections: bool = False


class IndicatorGroupReport(ApiModel):
    """One indicator, broken out by student group."""

    entity: EntityPublic
    reporting_year: int
    indicator_code: str
    indicator_name: str
    all_students: IndicatorResult | None = None
    groups: list[IndicatorResult]


class IndicatorTrendPoint(ApiModel):
    """One year of an indicator's history."""

    reporting_year: int
    curr_status: Decimal | None = None
    change: Decimal | None = None
    status_level: int | None = None
    change_level: int | None = None
    color: int | None = None
    color_name: str | None = None
    is_projected: bool = False


class IndicatorTrendReport(ApiModel):
    """One indicator over time for one entity."""

    entity: EntityPublic
    indicator_code: str
    indicator_name: str
    student_group_code: str
    points: list[IndicatorTrendPoint]
    #: The Dashboard was not published for these years.
    missing_years: list[int]


class ChildIndicatorResult(ApiModel):
    """One child entity's result, for ranking within a district or county."""

    entity: EntityPublic
    result: IndicatorResult


class ChildIndicatorReport(ApiModel):
    """The entities inside a district or county, ranked on one indicator."""

    entity: EntityPublic
    reporting_year: int
    indicator_code: str
    student_group_code: str
    children: list[ChildIndicatorResult]
    count: int


class DashboardCatalog(ApiModel):
    """Everything needed to populate the accountability filters."""

    reporting_year: int
    years: list[int]
    indicators: list[IndicatorPublic]
    student_groups: list[StudentGroupCodePublic]
    colors: dict[int, str] = COLOR_NAMES


class GrowthResultPublic(ApiModel):
    """One subject's growth figure for one entity."""

    subject: str
    denominator: int | None = None
    growth: Decimal | None = None
    estimate_method: str | None = None
    estimate_method_name: str | None = None
    performance_category: int | None = None
    performance_category_name: str | None = None
    number_improved: int | None = None
    percent_improved: Decimal | None = None


class GrowthReport(ApiModel):
    """Growth in ELA and mathematics for one entity and year.

    Growth is published for information only: the State Board adopted it in
    July 2025 and it is not used for Local Control Funding Formula
    eligibility.  ``isInformational`` is always true and clients must say so.
    """

    entity: EntityPublic
    reporting_year: int
    student_group_code: str
    results: list[GrowthResultPublic]
    available_years: list[int]
    is_informational: bool = True
