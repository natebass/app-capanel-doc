from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel
from sqlmodel.main import SQLModelConfig


class DashboardAggregation(SQLModel):
    """
    Aggegrated test data for a CDS code.
    """

    cds: str
    student_group_id: str
    test_year: str
    overall_met_and_above_pct: str | None = None
    overall_mean_scale_score: str | None = None

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class IndicatorSummary(SQLModel):
    """
    Summary of a specific CAASPP/ELPAC test result.
    """

    test_id: str
    test_type: str
    grade: str
    students_enrolled: str
    students_tested: str
    overall_mean_scale_score: str | None = None
    overall_met_and_above_pct: str | None = None
    levels: dict[str, float] | None = None

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class DashboardSummaryResponse(SQLModel):
    """Response containing multiple tests for a school/district/county."""

    cds: str
    test_year: str
    indicators: list[IndicatorSummary]

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class EquityGroupSummary(SQLModel):
    """Summary of a student group for the equity report."""

    student_group: str
    overall_met_and_above_pct: str | None = None
    students_tested: str | None = None

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class EquityReportResponse(SQLModel):
    """Response containing student group breakdown for a test."""

    cds: str
    test_id: str
    test_year: str
    groups: list[EquityGroupSummary]

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)
