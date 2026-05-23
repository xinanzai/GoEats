from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(..., gt=0, description="数量")


class OrderCreate(BaseModel):
    merchant_id: int = Field(..., description="商家ID")
    address_id: int = Field(..., description="收货地址ID")
    items: list[OrderItemCreate] = Field(..., description="订单项列表")
    remark: str | None = Field(None, max_length=500, description="备注")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    product_image: str | None = None
    price: Decimal
    quantity: int
    subtotal: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    user_id: int
    merchant_id: int
    address_id: int
    receiver: str
    receiver_phone: str
    receiver_address: str
    total_price: Decimal
    discount_amount: Decimal
    delivery_fee: Decimal
    pay_amount: Decimal
    status: str
    paid_at: datetime | None = None
    completed_at: datetime | None = None
    cancel_reason: str | None = None
    remark: str | None = None
    items: list[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime
