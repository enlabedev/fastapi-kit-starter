from fastapi import APIRouter

from app.routes.v1 import auth, categories, notes, users

router = APIRouter()
router.include_router(auth.router, tags=["auth"], prefix="/auth")
router.include_router(users.router, tags=["users"], prefix="/users")
router.include_router(categories.router, tags=["categories"], prefix="/categories")
router.include_router(notes.router, tags=["notes"], prefix="/notes")
