from __future__ import annotations

import datetime
import uuid

import sqlalchemy as sa
from models.base import BaseModel, uuid_v7
from sqlalchemy.dialects.postgresql import UUID


class Vocabulary(BaseModel):
    __tablename__ = "vocabularies"

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
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        server_default=sa.func.now(),
    )
    word: str = sa.Column(sa.String, index=True, nullable=False, unique=True)
    length: int = sa.Column(sa.Integer, index=True, nullable=False)

    def __str__(self) -> str:
        return (
            f"<vocabulary\n"
            f"id={self.id}\n"
            f"created_at={self.created_at}\n"
            f"updated_at={self.updated_at}\n"
            f"word={self.word}\n"
            f">"
        )
