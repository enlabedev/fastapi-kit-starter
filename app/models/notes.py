from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Notes(BaseModel):
    """Modelo de notas con relaciones a usuarios y categorías."""

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Boolean, nullable=False, default=True)

    category_id = Column(String(36), ForeignKey("category.id"), nullable=True)
    category = relationship("Category", back_populates="notes")

    users = relationship("User", secondary="usernotes", back_populates="notes")


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
