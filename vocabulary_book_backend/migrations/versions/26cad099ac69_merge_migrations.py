"""merge migrations

Revision ID: 26cad099ac69
Revises: 1db15409e73f, 8c7bbf78b15c
Create Date: 2025-10-16 14:46:44.629371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26cad099ac69'
down_revision = ('1db15409e73f', '8c7bbf78b15c')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass