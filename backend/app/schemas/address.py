from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AddressBase(BaseModel):
    receiver: str = Field(..., min_length=1, max_length=50, description="收货人")
    phone: str = Field(..., description="联系电话")
    province: str = Field(..., max_length=50, description="省")
    city: str = Field(..., max_length=50, description="市")
    district: str = Field(..., max_length=50, description="区")
    detail_address: str = Field(..., max_length=255, description="详细地址")
    is_default: bool = Field(False, description="是否默认地址")


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    receiver: str | None = Field(None, min_length=1, max_length=50)
    phone: str | None = Field(None)
    province: str | None = Field(None, max_length=50)
    city: str | None = Field(None, max_length=50)
    district: str | None = Field(None, max_length=50)
    detail_address: str | None = Field(None, max_length=255)
    is_default: bool | None = Field(None)


class AddressResponse(AddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
