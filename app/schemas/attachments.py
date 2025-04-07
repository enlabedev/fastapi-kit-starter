from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AttachmentBase(BaseModel):
    """Esquema base para archivos adjuntos"""

    filename: str
    description: Optional[str] = None
    note_id: str

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class AttachmentCreate(AttachmentBase):
    """Esquema para creación de archivos adjuntos"""

    pass


class AttachmentUpdate(BaseModel):
    """Esquema para actualización de archivos adjuntos"""

    filename: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class AttachmentInDB(AttachmentBase):
    """Esquema para archivo adjunto en la base de datos"""

    id: str
    file_path: str
    file_size: int
    mime_type: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class AttachmentResponse(AttachmentBase):
    """Esquema para respuesta de archivo adjunto"""

    id: str
    file_size: int
    mime_type: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class AttachmentListResponse(BaseModel):
    """Esquema para lista de archivos adjuntos"""

    data: List[AttachmentResponse]
    metadata: dict


class AttachmentDetailResponse(BaseModel):
    """Esquema para detalle de archivo adjunto"""

    data: AttachmentResponse
