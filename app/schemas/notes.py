from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categories import CategoryResponse
from app.schemas.users import UserResponse


class NoteBase(BaseModel):
    """Esquema base para notas"""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False
    category_id: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class NoteCreate(NoteBase):
    """Esquema para creación de notas"""

    pass


class NoteUpdate(BaseModel):
    """Esquema para actualización de notas"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    published: Optional[bool] = None
    category_id: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class NoteInDB(NoteBase):
    """Esquema para nota en la base de datos"""

    id: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class NoteResponse(NoteBase):
    """Esquema para respuesta de nota"""

    id: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    category: Optional[CategoryResponse] = None
    users: Optional[List[UserResponse]] = []


class NoteListResponse(BaseModel):
    """Esquema para lista de notas"""

    data: List[NoteResponse]
    metadata: dict


class NoteDetailResponse(BaseModel):
    """Esquema para detalle de nota"""

    data: NoteResponse
