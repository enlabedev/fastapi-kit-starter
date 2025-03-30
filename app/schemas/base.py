from typing import Generic, Optional, TypeVar

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


class DataResponse(ResponseSchemaBase, Generic[T]):
    data: Optional[T] = None

    def custom(self, resp_code: int, message: str) -> "DataResponse":
        self.code = resp_code
        self.message = message
        return self

    def success(self, data: T) -> "DataResponse":
        self.code = 0  # Changed to an integer to match the type of `code`
        self.data = data
        self.success = True  # Ensure `success` is updated correctly
        return self
