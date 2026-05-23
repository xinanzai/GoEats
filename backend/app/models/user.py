from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    role = Column(Enum("user", "merchant", "admin", name="user_role"), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")
    merchant_profile = relationship("Merchant", back_populates="user", uselist=False, foreign_keys="Merchant.user_id")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
