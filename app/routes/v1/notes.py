from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app import controllers
from app.config.database import get_db
from app.models.notes import Notes
from app.schemas.base import ResponseSchemaBase
from app.helpers.response import ResponseHelper
from app.schemas.notes import NoteListSchema, NoteDetailSchema, NoteSchemaCreate, NoteSchemaUpdate

router = APIRouter()


@router.get("", response_model=NoteListSchema)
async def get(page: int = 0, pageSize: int = 10):
    notes = controllers.notes.read()
    totalItems = len(notes)
    return {
        "data": notes,
        "metadata": ResponseHelper.pagination_meta(page, pageSize, totalItems),
    }


@router.get("/search/{text}", response_model=NoteListSchema)
async def search(text: str = "", page: int = 0, pageSize: int = 10):
    _query = controllers.notes.q()
    if text:
        _query = _query.filter(Notes.title == text)
    notes = _query.order_by(Notes.id.asc()).all()
    totalItems = len(notes)
    return {
        "data": notes,
        "metadata": ResponseHelper.pagination_meta(page, pageSize, totalItems),
    }


@router.get("/show/{id}", response_model=NoteDetailSchema)
async def show(id: str):
    notes = controllers.notes.get(id=id, error_out=True)
    return {"data": notes}


@router.post("", response_model=NoteDetailSchema)
async def create(*, notes: NoteSchemaCreate):
    notes = Notes(
        id=notes.id,
        title=notes.title,
        content=notes.content,
        category=notes.category,
        published=notes.published,
    )
    note = controllers.notes.create(schema=notes)
    return {"data": note}


@router.put("/{id}", response_model=NoteDetailSchema)
async def update(*, id: str, db: Session = Depends(get_db), note_data: NoteSchemaUpdate):
    note = controllers.notes.get(db=db, id=id, error_out=True)
    notes = controllers.notes.update(db=db, model=note, schema=note_data)
    return {"data": notes}


@router.delete("/{id}", response_model=ResponseSchemaBase)
async def delete(*, id: str, db: Session = Depends(get_db)):
    controllers.notes.delete(db=db, id=id)
    return {"message": "Resource was deleted"}
