from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    receiver = Column(String(50), nullable=False)  # Snapshot at order time
    receiver_phone = Column(String(20), nullable=False)
    receiver_address = Column(String(500), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    delivery_fee = Column(Numeric(10, 2), default=0)
    pay_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        Enum(
            "pending", "paid", "preparing", "delivering",
            "completed", "cancelled", "refunded",
            name="order_status"
        ),
        default="pending"
    )
    paid_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancel_reason = Column(String(255), nullable=True)
    remark = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="orders")
    merchant = relationship("Merchant", back_populates="orders")
    address = relationship("Address", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, order_no='{self.order_no}')>"
