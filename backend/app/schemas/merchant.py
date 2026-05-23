from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MerchantBase(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=100, description="商家名称")
    contact_phone: str = Field(..., description="联系电话")
    address: str = Field(..., max_length=255, description="商家地址")
    description: str | None = Field(None, description="商家描述")


class MerchantCreate(MerchantBase):
    pass


class MerchantUpdate(BaseModel):
    business_name: str | None = Field(None, min_length=2, max_length=100)
    contact_phone: str | None = Field(None)
    address: str | None = Field(None, max_length=255)
    description: str | None = Field(None)
    logo: str | None = Field(None, max_length=255)


class MerchantResponse(MerchantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    logo: str | None = None
    status: str
    rejection_reason: str | None = None
    approved_by: int | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
