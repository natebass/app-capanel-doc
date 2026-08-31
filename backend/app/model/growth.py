"""Student growth in ELA and mathematics.

Growth answers a different question from the rest of the Dashboard.  The
academic indicator says where a school's students *stand*; growth says how far
they *moved*, comparing each student against their own prior results.  A
high-poverty school can sit Red on status and Exceptional on growth, and the
two are both true.

Kept in its own table rather than folded into
:class:`app.model.dashboard.DashboardIndicatorResult` for three reasons:

* Three of that table's core columns -- ``color``, ``change`` and every
  ``prior_*`` figure -- have no meaning here.  Growth is a single measure with
  no year-on-year comparison of its own.
* ``performance_category`` is published by the state, not derived from cut
  points, so it is not the same kind of thing as a ``status_level`` and should
  not be queried as though it were.
* The State Board adopted growth for **informational purposes only** in July
  2025; it is explicitly not used for Local Control Funding Formula
  eligibility.  Keeping it structurally separate makes it hard to present as
  an accountability result by accident.

Science has no growth score: the California Science Test is not taken in
consecutive grades, so there is nothing to compare against.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Index
from sqlmodel import Field

from app.model.reference import ApiModel

#: The growth performance categories the State Board adopted in July 2025.
GROWTH_CATEGORY_NAMES = {
    1: "Minimal Growth",
    2: "Moderate Growth",
    3: "Average Growth",
    4: "Accelerated Growth",
    5: "Exceptional Growth",
}

#: How the state estimated the figure, or why it did not.
ESTIMATE_METHODS = {
    "WEIGHTED": "Weighted average",
    "SIMPLE": "Simple average",
    "NONE": "Not calculated; too few students",
}

SUBJECTS = ("ELA", "MATH")


class GrowthResult(ApiModel, table=True):
    """One growth figure for one entity, subject and student group."""

    __tablename__ = "growth_results"
    __table_args__ = (
        Index(
            "ix_growth_lookup",
            "reporting_year",
            "subject",
            "student_group_code",
            "cds_code",
        ),
    )

    cds_code: str = Field(
        primary_key=True, max_length=14, foreign_key="entities.cds_code"
    )
    reporting_year: int = Field(primary_key=True)
    subject: str = Field(primary_key=True, max_length=8, description="ELA or MATH.")
    student_group_code: str = Field(primary_key=True, max_length=8)

    #: Students with a valid growth score.
    denominator: int | None = Field(default=None)
    #: The reported growth estimate.  Runs roughly -91 to +110.
    growth: Decimal | None = Field(default=None, max_digits=6, decimal_places=1)
    #: WEIGHTED, SIMPLE or NONE.
    estimate_method: str | None = Field(default=None, max_length=10)
    #: 1 (Minimal) to 5 (Exceptional); null where the state assigned none.
    performance_category: int | None = Field(default=None)

    number_improved: int | None = Field(default=None)
    percent_improved: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )

    charter_flag: bool = Field(default=False)
    coe_flag: bool = Field(default=False)
    dass_flag: bool = Field(default=False)
