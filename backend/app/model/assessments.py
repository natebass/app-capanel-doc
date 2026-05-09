import uuid
from decimal import Decimal

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlmodel import Field, Relationship, SQLModel


class CaasppBase(SQLModel):
    """
    Base class for CAASPP / CAST / SBAC results (The "Spaces" Group).
    Provides Pydantic configuration and common fields.
    Specific database columns are defined in subclasses to avoid shared Column instance errors.
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class ElpacBase(SQLModel):
    """
    Base class for ELPAC results (The "PascalCase" Group).
    Provides Pydantic configuration and common fields.
    Specific database columns are defined in subclasses to avoid shared Column instance errors.
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class CaasppTest(SQLModel, table=True):
    """CAASPP test lookup: Test ID, Test ID Num, Test Name."""

    __tablename__ = "caaspp_tests"
    test_id: int = Field(primary_key=True)
    test_id_num: int | None = Field(default=None)
    test_name: str | None = Field(default=None, max_length=255)

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ElpacTest(SQLModel, table=True):
    """ELPAC test lookup: Test ID, Test Name."""

    __tablename__ = "elpac_tests"
    test_id: int = Field(primary_key=True)
    test_name: str | None = Field(default=None, max_length=255)

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CaasppStudentGroup(SQLModel, table=True):
    """CAASPP student group lookup: Demographic ID, Demographic ID Num, Demographic Name, Student Group."""

    __tablename__ = "caaspp_student_groups"
    demographic_id: str = Field(primary_key=True, max_length=10)
    demographic_id_num: int | None = Field(default=None)
    demographic_name: str | None = Field(default=None, max_length=255)
    student_group: str | None = Field(default=None, max_length=255)

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ElpacStudentGroup(SQLModel, table=True):
    """ELPAC student group lookup: Student Group ID, Student Group Name."""

    __tablename__ = "elpac_student_groups"
    student_group_id: str = Field(primary_key=True, max_length=10)
    student_group_name: str | None = Field(default=None, max_length=255)

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Entity(SQLModel, table=True):
    __tablename__ = "entities"

    cds_code: str = Field(primary_key=True, max_length=14)

    county_name: str | None = Field(default=None, max_length=25)
    district_name: str | None = Field(default=None, max_length=40)
    school_name: str | None = Field(default=None, max_length=60)

    filler: str | None = Field(default=None, max_length=4)
    zip_code: str | None = Field(default=None, max_length=9)
    type_id: int | None = Field(default=None)

    # Relationships to result tables
    caa_results: list[CaaResult] = Relationship(back_populates="entity")
    caas_results: list[CaasResult] = Relationship(back_populates="entity")
    cast_results: list[CastResult] = Relationship(back_populates="entity")
    csa_results: list[CsaResult] = Relationship(back_populates="entity")
    sb_results: list[SbResult] = Relationship(back_populates="entity")
    ia_elpac_results: list[IaElpacResult] = Relationship(back_populates="entity")
    altia_elpac_results: list[AltiaElpacResult] = Relationship(back_populates="entity")
    sa_elpac_results: list[SaElpacResult] = Relationship(back_populates="entity")
    altsa_elpac_results: list[AltsaElpacResult] = Relationship(back_populates="entity")

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CaaResult(CaasppBase, table=True):
    __tablename__ = "caa_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="Test Year", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="Student Group ID",
        sa_column=Column("student_group_id", String),
    )
    test_id: int = Field(
        validation_alias="Test ID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    test_type: str | None = Field(
        default=None,
        validation_alias="Test Type",
        sa_column=Column("test_type", String(1)),
    )
    type_id: int | None = Field(
        default=None, validation_alias="Type ID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="Total Students Enrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="Total Students Tested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="Total Students Tested with Scores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="Overall Total",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_caa_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["caaspp_student_groups.demographic_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["caaspp_tests.test_id"]),
        Index("ix_caa_results_year_grade", "test_year", "grade"),
        Index("ix_caa_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="caa_results")

    mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="Mean Scale Score",
        sa_column=Column("Mean Scale Score", Numeric(6, 1)),
    )
    count_level_1: int | None = Field(
        default=None,
        validation_alias="Count Level 1",
        sa_column=Column("Count Level 1", Integer),
    )
    count_level_2: int | None = Field(
        default=None,
        validation_alias="Count Level 2",
        sa_column=Column("Count Level 2", Integer),
    )
    count_level_3: int | None = Field(
        default=None,
        validation_alias="Count Level 3",
        sa_column=Column("Count Level 3", Integer),
    )
    percentage_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Level 1",
        sa_column=Column("Percentage Level 1", Numeric(5, 2)),
    )
    percentage_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Level 2",
        sa_column=Column("Percentage Level 2", Numeric(5, 2)),
    )
    percentage_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Level 3",
        sa_column=Column("Percentage Level 3", Numeric(5, 2)),
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class CaasResult(CaasppBase, table=True):
    __tablename__ = "caas_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="Test Year", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="Student Group ID",
        sa_column=Column("student_group_id", String),
    )
    test_id: int = Field(
        validation_alias="Test ID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    test_type: str | None = Field(
        default=None,
        validation_alias="Test Type",
        sa_column=Column("test_type", String(1)),
    )
    type_id: int | None = Field(
        default=None, validation_alias="Type ID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="Total Students Enrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="Total Students Tested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="Total Students Tested with Scores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="Overall Total",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_caas_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["caaspp_student_groups.demographic_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["caaspp_tests.test_id"]),
        Index("ix_caas_results_year_grade", "test_year", "grade"),
        Index("ix_caas_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="caas_results")

    mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="Mean Scale Score",
        sa_column=Column("Mean Scale Score", Numeric(6, 1)),
    )
    count_level_1: int | None = Field(
        default=None,
        validation_alias="Count Level 1",
        sa_column=Column("Count Level 1", Integer),
    )
    count_level_2: int | None = Field(
        default=None,
        validation_alias="Count Level 2",
        sa_column=Column("Count Level 2", Integer),
    )
    count_level_3: int | None = Field(
        default=None,
        validation_alias="Count Level 3",
        sa_column=Column("Count Level 3", Integer),
    )
    percentage_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Level 1",
        sa_column=Column("Percentage Level 1", Numeric(5, 2)),
    )
    percentage_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Level 2",
        sa_column=Column("Percentage Level 2", Numeric(5, 2)),
    )
    percentage_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Level 3",
        sa_column=Column("Percentage Level 3", Numeric(5, 2)),
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class CastResult(CaasppBase, table=True):
    __tablename__ = "cast_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="Test Year", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="Student Group ID",
        sa_column=Column("student_group_id", String),
    )
    test_id: int = Field(
        validation_alias="Test ID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    test_type: str | None = Field(
        default=None,
        validation_alias="Test Type",
        sa_column=Column("test_type", String(1)),
    )
    type_id: int | None = Field(
        default=None, validation_alias="Type ID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="Total Students Enrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="Total Students Tested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="Total Students Tested with Scores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="Overall Total",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_cast_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["caaspp_student_groups.demographic_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["caaspp_tests.test_id"]),
        Index("ix_cast_results_year_grade", "test_year", "grade"),
        Index("ix_cast_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="cast_results")

    mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="Mean Scale Score",
        sa_column=Column("Mean Scale Score", Numeric(6, 1)),
    )
    count_standard_exceeded: int | None = Field(
        default=None,
        validation_alias="Count Standard Exceeded",
        sa_column=Column("Count Standard Exceeded", Integer),
    )
    count_standard_met: int | None = Field(
        default=None,
        validation_alias="Count Standard Met",
        sa_column=Column("Count Standard Met", Integer),
    )
    count_standard_met_and_above: int | None = Field(
        default=None,
        validation_alias="Count Standard Met and Above",
        sa_column=Column("Count Standard Met and Above", Integer),
    )
    count_standard_nearly_met: int | None = Field(
        default=None,
        validation_alias="Count Standard Nearly Met",
        sa_column=Column("Count Standard Nearly Met", Integer),
    )
    count_standard_not_met: int | None = Field(
        default=None,
        validation_alias="Count Standard Not Met",
        sa_column=Column("Count Standard Not Met", Integer),
    )
    percentage_standard_exceeded: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Exceeded",
        sa_column=Column("Percentage Standard Exceeded", Numeric(5, 2)),
    )
    percentage_standard_met: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Met",
        sa_column=Column("Percentage Standard Met", Numeric(5, 2)),
    )
    percentage_standard_met_and_above: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Met and Above",
        sa_column=Column("Percentage Standard Met and Above", Numeric(5, 2)),
    )
    percentage_standard_nearly_met: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Nearly Met",
        sa_column=Column("Percentage Standard Nearly Met", Numeric(5, 2)),
    )
    percentage_standard_not_met: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Not Met",
        sa_column=Column("Percentage Standard Not Met", Numeric(5, 2)),
    )

    earth_and_space_sciences_domain_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Earth and Space Sciences Domain Count Above Standard",
        sa_column=Column(
            "Earth and Space Sciences Domain Count Above Standard", Integer
        ),
    )
    earth_and_space_sciences_domain_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Earth and Space Sciences Domain Count Below Standard",
        sa_column=Column(
            "Earth and Space Sciences Domain Count Below Standard", Integer
        ),
    )
    earth_and_space_sciences_domain_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Earth and Space Sciences Domain Count Near Standard",
        sa_column=Column(
            "Earth and Space Sciences Domain Count Near Standard", Integer
        ),
    )
    earth_and_space_sciences_domain_percent_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Earth and Space Sciences Domain Percent Above Standard",
        sa_column=Column(
            "Earth and Space Sciences Domain Percent Above Standard", Numeric(5, 2)
        ),
    )
    earth_and_space_sciences_domain_percent_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Earth and Space Sciences Domain Percent Below Standard",
        sa_column=Column(
            "Earth and Space Sciences Domain Percent Below Standard", Numeric(5, 2)
        ),
    )
    earth_and_space_sciences_domain_percent_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Earth and Space Sciences Domain Percent Near Standard",
        sa_column=Column(
            "Earth and Space Sciences Domain Percent Near Standard", Numeric(5, 2)
        ),
    )
    earth_and_space_sciences_domain_total: int | None = Field(
        default=None,
        validation_alias="Earth and Space Sciences Domain Total",
        sa_column=Column("Earth and Space Sciences Domain Total", Integer),
    )

    life_sciences_domain_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Life Sciences Domain Count Above Standard",
        sa_column=Column("Life Sciences Domain Count Above Standard", Integer),
    )
    life_sciences_domain_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Life Sciences Domain Count Below Standard",
        sa_column=Column("Life Sciences Domain Count Below Standard", Integer),
    )
    life_sciences_domain_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Life Sciences Domain Count Near Standard",
        sa_column=Column("Life Sciences Domain Count Near Standard", Integer),
    )
    life_sciences_domain_percent_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Life Sciences Domain Percent Above Standard",
        sa_column=Column("Life Sciences Domain Percent Above Standard", Numeric(5, 2)),
    )
    life_sciences_domain_percent_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Life Sciences Domain Percent Below Standard",
        sa_column=Column("Life Sciences Domain Percent Below Standard", Numeric(5, 2)),
    )
    life_sciences_domain_percent_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Life Sciences Domain Percent Near Standard",
        sa_column=Column("Life Sciences Domain Percent Near Standard", Numeric(5, 2)),
    )
    life_sciences_domain_total: int | None = Field(
        default=None,
        validation_alias="Life Sciences Domain Total",
        sa_column=Column("Life Sciences Domain Total", Integer),
    )

    physical_sciences_domain_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Physical Sciences Domain Count Above Standard",
        sa_column=Column("Physical Sciences Domain Count Above Standard", Integer),
    )
    physical_sciences_domain_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Physical Sciences Domain Count Below Standard",
        sa_column=Column("Physical Sciences Domain Count Below Standard", Integer),
    )
    physical_sciences_domain_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Physical Sciences Domain Count Near Standard",
        sa_column=Column("Physical Sciences Domain Count Near Standard", Integer),
    )
    physical_sciences_domain_percent_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Physical Sciences Domain Percent Above Standard",
        sa_column=Column(
            "Physical Sciences Domain Percent Above Standard", Numeric(5, 2)
        ),
    )
    physical_sciences_domain_percent_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Physical Sciences Domain Percent Below Standard",
        sa_column=Column(
            "Physical Sciences Domain Percent Below Standard", Numeric(5, 2)
        ),
    )
    physical_sciences_domain_percent_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Physical Sciences Domain Percent Near Standard",
        sa_column=Column(
            "Physical Sciences Domain Percent Near Standard", Numeric(5, 2)
        ),
    )
    physical_sciences_domain_total: int | None = Field(
        default=None,
        validation_alias="Physical Sciences Domain Total",
        sa_column=Column("Physical Sciences Domain Total", Integer),
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class CsaResult(CaasppBase, table=True):
    __tablename__ = "csa_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="Test Year", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="Student Group ID",
        sa_column=Column("student_group_id", String),
    )
    test_id: int = Field(
        validation_alias="Test ID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    test_type: str | None = Field(
        default=None,
        validation_alias="Test Type",
        sa_column=Column("test_type", String(1)),
    )
    type_id: int | None = Field(
        default=None, validation_alias="Type ID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="Total Students Enrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="Total Students Tested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="Total Students Tested with Scores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="Overall Total",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_csa_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["caaspp_student_groups.demographic_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["caaspp_tests.test_id"]),
        Index("ix_csa_results_year_grade", "test_year", "grade"),
        Index("ix_csa_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="csa_results")

    overall_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="Overall Mean Scale Score",
        sa_column=Column("Overall Mean Scale Score", Numeric(6, 1)),
    )
    count_level_1: int | None = Field(
        default=None,
        validation_alias="Count Level 1",
        sa_column=Column("Count Level 1", Integer),
    )
    count_level_2: int | None = Field(
        default=None,
        validation_alias="Count Level 2",
        sa_column=Column("Count Level 2", Integer),
    )
    count_level_3: int | None = Field(
        default=None,
        validation_alias="Count Level 3",
        sa_column=Column("Count Level 3", Integer),
    )
    percent_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Percent Level 1",
        sa_column=Column("Percent Level 1", Numeric(5, 2)),
    )
    percent_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Percent Level 2",
        sa_column=Column("Percent Level 2", Numeric(5, 2)),
    )
    percent_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Percent Level 3",
        sa_column=Column("Percent Level 3", Numeric(5, 2)),
    )
    composite_1_count_level_1: int | None = Field(
        default=None,
        validation_alias="Composite 1 Count Level 1",
        sa_column=Column("Composite 1 Count Level 1", Integer),
    )
    composite_1_count_level_2: int | None = Field(
        default=None,
        validation_alias="Composite 1 Count Level 2",
        sa_column=Column("Composite 1 Count Level 2", Integer),
    )
    composite_1_count_level_3: int | None = Field(
        default=None,
        validation_alias="Composite 1 Count Level 3",
        sa_column=Column("Composite 1 Count Level 3", Integer),
    )
    composite_1_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="Composite 1 Mean Scale Score",
        sa_column=Column("Composite 1 Mean Scale Score", Numeric(6, 1)),
    )
    composite_1_percent_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Composite 1 Percent Level 1",
        sa_column=Column("Composite 1 Percent Level 1", Numeric(5, 2)),
    )
    composite_1_percent_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Composite 1 Percent Level 2",
        sa_column=Column("Composite 1 Percent Level 2", Numeric(5, 2)),
    )
    composite_1_percent_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Composite 1 Percent Level 3",
        sa_column=Column("Composite 1 Percent Level 3", Numeric(5, 2)),
    )
    composite_1_total: int | None = Field(
        default=None,
        validation_alias="Composite 1 Total",
        sa_column=Column("Composite 1 Total", Integer),
    )
    composite_2_count_level_1: int | None = Field(
        default=None,
        validation_alias="Composite 2 Count Level 1",
        sa_column=Column("Composite 2 Count Level 1", Integer),
    )
    composite_2_count_level_2: int | None = Field(
        default=None,
        validation_alias="Composite 2 Count Level 2",
        sa_column=Column("Composite 2 Count Level 2", Integer),
    )
    composite_2_count_level_3: int | None = Field(
        default=None,
        validation_alias="Composite 2 Count Level 3",
        sa_column=Column("Composite 2 Count Level 3", Integer),
    )
    composite_2_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="Composite 2 Mean Scale Score",
        sa_column=Column("Composite 2 Mean Scale Score", Numeric(6, 1)),
    )
    composite_2_percent_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Composite 2 Percent Level 1",
        sa_column=Column("Composite 2 Percent Level 1", Numeric(5, 2)),
    )
    composite_2_percent_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Composite 2 Percent Level 2",
        sa_column=Column("Composite 2 Percent Level 2", Numeric(5, 2)),
    )
    composite_2_percent_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Composite 2 Percent Level 3",
        sa_column=Column("Composite 2 Percent Level 3", Numeric(5, 2)),
    )
    composite_2_total: int | None = Field(
        default=None,
        validation_alias="Composite 2 Total",
        sa_column=Column("Composite 2 Total", Integer),
    )
    listening_domain_count_level_1: int | None = Field(
        default=None,
        validation_alias="Listening Domain Count Level 1",
        sa_column=Column("Listening Domain Count Level 1", Integer),
    )
    listening_domain_count_level_2: int | None = Field(
        default=None,
        validation_alias="Listening Domain Count Level 2",
        sa_column=Column("Listening Domain Count Level 2", Integer),
    )
    listening_domain_count_level_3: int | None = Field(
        default=None,
        validation_alias="Listening Domain Count Level 3",
        sa_column=Column("Listening Domain Count Level 3", Integer),
    )
    listening_domain_percent_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Listening Domain Percent Level 1",
        sa_column=Column("Listening Domain Percent Level 1", Numeric(5, 2)),
    )
    listening_domain_percent_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Listening Domain Percent Level 2",
        sa_column=Column("Listening Domain Percent Level 2", Numeric(5, 2)),
    )
    listening_domain_percent_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Listening Domain Percent Level 3",
        sa_column=Column("Listening Domain Percent Level 3", Numeric(5, 2)),
    )
    listening_domain_total: int | None = Field(
        default=None,
        validation_alias="Listening Domain Total",
        sa_column=Column("Listening Domain Total", Integer),
    )
    reading_domain_count_level_1: int | None = Field(
        default=None,
        validation_alias="Reading Domain Count Level 1",
        sa_column=Column("Reading Domain Count Level 1", Integer),
    )
    reading_domain_count_level_2: int | None = Field(
        default=None,
        validation_alias="Reading Domain Count Level 2",
        sa_column=Column("Reading Domain Count Level 2", Integer),
    )
    reading_domain_count_level_3: int | None = Field(
        default=None,
        validation_alias="Reading Domain Count Level 3",
        sa_column=Column("Reading Domain Count Level 3", Integer),
    )
    reading_domain_percent_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Reading Domain Percent Level 1",
        sa_column=Column("Reading Domain Percent Level 1", Numeric(5, 2)),
    )
    reading_domain_percent_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Reading Domain Percent Level 2",
        sa_column=Column("Reading Domain Percent Level 2", Numeric(5, 2)),
    )
    reading_domain_percent_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Reading Domain Percent Level 3",
        sa_column=Column("Reading Domain Percent Level 3", Numeric(5, 2)),
    )
    reading_domain_total: int | None = Field(
        default=None,
        validation_alias="Reading Domain Total",
        sa_column=Column("Reading Domain Total", Integer),
    )
    speaking_domain_count_level_1: int | None = Field(
        default=None,
        validation_alias="Speaking Domain Count Level 1",
        sa_column=Column("Speaking Domain Count Level 1", Integer),
    )
    speaking_domain_count_level_2: int | None = Field(
        default=None,
        validation_alias="Speaking Domain Count Level 2",
        sa_column=Column("Speaking Domain Count Level 2", Integer),
    )
    speaking_domain_count_level_3: int | None = Field(
        default=None,
        validation_alias="Speaking Domain Count Level 3",
        sa_column=Column("Speaking Domain Count Level 3", Integer),
    )
    speaking_domain_percent_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Speaking Domain Percent Level 1",
        sa_column=Column("Speaking Domain Percent Level 1", Numeric(5, 2)),
    )
    speaking_domain_percent_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Speaking Domain Percent Level 2",
        sa_column=Column("Speaking Domain Percent Level 2", Numeric(5, 2)),
    )
    speaking_domain_percent_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Speaking Domain Percent Level 3",
        sa_column=Column("Speaking Domain Percent Level 3", Numeric(5, 2)),
    )
    speaking_domain_total: int | None = Field(
        default=None,
        validation_alias="Speaking Domain Total",
        sa_column=Column("Speaking Domain Total", Integer),
    )
    writing_domain_count_level_1: int | None = Field(
        default=None,
        validation_alias="Writing Domain Count Level 1",
        sa_column=Column("Writing Domain Count Level 1", Integer),
    )
    writing_domain_count_level_2: int | None = Field(
        default=None,
        validation_alias="Writing Domain Count Level 2",
        sa_column=Column("Writing Domain Count Level 2", Integer),
    )
    writing_domain_count_level_3: int | None = Field(
        default=None,
        validation_alias="Writing Domain Count Level 3",
        sa_column=Column("Writing Domain Count Level 3", Integer),
    )
    writing_domain_percent_level_1: Decimal | None = Field(
        default=None,
        validation_alias="Writing Domain Percent Level 1",
        sa_column=Column("Writing Domain Percent Level 1", Numeric(5, 2)),
    )
    writing_domain_percent_level_2: Decimal | None = Field(
        default=None,
        validation_alias="Writing Domain Percent Level 2",
        sa_column=Column("Writing Domain Percent Level 2", Numeric(5, 2)),
    )
    writing_domain_percent_level_3: Decimal | None = Field(
        default=None,
        validation_alias="Writing Domain Percent Level 3",
        sa_column=Column("Writing Domain Percent Level 3", Numeric(5, 2)),
    )
    writing_domain_total: int | None = Field(
        default=None,
        validation_alias="Writing Domain Total",
        sa_column=Column("Writing Domain Total", Integer),
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class SbResult(CaasppBase, table=True):
    __tablename__ = "sb_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="Test Year", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="Student Group ID",
        sa_column=Column("student_group_id", String),
    )
    test_id: int = Field(
        validation_alias="Test ID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    test_type: str | None = Field(
        default=None,
        validation_alias="Test Type",
        sa_column=Column("test_type", String(1)),
    )
    type_id: int | None = Field(
        default=None, validation_alias="Type ID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="Total Students Enrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="Total Students Tested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="Total Students Tested with Scores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="Overall Total",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_sb_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["caaspp_student_groups.demographic_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["caaspp_tests.test_id"]),
        Index("ix_sb_results_year_grade", "test_year", "grade"),
        Index("ix_sb_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="sb_results")

    mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="Mean Scale Score",
        sa_column=Column("Mean Scale Score", Numeric(6, 1)),
    )
    count_standard_exceeded: int | None = Field(
        default=None,
        validation_alias="Count Standard Exceeded",
        sa_column=Column("Count Standard Exceeded", Integer),
    )
    count_standard_met: int | None = Field(
        default=None,
        validation_alias="Count Standard Met",
        sa_column=Column("Count Standard Met", Integer),
    )
    count_standard_met_and_above: int | None = Field(
        default=None,
        validation_alias="Count Standard Met and Above",
        sa_column=Column("Count Standard Met and Above", Integer),
    )
    count_standard_nearly_met: int | None = Field(
        default=None,
        validation_alias="Count Standard Nearly Met",
        sa_column=Column("Count Standard Nearly Met", Integer),
    )
    count_standard_not_met: int | None = Field(
        default=None,
        validation_alias="Count Standard Not Met",
        sa_column=Column("Count Standard Not Met", Integer),
    )
    percentage_standard_exceeded: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Exceeded",
        sa_column=Column("Percentage Standard Exceeded", Numeric(5, 2)),
    )
    percentage_standard_met: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Met",
        sa_column=Column("Percentage Standard Met", Numeric(5, 2)),
    )
    percentage_standard_met_and_above: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Met and Above",
        sa_column=Column("Percentage Standard Met and Above", Numeric(5, 2)),
    )
    percentage_standard_nearly_met: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Nearly Met",
        sa_column=Column("Percentage Standard Nearly Met", Numeric(5, 2)),
    )
    percentage_standard_not_met: Decimal | None = Field(
        default=None,
        validation_alias="Percentage Standard Not Met",
        sa_column=Column("Percentage Standard Not Met", Numeric(5, 2)),
    )
    area_1_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Area 1 Count Above Standard",
        sa_column=Column("Area 1 Count Above Standard", Integer),
    )
    area_1_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Area 1 Count Below Standard",
        sa_column=Column("Area 1 Count Below Standard", Integer),
    )
    area_1_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Area 1 Count Near Standard",
        sa_column=Column("Area 1 Count Near Standard", Integer),
    )
    area_1_percentage_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 1 Percentage Above Standard",
        sa_column=Column("Area 1 Percentage Above Standard", Numeric(5, 2)),
    )
    area_1_percentage_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 1 Percentage Below Standard",
        sa_column=Column("Area 1 Percentage Below Standard", Numeric(5, 2)),
    )
    area_1_percentage_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 1 Percentage Near Standard",
        sa_column=Column("Area 1 Percentage Near Standard", Numeric(5, 2)),
    )
    area_1_total: int | None = Field(
        default=None,
        validation_alias="Area 1 Total",
        sa_column=Column("Area 1 Total", Integer),
    )
    area_2_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Area 2 Count Above Standard",
        sa_column=Column("Area 2 Count Above Standard", Integer),
    )
    area_2_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Area 2 Count Below Standard",
        sa_column=Column("Area 2 Count Below Standard", Integer),
    )
    area_2_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Area 2 Count Near Standard",
        sa_column=Column("Area 2 Count Near Standard", Integer),
    )
    area_2_percentage_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 2 Percentage Above Standard",
        sa_column=Column("Area 2 Percentage Above Standard", Numeric(5, 2)),
    )
    area_2_percentage_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 2 Percentage Below Standard",
        sa_column=Column("Area 2 Percentage Below Standard", Numeric(5, 2)),
    )
    area_2_percentage_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 2 Percentage Near Standard",
        sa_column=Column("Area 2 Percentage Near Standard", Numeric(5, 2)),
    )
    area_2_total: int | None = Field(
        default=None,
        validation_alias="Area 2 Total",
        sa_column=Column("Area 2 Total", Integer),
    )
    area_3_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Area 3 Count Above Standard",
        sa_column=Column("Area 3 Count Above Standard", Integer),
    )
    area_3_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Area 3 Count Below Standard",
        sa_column=Column("Area 3 Count Below Standard", Integer),
    )
    area_3_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Area 3 Count Near Standard",
        sa_column=Column("Area 3 Count Near Standard", Integer),
    )
    area_3_percentage_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 3 Percentage Above Standard",
        sa_column=Column("Area 3 Percentage Above Standard", Numeric(5, 2)),
    )
    area_3_percentage_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 3 Percentage Below Standard",
        sa_column=Column("Area 3 Percentage Below Standard", Numeric(5, 2)),
    )
    area_3_percentage_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 3 Percentage Near Standard",
        sa_column=Column("Area 3 Percentage Near Standard", Numeric(5, 2)),
    )
    area_3_total: int | None = Field(
        default=None,
        validation_alias="Area 3 Total",
        sa_column=Column("Area 3 Total", Integer),
    )
    area_4_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Area 4 Count Above Standard",
        sa_column=Column("Area 4 Count Above Standard", Integer),
    )
    area_4_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Area 4 Count Below Standard",
        sa_column=Column("Area 4 Count Below Standard", Integer),
    )
    area_4_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Area 4 Count Near Standard",
        sa_column=Column("Area 4 Count Near Standard", Integer),
    )
    area_4_percentage_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 4 Percentage Above Standard",
        sa_column=Column("Area 4 Percentage Above Standard", Numeric(5, 2)),
    )
    area_4_percentage_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 4 Percentage Below Standard",
        sa_column=Column("Area 4 Percentage Below Standard", Numeric(5, 2)),
    )
    area_4_percentage_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Area 4 Percentage Near Standard",
        sa_column=Column("Area 4 Percentage Near Standard", Numeric(5, 2)),
    )
    area_4_total: int | None = Field(
        default=None,
        validation_alias="Area 4 Total",
        sa_column=Column("Area 4 Total", Integer),
    )
    composite_area_1_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Composite Area 1 Count Above Standard",
        sa_column=Column("Composite Area 1 Count Above Standard", Integer),
    )
    composite_area_1_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Composite Area 1 Count Below Standard",
        sa_column=Column("Composite Area 1 Count Below Standard", Integer),
    )
    composite_area_1_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Composite Area 1 Count Near Standard",
        sa_column=Column("Composite Area 1 Count Near Standard", Integer),
    )
    composite_area_1_percentage_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Composite Area 1 Percentage Above Standard",
        sa_column=Column("Composite Area 1 Percentage Above Standard", Numeric(5, 2)),
    )
    composite_area_1_percentage_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Composite Area 1 Percentage Below Standard",
        sa_column=Column("Composite Area 1 Percentage Below Standard", Numeric(5, 2)),
    )
    composite_area_1_percentage_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Composite Area 1 Percentage Near Standard",
        sa_column=Column("Composite Area 1 Percentage Near Standard", Numeric(5, 2)),
    )
    composite_area_1_total: int | None = Field(
        default=None,
        validation_alias="Composite Area 1 Total",
        sa_column=Column("Composite Area 1 Total", Integer),
    )
    composite_area_2_count_above_standard: int | None = Field(
        default=None,
        validation_alias="Composite Area 2 Count Above Standard",
        sa_column=Column("Composite Area 2 Count Above Standard", Integer),
    )
    composite_area_2_count_below_standard: int | None = Field(
        default=None,
        validation_alias="Composite Area 2 Count Below Standard",
        sa_column=Column("Composite Area 2 Count Below Standard", Integer),
    )
    composite_area_2_count_near_standard: int | None = Field(
        default=None,
        validation_alias="Composite Area 2 Count Near Standard",
        sa_column=Column("Composite Area 2 Count Near Standard", Integer),
    )
    composite_area_2_percentage_above_standard: Decimal | None = Field(
        default=None,
        validation_alias="Composite Area 2 Percentage Above Standard",
        sa_column=Column("Composite Area 2 Percentage Above Standard", Numeric(5, 2)),
    )
    composite_area_2_percentage_below_standard: Decimal | None = Field(
        default=None,
        validation_alias="Composite Area 2 Percentage Below Standard",
        sa_column=Column("Composite Area 2 Percentage Below Standard", Numeric(5, 2)),
    )
    composite_area_2_percentage_near_standard: Decimal | None = Field(
        default=None,
        validation_alias="Composite Area 2 Percentage Near Standard",
        sa_column=Column("Composite Area 2 Percentage Near Standard", Numeric(5, 2)),
    )
    composite_area_2_total: int | None = Field(
        default=None,
        validation_alias="Composite Area 2 Total",
        sa_column=Column("Composite Area 2 Total", Integer),
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class IaElpacResult(ElpacBase, table=True):
    __tablename__ = "ia_elpac_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="TestYear", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="StudentGroupID", sa_column=Column("student_group_id", String)
    )
    test_id: int = Field(
        validation_alias="TestID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    type_id: int | None = Field(
        default=None, validation_alias="TypeID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="TotalStudentsEnrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="TotalStudentsTested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="TotalStudentsTestedWithScores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="OverallTotal",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_ia_elpac_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["elpac_student_groups.student_group_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["elpac_tests.test_id"]),
        Index("ix_ia_elpac_results_year_grade", "test_year", "grade"),
        Index("ix_ia_elpac_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="ia_elpac_results")

    overall_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="OverallMeanSclScr",
        sa_column=Column("OverallMeanSclScr", Numeric(6, 1)),
    )
    novice_el_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="NoviceELPerfLvlPcnt",
        sa_column=Column("NoviceELPerfLvlPcnt", Numeric(5, 2)),
    )
    novice_el_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="NoviceELPerfLvlCount",
        sa_column=Column("NoviceELPerfLvlCount", Integer),
    )
    intermediate_el_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="IntermediateELPerfLvlPcnt",
        sa_column=Column("IntermediateELPerfLvlPcnt", Numeric(5, 2)),
    )
    intermediate_el_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="IntermediateELPerfLvlCount",
        sa_column=Column("IntermediateELPerfLvlCount", Integer),
    )
    ifep_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="IFEPPerfLvlPcnt",
        sa_column=Column("IFEPPerfLvlPcnt", Numeric(5, 2)),
    )
    ifep_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="IFEPPerfLvlCount",
        sa_column=Column("IFEPPerfLvlCount", Integer),
    )
    overall_total: int | None = Field(default=None)
    oral_lang_minimally_developed_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="OralLangMinimallyDevelopedPerfLvlPcnt",
        sa_column=Column("OralLangMinimallyDevelopedPerfLvlPcnt", Numeric(5, 2)),
    )
    oral_lang_minimally_developed_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="OralLangMinimallyDevelopedPerfLvlCount",
        sa_column=Column("OralLangMinimallyDevelopedPerfLvlCount", Integer),
    )
    oral_lang_moderately_developed_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="OralLangModeratelyDevelopedPerfLvlPcnt",
        sa_column=Column("OralLangModeratelyDevelopedPerfLvlPcnt", Numeric(5, 2)),
    )
    oral_lang_moderately_developed_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="OralLangModeratelyDevelopedPerfLvlCount",
        sa_column=Column("OralLangModeratelyDevelopedPerfLvlCount", Integer),
    )
    oral_lang_well_developed_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="OralLangWellDevelopedPerfLvlPcnt",
        sa_column=Column("OralLangWellDevelopedPerfLvlPcnt", Numeric(5, 2)),
    )
    oral_lang_well_developed_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="OralLangWellDevelopedPerfLvlCount",
        sa_column=Column("OralLangWellDevelopedPerfLvlCount", Integer),
    )
    oral_lang_total: int | None = Field(
        default=None,
        validation_alias="OralLangTotal",
        sa_column=Column("OralLangTotal", Integer),
    )
    writ_lang_minimally_developed_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="WritLangMinimallyDevelopedPerfLvlPcnt",
        sa_column=Column("WritLangMinimallyDevelopedPerfLvlPcnt", Numeric(5, 2)),
    )
    writ_lang_minimally_developed_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="WritLangMinimallyDevelopedPerfLvlCount",
        sa_column=Column("WritLangMinimallyDevelopedPerfLvlCount", Integer),
    )
    writ_lang_moderately_developed_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="WritLangModeratelyDevelopedPerfLvlPcnt",
        sa_column=Column("WritLangModeratelyDevelopedPerfLvlPcnt", Numeric(5, 2)),
    )
    writ_lang_moderately_developed_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="WritLangModeratelyDevelopedPerfLvlCount",
        sa_column=Column("WritLangModeratelyDevelopedPerfLvlCount", Integer),
    )
    writ_lang_well_developed_perf_lvl_pcnt: Decimal | None = Field(
        default=None,
        validation_alias="WritLangWellDevelopedPerfLvlPcnt",
        sa_column=Column("WritLangWellDevelopedPerfLvlPcnt", Numeric(5, 2)),
    )
    writ_lang_well_developed_perf_lvl_count: int | None = Field(
        default=None,
        validation_alias="WritLangWellDevelopedPerfLvlCount",
        sa_column=Column("WritLangWellDevelopedPerfLvlCount", Integer),
    )
    writ_lang_total: int | None = Field(
        default=None,
        validation_alias="WritLangTotal",
        sa_column=Column("WritLangTotal", Integer),
    )
    listening_domain_begin_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    listening_domain_begin_count: int | None = Field(default=None)
    listening_domain_moderate_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    listening_domain_moderate_count: int | None = Field(default=None)
    listening_domain_developed_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    listening_domain_developed_count: int | None = Field(default=None)
    listening_domain_total: int | None = Field(default=None)
    speaking_domain_begin_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    speaking_domain_begin_count: int | None = Field(default=None)
    speaking_domain_moderate_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    speaking_domain_moderate_count: int | None = Field(default=None)
    speaking_domain_developed_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    speaking_domain_developed_count: int | None = Field(default=None)
    speaking_domain_total: int | None = Field(default=None)
    reading_domain_begin_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    reading_domain_begin_count: int | None = Field(default=None)
    reading_domain_moderate_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    reading_domain_moderate_count: int | None = Field(default=None)
    reading_domain_developed_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    reading_domain_developed_count: int | None = Field(default=None)
    reading_domain_total: int | None = Field(default=None)
    writing_domain_begin_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    writing_domain_begin_count: int | None = Field(default=None)
    writing_domain_moderate_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    writing_domain_moderate_count: int | None = Field(default=None)
    writing_domain_developed_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    writing_domain_developed_count: int | None = Field(default=None)
    writing_domain_total: int | None = Field(default=None)

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class AltiaElpacResult(ElpacBase, table=True):
    __tablename__ = "altia_elpac_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="TestYear", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="StudentGroupID", sa_column=Column("student_group_id", String)
    )
    test_id: int = Field(
        validation_alias="TestID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    type_id: int | None = Field(
        default=None, validation_alias="TypeID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="TotalStudentsEnrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="TotalStudentsTested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="TotalStudentsTestedWithScores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="OverallTotal",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_altia_elpac_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["elpac_student_groups.student_group_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["elpac_tests.test_id"]),
        Index("ix_altia_elpac_results_year_grade", "test_year", "grade"),
        Index("ix_altia_elpac_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="altia_elpac_results")

    overall_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="OverallMeanScaleScore",
        sa_column=Column("OverallMeanScaleScore", Numeric(6, 1)),
    )
    overall_perf_lvl_pcnt_1: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl1Pcnt",
        sa_column=Column("OverallPerfLvl1Pcnt", Numeric(5, 2)),
    )
    overall_perf_lvl_count_1: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl1Count",
        sa_column=Column("OverallPerfLvl1Count", Integer),
    )
    overall_perf_lvl_pcnt_2: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl2Pcnt",
        sa_column=Column("OverallPerfLvl2Pcnt", Numeric(5, 2)),
    )
    overall_perf_lvl_count_2: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl2Count",
        sa_column=Column("OverallPerfLvl2Count", Integer),
    )
    overall_perf_lvl_pcnt_3: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl3Pcnt",
        sa_column=Column("OverallPerfLvl3Pcnt", Numeric(5, 2)),
    )
    overall_perf_lvl_count_3: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl3Count",
        sa_column=Column("OverallPerfLvl3Count", Integer),
    )
    overall_perf_lvl_pcnt_4: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl4Pcnt",
        sa_column=Column("OverallPerfLvl4Pcnt", Numeric(5, 2)),
    )
    overall_perf_lvl_count_4: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl4Count",
        sa_column=Column("OverallPerfLvl4Count", Integer),
    )
    overall_total: int | None = Field(default=None)

    oral_lang_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="OralLangMeanScaleScore",
        sa_column=Column("OralLangMeanScaleScore", Numeric(6, 1)),
    )
    oral_lang_perf_lvl_pcnt_1: Decimal | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl1Pcnt",
        sa_column=Column("OralLangPerfLvl1Pcnt", Numeric(5, 2)),
    )
    oral_lang_perf_lvl_count_1: int | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl1Count",
        sa_column=Column("OralLangPerfLvl1Count", Integer),
    )
    oral_lang_perf_lvl_pcnt_2: Decimal | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl2Pcnt",
        sa_column=Column("OralLangPerfLvl2Pcnt", Numeric(5, 2)),
    )
    oral_lang_perf_lvl_count_2: int | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl2Count",
        sa_column=Column("OralLangPerfLvl2Count", Integer),
    )
    oral_lang_perf_lvl_pcnt_3: Decimal | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl3Pcnt",
        sa_column=Column("OralLangPerfLvl3Pcnt", Numeric(5, 2)),
    )
    oral_lang_perf_lvl_count_3: int | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl3Count",
        sa_column=Column("OralLangPerfLvl3Count", Integer),
    )
    oral_lang_perf_lvl_pcnt_4: Decimal | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl4Pcnt",
        sa_column=Column("OralLangPerfLvl4Pcnt", Numeric(5, 2)),
    )
    oral_lang_perf_lvl_count_4: int | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl4Count",
        sa_column=Column("OralLangPerfLvl4Count", Integer),
    )
    oral_lang_total: int | None = Field(
        default=None,
        validation_alias="OralLangTotal",
        sa_column=Column("OralLangTotal", Integer),
    )

    writ_lang_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="WritLangMeanScaleScore",
        sa_column=Column("WritLangMeanScaleScore", Numeric(6, 1)),
    )
    writ_lang_perf_lvl_pcnt_1: Decimal | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl1Pcnt",
        sa_column=Column("WritLangPerfLvl1Pcnt", Numeric(5, 2)),
    )
    writ_lang_perf_lvl_count_1: int | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl1Count",
        sa_column=Column("WritLangPerfLvl1Count", Integer),
    )
    writ_lang_perf_lvl_pcnt_2: Decimal | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl2Pcnt",
        sa_column=Column("WritLangPerfLvl2Pcnt", Numeric(5, 2)),
    )
    writ_lang_perf_lvl_count_2: int | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl2Count",
        sa_column=Column("WritLangPerfLvl2Count", Integer),
    )
    writ_lang_perf_lvl_pcnt_3: Decimal | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl3Pcnt",
        sa_column=Column("WritLangPerfLvl3Pcnt", Numeric(5, 2)),
    )
    writ_lang_perf_lvl_count_3: int | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl3Count",
        sa_column=Column("WritLangPerfLvl3Count", Integer),
    )
    writ_lang_perf_lvl_pcnt_4: Decimal | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl4Pcnt",
        sa_column=Column("WritLangPerfLvl4Pcnt", Numeric(5, 2)),
    )
    writ_lang_perf_lvl_count_4: int | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl4Count",
        sa_column=Column("WritLangPerfLvl4Count", Integer),
    )
    writ_lang_total: int | None = Field(
        default=None,
        validation_alias="WritLangTotal",
        sa_column=Column("WritLangTotal", Integer),
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class SaElpacResult(ElpacBase, table=True):
    __tablename__ = "sa_elpac_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="TestYear", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="StudentGroupID", sa_column=Column("student_group_id", String)
    )
    test_id: int = Field(
        validation_alias="TestID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    type_id: int | None = Field(
        default=None, validation_alias="TypeID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="TotalStudentsEnrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="TotalStudentsTested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="TotalStudentsTestedWithScores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="OverallTotal",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_sa_elpac_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["elpac_student_groups.student_group_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["elpac_tests.test_id"]),
        Index("ix_sa_elpac_results_year_grade", "test_year", "grade"),
        Index("ix_sa_elpac_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="sa_elpac_results")

    overall_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="OverallMeanScaleScore",
        sa_column=Column("OverallMeanScaleScore", Numeric(6, 1)),
    )
    overall_perf_lvl_pcnt_1: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl1Pcnt",
        sa_column=Column("OverallPerfLvl1Pcnt", Numeric(5, 2)),
    )
    overall_perf_lvl_count_1: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl1Count",
        sa_column=Column("OverallPerfLvl1Count", Integer),
    )
    overall_perf_lvl_pcnt_2: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl2Pcnt",
        sa_column=Column("OverallPerfLvl2Pcnt", Numeric(5, 2)),
    )
    overall_perf_lvl_count_2: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl2Count",
        sa_column=Column("OverallPerfLvl2Count", Integer),
    )
    overall_perf_lvl_pcnt_3: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl3Pcnt",
        sa_column=Column("OverallPerfLvl3Pcnt", Numeric(5, 2)),
    )
    overall_perf_lvl_count_3: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl3Count",
        sa_column=Column("OverallPerfLvl3Count", Integer),
    )
    overall_perf_lvl_pcnt_4: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl4Pcnt",
        sa_column=Column("OverallPerfLvl4Pcnt", Numeric(5, 2)),
    )
    overall_perf_lvl_count_4: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl4Count",
        sa_column=Column("OverallPerfLvl4Count", Integer),
    )

    oral_lang_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="OralLangMeanScaleScore",
        sa_column=Column("OralLangMeanScaleScore", Numeric(6, 1)),
    )
    oral_lang_perf_lvl_count_1: int | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl1Count",
        sa_column=Column("OralLangPerfLvl1Count", Integer),
    )
    oral_lang_perf_lvl_pcnt_1: Decimal | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl1Pcnt",
        sa_column=Column("OralLangPerfLvl1Pcnt", Numeric(5, 2)),
    )
    oral_lang_perf_lvl_count_2: int | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl2Count",
        sa_column=Column("OralLangPerfLvl2Count", Integer),
    )
    oral_lang_perf_lvl_pcnt_2: Decimal | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl2Pcnt",
        sa_column=Column("OralLangPerfLvl2Pcnt", Numeric(5, 2)),
    )
    oral_lang_perf_lvl_count_3: int | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl3Count",
        sa_column=Column("OralLangPerfLvl3Count", Integer),
    )
    oral_lang_perf_lvl_pcnt_3: Decimal | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl3Pcnt",
        sa_column=Column("OralLangPerfLvl3Pcnt", Numeric(5, 2)),
    )
    oral_lang_perf_lvl_count_4: int | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl4Count",
        sa_column=Column("OralLangPerfLvl4Count", Integer),
    )
    oral_lang_perf_lvl_pcnt_4: Decimal | None = Field(
        default=None,
        validation_alias="OralLangPerfLvl4Pcnt",
        sa_column=Column("OralLangPerfLvl4Pcnt", Numeric(5, 2)),
    )
    oral_lang_total: int | None = Field(
        default=None,
        validation_alias="OralLangTotal",
        sa_column=Column("OralLangTotal", Integer),
    )

    writ_lang_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="WritLangMeanScaleScore",
        sa_column=Column("WritLangMeanScaleScore", Numeric(6, 1)),
    )
    writ_lang_perf_lvl_count_1: int | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl1Count",
        sa_column=Column("WritLangPerfLvl1Count", Integer),
    )
    writ_lang_perf_lvl_pcnt_1: Decimal | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl1Pcnt",
        sa_column=Column("WritLangPerfLvl1Pcnt", Numeric(5, 2)),
    )
    writ_lang_perf_lvl_count_2: int | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl2Count",
        sa_column=Column("WritLangPerfLvl2Count", Integer),
    )
    writ_lang_perf_lvl_pcnt_2: Decimal | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl2Pcnt",
        sa_column=Column("WritLangPerfLvl2Pcnt", Numeric(5, 2)),
    )
    writ_lang_perf_lvl_count_3: int | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl3Count",
        sa_column=Column("WritLangPerfLvl3Count", Integer),
    )
    writ_lang_perf_lvl_pcnt_3: Decimal | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl3Pcnt",
        sa_column=Column("WritLangPerfLvl3Pcnt", Numeric(5, 2)),
    )
    writ_lang_perf_lvl_count_4: int | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl4Count",
        sa_column=Column("WritLangPerfLvl4Count", Integer),
    )
    writ_lang_perf_lvl_pcnt_4: Decimal | None = Field(
        default=None,
        validation_alias="WritLangPerfLvl4Pcnt",
        sa_column=Column("WritLangPerfLvl4Pcnt", Numeric(5, 2)),
    )
    writ_lang_total: int | None = Field(
        default=None,
        validation_alias="WritLangTotal",
        sa_column=Column("WritLangTotal", Integer),
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )
    listening_domain_begin_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    listening_domain_begin_count: int | None = Field(default=None)
    listening_domain_moderate_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    listening_domain_moderate_count: int | None = Field(default=None)
    listening_domain_developed_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    listening_domain_developed_count: int | None = Field(default=None)
    listening_domain_total: int | None = Field(default=None)
    speaking_domain_begin_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    speaking_domain_begin_count: int | None = Field(default=None)
    speaking_domain_moderate_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    speaking_domain_moderate_count: int | None = Field(default=None)
    speaking_domain_developed_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    speaking_domain_developed_count: int | None = Field(default=None)
    speaking_domain_total: int | None = Field(default=None)
    reading_domain_begin_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    reading_domain_begin_count: int | None = Field(default=None)
    reading_domain_moderate_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    reading_domain_moderate_count: int | None = Field(default=None)
    reading_domain_developed_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    reading_domain_developed_count: int | None = Field(default=None)
    reading_domain_total: int | None = Field(default=None)
    writing_domain_begin_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    writing_domain_begin_count: int | None = Field(default=None)
    writing_domain_moderate_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    writing_domain_moderate_count: int | None = Field(default=None)
    writing_domain_developed_pcnt: Decimal | None = Field(
        default=None, max_digits=5, decimal_places=2
    )
    writing_domain_developed_count: int | None = Field(default=None)
    writing_domain_total: int | None = Field(default=None)

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AltsaElpacResult(ElpacBase, table=True):
    __tablename__ = "altsa_elpac_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Composite natural key for unique constraint
    cds_code: str = Field(
        validation_alias="CDSCode", sa_column=Column("cds_code", String(14))
    )
    test_year: int = Field(
        validation_alias="TestYear", sa_column=Column("test_year", Integer)
    )
    student_group_id: str = Field(
        validation_alias="StudentGroupID", sa_column=Column("student_group_id", String)
    )
    test_id: int = Field(
        validation_alias="TestID", sa_column=Column("test_id", Integer)
    )
    grade: str = Field(validation_alias="Grade", sa_column=Column("grade", String(2)))

    # Common result fields (normalized)
    filler: str | None = Field(
        default=None, validation_alias="Filler", sa_column=Column("filler", String(4))
    )
    type_id: int | None = Field(
        default=None, validation_alias="TypeID", sa_column=Column("type_id", Integer)
    )
    total_students_enrolled: int | None = Field(
        default=None,
        validation_alias="TotalStudentsEnrolled",
        sa_column=Column("total_students_enrolled", Integer),
    )
    total_students_tested: int | None = Field(
        default=None,
        validation_alias="TotalStudentsTested",
        sa_column=Column("total_students_tested", Integer),
    )
    total_students_tested_with_scores: int | None = Field(
        default=None,
        validation_alias="TotalStudentsTestedWithScores",
        sa_column=Column("total_students_tested_with_scores", Integer),
    )
    overall_total: int | None = Field(
        default=None,
        validation_alias="OverallTotal",
        sa_column=Column("overall_total", Integer),
    )

    __table_args__ = (
        UniqueConstraint(
            "cds_code",
            "test_year",
            "student_group_id",
            "test_id",
            "grade",
            name="ix_altsa_elpac_results_natural_key",
        ),
        ForeignKeyConstraint(["cds_code"], ["entities.cds_code"]),
        ForeignKeyConstraint(
            ["student_group_id"], ["elpac_student_groups.student_group_id"]
        ),
        ForeignKeyConstraint(["test_id"], ["elpac_tests.test_id"]),
        Index("ix_altsa_elpac_results_year_grade", "test_year", "grade"),
        Index("ix_altsa_elpac_results_student_group", "student_group_id"),
    )

    entity: Entity = Relationship(back_populates="altsa_elpac_results")
    overall_mean_scale_score: Decimal | None = Field(
        default=None,
        validation_alias="OverallMeanScaleScore",
        sa_column=Column("OverallMeanScaleScore", Numeric(6, 1)),
    )
    overall_perf_lvl_pcnt_1: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl1Pcnt",
        sa_column=Column("OverallPerfLvl1Pcnt", Numeric(5, 2)),
    )
    count_level_1: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl1Count",
        sa_column=Column("OverallPerfLvl1Count", Integer),
    )
    overall_perf_lvl_pcnt_2: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl2Pcnt",
        sa_column=Column("OverallPerfLvl2Pcnt", Numeric(5, 2)),
    )
    count_level_2: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl2Count",
        sa_column=Column("OverallPerfLvl2Count", Integer),
    )
    overall_perf_lvl_pcnt_3: Decimal | None = Field(
        default=None,
        validation_alias="OverallPerfLvl3Pcnt",
        sa_column=Column("OverallPerfLvl3Pcnt", Numeric(5, 2)),
    )
    count_level_3: int | None = Field(
        default=None,
        validation_alias="OverallPerfLvl3Count",
        sa_column=Column("OverallPerfLvl3Count", Integer),
    )

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )
