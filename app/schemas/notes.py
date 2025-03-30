from datetime import datetime
from typing import Optional

from app.helpers.enum import NoteCategory
from app.schemas.base import MetadataSchema, ResponseSchemaBase
from pydantic import BaseModel, ConfigDict


class NoteBaseSchema(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    category: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    published: Optional[bool] = False

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
