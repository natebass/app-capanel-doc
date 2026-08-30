"""Response schemas for the reporting API.

These mirror the reports the state publishes at caaspp-elpac.ets.org: an
overall achievement distribution for a chosen entity, year, test, student group
and grade; the area, domain and composite breakdown beneath it; the same figure
across years, across grades, across student groups, and across the entities
inside a county or district.

Every distribution is returned already labelled.  A client should not have to
know that level 4 means "Standard Exceeded" for Smarter Balanced and "Well
developed English skills" for the Summative ELPAC, so the level names travel
with the numbers.
"""

from __future__ import annotations

from decimal import Decimal

from app.model.reference import (
    ApiModel,
    CharterFunding,
    EntityLevel,
    MetOrAboveSource,
    Program,
    SubscoreKind,
)


class EntityPublic(ApiModel):
    """An entity as the API presents it."""

    cds_code: str
    display_name: str
    entity_level: EntityLevel
    county_code: str
    district_code: str
    school_code: str
    county_name: str | None = None
    district_name: str | None = None
    school_name: str | None = None
    zip_code: str | None = None
    is_charter: bool = False
    charter_funding: CharterFunding | None = None
    parent_cds_code: str | None = None
    first_test_year: int | None = None
    last_test_year: int | None = None


class EntityList(ApiModel):
    data: list[EntityPublic]
    count: int


class EntityAncestry(ApiModel):
    """An entity together with the entities it rolls up into."""

    entity: EntityPublic
    ancestors: list[EntityPublic]


class LevelPublic(ApiModel):
    """One achievement level of a scheme."""

    level_number: int
    name: str
    short_name: str
    description: str | None = None


class LevelSchemePublic(ApiModel):
    code: str
    name: str
    level_count: int
    proficient_from_level: int | None = None
    description: str | None = None
    levels: list[LevelPublic]


class SubscorePublic(ApiModel):
    """An area, domain or composite a test reports in a given year."""

    code: str
    kind: SubscoreKind
    name: str
    reports_mean_scale_score: bool
    band_scheme: LevelSchemePublic
    sort_order: int


class AssessmentPublic(ApiModel):
    """A test, described for one administration year."""

    test_id: int
    code: str
    program: Program
    test_type: str
    name: str
    short_name: str
    subject: str
    is_alternate: bool
    sort_order: int
    level_scheme: LevelSchemePublic
    subscores: list[SubscorePublic]
    grades: list[str]
    grades_note: str | None = None


class StudentGroupPublic(ApiModel):
    program: Program
    student_group_id: int
    code: str
    name: str
    category: str
    sort_order: int


class GradePublic(ApiModel):
    code: str
    label: str
    sort_order: int
    is_aggregate: bool


class Catalog(ApiModel):
    """Everything a client needs to build the report controls."""

    test_year: int
    years: list[int]
    assessments: list[AssessmentPublic]
    student_groups: list[StudentGroupPublic]
    grades: list[GradePublic]


class LevelResult(ApiModel):
    """A labelled slice of a distribution."""

    level_number: int
    name: str
    short_name: str
    count: int | None = None
    pct: Decimal | None = None


class ResultSummary(ApiModel):
    """One test's overall result for the requested cell.

    ``suppressed`` means the state withheld the figures because too few
    students were tested.  Values can also be absent without suppression: the
    mean scale score is not reported for the "all grades" aggregate, because
    scale scores are not comparable between grades.
    """

    test_id: int
    test_code: str
    test_name: str
    short_name: str
    program: Program
    subject: str
    grade: str
    students_enrolled: int | None = None
    students_tested: int | None = None
    students_tested_with_scores: int | None = None
    participation_rate: Decimal | None = None
    mean_scale_score: Decimal | None = None
    met_or_above_count: int | None = None
    met_or_above_pct: Decimal | None = None
    met_or_above_source: MetOrAboveSource | None = None
    overall_total: int | None = None
    suppressed: bool = False
    level_scheme_code: str
    levels: list[LevelResult]
    derived_from_children: bool = False


class EntityResults(ApiModel):
    """An entity's results for one or more tests."""

    entity: EntityPublic
    results: list[ResultSummary]


class OverviewReport(ApiModel):
    """The equivalent of the state's "Test Results" landing report."""

    entity: EntityPublic
    test_year: int
    student_group_id: int
    grade: str
    school_type: str
    results: list[ResultSummary]
    comparisons: list[EntityResults]


class SubscoreResult(ApiModel):
    """One area, domain or composite for the requested cell."""

    code: str
    kind: SubscoreKind
    name: str
    sort_order: int
    mean_scale_score: Decimal | None = None
    total: int | None = None
    band_scheme_code: str
    bands: list[LevelResult]


class SubscoreReport(ApiModel):
    entity: EntityPublic
    test_year: int
    test_id: int
    student_group_id: int
    grade: str
    subscores: list[SubscoreResult]


class TrendPoint(ApiModel):
    """One year of a change-over-time series."""

    test_year: int
    students_tested: int | None = None
    mean_scale_score: Decimal | None = None
    met_or_above_pct: Decimal | None = None
    suppressed: bool = False
    levels: list[LevelResult]


class TrendReport(ApiModel):
    entity: EntityPublic
    test_id: int
    student_group_id: int
    grade: str
    points: list[TrendPoint]
    scale_break_note: str | None = None


class StudentGroupResult(ApiModel):
    """One student group's result, for the student group comparison report."""

    student_group_id: int
    name: str
    category: str
    sort_order: int
    students_enrolled: int | None = None
    students_tested: int | None = None
    mean_scale_score: Decimal | None = None
    met_or_above_pct: Decimal | None = None
    suppressed: bool = False
    levels: list[LevelResult]


class StudentGroupReport(ApiModel):
    entity: EntityPublic
    test_year: int
    test_id: int
    grade: str
    all_students: StudentGroupResult | None = None
    groups: list[StudentGroupResult]


class GradeResult(ApiModel):
    """One grade's result, for the by-grade report."""

    grade: str
    label: str
    sort_order: int
    students_tested: int | None = None
    mean_scale_score: Decimal | None = None
    met_or_above_pct: Decimal | None = None
    suppressed: bool = False
    levels: list[LevelResult]


class GradeReport(ApiModel):
    entity: EntityPublic
    test_year: int
    test_id: int
    student_group_id: int
    grades: list[GradeResult]


class ChildEntityResult(ApiModel):
    """One county, district or school inside the requested entity."""

    entity: EntityPublic
    students_tested: int | None = None
    mean_scale_score: Decimal | None = None
    met_or_above_pct: Decimal | None = None
    suppressed: bool = False


class ChildEntityReport(ApiModel):
    entity: EntityPublic
    test_year: int
    test_id: int
    student_group_id: int
    grade: str
    child_level: EntityLevel
    count: int
    data: list[ChildEntityResult]


class CompareReport(ApiModel):
    """Side-by-side results for an explicit list of entities."""

    test_year: int
    test_id: int
    student_group_id: int
    grade: str
    entries: list[EntityResults]
