"""Create tables

Revision ID: fa55b755ccc4
Revises:
Create Date: 2024-10-09 17:52:57.229374

"""

import datetime
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from models.base import uuid_v7
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "fa55b755ccc4"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid_v7,
            nullable=False,
            index=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            default=datetime.datetime.now,
            nullable=False,
            index=True,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            default=datetime.datetime.now,
            onupdate=datetime.datetime.now,
            server_default=sa.func.now(),
        ),
        sa.Column("name", sa.String, index=True, nullable=False, unique=True),
    )

    op.create_table(
        "vocabularies",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid_v7,
            nullable=False,
            index=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            default=datetime.datetime.now,
            nullable=False,
            index=True,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            default=datetime.datetime.now,
            onupdate=datetime.datetime.now,
            server_default=sa.func.now(),
        ),
        sa.Column("word", sa.String, index=True, nullable=False, unique=True),
        sa.Column("length", sa.Integer, index=True, nullable=False),
    )

    op.create_table(
        "games",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid_v7,
            nullable=False,
            index=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            default=datetime.datetime.now,
            nullable=False,
            index=True,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            default=datetime.datetime.now,
            onupdate=datetime.datetime.now,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True
        ),
        sa.Column("answer", sa.String, nullable=False),
        sa.Column("max_rounds", sa.Integer, nullable=False),
        sa.Column("num_attemps", sa.Integer, nullable=False),
        sa.Column("is_end", sa.Boolean, nullable=False, index=True),
    )
    op.create_table(
        "game_history",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid_v7,
            nullable=False,
            index=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            default=datetime.datetime.now,
            nullable=False,
            index=True,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            default=datetime.datetime.now,
            onupdate=datetime.datetime.now,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "game_id",
            UUID(as_uuid=True),
            sa.ForeignKey("games.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("word", sa.String, nullable=False),
        sa.Column("answer", sa.String, nullable=False),
        sa.Column("hit_count", sa.Integer, nullable=False),
        sa.Column("present_count", sa.Integer, nullable=False),
        sa.Column("miss_count", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("game_history")
    op.drop_table("games")
    op.drop_table("vocabularies")
    op.drop_table("users")
