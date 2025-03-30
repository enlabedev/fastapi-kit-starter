from typing import Optional, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


class ResponseSchemaBase(BaseModel):
    __abstract__ = True
    code: int = 200
    success: bool = True
    message: str = ""


class MetadataSchema(BaseModel):
    current_page: int
    page_size: int
    total_items: int
    next_page: Optional[int] = None
    previous_page: Optional[int] = None
    total_pages: int


class DataResponse(ResponseSchemaBase, BaseModel, Generic[T]):
    data: Optional[T] = None

    def custom(self, resp_code: str, message: str):
        self.code = resp_code
        self.message = message
        return self

    def success(self, data: T):
        self.code = "00"
        self.data = data
        return self
