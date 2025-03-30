from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker
from sqlalchemy import TIMESTAMP, Column, UUID, create_engine, String
from sqlalchemy.sql import func
from uuid import uuid4

# Define the engine (replace 'sqlite:///example.db' with your database URL)
engine = create_engine("sqlite:///example.db")


class Base:
    __abstract__ = True
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
