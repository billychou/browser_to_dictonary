"""add word review progress

Revision ID: 7f3a9c2e5b81
Revises: de79dc5ccad7
Create Date: 2026-08-29 09:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f3a9c2e5b81'
down_revision = 'de79dc5ccad7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('vocabulary_word', sa.Column('stage', sa.Integer(), server_default='0', nullable=False))
    op.add_column('vocabulary_word', sa.Column('due', sa.DateTime(), nullable=True))
    op.add_column('vocabulary_word', sa.Column('review_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('vocabulary_word', sa.Column('lapse_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('vocabulary_word', sa.Column('last_review', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('vocabulary_word', 'last_review')
    op.drop_column('vocabulary_word', 'lapse_count')
    op.drop_column('vocabulary_word', 'review_count')
    op.drop_column('vocabulary_word', 'due')
    op.drop_column('vocabulary_word', 'stage')
