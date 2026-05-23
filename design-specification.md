# 外卖点餐系统 - 开发设计规范

> **版本**: v1.0  
> **更新日期**: 2026-05-23  
> **适用范围**: 外卖点餐系统全项目（后端 + 前端三端）

---

## 目录
- [一、后端代码规范](#一后端代码规范)
- [二、前端代码规范](#二前端代码规范)
- [三、数据库设计规范](#三数据库设计规范)
- [四、API 设计规范](#四api-设计规范)
- [五、测试规范（核心）](#五测试规范核心)
- [六、Git 协作规范](#六git-协作规范)
- [七、代码审查规范](#七代码审查规范)
- [八、安全规范](#八安全规范)
- [九、文档规范](#九文档规范)

---

## 一、后端代码规范

### 1.1 命名规范

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

### 1.2 代码结构规范

#### 1.2.1 文件组织
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

#### 1.2.2 文件长度限制
- 单个 Python 文件不超过 **300 行**
- 单个函数不超过 **50 行**
- 单个类的公共方法不超过 **10 个**
- 超过限制时应考虑拆分为多个模块

#### 1.2.3 导入规范
- 禁止使用通配符导入：`from module import *`
- 相对导入使用 `.` 前缀：`from .database import get_db`
- 避免循环导入，使用依赖注入解决

### 1.3 类型注解规范

所有函数必须添加类型注解：
```python
# ✅ 正确
async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

# ❌ 错误
async def get_user_by_id(user_id, db):
    return db.query(User).filter(User.id == user_id).first()
```

### 1.4 文档字符串规范

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

### 1.5 异常处理规范

#### 1.5.1 自定义异常
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

#### 1.5.2 异常处理原则
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

### 1.6 日志规范

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

### 1.7 异步编程规范

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

### 1.8 SQLAlchemy 模型规范

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

### 1.9 Pydantic Schema 规范

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

### 1.10 Service 层规范

- 所有业务逻辑必须在 Service 层处理，API 层只负责参数接收和响应返回
- Service 类通过依赖注入获取数据库会话
- 每个领域实体应有独立的 Service 类
- Service 方法应抛出业务异常，由全局异常处理器统一处理

---

## 二、前端代码规范

### 2.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件夹名 | kebab-case | `user-profile`, `order-list` |
| 组件文件名 | PascalCase | `UserProfile.vue`, `OrderCard.vue` |
| 组合式函数 | camelCase, use 前缀 | `useAuth.js`, `useCart.js` |
| 变量/函数名 | camelCase | `userName`, `fetchOrders()` |
| 常量名 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| CSS 类名 | BEM 命名 | `.order-card__title`, `.btn--primary` |

### 2.2 目录结构规范

```
src/
├── api/                    # API 请求模块
├── assets/                 # 静态资源
├── components/             # 公共组件
│   ├── common/            # 通用组件
│   └── business/          # 业务组件
├── composables/            # 组合式函数
├── constants/              # 常量定义
├── directives/             # 自定义指令
├── layouts/                # 布局组件
├── router/                 # 路由配置
├── store/                  # Pinia 状态管理
├── utils/                  # 工具函数
├── views/                  # 页面组件
└── App.vue
```

### 2.3 Vue 组件规范

#### 2.3.1 单文件组件结构顺序
```vue
<template>
  <!-- 1. 模板部分 -->
</template>

<script setup>
// 2. 导入
// 3. Props 定义
// 4. Emits 定义
// 5. 响应式数据
// 6. 计算属性
// 7. 方法
// 8. 生命周期钩子
</script>

<style scoped>
/* 9. 样式部分 */
</style>
```

#### 2.3.2 组件 Props 规范
```javascript
// ✅ 正确 - 完整定义 Props
const props = defineProps({
  title: {
    type: String,
    required: true,
    default: ''
  },
  count: {
    type: Number,
    default: 0
  }
})
```

### 2.4 API 请求规范

- 所有 API 请求必须通过 `utils/request.js` 封装的 axios 实例
- 每个业务模块独立的 API 文件
- API 函数必须有 JSDoc 注释说明参数和返回值
- 统一的错误处理在 axios 拦截器中处理

### 2.5 Pinia Store 规范

- 使用 Composition API 风格 (`setup` 函数)
- State 使用 `ref`/`reactive`
- Getters 使用 `computed`
- Actions 使用普通函数
- Store 文件按业务模块拆分

### 2.6 路由规范

- 使用懒加载：`component: () => import('...')`
- 所有页面路由必须配置 `meta.title`
- 需要认证的路由配置 `meta.requiresAuth: true`
- 路由守卫统一在 `router/index.js` 中处理

---

## 三、数据库设计规范

### 3.1 表设计规范

#### 3.1.1 必须字段
每个表必须包含以下字段：
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### 3.1.2 命名规范
| 规则 | 示例 |
|------|------|
| 表名复数 | `users`, `orders`, `products` |
| 外键命名 | `{表名单数}_id` → `user_id`, `merchant_id` |
| 索引命名 | `idx_{表名}_{字段名}` → `idx_users_phone` |
| 唯一索引 | `uq_{表名}_{字段名}` → `uq_users_username` |

### 3.2 字段类型选择

| 数据类型 | SQLite 类型 | 说明 |
|---------|------------|------|
| 整数ID | `INTEGER` | 自增主键 |
| 字符串(短) | `VARCHAR(n)` | 用户名、手机号等 |
| 字符串(长) | `TEXT` | 描述、备注等 |
| 金额 | `DECIMAL(10, 2)` | 价格相关 |
| 布尔值 | `BOOLEAN` | 状态标志 |
| 时间 | `TIMESTAMP` | 日期时间 |
| 枚举 | `VARCHAR + CHECK` | 状态、角色等 |

### 3.3 索引设计规范

**索引原则**：
- WHERE、JOIN、ORDER BY 频繁使用的字段建立索引
- 高区分度的字段适合建索引
- 避免过多索引影响写入性能
- 联合索引遵循最左前缀原则

### 3.4 外键约束

**外键删除策略**：
| 策略 | 说明 | 使用场景 |
|------|------|---------|
| CASCADE | 级联删除 | 订单项随订单删除 |
| RESTRICT | 禁止删除 | 有订单时不能删除商家 |
| SET NULL | 设为 NULL | 用户删除时相关字段设为NULL |

---

## 四、API 设计规范

### 4.1 统一响应格式

#### 成功响应
```json
{
    "code": 200,
    "message": "success",
    "data": { }
}
```

#### 分页响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
}
```

#### 错误响应
```json
{
    "code": 400,
    "message": "错误信息",
    "data": null
}
```

### 4.2 响应码规范

| Code | 说明 | 使用场景 |
|------|------|---------|
| 200 | 成功 | 请求成功处理 |
| 201 | 创建成功 | POST 创建资源 |
| 400 | 请求错误 | 参数验证失败 |
| 401 | 未授权 | 未登录或 Token 失效 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 资源不存在 | 请求的资源未找到 |
| 409 | 冲突 | 资源已存在 |
| 422 | 校验失败 | 业务规则校验失败 |
| 500 | 服务器错误 | 服务器内部错误 |

### 4.3 RESTful 规范

| 操作 | 方法 | 路径 | 示例 |
|------|------|------|------|
| 获取列表 | GET | /resources | GET /api/v1/merchants |
| 获取详情 | GET | /resources/{id} | GET /api/v1/merchants/1 |
| 创建 | POST | /resources | POST /api/v1/orders |
| 更新 | PUT | /resources/{id} | PUT /api/v1/users/profile |
| 部分更新 | PATCH | /resources/{id} | PATCH /api/v1/orders/1/status |
| 删除 | DELETE | /resources/{id} | DELETE /api/v1/products/1 |

---

## 五、测试规范（核心）

### 5.1 测试框架与工具

| 层级 | 工具 | 说明 |
|------|------|------|
| 后端单元测试 | pytest | Python 标准测试框架 |
| 后端 API 测试 | pytest + httpx | 异步 HTTP 客户端测试 |
| 后端异步测试 | pytest-asyncio | 异步测试支持 |
| 前端单元测试 | Vitest | Vue 3 推荐的测试框架 |
| 前端组件测试 | @vue/test-utils | Vue 组件测试工具 |
| E2E 测试 | Playwright | 浏览器自动化测试 |
| 覆盖率统计 | coverage.py (后端), vitest (前端) | 代码覆盖率 |

### 5.2 后端测试依赖

```txt
# requirements-test.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.26.0
aiosqlite==0.19.0
```

### 5.3 测试目录结构

```
backend/tests/
├── __init__.py
├── conftest.py                  # 全局 fixture
├── fixtures/                    # 测试数据 fixtures
│   ├── __init__.py
│   ├── users.py
│   ├── merchants.py
│   ├── products.py
│   └── orders.py
├── unit/                        # 单元测试
│   ├── __init__.py
│   ├── test_security.py
│   ├── test_utils.py
│   ├── test_schemas.py
│   └── services/
│       ├── __init__.py
│       ├── test_user_service.py
│       ├── test_merchant_service.py
│       ├── test_product_service.py
│       └── test_order_service.py
├── integration/                 # API 集成测试
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_merchants.py
│   ├── test_products.py
│   ├── test_orders.py
│   └── test_admin.py
└── e2e/                         # 端到端流程测试
    ├── __init__.py
    ├── test_register_flow.py
    ├── test_order_flow.py
    └── test_approval_flow.py
```

### 5.4 测试配置 (conftest.py)

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app.core.security import hash_password

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
async def admin_user(db_session):
    from app.models.user import User
    user = User(
        username="admin",
        phone="13800000001",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def admin_token(admin_user):
    from app.core.security import create_access_token
    return create_access_token(data={"user_id": admin_user.id})

@pytest.fixture
async def merchant_user(db_session):
    from app.models.user import User
    user = User(
        username="merchant_user",
        phone="13800000002",
        password_hash=hash_password("merchant123"),
        role="merchant",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def normal_user(db_session):
    from app.models.user import User
    user = User(
        username="normal_user",
        phone="13800000003",
        password_hash=hash_password("user123"),
        role="user",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user
```

### 5.5 单元测试规范

#### 5.5.1 测试命名规范
```
test_{方法名}_{场景}_{预期结果}
```

示例：
```python
def test_create_user_with_valid_data_should_return_user()
def test_get_user_with_invalid_id_should_raise_404()
def test_login_with_wrong_password_should_return_401()
```

#### 5.5.2 Service 层单元测试示例

```python
# tests/unit/services/test_user_service.py
import pytest
from app.services.user_service import UserService
from app.core.exceptions import NotFoundException, ValidationException
from app.schemas.user import UserCreate

class TestUserService:
    """用户服务测试类"""

    async def test_create_user_success(self, db_session):
        """测试创建用户成功"""
        service = UserService(db_session)
        data = UserCreate(
            username="testuser",
            phone="13900000001",
            password="password123"
        )
        user = await service.create(data)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.phone == "13900000001"
        assert user.role == "user"
        assert user.is_active is True

    async def test_create_user_duplicate_phone_should_raise(self, db_session):
        """测试手机号重复时抛出异常"""
        service = UserService(db_session)
        data = UserCreate(
            username="testuser",
            phone="13900000001",
            password="password123"
        )
        await service.create(data)

        with pytest.raises(ValidationException) as exc:
            await service.create(data)
        assert "手机号已注册" in str(exc.value)

    async def test_get_by_id_not_found_should_raise(self, db_session):
        """测试获取不存在的用户抛出 404"""
        service = UserService(db_session)
        with pytest.raises(NotFoundException):
            await service.get_by_id(99999)

    async def test_update_user_success(self, db_session, normal_user):
        """测试更新用户信息成功"""
        from app.schemas.user import UserUpdate
        service = UserService(db_session)
        update_data = UserUpdate(username="new_username")
        user = await service.update(normal_user.id, update_data)

        assert user.username == "new_username"

    async def test_list_users_with_pagination(self, db_session):
        """测试用户列表分页"""
        service = UserService(db_session)
        for i in range(25):
            await service.create(UserCreate(
                username=f"user{i}",
                phone=f"1390000010{i}",
                password="password123"
            ))

        users, total = await service.list_users(skip=0, limit=10)
        assert len(users) == 10
        assert total >= 25
```

#### 5.5.3 Schema 验证测试示例

```python
# tests/unit/test_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserUpdate

class TestUserSchemas:
    """用户 Schema 验证测试"""

    def test_user_create_valid_data(self):
        """测试有效的用户创建数据"""
        data = UserCreate(
            username="testuser",
            phone="13900000001",
            password="password123"
        )
        assert data.username == "testuser"

    def test_user_create_invalid_phone(self):
        """测试无效的手机号格式"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                phone="123",
                password="password123"
            )

    def test_user_create_short_password(self):
        """测试密码长度不足"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                phone="13900000001",
                password="123"
            )

    def test_user_update_partial_data(self):
        """测试部分更新数据"""
        data = UserUpdate(username="new_name")
        assert data.username == "new_name"
        assert data.phone is None
```

#### 5.5.4 安全模块测试示例

```python
# tests/unit/test_security.py
import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

class TestSecurity:
    """安全模块测试"""

    def test_hash_password(self):
        """测试密码哈希"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert hashed != password
        assert hashed.startswith("$2")

    def test_verify_password_correct(self):
        """测试正确的密码验证"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """测试错误的密码验证"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_create_and_decode_token(self):
        """测试 Token 创建和解码"""
        user_id = 123
        token = create_access_token(data={"user_id": user_id})
        payload = decode_access_token(token)
        assert payload["user_id"] == user_id

    def test_decode_invalid_token(self):
        """测试无效 Token 解码"""
        payload = decode_access_token("invalid.token.here")
        assert payload is None
```

### 5.6 API 集成测试规范

#### 5.6.1 认证接口测试示例

```python
# tests/integration/test_auth.py
import pytest

class TestAuthAPI:
    """认证接口测试"""

    async def test_register_success(self, client):
        """测试用户注册成功"""
        response = await client.post("/auth/register", json={
            "username": "newuser",
            "phone": "13900000001",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == "newuser"

    async def test_register_duplicate_phone(self, client):
        """测试手机号重复注册"""
        await client.post("/auth/register", json={
            "username": "user1",
            "phone": "13900000001",
            "password": "password123"
        })
        response = await client.post("/auth/register", json={
            "username": "user2",
            "phone": "13900000001",
            "password": "password123"
        })
        assert response.status_code == 400

    async def test_login_success(self, client, normal_user):
        """测试登录成功"""
        response = await client.post("/auth/login", json={
            "phone": normal_user.phone,
            "password": "user123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]

    async def test_login_wrong_password(self, client, normal_user):
        """测试密码错误登录"""
        response = await client.post("/auth/login", json={
            "phone": normal_user.phone,
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    async def test_access_protected_route_without_token(self, client):
        """测试无 Token 访问受保护接口"""
        response = await client.get("/users/profile")
        assert response.status_code == 401

    async def test_access_protected_route_with_token(self, client, normal_user):
        """测试有 Token 访问受保护接口"""
        login_resp = await client.post("/auth/login", json={
            "phone": normal_user.phone,
            "password": "user123"
        })
        token = login_resp.json()["data"]["access_token"]

        response = await client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
```

#### 5.6.2 订单接口测试示例

```python
# tests/integration/test_orders.py
import pytest

class TestOrderAPI:
    """订单接口测试"""

    async def test_create_order_success(self, client, normal_user, db_session):
        """测试创建订单成功"""
        from app.core.security import create_access_token
        from app.models.address import Address

        address = Address(
            user_id=normal_user.id,
            receiver="张三",
            phone="13900000001",
            province="广东省",
            city="深圳市",
            district="南山区",
            detail_address="科技园路1号",
            is_default=True
        )
        db_session.add(address)
        await db_session.flush()

        token = create_access_token(data={"user_id": normal_user.id})

        response = await client.post(
            "/orders",
            json={
                "merchant_id": 1,
                "address_id": address.id,
                "items": [
                    {"product_id": 1, "quantity": 2},
                    {"product_id": 2, "quantity": 1}
                ],
                "remark": "少辣"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "pending"

    async def test_cancel_order_success(self, client, normal_user):
        """测试取消订单成功"""
        from app.core.security import create_access_token
        token = create_access_token(data={"user_id": normal_user.id})

        # 创建订单
        create_resp = await client.post(
            "/orders",
            json={"merchant_id": 1, "address_id": 1, "items": []},
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = create_resp.json()["data"]["id"]

        # 取消订单
        response = await client.post(
            f"/users/orders/{order_id}/cancel",
            json={"reason": "不想要了"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
```

### 5.7 E2E 端到端测试规范

#### 5.7.1 商家注册审批流程测试

```python
# tests/e2e/test_approval_flow.py
import pytest

class TestApprovalFlow:
    """商家注册审批流程端到端测试"""

    async def test_merchant_approval_flow(self, client):
        """测试完整的商家审批流程"""
        # 1. 商家注册
        register_resp = await client.post("/auth/merchant/register", json={
            "username": "new_merchant",
            "phone": "13900000100",
            "password": "merchant123",
            "business_name": "美味餐厅",
            "contact_phone": "13900000100",
            "address": "深圳市南山区",
            "description": "美味佳肴"
        })
        assert register_resp.status_code == 200
        merchant_data = register_resp.json()["data"]
        assert merchant_data["status"] == "pending"

        # 2. 商家登录，确认状态为 pending
        login_resp = await client.post("/auth/login", json={
            "phone": "13900000100",
            "password": "merchant123"
        })
        merchant_token = login_resp.json()["data"]["access_token"]

        # 3. 管理员登录
        admin_login = await client.post("/auth/login", json={
            "phone": "13800000001",
            "password": "admin123"
        })
        admin_token = admin_login.json()["data"]["access_token"]

        # 4. 管理员查看待审核商家
        merchants_resp = await client.get(
            "/admin/merchants?status=pending",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert merchants_resp.status_code == 200

        # 5. 管理员审批通过
        merchant_id = merchant_data["id"]
        approve_resp = await client.put(
            f"/admin/merchants/{merchant_id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert approve_resp.status_code == 200

        # 6. 商家重新获取信息，确认状态为 approved
        merchant_info = await client.get(
            "/merchants/me",
            headers={"Authorization": f"Bearer {merchant_token}"}
        )
        assert merchant_info.json()["data"]["status"] == "approved"
```

#### 5.7.2 完整下单流程测试

```python
# tests/e2e/test_order_flow.py
import pytest

class TestOrderFlow:
    """完整下单流程端到端测试"""

    async def test_complete_order_flow(self, client):
        """测试从浏览到下单的完整流程"""
        # 1. 用户注册
        # 2. 用户登录
        # 3. 浏览商家列表
        # 4. 查看商家详情
        # 5. 查看商品列表
        # 6. 添加收货地址
        # 7. 创建订单
        # 8. 确认订单状态为 pending
        # 9. 支付订单
        # 10. 确认订单状态为 paid
        pass
```

### 5.8 前端测试规范

#### 5.8.1 Vitest 配置

```javascript
// frontend/*/vitest.config.js
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
})
```

#### 5.8.2 组件测试示例

```javascript
// frontend/user/tests/components/ProductCard.test.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductCard from '@/components/business/ProductCard.vue'

describe('ProductCard', () => {
  it('应该正确渲染商品信息', () => {
    const product = {
      id: 1,
      name: '宫保鸡丁',
      price: 38.00,
      description: '经典川菜',
      image_url: '/images/product.jpg'
    }

    const wrapper = mount(ProductCard, {
      props: { product }
    })

    expect(wrapper.text()).toContain('宫保鸡丁')
    expect(wrapper.text()).toContain('38.00')
  })

  it('点击添加到购物车应该触发事件', async () => {
    const product = { id: 1, name: '宫保鸡丁', price: 38.00 }
    const wrapper = mount(ProductCard, { props: { product } })

    await wrapper.find('.add-to-cart-btn').trigger('click')

    expect(wrapper.emitted('add-to-cart')).toBeTruthy()
    expect(wrapper.emitted('add-to-cart')[0]).toEqual([{ productId: 1, quantity: 1 }])
  })
})
```

#### 5.8.3 Composable 测试示例

```javascript
// frontend/user/tests/composables/useCart.test.js
import { describe, it, expect } from 'vitest'
import { useCartStore } from '@/store/modules/cart'

describe('useCartStore', () => {
  it('应该正确计算总价', () => {
    const store = useCartStore()
    store.items = [
      { productId: 1, name: '商品1', price: 10, quantity: 2 },
      { productId: 2, name: '商品2', price: 15, quantity: 1 }
    ]

    expect(store.totalPrice).toBe(35)
    expect(store.totalCount).toBe(3)
  })

  it('空购物车总价应该为0', () => {
    const store = useCartStore()
    store.items = []

    expect(store.totalPrice).toBe(0)
    expect(store.isEmpty).toBe(true)
  })
})
```

### 5.9 测试运行命令

#### 后端测试
```bash
# 运行所有测试
cd backend
pytest

# 运行特定测试文件
pytest tests/unit/services/test_user_service.py

# 运行特定标记的测试
pytest -m "slow"
pytest -m "not slow"

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看详细输出
pytest -v -s

# 运行失败的测试
pytest --lf
```

#### 前端测试
```bash
# 运行所有测试
cd frontend/user
npm run test

# 监听模式
npm run test -- --watch

# 生成覆盖率报告
npm run test -- --coverage

# 运行特定测试文件
npm run test -- src/components/ProductCard.test.js
```

### 5.10 测试覆盖率要求

| 模块 | 最低覆盖率 | 说明 |
|------|-----------|------|
| Service 层 | ≥ 90% | 核心业务逻辑 |
| Schema 验证 | ≥ 95% | 数据验证 |
| API 端点 | ≥ 85% | 接口测试 |
| 工具函数 | ≥ 90% | 纯函数易于测试 |
| 前端组件 | ≥ 80% | UI 组件 |
| 前端 Store | ≥ 85% | 状态管理 |
| 整体项目 | ≥ 85% | 最低要求 |

### 5.11 测试编写原则

1. **AAA 模式**: Arrange(安排) → Act(执行) → Assert(断言)
2. **测试独立性**: 每个测试用例应独立运行，不依赖执行顺序
3. **测试可重复性**: 测试结果应该确定，不依赖外部状态
4. **测试命名清晰**: 从命名能知道测试什么场景
5. **一个测试一个断言**: 尽量保持测试的单一职责
6. **测试边界条件**: 空值、最大值、最小值、异常情况
7. **使用 Fixture**: 重复的测试数据使用 fixture 管理

---

## 六、Git 协作规范

### 6.1 分支策略

```
main (生产环境)
  ↑
develop (开发环境)
  ↑
feature/* (功能分支)
bugfix/* (修复分支)
hotfix/* (紧急修复)
```

**分支命名**：
| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/功能描述` | `feature/user-registration` |
| 修复 | `bugfix/问题描述` | `bugfix/order-calculate-error` |
| 紧急 | `hotfix/问题描述` | `hotfix/payment-failure` |
| 重构 | `refactor/重构描述` | `refactor/optimize-query` |

### 6.2 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Type 类型**：
| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档变更 |
| `style` | 代码格式（不影响代码运行） |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/辅助工具变动 |
| `perf` | 性能优化 |
| `ci` | CI/CD 配置变更 |

**示例**：
```bash
# 新功能
git commit -m "feat(order): 添加订单取消功能"

# Bug 修复
git commit -m "fix(cart): 修复购物车总价计算错误"

# 文档
git commit -m "docs(api): 更新订单接口文档"

# 测试
git commit -m "test(order): 添加订单服务单元测试"

# 带详细说明
git commit -m "feat(payment): 添加微信支付集成

- 添加微信支付SDK
- 实现支付回调处理
- 添加支付状态轮询

Closes #123"
```

### 6.3 .gitignore 规范

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/

# 环境文件
.env
.env.local
*.db

# IDE
.vscode/
.idea/

# 测试覆盖率
htmlcov/
.coverage

# 上传文件
uploads/

# 前端
node_modules/
dist/
.DS_Store
```

---

## 七、代码审查规范

### 7.1 审查检查清单

#### 功能正确性
- [ ] 代码是否实现了需求描述的功能
- [ ] 边界情况是否处理
- [ ] 错误情况是否有适当的处理

#### 代码质量
- [ ] 是否符合项目命名规范
- [ ] 是否有适当的类型注解
- [ ] 代码是否清晰可读
- [ ] 是否有重复代码可以提取

#### 测试
- [ ] 是否有对应的测试用例
- [ ] 测试是否覆盖了主要场景
- [ ] 测试是否通过

#### 安全
- [ ] 是否有 SQL 注入风险
- [ ] 敏感信息是否妥善处理
- [ ] 权限验证是否正确

#### 性能
- [ ] 是否有 N+1 查询问题
- [ ] 大数据量是否有分页
- [ ] 是否有不必要的数据库查询

### 7.2 Pull Request 规范

PR 标题格式：
```
[type] 简短描述

示例：[feat] 添加用户地址管理功能
```

PR 描述模板：
```markdown
## 变更内容
描述此次 PR 的主要变更

## 相关 Issue
Closes #123

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过

## 截图（前端变更）
[可选] 添加 UI 变更截图
```

---

## 八、安全规范

### 8.1 密码安全

- 使用 `bcrypt` 进行密码哈希
- 禁止存储明文密码
- 密码最小长度：6 位
- 密码修改需要验证旧密码

### 8.2 Token 安全

- Access Token 有效期：2 小时
- Refresh Token 有效期：7 天
- Token 存储在 HTTP-only Cookie 或 localStorage
- 登出时清除 Token

### 8.3 输入验证

- 所有用户输入必须验证
- 使用 Pydantic 进行请求体验证
- 手机号格式验证：`^1[3-9]\d{9}$`
- 文件上传类型和大小限制

### 8.4 SQL 注入防护

- 使用 SQLAlchemy ORM，禁止拼接 SQL
- 参数化查询
- 对用户输入进行过滤

### 8.5 XSS 防护

- 前端框架自动转义输出
- 富文本输入使用安全库处理
- Content-Security-Policy 头设置

---

## 九、文档规范

### 9.1 API 文档

- 使用 FastAPI 自动生成 Swagger 文档
- 每个 API 端点必须有描述
- 请求/响应示例
- 错误码说明

### 9.2 代码注释

- 公共 API 必须有文档字符串
- 复杂逻辑需要行内注释说明
- 魔法数字需要常量定义并注释

### 9.3 项目文档

- README.md：项目说明、快速开始
- CHANGELOG.md：版本更新日志
- 架构文档：系统架构图、数据流图

---

## 附录：常用命令速查

### 后端
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest -v

# 运行测试并生成覆盖率
pytest --cov=app --cov-report=html

# 代码格式检查
ruff check app/

# 代码格式化
ruff format app/

# 类型检查
mypy app/
```

### 前端
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm run test

# 运行测试并生成覆盖率
npm run test -- --coverage

# 代码检查
npm run lint

# 代码格式化
npm run format

# 构建生产版本
npm run build
```
