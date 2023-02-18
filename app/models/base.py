from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import TIMESTAMP, Column, text, UUID
from sqlalchemy.sql import func


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
        UUID(as_uuid=True),
        primary_key=True,
        default=text("gen_random_uuid()"),
        unique=True,
    )
    createdAt = Column(TIMESTAMP(timezone=True), default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True), onupdate=func.now())
