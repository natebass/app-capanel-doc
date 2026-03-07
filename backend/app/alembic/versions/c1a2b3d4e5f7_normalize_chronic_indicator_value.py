"""Normalize CHRO indicator value to CHRONIC

Revision ID: c1a2b3d4e5f7
Revises: f5a83e87d6ee
Create Date: 2026-03-04 23:24:00.000000

The CDE Excel files store the chronic absenteeism indicator as "CHRO" in the
``indicator`` column, while the canonical name used everywhere else in the
application is "CHRONIC".  This migration normalises all existing rows so the
column contains a single consistent value.
"""

# revision identifiers, used by Alembic.
revision = 'c1a2b3d4e5f7'
down_revision = 'f5a83e87d6ee'
branch_labels = None
depends_on = None

from alembic import op


def upgrade() -> None:
    # Delete CHRO rows that would conflict with an existing CHRONIC row for the
    # same natural key (cds, studentgroup, reportingyear), then rename the rest.
    op.execute("""
        DELETE FROM academicindicator a
        USING academicindicator b
        WHERE a.indicator = 'CHRO'
          AND b.indicator = 'CHRONIC'
          AND a.cds = b.cds
          AND a.studentgroup = b.studentgroup
          AND a.reportingyear = b.reportingyear
    """)
    op.execute("UPDATE academicindicator SET indicator = 'CHRONIC' WHERE indicator = 'CHRO'")


def downgrade() -> None:
    op.execute("UPDATE academicindicator SET indicator = 'CHRO' WHERE indicator = 'CHRONIC'")
