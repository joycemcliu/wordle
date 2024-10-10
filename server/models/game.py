from __future__ import annotations

import datetime
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as orm
from models.base import BaseModel, uuid_v7
from sqlalchemy.dialects.postgresql import UUID


class Game(BaseModel):
    __tablename__ = "games"

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
    user_id: str = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True
    )
    user = orm.relationship("User")
    answer = sa.Column(sa.String, nullable=False)
    max_rounds = sa.Column(sa.Integer, nullable=False)
    num_attemps = sa.Column(sa.Integer, nullable=False, default=0)
    is_end = sa.Column(sa.Boolean, nullable=False, index=True, default=False)

    def __str__(self):
        return (
            f"\n<Game\n"
            f"id={self.id}\n"
            f"created_at={self.created_at}\n"
            f"updated_at={self.updated_at}\n"
            f"user_id={self.user_id}\n"
            f"answer={self.answer}\n"
            f"max_rounds={self.max_rounds}\n"
            f"num_attemps={self.num_attemps}\n"
            f"score={self.score}\n"
            f">"
        )
