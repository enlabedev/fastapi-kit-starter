from typing import Any, Type
from uuid import uuid4

from sqlalchemy import TIMESTAMP, Column, String
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.sql import func


class BaseClass:
    __abstract__ = True
    __name__: str

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


Base: Type[Any] = declarative_base(cls=BaseClass)


class BareBaseModel(Base, BaseClass):  # type: ignore
    __abstract__ = True

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        unique=True,
        index=True,
    )
    createdAt = Column(TIMESTAMP(timezone=True), default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True), onupdate=func.now())
