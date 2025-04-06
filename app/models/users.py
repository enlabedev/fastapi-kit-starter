from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
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


class UserNotes(BaseModel):
    """Modelo de relación entre usuarios y notas."""

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


class Attachment(BaseModel):
    """Modelo para archivos adjuntos a notas."""

    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

    # Relación con la nota a la que pertenece
    note_id = Column(
        String(36), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False
    )
    note = relationship("Notes", backref="attachments")
    note = relationship("Notes", backref="attachments")
