from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.base import ResponseSchemaBase, MetadataSchema
from app.helpers.enum import NoteCategory


class NoteBaseSchema(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    category: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    published: bool

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class NoteListSchema(ResponseSchemaBase):
    class NoteList(NoteBaseSchema):
        id: str
        title: str

    data: Optional[list[NoteList]]
    metadata: Optional[MetadataSchema]


class NoteDetailSchema(ResponseSchemaBase):
    class NoteDetail(NoteBaseSchema):
        id: str
        title: str

    data: Optional[NoteDetail]


class NoteSchemaCreate(NoteBaseSchema):
    title: str
    content: str
    category: NoteCategory
    published: Optional[bool]


class NoteSchemaUpdate(NoteBaseSchema):
    id: str
    title: str
    content: str
    category: NoteCategory
    published: Optional[bool]


class NoteSchemaDelete(NoteBaseSchema):
    id: str
