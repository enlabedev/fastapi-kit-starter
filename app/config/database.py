from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config.settings import settings


SQLITE_URL = settings.SQLITE_URL


engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
