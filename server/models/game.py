from __future__ import annotations

import datetime
import logging
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as orm
from models.base import BaseModel, uuid_v7
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


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
    user_id: uuid.UUID = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True
    )
    user = orm.relationship("User")
    answer = sa.Column(sa.String, nullable=False)
    max_rounds = sa.Column(sa.Integer, nullable=False)
    num_attempts = sa.Column(sa.Integer, nullable=False, default=0)
    word_length = sa.Column(sa.Integer, nullable=False)
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
            f"num_attempts={self.num_attempts}\n"
            f"word_length={self.word_length}\n"
            f">"
        )

    @classmethod
    async def get(cls, db: AsyncSession, id: str):
        try:
            transaction = await db.get(cls, id)
        except NoResultFound:
            return None
        except Exception as e:
            log.error(e)
            return None
        return transaction

    @classmethod
    async def get_all(cls, db: AsyncSession):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def create(cls, db: AsyncSession, user_id, answer, max_rounds, word_length, **kwargs):
        transaction = cls(
            id=uuid_v7(),
            user_id=user_id,
            answer=answer,
            max_rounds=max_rounds,
            word_length=word_length,
            **kwargs,
        )
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction
