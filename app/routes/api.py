from fastapi import APIRouter

from app.routes.v1 import notes

router = APIRouter()
router.include_router(notes.router, tags=["notes"], prefix="/notes")
router.include_router(notes.router, tags=["notes"], prefix="/notes")
