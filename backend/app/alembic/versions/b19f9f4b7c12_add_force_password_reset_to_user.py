"""Add force_password_reset flag to user

Revision ID: b19f9f4b7c12
Revises: a1b2c3d4e5f6
Create Date: 2026-03-04 16:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b19f9f4b7c12"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column(
            "force_password_reset",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column("user", "force_password_reset", server_default=None)


def downgrade():
    op.drop_column("user", "force_password_reset")
