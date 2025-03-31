from sqlalchemy import Boolean, Column, String, Text

from app.models.base import BareBaseModel


class Notes(BareBaseModel):
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    published = Column(Boolean, nullable=False, default=True)
    published = Column(Boolean, nullable=False, default=True)
