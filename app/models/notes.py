from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Notes(BaseModel):
    """Modelo de notas con relaciones a usuarios y categorías."""

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Boolean, nullable=False, default=True)

    category_id = Column(String(36), ForeignKey("category.id"), nullable=True)
    category = relationship("Category", back_populates="notes")

    users = relationship("User", secondary="user_notes", back_populates="notes")
