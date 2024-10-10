import uuid_utils as uuid
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    pass


def uuid_v7():
    return uuid.uuid7().__str__()
