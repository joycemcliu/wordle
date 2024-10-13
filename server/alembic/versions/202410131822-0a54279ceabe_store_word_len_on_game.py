"""Store word_len on Game

Revision ID: 0a54279ceabe
Revises: b61312d03418
Create Date: 2024-10-13 18:22:55.816725

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0a54279ceabe"
down_revision: str | None = "b61312d03418"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "games", sa.Column("word_length", sa.Integer, nullable=False, default=5, server_default="5")
    )


def downgrade() -> None:
    op.drop_column("games", "word_length")
