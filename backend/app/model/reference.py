"""Reference (dimension) tables for the CAASPP and ELPAC reporting model.

Every table here mirrors a lookup that the California Assessment of Student
Performance and Progress (CAASPP) and English Language Proficiency Assessments
for California (ELPAC) reporting system publishes alongside its research files:

* :class:`Assessment` mirrors *Table C — Test IDs and Names*.
* :class:`StudentGroup` mirrors *Table A — Student Groups*.
* :class:`GradeLevel` mirrors *Table B — Grades*.
* :class:`Entity` mirrors the entities file that accompanies every research file.
* :class:`PerformanceLevelScheme` / :class:`PerformanceLevel` and
  :class:`SubscoreDefinition` capture the achievement-level and
  area/domain vocabulary that differs between tests, which the layouts express
  only in prose.

Reference rows are versioned by test year wherever the state has changed a
test.  The California Spanish Assessment, for example, reported three *score
ranges* and no domains through 2023-24 and three *performance levels* with four
domains and two composites from 2024-25 onward, so the level scheme and the
subscore vocabulary hang off :class:`AssessmentYear` rather than
:class:`Assessment`.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic.alias_generators import to_camel
from sqlalchemy import ForeignKeyConstraint, Index
from sqlmodel import Field, SQLModel
from sqlmodel.main import SQLModelConfig


class ApiModel(SQLModel):
    """Base for models serialised to the API as camelCase."""

    model_config = SQLModelConfig(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class Program(StrEnum):
    """The two assessment programs reported by the state's public site."""

    CAASPP = "CAASPP"
    ELPAC = "ELPAC"


class EntityLevel(StrEnum):
    """Reporting level of an entity in a research file."""

    STATE = "state"
    COUNTY = "county"
    DISTRICT = "district"
    SCHOOL = "school"


class CharterFunding(StrEnum):
    """How a charter school is funded, per the entity ``Type ID``."""

    DIRECT = "direct"
    LOCAL = "local"


class SubscoreKind(StrEnum):
    """Kind of reported subscore.

    ``AREA`` and ``COMPOSITE_AREA`` are Smarter Balanced claim reporting
    categories; ``DOMAIN`` is used by CAST, CSA and ELPAC; ``COMPOSITE`` is an
    ELPAC/CSA composite that carries its own mean scale score.
    """

    AREA = "area"
    COMPOSITE_AREA = "composite_area"
    DOMAIN = "domain"
    COMPOSITE = "composite"


class MetOrAboveSource(StrEnum):
    """Where the "met or above" figure on a result row came from."""

    PUBLISHED = "published"
    DERIVED = "derived"


class PerformanceLevelScheme(ApiModel, table=True):
    """A named set of ordered achievement levels.

    ``proficient_from_level`` is the lowest level the state treats as meeting
    the standard.  It is ``None`` for schemes where the state publishes no
    proficiency cut, such as the three ELPAC domain bands.
    """

    __tablename__ = "performance_level_schemes"

    code: str = Field(primary_key=True, max_length=40)
    name: str = Field(max_length=120)
    level_count: int
    proficient_from_level: int | None = Field(default=None)
    description: str | None = Field(default=None)


class PerformanceLevel(ApiModel, table=True):
    """One achievement level within a :class:`PerformanceLevelScheme`."""

    __tablename__ = "performance_levels"

    scheme_code: str = Field(
        primary_key=True, max_length=40, foreign_key="performance_level_schemes.code"
    )
    level_number: int = Field(primary_key=True)
    name: str = Field(max_length=120)
    short_name: str = Field(max_length=40)
    description: str | None = Field(default=None)


class Assessment(ApiModel, table=True):
    """A test reported by CAASPP or ELPAC (*Table C* of the record layouts)."""

    __tablename__ = "assessments"

    test_id: int = Field(primary_key=True)
    code: str = Field(max_length=40, unique=True)
    program: Program = Field(max_length=10)
    test_type: str = Field(
        max_length=5,
        description="File-level test type code, e.g. 'B' for Smarter Balanced.",
    )
    name: str = Field(max_length=120)
    short_name: str = Field(max_length=40)
    subject: str = Field(max_length=60)
    is_alternate: bool = Field(default=False)
    sort_order: int = Field(default=0)


class AssessmentYear(ApiModel, table=True):
    """Per-year facts about a test whose reporting has changed over time."""

    __tablename__ = "assessment_years"

    test_id: int = Field(primary_key=True, foreign_key="assessments.test_id")
    test_year: int = Field(
        primary_key=True,
        description="Spring year of the administration; 2025 means 2024-25.",
    )
    level_scheme_code: str = Field(
        max_length=40, foreign_key="performance_level_schemes.code"
    )
    reports_mean_scale_score: bool = Field(default=True)
    grades_note: str | None = Field(default=None)


class SubscoreDefinition(ApiModel, table=True):
    """An area, domain or composite reported beneath a test's overall score.

    The research files name Smarter Balanced reporting categories positionally
    ("Area 1"), and the meaning of each position differs between ELA and
    mathematics.  This table resolves the position to the published name so the
    API never has to.
    """

    __tablename__ = "subscore_definitions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["test_id", "test_year"],
            ["assessment_years.test_id", "assessment_years.test_year"],
        ),
    )

    test_id: int = Field(primary_key=True)
    test_year: int = Field(primary_key=True)
    code: str = Field(primary_key=True, max_length=40)
    kind: SubscoreKind = Field(max_length=20)
    name: str = Field(max_length=120)
    band_scheme_code: str = Field(
        max_length=40, foreign_key="performance_level_schemes.code"
    )
    reports_mean_scale_score: bool = Field(default=False)
    sort_order: int = Field(default=0)


class StudentGroup(ApiModel, table=True):
    """A reported student group (*Table A*).

    CAASPP and ELPAC reuse the same numeric identifiers with different wording
    -- 128 is "Reported disabilities" for CAASPP and "Students Receiving
    Special Education Services" for ELPAC -- so the program is part of the key.
    """

    __tablename__ = "student_groups"

    program: Program = Field(primary_key=True, max_length=10)
    student_group_id: int = Field(primary_key=True)
    code: str = Field(max_length=3, description="Zero-padded identifier, e.g. '001'.")
    name: str = Field(max_length=200)
    category: str = Field(max_length=80)
    sort_order: int = Field(default=0)


class GradeLevel(ApiModel, table=True):
    """A grade code used in the research files (*Table B*).

    Includes the aggregate codes: ``13`` (all grades tested), ``14`` (all high
    school) and ``99`` (high school graduating class).
    """

    __tablename__ = "grade_levels"

    code: str = Field(primary_key=True, max_length=2)
    label: str = Field(max_length=80)
    sort_order: int = Field(default=0)
    is_aggregate: bool = Field(default=False)


class Entity(ApiModel, table=True):
    """A state, county, district or school that results are reported for.

    The 14-character CDS code is the natural key used throughout the research
    files: two characters of county, five of district and seven of school, with
    zeroes standing in for the levels that do not apply.
    """

    __tablename__ = "entities"
    __table_args__ = (
        Index("ix_entities_county_code", "county_code"),
        Index("ix_entities_district", "county_code", "district_code"),
        Index("ix_entities_level", "entity_level"),
    )

    cds_code: str = Field(primary_key=True, max_length=14)
    county_code: str = Field(max_length=2)
    district_code: str = Field(max_length=5)
    school_code: str = Field(max_length=7)
    entity_level: EntityLevel = Field(max_length=10)
    type_id: int
    is_charter: bool = Field(default=False)
    charter_funding: CharterFunding | None = Field(default=None, max_length=10)
    county_name: str | None = Field(default=None, max_length=120)
    district_name: str | None = Field(default=None, max_length=120)
    school_name: str | None = Field(default=None, max_length=200)
    zip_code: str | None = Field(default=None, max_length=10)
    display_name: str = Field(max_length=200)
    parent_cds_code: str | None = Field(default=None, max_length=14)
    first_test_year: int | None = Field(default=None)
    last_test_year: int | None = Field(default=None)
