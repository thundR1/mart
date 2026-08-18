from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import EventType

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    category: str
    price: float
    image_seed: str
    stock: int


class ProductWithReason(ProductOut):
    reason: Optional[str] = None
    score: Optional[float] = None


class ActivityCreate(BaseModel):
    event_type: EventType
    product_id: Optional[int] = None
    query: Optional[str] = None


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product: ProductOut
    quantity: int


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product: ProductOut
    quantity: int
    price_at_purchase: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total: float
    created_at: datetime
    items: List[OrderItemOut]
