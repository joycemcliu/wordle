from __future__ import annotations

import datetime
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as orm
from models.base import BaseModel, uuid_v7
from sqlalchemy.dialects.postgresql import UUID


class GameHistory(BaseModel):
    __tablename__ = "game_history"

    id: uuid.UUID = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid_v7,
        nullable=False,
        index=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    created_at: datetime.datetime = sa.Column(
        sa.DateTime,
        default=datetime.datetime.now,
        index=True,
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: datetime.datetime = sa.Column(
        sa.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False,
        server_default=sa.func.now(),
    )
    game_id: str = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("games.id"), nullable=False, index=True
    )
    game = orm.relationship("Game")
    word = sa.Column(sa.String, nullable=False)
    answer = sa.Column(sa.String, nullable=False)
    hit_count = sa.Column(sa.Integer, nullable=False)
    present_count = sa.Column(sa.Integer, nullable=False)
    miss_count = sa.Column(sa.Integer, nullable=False)

    def __str__(self):
        return (
            f"<Score\n"
            f"id={self.id}\n"
            f"created_at={self.created_at}\n"
            f"updated_at={self.updated_at}\n"
            f"game_id={self.game_id}\n"
            f"word={self.word}\n"
            f"answer={self.answer}\n"
            f"hit_count={self.hit_count}\n"
            f"present_count={self.present_count}\n"
            f"miss_count={self.miss_count}\n"
            f">"
        )
