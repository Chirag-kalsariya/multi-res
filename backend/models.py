from pydantic import BaseModel
from typing import Optional, Generic, TypeVar

T = TypeVar('T')


class StandardErrorResponse(BaseModel):
    status: bool = False
    message: str


class StandardApiResponse(BaseModel, Generic[T]):
    status: bool
    message: str
    data: Optional[T] = None
