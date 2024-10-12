"""Store hint on GameHistory

Revision ID: b61312d03418
Revises: 84bac59db6e2
Create Date: 2024-10-13 08:54:52.631621

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, text
from src.game_guess import compare_two_words

# revision identifiers, used by Alembic.
revision: str = "b61312d03418"
down_revision: str | None = "84bac59db6e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("game_history", sa.Column("hint", sa.String, default="_____"))

    bind = op.get_bind()
    session = orm.Session(bind=bind)
    game_histories = session.execute(text("SELECT id, answer, word FROM game_history")).fetchall()

    for game_history in game_histories:
        hint, _ = compare_two_words(ref=game_history.answer, word=game_history.word)
        session.execute(
            text("UPDATE game_history SET hint=:hint WHERE id=:id"),
            {"hint": hint, "id": game_history.id},
        )
    session.commit()
    op.alter_column("game_history", "hint", nullable=False)


def downgrade() -> None:
    op.drop_column("game_history", "hint")
