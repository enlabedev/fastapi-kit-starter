from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Category(BaseModel):
    """Modelo de categoría con relación a notas."""

    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(200), nullable=True)

    # Relación uno a muchos con notas
    notes = relationship("Notes", back_populates="category")
    notes = relationship("Notes", back_populates="category")
