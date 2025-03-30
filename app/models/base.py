from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import TIMESTAMP, Column, String
from sqlalchemy.sql import func
from uuid import uuid4


class Base:
    __abstract__ = True
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


Base = declarative_base(cls=Base)


class BareBaseModel(Base):
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
