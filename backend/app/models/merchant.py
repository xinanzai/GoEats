from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(100), nullable=False, index=True)
    contact_phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    logo = Column(String(255), nullable=True)
    status = Column(Enum("pending", "approved", "rejected", name="merchant_status"), default="pending")
    rejection_reason = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="merchant_profile", foreign_keys="[Merchant.user_id]")
    categories = relationship("Category", back_populates="merchant")
    products = relationship("Product", back_populates="merchant")
    orders = relationship("Order", back_populates="merchant")

    def __repr__(self):
        return f"<Merchant(id={self.id}, name='{self.business_name}')>"
