"""Initial migration

Revision ID: 1db15409e73f
Revises:
Create Date: 2025-10-16 14:43:13.648863

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1db15409e73f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create vocabulary_word table
    op.create_table(
        "vocabulary_word",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("uid", sa.String(length=64), nullable=False),
        sa.Column("word", sa.String(length=64), nullable=False),
        sa.Column(
            "gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "gmt_update",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            onupdate=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="vocabulary_pkid"),
        sa.UniqueConstraint("uid", "word", name="vocabulary_unique"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )


def downgrade():
    # Drop vocabulary_word table
    op.drop_table("vocabulary_word")
