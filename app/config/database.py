from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config.settings import settings

POSTGRES_URL = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
    settings.POSTGRES_USER,
    settings.POSTGRES_PASSWORD,
    settings.POSTGRES_HOSTNAME,
    settings.DATABASE_PORT,
    settings.POSTGRES_DB,
)


engine = create_engine(POSTGRES_URL, pool_pre_ping=True, echo=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
