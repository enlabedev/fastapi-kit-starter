from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Esquema base para usuarios"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class UserCreate(UserBase):
    """Esquema para creación de usuarios"""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Esquema para actualización de usuarios"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class UserInDB(UserBase):
    """Esquema para usuario en la base de datos"""

    id: str
    hashed_password: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class UserResponse(UserBase):
    """Esquema para respuesta de usuario"""

    id: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class UserListResponse(BaseModel):
    """Esquema para lista de usuarios"""

    data: List[UserResponse]
    metadata: dict


class UserDetailResponse(BaseModel):
    """Esquema para detalle de usuario"""

    data: UserResponse
