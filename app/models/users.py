from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """Modelo de usuario con relaciones a notas."""

    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    notes = relationship("Notes", secondary="usernotes", back_populates="users")


class UserNotes(BaseModel):
    """Modelo de relación entre usuarios y notas."""

    __tablename__ = "usernotes"

    user_id = Column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    note_id = Column(
        String(36),
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
    )
