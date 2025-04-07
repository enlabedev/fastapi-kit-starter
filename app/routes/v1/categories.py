from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import controllers
from app.auth.jwt import get_current_active_user, get_current_admin_user
from app.config.database import get_db
from app.helpers.response import ResponseHelper
from app.models.categories import Category
from app.models.users import User
from app.schemas.base import ResponseSchemaBase
from app.schemas.categories import (
    CategoryCreate,
    CategoryDetailResponse,
    CategoryListResponse,
    CategoryUpdate,
)

router = APIRouter()


@router.get("", response_model=CategoryListResponse)
async def get_categories(
    page: int = 0,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Obtiene todas las categorías."""
    categories = controllers.categories.read(
        db=db, skip=page * page_size, limit=page_size
    )
    total_items = db.query(Category).count()
    return {
        "data": categories,
        "metadata": ResponseHelper.pagination_meta(page, page_size, total_items),
    }


@router.post(
    "", response_model=CategoryDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_create: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin_user
    ),  # Solo admin puede crear categorías
) -> Dict[str, Any]:
    """Crea una nueva categoría (solo admin)."""
    # Verificar si ya existe una categoría con ese nombre
    existing = db.query(Category).filter(Category.name == category_create.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una categoría con ese nombre",
        )

    category = controllers.categories.create(db=db, schema=category_create)
    return {"data": category}


@router.get("/{category_id}", response_model=CategoryDetailResponse)
async def get_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Obtiene una categoría por ID."""
    category = controllers.categories.get(id=category_id, db=db, error_out=True)
    return {"data": category}


@router.put("/{category_id}", response_model=CategoryDetailResponse)
async def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin_user
    ),  # Solo admin puede actualizar categorías
) -> Dict[str, Any]:
    """Actualiza una categoría por ID (solo admin)."""
    # Verificar si la categoría existe
    category = controllers.categories.get(id=category_id, db=db, error_out=True)

    # Si se actualiza el nombre, verificar que no exista otro con ese nombre
    if category_update.name and category_update.name != category.name:
        existing = (
            db.query(Category).filter(Category.name == category_update.name).first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre",
            )

    updated_category = controllers.categories.update(
        db=db, model=category, schema=category_update
    )
    return {"data": updated_category}


@router.delete("/{category_id}", response_model=ResponseSchemaBase)
async def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin_user
    ),  # Solo admin puede eliminar categorías
) -> Dict[str, str]:
    """Elimina una categoría por ID (solo admin)."""
    # Primero, verificar si hay notas asociadas a esta categoría
    category = controllers.categories.get(id=category_id, db=db, error_out=True)

    if len(category.notes) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una categoría con notas asociadas",
        )

    controllers.categories.delete(db=db, id=category_id)
    return {"message": "Categoría eliminada correctamente"}
