from __future__ import annotations

import datetime
import logging
import random
import uuid

import sqlalchemy as sa
from models.base import BaseModel, uuid_v7
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


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

    @classmethod
    async def get(cls, db: AsyncSession, word: str) -> Vocabulary | None:
        return (await db.execute(select(cls).where(cls.word == word))).scalar_one_or_none()

    @classmethod
    async def get_random_word(cls, db: AsyncSession, length: int) -> Vocabulary | None:
        total_count = (
            await db.execute(
                select(func.count()).select_from(Vocabulary).where(Vocabulary.length == length)
            )
        ).scalar()

        if not total_count:
            return None

        return (
            await db.execute(
                select(cls)
                .where(cls.length == length)
                .offset(random.randint(0, total_count - 1))
                .limit(1)
            )
        ).scalar_one()

    @classmethod
    def get_random_word_from_list(cls, words: list[str]) -> str:
        return random.choice(words)

    @classmethod
    async def get_random_words(cls, db: AsyncSession, length: int, count: int) -> list[Vocabulary]:
        return (
            (
                await db.execute(
                    select(cls).where(cls.length == length).order_by(func.random()).limit(count)
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    async def get_all_word_lengths(cls, db: AsyncSession) -> list[int]:
        result = await db.execute(select(func.distinct(cls.length)).order_by(cls.length))
        return [row[0] for row in result.fetchall()]
