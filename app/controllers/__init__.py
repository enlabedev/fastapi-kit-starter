from app.models.notes import Notes
from app.schemas.notes import NoteSchemaCreate, NoteSchemaUpdate

from .base import ControllerBase

notes = ControllerBase[Notes, NoteSchemaCreate, NoteSchemaUpdate](Notes)
