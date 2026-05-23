# 外卖点餐系统 - 完整开发计划

## 一、项目概述

### 1.1 项目简介
构建一个完整的外卖点餐系统，包含三个端：
- **平台管理端**：管理员审核商家、管理用户、查看数据统计等
- **商家端**：商家注册申请、菜品管理、订单处理、数据统计等
- **用户端**：用户注册登录、浏览商家、点餐下单、订单跟踪等

### 1.2 技术栈
- **后端**：Python + FastAPI + SQLAlchemy
- **数据库**：SQLite
- **前端**：Vue 3 + Vite + Element Plus（管理端/商家端） / Vue 3 + Vite + Vant（用户端移动端）
- **认证**：JWT Token
- **文件存储**：本地文件系统

---

## 二、系统架构设计

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                     前端层 (Frontend)                     │
├──────────────┬──────────────────┬───────────────────────┤
│  平台管理端   │     商家端        │      用户端           │
│  (Vue+Elem)  │    (Vue+Elem)    │    (Vue+Vant)        │
└──────┬───────┴────────┬─────────┴──────────┬────────────┘
       │                │                    │
       └────────────────┼────────────────────┘
                        │
┌───────────────────────┼─────────────────────────────────┐
│                 API 网关层 (FastAPI)                      │
├───────────────────────┼─────────────────────────────────┤
│                     业务逻辑层 (Services)                  │
├───────────────────────┼─────────────────────────────────┤
│                   数据访问层 (Repository)                  │
├───────────────────────┼─────────────────────────────────┤
│                   SQLite 数据库                           │
└───────────────────────┴─────────────────────────────────┘
```

### 2.2 项目目录结构
```
food-delivery/
├── backend/                      # 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── merchant.py
│   │   │   ├── category.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   └── ...
│   │   ├── schemas/             # Pydantic 数据验证模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── merchant.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   └── ...
│   │   ├── api/                 # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── router.py        # 路由聚合
│   │   │   └── endpoints/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── merchants.py
│   │   │       ├── categories.py
│   │   │       ├── products.py
│   │   │       ├── orders.py
│   │   │       ├── admin.py
│   │   │       └── ...
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── merchant_service.py
│   │   │   ├── product_service.py
│   │   │   ├── order_service.py
│   │   │   └── ...
│   │   ├── core/                # 核心功能
│   │   │   ├── security.py      # 密码加密、JWT
│   │   │   ├── dependencies.py  # 依赖注入
│   │   │   └── exceptions.py    # 自定义异常
│   │   ├── utils/               # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py
│   │   │   └── ...
│   │   └── middleware/          # 中间件
│   │       ├── __init__.py
│   │       └── ...
│   ├── migrations/              # 数据库迁移 (可选)
│   ├── tests/                   # 测试文件
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── ...
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── admin/                   # 平台管理端
│   │   ├── src/
│   │   │   ├── api/
│   │   │   ├── views/
│   │   │   ├── components/
│   │   │   ├── router/
│   │   │   ├── store/
│   │   │   └── ...
│   │   ├── package.json
│   │   └── ...
│   ├── merchant/                # 商家端
│   │   ├── src/
│   │   │   ├── api/
│   │   │   ├── views/
│   │   │   ├── components/
│   │   │   ├── router/
│   │   │   ├── store/
│   │   │   └── ...
│   │   ├── package.json
│   │   └── ...
│   └── user/                    # 用户端
│       ├── src/
│       │   ├── api/
│       │   ├── views/
│       │   ├── components/
│       │   ├── router/
│       │   ├── store/
│       │   └── ...
│       ├── package.json
│       └── ...
└── docs/                        # 文档
    └── development-plan.md      # 本文档
```

---

## 三、数据模型设计

### 3.1 ER 关系图
```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   User      │     │   Merchant       │     │  Category   │
├─────────────┤     ├──────────────────┤     ├─────────────┤
│ id          │     │ id               │     │ id          │
│ username    │     │ user_id (FK)     │     │ name        │
│ phone       │─────│ business_name    │     │ merchant_id │
│ password    │     │ contact_phone    │     │   (FK)      │
│ avatar      │     │ address          │     │ sort_order  │
│ role        │     │ status           │     └─────────────┘
│ created_at  │     │ created_at       │              ▲
│ updated_at  │     │ approved_at      │              │
└─────────────┘     │ approved_by      │     ┌────────┴────────┐
                    └──────────────────┘     │   Product       │
┌─────────────┐                              ├─────────────────┤
│   Address   │     ┌──────────────┐        │ id              │
├─────────────┤     │    Order     │        │ name            │
│ id          │     ├──────────────┤        │ description     │
│ user_id(FK) │─────│ id           │        │ category_id(FK) │
│ receiver    │     │ user_id(FK)  │        │ merchant_id(FK) │
│ phone       │     │ merchant_id  │        │ price           │
│ address     │     │   (FK)       │        │ image_url       │
│ is_default  │     │ address_id   │        │ stock           │
└─────────────┘     │   (FK)       │        │ is_available    │
                    │ total_price  │        │ sort_order      │
                    │ status       │        │ created_at      │
                    │ created_at   │        │ updated_at      │
                    │ updated_at   │        └─────────────────┘
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │  OrderItem   │
                    ├──────────────┤
                    │ id           │
                    │ order_id(FK) │
                    │ product_id   │
                    │   (FK)       │
                    │ quantity     │
                    │ price        │
                    └──────────────┘
```

### 3.2 详细数据模型

#### 3.2.1 用户模型 (User)
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    role = Column(Enum('user', 'merchant', 'admin'), nullable=False, default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 3.2.2 商家模型 (Merchant)
```python
class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(100), nullable=False, index=True)
    contact_phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    logo = Column(String(255), nullable=True)
    # 审批状态: pending-待审核, approved-已通过, rejected-已拒绝
    status = Column(Enum('pending', 'approved', 'rejected'), default='pending')
    rejection_reason = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 3.2.3 分类模型 (Category)
```python
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 3.2.4 商品模型 (Product)
```python
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)  # 原价，用于展示折扣
    image_url = Column(String(255), nullable=True)
    images = Column(Text, nullable=True)  # JSON 数组，多张图片
    stock = Column(Integer, default=0)  # 0表示不限库存
    is_available = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 3.2.5 用户地址模型 (Address)
```python
class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    province = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    detail_address = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 3.2.6 订单模型 (Order)
```python
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)  # 订单编号
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    receiver = Column(String(50), nullable=False)  # 下单时快照
    receiver_phone = Column(String(20), nullable=False)  # 下单时快照
    receiver_address = Column(String(500), nullable=False)  # 下单时快照
    total_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)  # 优惠金额
    delivery_fee = Column(Numeric(10, 2), default=0)  # 配送费
    pay_amount = Column(Numeric(10, 2), nullable=False)  # 实付金额
    # 订单状态: pending-待付款, paid-已付款, preparing-制作中, 
    #          delivering-配送中, completed-已完成, cancelled-已取消, refunded-已退款
    status = Column(Enum('pending', 'paid', 'preparing', 'delivering', 
                         'completed', 'cancelled', 'refunded'), default='pending')
    paid_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancel_reason = Column(String(255), nullable=True)
    remark = Column(String(500), nullable=True)  # 用户备注
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 3.2.7 订单项模型 (OrderItem)
```python
class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(100), nullable=False)  # 下单时快照
    product_image = Column(String(255), nullable=True)  # 下单时快照
    price = Column(Numeric(10, 2), nullable=False)  # 下单时价格快照
    quantity = Column(Integer, nullable=False, default=1)
    subtotal = Column(Numeric(10, 2), nullable=False)  # 小计
```

#### 3.2.8 商家评价模型 (Review) - 可选扩展
```python
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5分
    comment = Column(Text, nullable=True)
    images = Column(Text, nullable=True)  # JSON 数组
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 四、数据库设计

### 4.1 SQLite 表结构设计

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'merchant', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_phone ON users(phone);

-- 商家表
CREATE TABLE merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    business_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    description TEXT,
    logo VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
    rejection_reason VARCHAR(255),
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_merchants_business_name ON merchants(business_name);
CREATE INDEX idx_merchants_status ON merchants(status);
CREATE INDEX idx_merchants_user_id ON merchants(user_id);

-- 分类表
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    name VARCHAR(50) NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_merchant_id ON categories(merchant_id);

-- 商品表
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2),
    image_url VARCHAR(255),
    images TEXT,
    stock INTEGER NOT NULL DEFAULT 0,
    is_available BOOLEAN NOT NULL DEFAULT 1,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_merchant_id ON products(merchant_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_available ON products(is_available);

-- 用户地址表
CREATE TABLE addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    receiver VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    detail_address VARCHAR(255) NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_addresses_user_id ON addresses(user_id);

-- 订单表
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    address_id INTEGER NOT NULL REFERENCES addresses(id),
    receiver VARCHAR(50) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    receiver_address VARCHAR(500) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    delivery_fee DECIMAL(10, 2) NOT NULL DEFAULT 0,
    pay_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK(status IN ('pending', 'paid', 'preparing', 'delivering', 'completed', 'cancelled', 'refunded')),
    paid_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancel_reason VARCHAR(255),
    remark VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_merchant_id ON orders(merchant_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- 订单项表
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    product_name VARCHAR(100) NOT NULL,
    product_image VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    subtotal DECIMAL(10, 2) NOT NULL
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- 评价表 (可选)
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    images TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_merchant_id ON reviews(merchant_id);
CREATE INDEX idx_reviews_order_id ON reviews(order_id);
```

### 4.2 分表策略说明

由于使用 SQLite，以下场景需要考虑数据量增长后的优化：

| 表名 | 预计增长速度 | 优化策略 |
|------|-------------|---------|
| users | 中等 | 当前设计可满足，按用户名/手机号索引查询 |
| merchants | 中等 | 按状态索引，便于审核查询 |
| orders | 快速 | 按创建时间索引，可考虑按月归档历史订单 |
| order_items | 快速 | 跟随订单表，按订单ID索引 |
| products | 中等 | 按商家ID和分类ID联合索引 |

**历史数据归档策略**（可选扩展）：
- 完成超过 6 个月的订单可迁移至 `orders_archive` 表
- 保留主表最近 6 个月数据保证查询性能

---

## 五、后端模型设计

### 5.1 SQLAlchemy ORM 模型

使用 SQLAlchemy 2.0 风格定义模型，位于 `backend/app/models/` 目录下。

### 5.2 Pydantic Schema 设计

每个模型对应以下 Schema：

```python
# 示例：用户 Schema (schemas/user.py)

class UserBase(BaseModel):
    username: str
    phone: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    phone: str | None = None
    avatar: str | None = None

class UserResponse(UserBase):
    id: int
    avatar: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

### 5.3 依赖注入设计

```python
# core/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.database import get_db
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的令牌")
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """验证管理员权限"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

async def get_current_merchant(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> User:
    """验证商家权限"""
    if current_user.role != "merchant":
        raise HTTPException(status_code=403, detail="需要商家权限")
    return current_user
```

---

## 六、API 接口设计

### 6.1 API 规范
- 基础路径：`/api/v1`
- 认证方式：Bearer Token (JWT)
- 数据格式：JSON
- 统一响应格式：
```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

错误响应：
```json
{
    "code": 400,
    "message": "错误信息",
    "data": null
}
```

### 6.2 认证接口 (/api/v1/auth)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /auth/login | 用户登录 | 公开 |
| POST | /auth/register | 用户注册 | 公开 |
| POST | /auth/merchant/register | 商家注册 | 公开 |
| POST | /auth/refresh | 刷新令牌 | 已登录 |
| POST | /auth/logout | 登出 | 已登录 |
| GET | /auth/me | 获取当前用户信息 | 已登录 |

### 6.3 用户接口 (/api/v1/users)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /users/profile | 获取个人信息 | 已登录 |
| PUT | /users/profile | 更新个人信息 | 已登录 |
| PUT | /users/password | 修改密码 | 已登录 |
| POST | /users/avatar | 上传头像 | 已登录 |
| GET | /users/addresses | 获取地址列表 | 已登录 |
| POST | /users/addresses | 添加地址 | 已登录 |
| GET | /users/addresses/{id} | 获取地址详情 | 已登录 |
| PUT | /users/addresses/{id} | 更新地址 | 已登录 |
| DELETE | /users/addresses/{id} | 删除地址 | 已登录 |
| PUT | /users/addresses/{id}/set-default | 设为默认地址 | 已登录 |

### 6.4 商家接口 (/api/v1/merchants)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /merchants | 商家列表（分页、搜索） | 公开 |
| GET | /merchants/{id} | 商家详情 | 公开 |
| GET | /merchants/me | 当前商家信息 | 商家 |
| PUT | /merchants/me | 更新商家信息 | 商家 |
| POST | /merchants/me/logo | 上传商家logo | 商家 |
| GET | /merchants/me/categories | 获取分类列表 | 商家 |
| POST | /merchants/me/categories | 添加分类 | 商家 |
| PUT | /merchants/me/categories/{id} | 更新分类 | 商家 |
| DELETE | /merchants/me/categories/{id} | 删除分类 | 商家 |
| GET | /merchants/{id}/categories | 获取商家分类 | 公开 |

### 6.5 商品接口 (/api/v1/products)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /products | 商品列表（分页、筛选） | 公开 |
| GET | /products/{id} | 商品详情 | 公开 |
| GET | /merchants/me/products | 我的商品列表 | 商家 |
| POST | /merchants/me/products | 添加商品 | 商家 |
| GET | /merchants/me/products/{id} | 商品详情 | 商家 |
| PUT | /merchants/me/products/{id} | 更新商品 | 商家 |
| DELETE | /merchants/me/products/{id} | 删除商品 | 商家 |
| PUT | /merchants/me/products/{id}/toggle | 上架/下架商品 | 商家 |
| POST | /merchants/me/products/{id}/images | 上传商品图片 | 商家 |

### 6.6 订单接口 (/api/v1/orders)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /orders | 创建订单 | 已登录用户 |
| GET | /users/orders | 我的订单列表 | 已登录用户 |
| GET | /users/orders/{id} | 订单详情 | 已登录用户 |
| POST | /users/orders/{id}/cancel | 取消订单 | 已登录用户 |
| POST | /users/orders/{id}/pay | 支付订单 | 已登录用户 |
| POST | /users/orders/{id}/review | 评价订单 | 已登录用户 |
| GET | /merchants/me/orders | 商家订单列表 | 商家 |
| GET | /merchants/me/orders/{id} | 订单详情 | 商家 |
| PUT | /merchants/me/orders/{id}/status | 更新订单状态 | 商家 |
| POST | /merchants/me/orders/{id}/prepare | 开始制作 | 商家 |
| POST | /merchants/me/orders/{id}/deliver | 开始配送 | 商家 |
| POST | /merchants/me/orders/{id}/complete | 完成订单 | 商家 |

### 6.7 管理后台接口 (/api/v1/admin)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /admin/dashboard | 仪表盘数据 | 管理员 |
| GET | /admin/users | 用户列表 | 管理员 |
| GET | /admin/users/{id} | 用户详情 | 管理员 |
| PUT | /admin/users/{id} | 更新用户信息 | 管理员 |
| PUT | /admin/users/{id}/status | 启用/禁用用户 | 管理员 |
| GET | /admin/merchants | 商家列表 | 管理员 |
| GET | /admin/merchants/{id} | 商家详情 | 管理员 |
| PUT | /admin/merchants/{id}/approve | 审批商家（通过） | 管理员 |
| PUT | /admin/merchants/{id}/reject | 审批商家（拒绝） | 管理员 |
| GET | /admin/orders | 订单列表 | 管理员 |
| GET | /admin/orders/{id} | 订单详情 | 管理员 |
| GET | /admin/statistics | 统计数据 | 管理员 |

---

## 七、前端页面设计

### 7.1 平台管理端 (Admin)

**技术栈**：Vue 3 + Vite + Element Plus + Pinia + Vue Router + Axios

**页面结构**：

#### 7.1.1 登录页 (/admin/login)
- 账号密码登录表单
- 记住密码功能

#### 7.1.2 首页/仪表盘 (/admin/dashboard)
- 统计卡片：总用户数、总商家数、总订单数、今日订单数
- 订单趋势图表（折线图）
- 商家增长图表（柱状图）
- 最近订单列表

#### 7.1.3 用户管理 (/admin/users)
- 用户列表（表格展示，支持搜索、分页）
- 用户详情（弹窗或详情页）
- 启用/禁用用户操作
- 用户角色查看

#### 7.1.4 商家管理 (/admin/merchants)
- 商家列表（表格展示，支持搜索、分页、按状态筛选）
- 待审核商家列表
- 商家详情查看
- 商家审批操作（通过/拒绝，填写拒绝原因）

#### 7.1.5 订单管理 (/admin/orders)
- 订单列表（表格展示，支持搜索、分页、按状态/时间筛选）
- 订单详情查看
- 订单状态追踪

#### 7.1.6 数据统计 (/admin/statistics)
- 订单统计（按日/周/月）
- 商家统计
- 用户统计
- 热销商品排行

### 7.2 商家端 (Merchant)

**技术栈**：Vue 3 + Vite + Element Plus + Pinia + Vue Router + Axios

**页面结构**：

#### 7.2.1 注册页 (/merchant/register)
- 商家注册表单
  - 手机号、验证码
  - 设置密码
  - 店铺名称
  - 联系人电话
  - 店铺地址
  - 店铺描述

#### 7.2.2 登录页 (/merchant/login)
- 手机号密码登录

#### 7.2.3 审核等待页 (/merchant/pending)
- 显示审核状态
- 如被拒绝，显示拒绝原因

#### 7.2.4 首页/仪表盘 (/merchant/dashboard)
- 今日订单数、待处理订单数
- 今日收入统计
- 最近订单列表
- 待处理订单提醒

#### 7.2.5 商品管理 (/merchant/products)
- 商品列表（表格/卡片展示）
- 添加商品（弹窗表单）
  - 商品名称、描述
  - 选择分类
  - 价格、原价
  - 上传图片
  - 库存设置
  - 上架/下架状态
- 编辑商品
- 删除商品
- 批量上架/下架

#### 7.2.6 分类管理 (/merchant/categories)
- 分类列表
- 添加/编辑/删除分类
- 分类排序

#### 7.2.7 订单管理 (/merchant/orders)
- 订单列表（按状态 Tab 切换：待付款、制作中、配送中、已完成、已取消）
- 订单详情
- 订单操作：
  - 开始制作（paid → preparing）
  - 开始配送（preparing → delivering）
  - 完成订单（delivering → completed）
  - 拒绝订单（填写原因）

#### 7.2.8 店铺设置 (/merchant/settings)
- 店铺基本信息编辑
- Logo 上传
- 店铺描述修改
- 联系方式修改
- 店铺地址修改

### 7.3 用户端 (User)

**技术栈**：Vue 3 + Vite + Vant (移动端 UI) + Pinia + Vue Router + Axios

**页面结构**：

#### 7.3.1 注册/登录页 (/user/login, /user/register)
- 手机号验证码注册
- 手机号密码登录
- 第三方登录（可选扩展）

#### 7.3.2 首页 (/user/home)
- 搜索栏（搜索商家/商品）
- Banner 轮播（可选）
- 商家列表（按距离/评分/销量排序）
- 商家卡片：Logo、名称、评分、起送价、配送费

#### 7.3.3 商家详情页 (/user/merchant/:id)
- 商家信息头图
- 商家基本信息（名称、描述、评分、月售）
- 分类导航（侧边栏固定）
- 商品列表（按分类分组）
- 购物车浮窗
- 加入购物车按钮

#### 7.3.4 购物车页 (/user/cart)
- 已选商品列表
- 数量调整
- 删除商品
- 商品小计
- 底部结算栏（总价、去结算按钮）

#### 7.3.5 确认订单页 (/user/checkout)
- 地址选择（可添加新地址）
- 商品清单
- 金额明细（商品总价、优惠、配送费、实付）
- 备注输入
- 提交订单按钮

#### 7.3.6 订单确认页 (/user/order-created/:id)
- 订单信息展示
- 倒计时支付提醒
- 去支付按钮

#### 7.3.7 订单列表页 (/user/orders)
- 订单状态 Tab（全部、待付款、制作中、配送中、已完成）
- 订单卡片列表
- 订单操作按钮（取消、支付、查看详情等）

#### 7.3.8 订单详情页 (/user/order/:id)
- 订单状态进度条
- 商家信息
- 商品清单
- 金额明细
- 收货地址
- 订单操作

#### 7.3.9 个人中心 (/user/profile)
- 用户信息展示
- 我的订单入口
- 我的地址
- 设置
- 退出登录

#### 7.3.10 地址管理 (/user/addresses)
- 地址列表
- 添加/编辑地址
- 设置默认地址
- 删除地址

---

## 八、核心业务流程

### 8.1 商家注册审批流程
```
商家填写注册信息 
    → 提交注册申请 (status=pending)
    → 商家登录显示"等待审核"
    → 管理员查看待审核商家
    → 管理员审批（通过/拒绝）
    → 通过：status=approved，商家可管理店铺
    → 拒绝：status=rejected，填写拒绝原因
```

### 8.2 用户点餐下单流程
```
用户浏览商家列表
    → 进入商家详情页
    → 浏览商品，加入购物车
    → 进入购物车，确认商品
    → 选择/填写收货地址
    → 确认订单，提交订单 (status=pending)
    → 支付订单 (status=paid)
    → 商家收到订单通知
```

### 8.3 订单处理流程
```
商家查看待处理订单
    → 开始制作 (status=preparing)
    → 制作完成，开始配送 (status=delivering)
    → 用户确认收货 (status=completed)
    → 用户评价订单（可选）
```

### 8.4 订单状态流转图
```
pending → paid → preparing → delivering → completed
   ↓        ↓                                       ↓
 cancelled                         cancelled       reviewed
                                      ↓
                                 refunded
```

---

## 九、开发阶段规划

### 第一阶段：基础框架搭建

**目标**：完成项目初始化、数据库设计、基础模型和认证系统

**后端任务**：
1. 初始化 FastAPI 项目结构
2. 配置 SQLite 数据库连接
3. 创建所有数据模型 (models)
4. 创建 Pydantic Schema
5. 实现 JWT 认证系统
6. 实现用户注册/登录接口
7. 实现基础依赖注入和权限验证

**前端任务**：
1. 初始化三个前端项目（admin、merchant、user）
2. 配置路由、状态管理、HTTP 请求封装
3. 实现登录/注册页面
4. 实现基础布局组件

**交付物**：
- 可运行的后端服务
- 用户注册登录功能可用
- 三个前端项目可正常访问

---

### 第二阶段：平台管理端开发

**目标**：完成平台管理端核心功能

**后端任务**：
1. 实现商家注册接口
2. 实现商家审批接口
3. 实现用户管理接口
4. 实现订单管理接口
5. 实现数据统计接口
6. 实现文件上传接口

**前端任务（admin）**：
1. 实现仪表盘页面
2. 实现用户管理页面
3. 实现商家管理页面（含审批功能）
4. 实现订单管理页面
5. 实现数据统计页面

**交付物**：
- 管理员可审核商家
- 管理员可查看用户、订单
- 管理员可查看数据统计

---

### 第三阶段：商家端开发

**目标**：完成商家端核心功能

**后端任务**：
1. 实现商家信息管理接口
2. 实现商品分类 CRUD 接口
3. 实现商品 CRUD 接口
4. 实现商家订单管理接口
5. 实现商品图片上传接口

**前端任务（merchant）**：
1. 实现商家注册/登录页面
2. 实现审核等待页面
3. 实现仪表盘页面
4. 实现商品分类管理页面
5. 实现商品管理页面（增删改查、上架下架）
6. 实现订单管理页面（订单处理流程）
7. 实现店铺设置页面

**交付物**：
- 商家可注册并等待审核
- 审核通过后可管理商品和分类
- 商家可处理订单

---

### 第四阶段：用户端开发

**目标**：完成用户端核心功能

**后端任务**：
1. 实现商家列表/详情接口
2. 实现商品列表/详情接口
3. 实现订单创建接口
4. 实现用户订单查询接口
5. 实现用户地址管理接口
6. 实现订单支付接口（模拟）
7. 实现订单取消接口
8. 实现订单评价接口（可选）

**前端任务（user）**：
1. 实现首页（商家列表、搜索）
2. 实现商家详情页（分类导航、商品列表）
3. 实现购物车功能
4. 实现确认订单页
5. 实现订单列表/详情页
6. 实现个人中心页面
7. 实现地址管理页面
8. 实现订单评价页面（可选）

**交付物**：
- 用户可浏览商家和商品
- 用户可下单、支付
- 用户可查看订单状态
- 用户可管理收货地址

---

### 第五阶段：联调优化与测试

**目标**：完成系统联调、Bug 修复、性能优化

**任务**：
1. 全流程联调测试
   - 商家注册 → 审核 → 上架商品
   - 用户浏览 → 下单 → 支付
   - 商家接单 → 制作 → 配送 → 完成
2. 边界情况测试
   - 并发下单
   - 库存扣减
   - 订单取消
3. 安全性检查
   - SQL 注入防护
   - XSS 防护
   - Token 过期处理
4. 性能优化
   - 数据库索引优化
   - 接口响应优化
5. 代码重构与优化
6. 编写 API 文档（Swagger 自动生成）
7. 编写单元测试

**交付物**：
- 完整可用的外卖点餐系统
- API 文档
- 测试用例

---

## 十、关键技术点

### 10.1 JWT 认证
- Access Token 有效期：2 小时
- Refresh Token 有效期：7 天
- Token 存储在 localStorage（前端）

### 10.2 密码安全
- 使用 bcrypt 进行密码哈希
- 盐值自动添加

### 10.3 文件上传
- 图片存储于 `backend/uploads/` 目录
- 支持图片类型：jpg、jpeg、png
- 单文件大小限制：5MB
- 返回相对路径，由 Nginx 或 FastAPI 静态文件服务提供

### 10.4 订单编号生成
- 格式：时间戳 + 随机数
- 示例：OD202401011234560001

### 10.5 数据验证
- 使用 Pydantic 进行请求数据验证
- 自定义验证规则（手机号格式、价格范围等）

### 10.6 错误处理
- 全局异常处理器
- 统一错误响应格式
- 友好错误提示

### 10.7 CORS 配置
- 允许前端域名访问
- 允许携带凭证
- 允许的方法：GET、POST、PUT、DELETE

---

## 十一、环境配置

### 11.1 后端依赖 (requirements.txt)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
aiosqlite==0.19.0
```

### 11.2 环境变量 (.env)
```env
# 数据库配置
DATABASE_URL=sqlite:///./food_delivery.db

# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=5242880

# CORS 配置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175
```

### 11.3 前端依赖

**admin/merchant**:
```json
{
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.4.0",
    "axios": "^1.6.0",
    "@element-plus/icons-vue": "^2.3.0",
    "echarts": "^5.4.0"
  }
}
```

**user**:
```json
{
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "vant": "^4.6.0",
    "axios": "^1.6.0",
    "@vant/icons": "^1.0.0"
  }
}
```

---

## 十二、运行说明

### 12.1 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 12.2 前端启动

```bash
# 平台管理端
cd frontend/admin
npm install
npm run dev  # 默认端口 5173

# 商家端
cd frontend/merchant
npm install
npm run dev  # 默认端口 5174

# 用户端
cd frontend/user
npm install
npm run dev  # 默认端口 5175
```

### 12.3 API 文档
启动后端后访问：`http://localhost:8000/docs`

---

## 十三、扩展功能（可选）

以下功能可在基础功能完成后逐步添加：

1. **消息通知**：订单状态变更通知（WebSocket）
2. **优惠券系统**：商家发放优惠券，用户使用
3. **会员系统**：用户会员等级、积分
4. **评论系统**：用户对商品/商家评价
5. **搜索优化**：全文搜索、热门搜索
6. **推荐系统**：基于用户历史推荐商家/商品
7. **多支付方式**：对接微信/支付宝支付
8. **骑手端**：配送员 App
9. **数据统计报表**：导出 Excel/PDF 报表
10. **多语言支持**：国际化

---

## 十四、注意事项

1. **SQLite 限制**：SQLite 不支持高并发写入，生产环境建议迁移至 PostgreSQL/MySQL
2. **文件上传**：生产环境建议使用对象存储（如阿里云 OSS、腾讯云 COS）
3. **安全性**：生产环境必须使用 HTTPS，更换 SECRET_KEY
4. **数据备份**：定期备份 SQLite 数据库文件
5. **密码策略**：建议强制密码复杂度要求
6. **限流**：高频接口建议添加限流保护

---

## 十五、总结

本开发计划涵盖了外卖点餐系统的完整设计方案，包括：
- 三端架构（平台管理端、商家端、用户端）
- 8 张核心数据表设计
- 完整的 RESTful API 设计（约 50+ 接口）
- 详细的前端页面规划
- 5 个开发阶段的明确任务划分

按照此计划逐步开发，可以构建一个功能完整的外卖点餐系统。

---

## 附录：设计规规范文档位置

详细的设计规范文档（代码规范、测试规范、Git 规范等）请查看项目根目录下的 `design-specification.md` 文件。
