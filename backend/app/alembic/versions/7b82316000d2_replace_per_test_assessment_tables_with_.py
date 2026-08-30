"""Replace per-test assessment tables with the CAASPP and ELPAC reporting model

The previous schema gave every test its own wide table, so the shape of a query
depended on which assessment it asked about and adding a test meant adding a
table.  This revision replaces all of them with the model the state's own
reporting uses: year-scoped reference tables for the assessment catalogue,
student groups, grades, achievement levels and reporting categories, plus two
fact tables -- one overall result per reported cell, and one row per area,
domain or composite beneath it.

The dropped tables held only imported figures, so nothing is carried across;
the data is restored by running the importer against the research files.  For
the same reason ``downgrade`` drops the new tables rather than rebuilding the
old ones.

Revision ID: 7b82316000d2
Revises: 8c1f4a2b7d90
Create Date: 2026-08-30

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

revision = "7b82316000d2"
down_revision = "8c1f4a2b7d90"
branch_labels = None
depends_on = None

# Tables from the per-test schema.  Dropped with CASCADE because several carry
# foreign keys to the old ``entities`` table, which is replaced as well.
LEGACY_TABLES = (
    "sb_results",
    "cast_results",
    "caa_results",
    "caas_results",
    "csa_results",
    "sa_elpac_results",
    "ia_elpac_results",
    "altsa_elpac_results",
    "altia_elpac_results",
    "caaspp_tests",
    "elpac_tests",
    "caaspp_student_groups",
    "elpac_student_groups",
    "entities",
)

NEW_TABLES = (
    "ingest_files",
    "ingest_runs",
    "assessment_subscores",
    "assessment_results",
    "entities",
    "grade_levels",
    "student_groups",
    "subscore_definitions",
    "assessment_years",
    "assessments",
    "performance_levels",
    "performance_level_schemes",
)

# Enum types are created implicitly by the tables that use them and have to be
# dropped explicitly once those tables are gone.
ENUM_TYPES = (
    "program",
    "entitylevel",
    "charterfunding",
    "subscorekind",
    "metorabovesource",
    "ingeststatus",
)


def upgrade() -> None:
    for table in LEGACY_TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")

    op.create_table(
        "performance_level_schemes",
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column("level_count", sa.Integer(), nullable=False),
        sa.Column("proficient_from_level", sa.Integer(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_table(
        "performance_levels",
        sa.Column(
            "scheme_code", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False
        ),
        sa.Column("level_number", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column(
            "short_name", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False
        ),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["scheme_code"],
            ["performance_level_schemes.code"],
        ),
        sa.PrimaryKeyConstraint("scheme_code", "level_number"),
    )
    op.create_table(
        "assessments",
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column(
            "program", sa.Enum("CAASPP", "ELPAC", name="program"), nullable=False
        ),
        sa.Column(
            "test_type", sqlmodel.sql.sqltypes.AutoString(length=5), nullable=False
        ),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column(
            "short_name", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False
        ),
        sa.Column(
            "subject", sqlmodel.sql.sqltypes.AutoString(length=60), nullable=False
        ),
        sa.Column("is_alternate", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("test_id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "assessment_years",
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("test_year", sa.Integer(), nullable=False),
        sa.Column(
            "level_scheme_code",
            sqlmodel.sql.sqltypes.AutoString(length=40),
            nullable=False,
        ),
        sa.Column("reports_mean_scale_score", sa.Boolean(), nullable=False),
        sa.Column("grades_note", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["level_scheme_code"],
            ["performance_level_schemes.code"],
        ),
        sa.ForeignKeyConstraint(
            ["test_id"],
            ["assessments.test_id"],
        ),
        sa.PrimaryKeyConstraint("test_id", "test_year"),
    )
    op.create_table(
        "subscore_definitions",
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("test_year", sa.Integer(), nullable=False),
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "area", "composite_area", "domain", "composite", name="subscorekind"
            ),
            nullable=False,
        ),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column(
            "band_scheme_code",
            sqlmodel.sql.sqltypes.AutoString(length=40),
            nullable=False,
        ),
        sa.Column("reports_mean_scale_score", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["band_scheme_code"],
            ["performance_level_schemes.code"],
        ),
        sa.ForeignKeyConstraint(
            ["test_id", "test_year"],
            ["assessment_years.test_id", "assessment_years.test_year"],
        ),
        sa.PrimaryKeyConstraint("test_id", "test_year", "code"),
    )
    op.create_table(
        "student_groups",
        sa.Column(
            "program", sa.Enum("CAASPP", "ELPAC", name="program"), nullable=False
        ),
        sa.Column("student_group_id", sa.Integer(), nullable=False),
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(length=3), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column(
            "category", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=False
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("program", "student_group_id"),
    )
    op.create_table(
        "grade_levels",
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=False),
        sa.Column("label", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_aggregate", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_table(
        "entities",
        sa.Column(
            "cds_code", sqlmodel.sql.sqltypes.AutoString(length=14), nullable=False
        ),
        sa.Column(
            "county_code", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=False
        ),
        sa.Column(
            "district_code", sqlmodel.sql.sqltypes.AutoString(length=5), nullable=False
        ),
        sa.Column(
            "school_code", sqlmodel.sql.sqltypes.AutoString(length=7), nullable=False
        ),
        sa.Column(
            "entity_level",
            sa.Enum("state", "county", "district", "school", name="entitylevel"),
            nullable=False,
        ),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column("is_charter", sa.Boolean(), nullable=False),
        sa.Column(
            "charter_funding",
            sa.Enum("direct", "local", name="charterfunding"),
            nullable=True,
        ),
        sa.Column(
            "county_name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True
        ),
        sa.Column(
            "district_name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True
        ),
        sa.Column(
            "school_name", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True
        ),
        sa.Column(
            "zip_code", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True
        ),
        sa.Column(
            "display_name", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False
        ),
        sa.Column(
            "parent_cds_code",
            sqlmodel.sql.sqltypes.AutoString(length=14),
            nullable=True,
        ),
        sa.Column("first_test_year", sa.Integer(), nullable=True),
        sa.Column("last_test_year", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("cds_code"),
    )
    op.create_index(
        "ix_entities_county_code", "entities", ["county_code"], unique=False
    )
    op.create_index(
        "ix_entities_district",
        "entities",
        ["county_code", "district_code"],
        unique=False,
    )
    op.create_index("ix_entities_level", "entities", ["entity_level"], unique=False)
    op.create_table(
        "assessment_results",
        sa.Column(
            "cds_code", sqlmodel.sql.sqltypes.AutoString(length=14), nullable=False
        ),
        sa.Column("test_year", sa.Integer(), nullable=False),
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("student_group_id", sa.Integer(), nullable=False),
        sa.Column("grade", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=False),
        sa.Column("students_enrolled", sa.Integer(), nullable=True),
        sa.Column("students_tested", sa.Integer(), nullable=True),
        sa.Column("students_tested_with_scores", sa.Integer(), nullable=True),
        sa.Column("mean_scale_score", sa.Numeric(precision=6, scale=1), nullable=True),
        sa.Column("level1_count", sa.Integer(), nullable=True),
        sa.Column("level1_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("level2_count", sa.Integer(), nullable=True),
        sa.Column("level2_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("level3_count", sa.Integer(), nullable=True),
        sa.Column("level3_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("level4_count", sa.Integer(), nullable=True),
        sa.Column("level4_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("met_or_above_count", sa.Integer(), nullable=True),
        sa.Column("met_or_above_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "met_or_above_source",
            sa.Enum("published", "derived", name="metorabovesource"),
            nullable=True,
        ),
        sa.Column("overall_total", sa.Integer(), nullable=True),
        sa.Column("suppressed", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cds_code"],
            ["entities.cds_code"],
        ),
        sa.ForeignKeyConstraint(
            ["test_id"],
            ["assessments.test_id"],
        ),
        sa.PrimaryKeyConstraint(
            "cds_code", "test_year", "test_id", "student_group_id", "grade"
        ),
    )
    op.create_index(
        "ix_results_lookup",
        "assessment_results",
        ["test_year", "test_id", "grade", "student_group_id", "cds_code"],
        unique=False,
    )
    op.create_table(
        "assessment_subscores",
        sa.Column(
            "cds_code", sqlmodel.sql.sqltypes.AutoString(length=14), nullable=False
        ),
        sa.Column("test_year", sa.Integer(), nullable=False),
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("student_group_id", sa.Integer(), nullable=False),
        sa.Column("grade", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=False),
        sa.Column(
            "subscore_code", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False
        ),
        sa.Column("mean_scale_score", sa.Numeric(precision=6, scale=1), nullable=True),
        sa.Column("band1_count", sa.Integer(), nullable=True),
        sa.Column("band1_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("band2_count", sa.Integer(), nullable=True),
        sa.Column("band2_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("band3_count", sa.Integer(), nullable=True),
        sa.Column("band3_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("band4_count", sa.Integer(), nullable=True),
        sa.Column("band4_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("subscore_total", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["cds_code"],
            ["entities.cds_code"],
        ),
        sa.PrimaryKeyConstraint(
            "cds_code",
            "test_year",
            "test_id",
            "student_group_id",
            "grade",
            "subscore_code",
        ),
    )
    op.create_table(
        "ingest_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "source_uri", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum("running", "succeeded", "failed", "skipped", name="ingeststatus"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("files_seen", sa.Integer(), nullable=False),
        sa.Column("files_loaded", sa.Integer(), nullable=False),
        sa.Column("files_skipped", sa.Integer(), nullable=False),
        sa.Column("result_rows", sa.Integer(), nullable=False),
        sa.Column("subscore_rows", sa.Integer(), nullable=False),
        sa.Column("error", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ingest_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column(
            "source_key", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False
        ),
        sa.Column("etag", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("last_modified", sa.DateTime(), nullable=True),
        sa.Column(
            "program", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True
        ),
        sa.Column(
            "test_type", sqlmodel.sql.sqltypes.AutoString(length=5), nullable=True
        ),
        sa.Column("test_year", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("running", "succeeded", "failed", "skipped", name="ingeststatus"),
            nullable=False,
        ),
        sa.Column("result_rows", sa.Integer(), nullable=False),
        sa.Column("subscore_rows", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("error", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("loaded_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["ingest_runs.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingest_files_key", "ingest_files", ["source_key"], unique=False)
    op.create_index(
        op.f("ix_ingest_files_run_id"), "ingest_files", ["run_id"], unique=False
    )


def downgrade() -> None:
    for table in NEW_TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    for enum_name in ENUM_TYPES:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
