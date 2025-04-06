from app.models.categories import Category
from app.models.notes import Attachment, Notes
from app.models.users import User
from app.schemas.attachments import AttachmentCreate, AttachmentUpdate
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.schemas.notes import NoteCreate, NoteUpdate
from app.schemas.users import UserCreate, UserUpdate

from .base import ControllerBase

notes = ControllerBase[Notes, NoteCreate, NoteUpdate](Notes)
users = ControllerBase[User, UserCreate, UserUpdate](User)
categories = ControllerBase[Category, CategoryCreate, CategoryUpdate](Category)
attachments = ControllerBase[Attachment, AttachmentCreate, AttachmentUpdate](Attachment)
