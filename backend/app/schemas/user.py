import re
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    phone: str = Field(..., description="手机号")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=2, max_length=50)
    phone: str | None = Field(None)
    avatar: str | None = Field(None, max_length=255)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    avatar: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class MerchantRegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    business_name: str = Field(..., min_length=2, max_length=100, description="商家名称")
    contact_phone: str = Field(..., description="联系电话")
    address: str = Field(..., max_length=255, description="商家地址")
    description: str | None = Field(None, description="商家描述")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
