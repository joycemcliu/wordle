from __future__ import annotations

import datetime
import logging
import uuid

import sqlalchemy as sa
from models.base import BaseModel, uuid_v7
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


class User(BaseModel):
    __tablename__ = "users"

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
    name: str = sa.Column(sa.String, index=True, unique=True, nullable=False)

    def __str__(self):
        return (
            f"<User\n"
            f"id={self.id}\n"
            f"created_at={self.created_at}\n"
            f"updated_at={self.updated_at}\n"
            f"name={self.name}\n"
            f">"
        )

    @classmethod
    async def get(cls, db: AsyncSession, id: str):
        try:
            transaction = await db.get(cls, id)
        except Exception as e:
            log.error(f"Error getting user: {e}")
            return None
        return transaction

    @classmethod
    @classmethod
    async def create(cls, db: AsyncSession, id=None, name=None, **kwargs) -> User:
        if not id:
            id = uuid_v7()

        if not name:
            name = "user_" + str(id[-7:])

        transaction = cls(id=id, name=name, **kwargs)
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction
