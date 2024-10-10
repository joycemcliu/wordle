"""Add vocabulary

Revision ID: 84bac59db6e2
Revises: fa55b755ccc4
Create Date: 2024-10-10 09:25:57.916215

"""

from collections.abc import Sequence

from alembic import op
from models.vocab import Vocabulary
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import insert

# revision identifiers, used by Alembic.
revision: str = "84bac59db6e2"
down_revision: str | None = "fa55b755ccc4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    with open("alembic/vocab/words.txt") as f:
        for line in f:
            word = line.strip().lower()
            if len(word) > 0:
                session.execute(
                    insert(Vocabulary)
                    .values(word=word, length=len(word))
                    .on_conflict_do_update(
                        index_elements=[Vocabulary.word], set_={"length": len(word)}
                    )
                )
    session.commit()


def downgrade() -> None:
    pass
