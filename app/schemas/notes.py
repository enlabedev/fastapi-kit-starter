from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.base import ResponseSchemaBase, MetadataSchema
from app.helpers.enum import NoteCategory


class NoteBaseSchema(BaseModel):
    id: Optional[str]
    title: str = Field(..., max_length=200)
    content: str
    category: Optional[str] = Field(None, max_length=50)
    published: bool = False
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class NoteListSchema(ResponseSchemaBase):
    class NoteList(NoteBaseSchema):
        id: UUID
        title: str

    data: Optional[list[NoteList]]
    metadata: Optional[MetadataSchema]


class NoteDetailSchema(ResponseSchemaBase):
    class NoteDetail(NoteBaseSchema):
        id: UUID
        title: str

    data: Optional[NoteDetail]


class NoteSchemaCreate(NoteBaseSchema):
    id: str = str(uuid4())
    title: str
    content: str
    category: NoteCategory
    published: Optional[bool]


class NoteSchemaUpdate(NoteBaseSchema):
    title: str
    content: str
    category: NoteCategory
    published: Optional[bool]


class NoteSchemaDelete(NoteBaseSchema):
    id: str
