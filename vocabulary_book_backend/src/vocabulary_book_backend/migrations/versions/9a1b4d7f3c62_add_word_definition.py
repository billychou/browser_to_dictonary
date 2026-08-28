"""add word definition

Revision ID: 9a1b4d7f3c62
Revises: 7f3a9c2e5b81
Create Date: 2026-08-29 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a1b4d7f3c62'
down_revision = '7f3a9c2e5b81'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('vocabulary_word', sa.Column('phonetic', sa.String(length=128), nullable=True))
    op.add_column('vocabulary_word', sa.Column('definition', sa.Text(), nullable=True))
    op.add_column('vocabulary_word', sa.Column('detail', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('vocabulary_word', 'detail')
    op.drop_column('vocabulary_word', 'definition')
    op.drop_column('vocabulary_word', 'phonetic')
