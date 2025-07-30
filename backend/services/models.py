from pydantic import BaseModel
from typing import Optional, List

class ServiceCreateModel(BaseModel):
    name: str
    description: Optional[str] = None
    price: int

class ServiceUpdateModel(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None

class ServiceResponseModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int

    class Config:
        from_attributes = True