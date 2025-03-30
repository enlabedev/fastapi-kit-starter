from typing import Generator

from app.config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

SQLITE_URL = settings.SQLITE_URL


engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
