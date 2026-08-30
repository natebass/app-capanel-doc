"""Fact tables holding published CAASPP and ELPAC results.

Two tables carry every test.  :class:`AssessmentResult` holds one row per
reported cell -- entity x year x test x student group x grade -- with the
overall achievement distribution flattened into four generic level slots.
:class:`AssessmentSubscore` holds the area, domain and composite breakdowns
beneath that cell, three bands wide.

Both tables normalise the direction of the reported bands: band 1 and level 1
are always the *lowest* performance.  The research files are inconsistent here
-- Smarter Balanced lists areas as above/near/below standard while CAST lists
domains as below/near/above -- and the importer reorders them so a single query
serves every test.

Suppression is preserved rather than erased.  The state replaces a value with
``*`` when the group is too small to report and leaves it empty when the figure
does not apply, so ``suppressed`` records the former while the value columns
stay ``NULL`` in both cases.  Mean scale scores are legitimately empty for the
"all grades" aggregate, because scale scores are not comparable across grades.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TypedDict

from sqlalchemy import Index
from sqlmodel import Field

from app.model.reference import ApiModel, MetOrAboveSource, enum_type


class _Precision(TypedDict):
    """Column precision shared by the percentage and score fields."""

    max_digits: int
    decimal_places: int


_PCT: _Precision = {"max_digits": 5, "decimal_places": 2}
_SCORE: _Precision = {"max_digits": 6, "decimal_places": 1}


class AssessmentResult(ApiModel, table=True):
    """One published overall result cell.

    The key mirrors the grain of every research file row: an entity, a test
    year, a test, a student group and a grade.
    """

    __tablename__ = "assessment_results"
    # The primary key already leads with ``cds_code, test_year``, which serves
    # every entity-scoped report.  This index covers the opposite direction --
    # one test and grade across many entities -- for the ranking and comparison
    # reports.
    __table_args__ = (
        Index(
            "ix_results_lookup",
            "test_year",
            "test_id",
            "grade",
            "student_group_id",
            "cds_code",
        ),
    )

    cds_code: str = Field(
        primary_key=True, max_length=14, foreign_key="entities.cds_code"
    )
    test_year: int = Field(primary_key=True)
    test_id: int = Field(primary_key=True, foreign_key="assessments.test_id")
    student_group_id: int = Field(primary_key=True)
    grade: str = Field(primary_key=True, max_length=2)

    students_enrolled: int | None = Field(default=None)
    students_tested: int | None = Field(default=None)
    students_tested_with_scores: int | None = Field(default=None)

    mean_scale_score: Decimal | None = Field(default=None, **_SCORE)

    level1_count: int | None = Field(default=None)
    level1_pct: Decimal | None = Field(default=None, **_PCT)
    level2_count: int | None = Field(default=None)
    level2_pct: Decimal | None = Field(default=None, **_PCT)
    level3_count: int | None = Field(default=None)
    level3_pct: Decimal | None = Field(default=None, **_PCT)
    level4_count: int | None = Field(default=None)
    level4_pct: Decimal | None = Field(default=None, **_PCT)

    met_or_above_count: int | None = Field(default=None)
    met_or_above_pct: Decimal | None = Field(default=None, **_PCT)
    met_or_above_source: MetOrAboveSource | None = Field(
        default=None, sa_type=enum_type(MetOrAboveSource), nullable=True
    )

    overall_total: int | None = Field(default=None)
    suppressed: bool = Field(default=False)


class AssessmentSubscore(ApiModel, table=True):
    """One area, domain or composite breakdown beneath an overall result.

    Rows are only written when the state reported at least one figure, so a
    missing row means "not reported for this cell" rather than zero.

    Three bands cover most breakdowns; the fourth exists for the Summative
    ELPAC oral and written language composites, which carry the same four
    performance levels as the overall score.
    """

    # Subscores are only ever read for a cell that has already been located by
    # entity, so the primary key is the only index they need.  At roughly two
    # rows per result row, a second index here costs more than a gigabyte.
    __tablename__ = "assessment_subscores"

    cds_code: str = Field(
        primary_key=True, max_length=14, foreign_key="entities.cds_code"
    )
    test_year: int = Field(primary_key=True)
    test_id: int = Field(primary_key=True)
    student_group_id: int = Field(primary_key=True)
    grade: str = Field(primary_key=True, max_length=2)
    subscore_code: str = Field(primary_key=True, max_length=40)

    mean_scale_score: Decimal | None = Field(default=None, **_SCORE)
    band1_count: int | None = Field(default=None)
    band1_pct: Decimal | None = Field(default=None, **_PCT)
    band2_count: int | None = Field(default=None)
    band2_pct: Decimal | None = Field(default=None, **_PCT)
    band3_count: int | None = Field(default=None)
    band3_pct: Decimal | None = Field(default=None, **_PCT)
    band4_count: int | None = Field(default=None)
    band4_pct: Decimal | None = Field(default=None, **_PCT)
    subscore_total: int | None = Field(default=None)
