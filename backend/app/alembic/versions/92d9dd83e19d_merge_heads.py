"""Merge heads

Revision ID: 92d9dd83e19d
Revises: d3deb8989ec8, fe56fa70289e
Create Date: 2026-02-03 20:39:54.155445

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '92d9dd83e19d'
down_revision = ('d3deb8989ec8', 'fe56fa70289e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
