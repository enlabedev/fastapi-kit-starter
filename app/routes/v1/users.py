from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import controllers
from app.auth.jwt import (
    get_current_active_user,
    get_current_admin_user,
    get_password_hash,
)
from app.config.database import get_db
from app.helpers.response import ResponseHelper
from app.models.users import User
from app.schemas.base import ResponseSchemaBase
from app.schemas.users import (
    UserCreate,
    UserDetailResponse,
    UserListResponse,
    UserUpdate,
)

router = APIRouter()


@router.get("", response_model=UserListResponse)
async def get_users(
    page: int = 0,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin_user
    ),  # Solo admin puede ver todos los usuarios
) -> Dict[str, Any]:
    """Obtiene todos los usuarios (solo admin)."""
    users = controllers.users.read(db=db, skip=page * page_size, limit=page_size)
    total_items = db.query(User).count()
    return {
        "data": users,
        "metadata": ResponseHelper.pagination_meta(page, page_size, total_items),
    }


@router.post("", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Crea un nuevo usuario."""
    # Verificar si ya existe un usuario con ese nombre o email
    db_user = (
        db.query(User)
        .filter(
            (User.username == user_create.username) | (User.email == user_create.email)
        )
        .first()
    )
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario o email ya está en uso",
        )

    # Crear usuario con contraseña hasheada
    user_dict = user_create.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user = User(**user_dict)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"data": user}


@router.get("/me", response_model=UserDetailResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Obtiene información del usuario actual."""
    return {"data": current_user}


@router.put("/me", response_model=UserDetailResponse)
async def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Actualiza la información del usuario actual."""
    # Si se actualiza la contraseña, hashearla
    if user_update.password:
        user_dict = user_update.model_dump(exclude_unset=True)
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        for key, value in user_dict.items():
            setattr(current_user, key, value)
    else:
        # Actualizar solo los campos proporcionados
        for key, value in user_update.model_dump(
            exclude_unset=True, exclude={"password"}
        ).items():
            setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"data": current_user}


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin_user
    ),  # Solo admin puede ver otros usuarios
) -> Dict[str, Any]:
    """Obtiene un usuario por ID (solo admin)."""
    user = controllers.users.get(id=user_id, db=db, error_out=True)
    return {"data": user}


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin_user
    ),  # Solo admin puede actualizar otros usuarios
) -> Dict[str, Any]:
    """Actualiza un usuario por ID (solo admin)."""
    user = controllers.users.get(id=user_id, db=db, error_out=True)

    # Si se actualiza la contraseña, hashearla
    if user_update.password:
        user_dict = user_update.model_dump(exclude_unset=True)
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        controllers.users.update(db=db, model=user, schema=user_dict)
    else:
        controllers.users.update(
            db=db,
            model=user,
            schema=user_update.model_dump(exclude_unset=True, exclude={"password"}),
        )

    return {"data": user}


@router.delete("/{user_id}", response_model=ResponseSchemaBase)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_admin_user
    ),  # Solo admin puede eliminar usuarios
) -> Dict[str, str]:
    """Elimina un usuario por ID (solo admin)."""
    # No permitir eliminar al propio usuario administrador
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario",
        )

    controllers.users.delete(db=db, id=user_id)
    return {"message": "Usuario eliminado correctamente"}
