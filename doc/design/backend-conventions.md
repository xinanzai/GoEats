# 后端代码规范

> **版本**: v1.0
> **更新日期**: 2026-05-24
> **适用范围**: GoEats 后端项目 (backend/)

---

## 目录

- [命名规范](#命名规范)
- [代码结构规范](#代码结构规范)
- [类型注解规范](#类型注解规范)
- [文档字符串规范](#文档字符串规范)
- [异常处理规范](#异常处理规范)
- [日志规范](#日志规范)
- [异步编程规范](#异步编程规范)
- [SQLAlchemy 模型规范](#sqlalchemy-模型规范)
- [Pydantic Schema 规范](#pydantic-schema-规范)
- [Service 层规范](#service-层规范)

---

## 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/包名 | 小写，下划线分隔 | `user_service.py`, `order_service.py` |
| 类名 | PascalCase | `UserService`, `OrderRepository` |
| 函数/方法名 | 小写，下划线分隔 | `get_user_by_id()`, `create_order()` |
| 变量名 | 小写，下划线分隔 | `user_id`, `order_list` |
| 常量名 | 全大写，下划线分隔 | `MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE` |
| 私有方法/属性 | 单下划线前缀 | `_validate_token()`, `_cache_data` |
| 数据库表名 | 小写，下划线分隔，复数 | `users`, `order_items` |
| 数据库字段名 | 小写，下划线分隔 | `created_at`, `business_name` |
| API 路由 | 小写，中划线分隔 | `/api/v1/order-items` |

---

## 代码结构规范

### 文件组织

每个 Python 文件应遵循以下顺序：

```python
# 1. 标准库导入
import os
import datetime
from typing import List, Optional

# 2. 第三方库导入（空一行）
from fastapi import Depends, HTTPException
from sqlalchemy import Column, Integer, String

# 3. 项目内部导入（空一行）
from app.database import get_db
from app.schemas.user import UserCreate
from app.core.security import hash_password
```

### 文件长度限制

- 单个 Python 文件不超过 **300 行**
- 单个函数不超过 **50 行**
- 单个类的公共方法不超过 **10 个**
- 超过限制时应考虑拆分为多个模块

### 导入规范

- 禁止使用通配符导入：`from module import *`
- 相对导入使用 `.` 前缀：`from .database import get_db`
- 避免循环导入，使用依赖注入解决

---

## 类型注解规范

所有函数必须添加类型注解：

```python
# ✅ 正确
async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

# ❌ 错误
async def get_user_by_id(user_id, db):
    return db.query(User).filter(User.id == user_id).first()
```

---

## 文档字符串规范

使用 Google 风格文档字符串：

```python
async def create_order(
    order_data: OrderCreate,
    current_user: User,
    db: Session
) -> Order:
    """创建新订单。

    Args:
        order_data: 订单创建数据。
        current_user: 当前登录用户。
        db: 数据库会话。

    Returns:
        创建的订单对象。

    Raises:
        ValueError: 当商品库存不足时。
        HTTPException: 当用户地址不存在时。
    """
```

---

## 异常处理规范

### 自定义异常

```python
# core/exceptions.py

class AppException(HTTPException):
    """应用基础异常"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(status_code=code, detail=message)

class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            code=404,
            message=f"{resource} {resource_id} 不存在"
        )

class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__(code=400, message=message)

class PermissionException(AppException):
    def __init__(self, message: str = "没有权限执行此操作"):
        super().__init__(code=403, message=message)
```

### 异常处理原则

- 禁止裸 `except:` 语句
- 捕获具体异常类型
- 记录异常日志后向上抛出
- 不要在异常处理中吞掉异常

```python
# ✅ 正确
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"值错误: {e}")
    raise ValidationException(f"参数错误: {e}")

# ❌ 错误
try:
    result = risky_operation()
except:
    pass  # 永远不要这样做
```

---

## 日志规范

```python
import logging

logger = logging.getLogger(__name__)

# 日志级别使用规范
logger.debug("调试信息 - 仅在开发环境")
logger.info("正常操作信息")
logger.warning("警告信息 - 非错误但需要关注")
logger.error("错误信息 - 操作失败")
logger.critical("严重错误 - 系统可能无法继续运行")
```

---

## 异步编程规范

```python
# ✅ 正确 - 使用 async/await
async def get_user(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# ✅ 正确 - 调用异步函数时使用 await
user = await get_user(user_id, db)

# ❌ 错误 - 忘记 await
user = get_user(user_id, db)  # 返回 coroutine 对象
```

---

## SQLAlchemy 模型规范

```python
# models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    role = Column(
        Enum('user', 'merchant', 'admin', name='user_role'),
        nullable=False,
        default='user'
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # 关系定义
    addresses = relationship("Address", back_populates="user", lazy="selectin")
    orders = relationship("Order", back_populates="user", lazy="selectin")
    merchant = relationship("Merchant", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

---

## Pydantic Schema 规范

```python
# schemas/user.py
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

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
```

---

## Service 层规范

- 所有业务逻辑必须在 Service 层处理，API 层只负责参数接收和响应返回
- Service 类通过依赖注入获取数据库会话
- 每个领域实体应有独立的 Service 类
- Service 方法应抛出业务异常，由全局异常处理器统一处理

---

## 相关文档

- [前端代码规范](./frontend-conventions.md) - 前端开发规范
- [API 设计规范](./api-design.md) - API 接口规范
- [数据库设计规范](./database-design.md) - 数据库设计原则
