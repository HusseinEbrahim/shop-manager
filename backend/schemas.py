from typing import Literal
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: str | None = None
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(ge=0, default=0)
    low_stock_threshold: int = Field(ge=0, default=10)
    supplier: str | None = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = None
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)
    supplier: str | None = None

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class SaleCreate(BaseModel):
    customer_name: str | None = Field(default=None, max_length=100)
    items: list[SaleItemCreate] = Field(min_length=1)

class SaleItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)

class SaleResponse(BaseModel):
    id: int
    customer_name: str | None
    total_amount: Decimal
    created_at: datetime
    items: list[SaleItemResponse]

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: Literal["owner", "staff"] = "staff"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str