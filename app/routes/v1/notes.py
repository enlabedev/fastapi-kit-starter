import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app import controllers
from app.auth.jwt import get_current_active_user
from app.config.database import get_db
from app.helpers.response import ResponseHelper
from app.models.categories import Category
from app.models.notes import Attachment, Notes
from app.models.users import User
from app.schemas.attachments import (
    AttachmentDetailResponse,
    AttachmentListResponse,
)
from app.schemas.base import ResponseSchemaBase
from app.schemas.notes import (
    NoteCreate,
    NoteDetailResponse,
    NoteListResponse,
    NoteUpdate,
)

router = APIRouter()


@router.get("", response_model=NoteListResponse)
async def get_notes(
    page: int = 0,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Obtiene las notas del usuario actual."""
    # Obtener las notas asociadas al usuario actual
    notes = (
        db.query(Notes)
        .filter(Notes.users.any(id=current_user.id))
        .offset(page * page_size)
        .limit(page_size)
        .all()
    )

    # Contar el total de notas del usuario
    total_items = db.query(Notes).filter(Notes.users.any(id=current_user.id)).count()

    return {
        "data": notes,
        "metadata": ResponseHelper.pagination_meta(page, page_size, total_items),
    }


@router.post("", response_model=NoteDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_create: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Crea una nueva nota para el usuario actual."""
    # Verificar si la categoría existe (si se proporcionó)
    if note_create.category_id:
        category = (
            db.query(Category).filter(Category.id == note_create.category_id).first()
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría especificada no existe",
            )

    # Crear la nota
    note = Notes(
        title=note_create.title,
        content=note_create.content,
        category_id=note_create.category_id,
        published=note_create.published,
    )

    # Guardar en base de datos
    db.add(note)
    db.flush()  # Para obtener el ID asignado

    # Asociar al usuario actual
    note.users.append(current_user)
    db.commit()
    db.refresh(note)

    return {"data": note}


@router.get("/{note_id}", response_model=NoteDetailResponse)
async def get_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Obtiene una nota por ID."""
    # Obtener la nota asegurándose de que pertenezca al usuario actual
    note = (
        db.query(Notes)
        .filter(Notes.id == note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada o no tienes permiso para acceder a ella",
        )

    return {"data": note}


@router.put("/{note_id}", response_model=NoteDetailResponse)
async def update_note(
    note_id: str,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Actualiza una nota por ID."""
    # Obtener la nota asegurándose de que pertenezca al usuario actual
    note = (
        db.query(Notes)
        .filter(Notes.id == note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada o no tienes permiso para actualizarla",
        )

    # Verificar si la categoría existe (si se proporciona)
    if note_update.category_id:
        category = (
            db.query(Category).filter(Category.id == note_update.category_id).first()
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría especificada no existe",
            )

    # Actualizar la nota
    updated_note = controllers.notes.update(db=db, model=note, schema=note_update)
    return {"data": updated_note}


@router.delete("/{note_id}", response_model=ResponseSchemaBase)
async def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Elimina una nota por ID."""
    # Obtener la nota asegurándose de que pertenezca al usuario actual
    note = (
        db.query(Notes)
        .filter(Notes.id == note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada o no tienes permiso para eliminarla",
        )

    # Eliminar archivos adjuntos relacionados
    attachments = db.query(Attachment).filter(Attachment.note_id == note_id).all()
    for attachment in attachments:
        # Eliminar el archivo físico
        try:
            os.remove(attachment.file_path)
        finally:
            db.delete(attachment)

    # Eliminar la nota
    db.delete(note)
    db.commit()

    return {"message": "Nota y archivos adjuntos eliminados correctamente"}


@router.post("/{note_id}/share/{user_id}", response_model=ResponseSchemaBase)
async def share_note(
    note_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Comparte una nota con otro usuario."""
    # Verificar que la nota exista y pertenezca al usuario actual
    note = (
        db.query(Notes)
        .filter(Notes.id == note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada o no tienes permiso para compartirla",
        )

    # Verificar que el usuario exista
    user_to_share = db.query(User).filter(User.id == user_id).first()
    if not user_to_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # Verificar que la nota no esté ya compartida con el usuario
    if user_to_share in note.users:
        return {"message": "La nota ya está compartida con este usuario"}

    # Compartir la nota
    note.users.append(user_to_share)
    db.commit()

    return {"message": "Nota compartida correctamente"}


@router.delete("/{note_id}/share/{user_id}", response_model=ResponseSchemaBase)
async def unshare_note(
    note_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Deja de compartir una nota con otro usuario."""
    # Verificar que la nota exista y pertenezca al usuario actual
    note = (
        db.query(Notes)
        .filter(Notes.id == note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada o no tienes permiso para modificar su compartición",
        )

    # Verificar que el usuario exista
    user_to_unshare = db.query(User).filter(User.id == user_id).first()
    if not user_to_unshare:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # No permitir quitar al propietario original (asumiendo que es el que la creó primero)
    if len(note.users) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede quitar al último usuario con acceso a la nota",
        )

    # Verificar que la nota esté compartida con el usuario
    if user_to_unshare not in note.users:
        return {"message": "La nota no está compartida con este usuario"}

    # Dejar de compartir la nota
    note.users.remove(user_to_unshare)
    db.commit()

    return {"message": "Se ha dejado de compartir la nota con el usuario"}


# UPLOADS AND ATTACHMENTS

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/{note_id}/attachments", response_model=AttachmentDetailResponse)
async def create_attachment(
    note_id: str,
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Sube un archivo y lo adjunta a una nota.
    """
    # Verificar que la nota exista y pertenezca al usuario actual
    note = (
        db.query(Notes)
        .filter(Notes.id == note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada o no tienes permiso para adjuntar archivos",
        )

    # Crear directorio para el usuario si no existe
    user_upload_dir = UPLOAD_DIR / current_user.id
    user_upload_dir.mkdir(exist_ok=True)

    # Generar nombre de archivo único
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{file_id}{file_extension}"
    file_path = user_upload_dir / safe_filename

    # Guardar el archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Crear registro en la base de datos
    attachment = Attachment(
        filename=file.filename,
        file_path=str(file_path),
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type or "application/octet-stream",
        description=description,
        note_id=note_id,
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return {"data": attachment}


@router.get("/{note_id}/attachments", response_model=AttachmentListResponse)
async def get_attachments(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Obtiene todos los archivos adjuntos a una nota.
    """
    # Verificar que la nota exista y pertenezca al usuario actual
    note = (
        db.query(Notes)
        .filter(Notes.id == note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada o no tienes permiso para ver sus adjuntos",
        )

    # Obtener adjuntos
    attachments = db.query(Attachment).filter(Attachment.note_id == note_id).all()

    return {"data": attachments, "metadata": {"total_items": len(attachments)}}


@router.get("/attachments/{attachment_id}", response_model=AttachmentDetailResponse)
async def get_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Obtiene un archivo adjunto específico.
    """
    # Obtener el adjunto y verificar permisos
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo adjunto no encontrado",
        )

    # Verificar que el usuario tenga acceso a la nota asociada
    note = (
        db.query(Notes)
        .filter(Notes.id == attachment.note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este archivo adjunto",
        )

    return {"data": attachment}


@router.delete("/attachments/{attachment_id}", response_model=ResponseSchemaBase)
async def delete_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """
    Elimina un archivo adjunto.
    """
    # Obtener el adjunto y verificar permisos
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo adjunto no encontrado",
        )

    # Verificar que el usuario tenga acceso a la nota asociada
    note = (
        db.query(Notes)
        .filter(Notes.id == attachment.note_id, Notes.users.any(id=current_user.id))
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este archivo adjunto",
        )

    # Eliminar el archivo físico
    try:
        os.remove(attachment.file_path)
    finally:
        db.delete(attachment)
        db.commit()

    return {"message": "Archivo adjunto eliminado correctamente"}
