from datetime import datetime
from typing import List, Optional

from app.helpers.enum import NoteCategory
from app.schemas.base import MetadataSchema, ResponseSchemaBase
from pydantic import BaseModel, ConfigDict, Field


class NoteBaseSchema(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    category: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    published: Optional[bool] = False

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class NoteListSchema(ResponseSchemaBase):
    class NoteList(NoteBaseSchema):
        id: str = Field(..., description="ID de la nota")
        title: str = Field(..., description="Título de la nota")

    data: Optional[List[NoteList]] = None
    metadata: Optional[MetadataSchema] = None


class NoteDetailSchema(ResponseSchemaBase):
    class NoteDetail(NoteBaseSchema):
        id: str = Field(..., description="ID de la nota")
        title: str = Field(..., description="Título de la nota")

    data: Optional[NoteDetail] = None


class NoteSchemaCreate(NoteBaseSchema):
    # Campos requeridos con anotaciones
    title: str = Field(..., description="Título de la nota")
    content: str = Field(..., description="Contenido de la nota")
    # Usar el Enum directamente
    category: NoteCategory = Field(..., description="Categoría de la nota")
    # Field opcional con valor predeterminado
    published: Optional[bool] = Field(
        False, description="Estado de publicación"
    )


class NoteSchemaUpdate(NoteBaseSchema):
    # Campos requeridos con anotaciones
    id: str = Field(..., description="ID de la nota a actualizar")
    title: str = Field(..., description="Título de la nota")
    content: str = Field(..., description="Contenido de la nota")
    category: NoteCategory = Field(..., description="Categoría de la nota")
    published: Optional[bool] = Field(
        False, description="Estado de publicación"
    )


class NoteSchemaDelete(NoteBaseSchema):
    # Campo requerido con anotación
    id: str = Field(..., description="ID de la nota a eliminar")
