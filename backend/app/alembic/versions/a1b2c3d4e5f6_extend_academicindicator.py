"""Extend academicindicator with all indicator fields

Revision ID: a1b2c3d4e5f6
Revises: eb9bef92a74f
Create Date: 2026-02-04 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "eb9bef92a74f"
branch_labels = None
depends_on = None


def upgrade():
    # Common fields (Chronic, Suspension, Graduation, ELPI)
    op.add_column(
        "academicindicator", sa.Column("currnumer", sa.Integer(), nullable=True)
    )
    op.add_column(
        "academicindicator", sa.Column("priornumer", sa.Integer(), nullable=True)
    )
    op.add_column(
        "academicindicator", sa.Column("smalldenom", sa.String(10), nullable=True)
    )
    op.add_column(
        "academicindicator", sa.Column("certifyflag", sa.String(10), nullable=True)
    )
    op.add_column(
        "academicindicator", sa.Column("priorcertifyflag", sa.String(10), nullable=True)
    )
    op.add_column(
        "academicindicator", sa.Column("dataerrorflag", sa.String(10), nullable=True)
    )

    # Suspension-specific
    op.add_column(
        "academicindicator", sa.Column("school_type", sa.String(50), nullable=True)
    )

    # Graduation-specific
    op.add_column(
        "academicindicator", sa.Column("fiveyrnumer", sa.Integer(), nullable=True)
    )

    # ELPI fields (16 total)
    elpi_fields = [
        "currprogressed",
        "currmaintainpl4",
        "currmaintainoth",
        "currdeclined",
        "currprogressed_alternate",
        "currmaintainpl3_alternate",
        "currnotprognotmain_alternate",
        "curr95",
        "priorprogressed",
        "priormaintainpl4",
        "priormaintainoth",
        "priordeclined",
        "priorprogressed_alternate",
        "priormaintainpl3_alternate",
        "priornotprognotmain_alternate",
        "prior95",
    ]
    for field in elpi_fields:
        op.add_column(
            "academicindicator", sa.Column(field, sa.Integer(), nullable=True)
        )

    # CCI JSON and studentgroup_pct
    op.add_column(
        "academicindicator", sa.Column("cci_details", sa.JSON(), nullable=True)
    )
    op.add_column(
        "academicindicator", sa.Column("studentgroup_pct", sa.Float(), nullable=True)
    )

    # Indexes for better query performance
    op.create_index(
        "ix_academicindicator_indicator", "academicindicator", ["indicator"]
    )
    op.create_index(
        "ix_academicindicator_cds_indicator_year",
        "academicindicator",
        ["cds", "indicator", "reportingyear"],
    )

    # User preferences - add last_viewed_cds
    op.add_column("user", sa.Column("last_viewed_cds", sa.String(14), nullable=True))


def downgrade():
    # Remove user preferences
    op.drop_column("user", "last_viewed_cds")

    # Remove indexes
    op.drop_index("ix_academicindicator_cds_indicator_year", table_name="academicindicator")
    op.drop_index("ix_academicindicator_indicator", table_name="academicindicator")

    # Remove CCI and studentgroup_pct
    op.drop_column("academicindicator", "studentgroup_pct")
    op.drop_column("academicindicator", "cci_details")

    # Remove ELPI fields
    elpi_fields = [
        "currprogressed",
        "currmaintainpl4",
        "currmaintainoth",
        "currdeclined",
        "currprogressed_alternate",
        "currmaintainpl3_alternate",
        "currnotprognotmain_alternate",
        "curr95",
        "priorprogressed",
        "priormaintainpl4",
        "priormaintainoth",
        "priordeclined",
        "priorprogressed_alternate",
        "priormaintainpl3_alternate",
        "priornotprognotmain_alternate",
        "prior95",
    ]
    for field in elpi_fields:
        op.drop_column("academicindicator", field)

    # Remove Graduation-specific
    op.drop_column("academicindicator", "fiveyrnumer")

    # Remove Suspension-specific
    op.drop_column("academicindicator", "school_type")

    # Remove common fields
    op.drop_column("academicindicator", "dataerrorflag")
    op.drop_column("academicindicator", "priorcertifyflag")
    op.drop_column("academicindicator", "certifyflag")
    op.drop_column("academicindicator", "smalldenom")
    op.drop_column("academicindicator", "priornumer")
    op.drop_column("academicindicator", "currnumer")
