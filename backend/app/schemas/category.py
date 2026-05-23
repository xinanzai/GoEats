from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    sort_order: int = Field(0, description="排序")


class CategoryCreate(CategoryBase):
    merchant_id: int | None = Field(None, description="商家ID")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    sort_order: int | None = Field(None)


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    merchant_id: int
    created_at: datetime
