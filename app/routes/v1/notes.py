from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import controllers
from app.config.database import get_db
from app.helpers.response import ResponseHelper
from app.models.notes import Notes
from app.schemas.base import ResponseSchemaBase
from app.schemas.notes import (
    NoteDetailSchema,
    NoteListSchema,
    NoteSchemaCreate,
    NoteSchemaUpdate,
)

router = APIRouter()


@router.get("", response_model=NoteListSchema)
async def get(
    page: int = 0, pageSize: int = 10, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    notes = controllers.notes.read(db=db, skip=page, limit=pageSize)
    totalItems = len(notes)
    return {
        "data": notes,
        "metadata": ResponseHelper.pagination_meta(page, pageSize, totalItems),
    }


@router.get("/search/{text}", response_model=NoteListSchema)
async def search(
    text: str = "", page: int = 0, pageSize: int = 10, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    _query = controllers.notes.q(db=db)
    if text:
        _query = _query.filter(Notes.title.ilike(f"%{text}%"))
    notes = _query.order_by(Notes.id.asc()).all()
    totalItems = len(notes)
    return {
        "data": notes,
        "metadata": ResponseHelper.pagination_meta(page, pageSize, totalItems),
    }


@router.get("/show/{id}", response_model=NoteDetailSchema)
async def show(
    id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    notes = controllers.notes.get(id=id, db=db, error_out=True)
    return {"data": notes}


@router.post("", response_model=NoteDetailSchema)
async def create(
    *, notes: NoteSchemaCreate, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    notes = Notes(
        title=notes.title,
        content=notes.content,
        category=notes.category,
        published=notes.published,
    )
    note = controllers.notes.create(schema=notes, db=db)
    return {"data": note}


@router.put("/{id}", response_model=NoteDetailSchema)
async def update(
    *, id: str, db: Session = Depends(get_db), note_data: NoteSchemaUpdate
) -> Dict[str, Any]:
    note = controllers.notes.get(db=db, id=id, error_out=True)
    if note is None:
        raise ValueError("Note not found")  # Ensure `note` is not None
    notes = controllers.notes.update(db=db, model=note, schema=note_data)
    return {"data": notes}


@router.delete("/{id}", response_model=ResponseSchemaBase)
async def delete(*, id: str, db: Session = Depends(get_db)) -> Dict[str, str]:
    controllers.notes.delete(db=db, id=id)
    return {"message": "Resource was deleted"}
    return {"message": "Resource was deleted"}
