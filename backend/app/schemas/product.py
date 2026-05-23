from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    description: str | None = Field(None, description="商品描述")
    price: Decimal = Field(..., description="价格")
    original_price: Decimal | None = Field(None, description="原价")
    stock: int = Field(0, description="库存，0表示不限")
    is_available: bool = Field(True, description="是否上架")
    sort_order: int = Field(0, description="排序")


class ProductCreate(ProductBase):
    category_id: int = Field(..., description="分类ID")


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None)
    price: Decimal | None = Field(None)
    original_price: Decimal | None = Field(None)
    image_url: str | None = Field(None, max_length=255)
    images: str | None = Field(None)
    stock: int | None = Field(None)
    is_available: bool | None = Field(None)
    sort_order: int | None = Field(None)


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    merchant_id: int
    category_id: int
    image_url: str | None = None
    images: str | None = None
    created_at: datetime
    updated_at: datetime
