from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Esquema base para categorías"""

    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class CategoryCreate(CategoryBase):
    """Esquema para creación de categorías"""

    pass


class CategoryUpdate(BaseModel):
    """Esquema para actualización de categorías"""

    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
    )


class CategoryInDB(CategoryBase):
    """Esquema para categoría en la base de datos"""

    id: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class CategoryResponse(CategoryBase):
    """Esquema para respuesta de categoría"""

    id: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class CategoryListResponse(BaseModel):
    """Esquema para lista de categorías"""

    data: List[CategoryResponse]
    metadata: dict


class CategoryDetailResponse(BaseModel):
    """Esquema para detalle de categoría"""

    data: CategoryResponse
