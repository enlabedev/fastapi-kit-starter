from app.routes.v1 import notes
from fastapi import APIRouter

router = APIRouter()
router.include_router(notes.router, tags=["notes"], prefix="/notes")
