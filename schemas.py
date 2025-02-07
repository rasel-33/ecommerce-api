# schemas.py
from typing import List

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserOut(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        orm_mode = True


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)

class CategoryOut(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    stock: int
    category_id: int

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: int
    stock: int
    category_id: int

    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemOut(BaseModel):
    id: int
    cart_id: int
    user_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    total_price: int

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    items: List[OrderItemOut]
    total_price: int
    status: str

    class Config:
        from_attributes = True