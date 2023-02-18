from .base import ControllerBase
from app.models.notes import Notes
from app.schemas.notes import NoteSchemaCreate, NoteSchemaUpdate

notes = ControllerBase[Notes, NoteSchemaCreate, NoteSchemaUpdate](Notes)
