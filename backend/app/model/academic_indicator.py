from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class AcademicIndicatorBase(SQLModel):
    """
    CAASPP Academic Indicators based on the new schema.
    """

    # Identifiers
    county_code: str | None = Field(default=None, max_length=2)
    district_code: str = Field(
        max_length=5, primary_key=True
    )  # Used as part of PK for SQLAlchemy
    school_code: str | None = Field(default=None, max_length=7)
    record_type_id: str | None = Field(default=None, max_length=2)
    charter_number: str | None = Field(default=None, max_length=4)
    test_year: str = Field(max_length=4, primary_key=True)
    test_type: str = Field(max_length=2, primary_key=True)
    test_id: str = Field(max_length=2, primary_key=True)
    student_group_id: str = Field(max_length=3, primary_key=True)
    grade: str = Field(max_length=2, primary_key=True)

    # Participation
    students_enrolled: str = Field(max_length=10)
    students_tested: str = Field(max_length=10)
    students_tested_with_scores: str | None = Field(default=None, max_length=10)

    # Overall Scores
    overall_mean_scale_score: str | None = Field(default=None, max_length=10)
    overall_total: str | None = Field(default=None, max_length=10)
    overall_level_1_pct: str | None = Field(default=None, max_length=10)
    overall_level_1_count: str | None = Field(default=None, max_length=10)
    overall_level_2_pct: str | None = Field(default=None, max_length=10)
    overall_level_2_count: str | None = Field(default=None, max_length=10)
    overall_level_3_pct: str | None = Field(default=None, max_length=10)
    overall_level_3_count: str | None = Field(default=None, max_length=10)
    overall_level_4_pct: str | None = Field(default=None, max_length=10)
    overall_level_4_count: str | None = Field(default=None, max_length=10)
    overall_met_and_above_pct: str | None = Field(default=None, max_length=10)
    overall_met_and_above_count: str | None = Field(default=None, max_length=10)


class AcademicIndicator(AcademicIndicatorBase, table=True):
    __tablename__ = "academic_indicators"
    domain_data: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))


class AcademicIndicatorCreate(AcademicIndicatorBase):
    domain_data: dict[str, Any] | None = None


class AcademicIndicatorUpdate(SQLModel):
    county_code: str | None = None
    district_code: str | None = None
    school_code: str | None = None
    record_type_id: str | None = None
    charter_number: str | None = None
    test_year: str | None = None
    test_type: str | None = None
    test_id: str | None = None
    student_group_id: str | None = None
    grade: str | None = None
    students_enrolled: str | None = None
    students_tested: str | None = None
    students_tested_with_scores: str | None = None
    overall_mean_scale_score: str | None = None
    overall_total: str | None = None
    overall_level_1_pct: str | None = None
    overall_level_1_count: str | None = None
    overall_level_2_pct: str | None = None
    overall_level_2_count: str | None = None
    overall_level_3_pct: str | None = None
    overall_level_3_count: str | None = None
    overall_level_4_pct: str | None = None
    overall_level_4_count: str | None = None
    overall_met_and_above_pct: str | None = None
    overall_met_and_above_count: str | None = None
    domain_data: dict[str, Any] | None = None


class AcademicIndicatorPublic(AcademicIndicatorBase):
    domain_data: dict[str, Any] | None = None


class AcademicIndicatorsPublic(SQLModel):
    data: list[AcademicIndicatorPublic]
    count: int
