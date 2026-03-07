"""merge_b19f9f4b7c12_and_c1a2b3d4e5f7

Revision ID: a3afd5df08ce
Revises: b19f9f4b7c12, c1a2b3d4e5f7
Create Date: 2026-03-04 23:41:21.018207

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a3afd5df08ce'
down_revision = ('b19f9f4b7c12', 'c1a2b3d4e5f7')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
