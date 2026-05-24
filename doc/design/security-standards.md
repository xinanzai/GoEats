# 安全规范

> **版本**: v1.0
> **更新日期**: 2026-05-24
> **适用范围**: GoEats 全项目安全设计

---

## 目录

- [密码安全](#密码安全)
- [Token 安全](#token-安全)
- [输入验证](#输入验证)
- [SQL 注入防护](#sql-注入防护)
- [XSS 防护](#xss-防护)
- [CSRF 防护](#csrf-防护)
- [文件上传安全](#文件上传安全)
- [权限控制](#权限控制)

---

## 密码安全

- 使用 `bcrypt` 进行密码哈希
- 禁止存储明文密码
- 密码最小长度：6 位
- 密码修改需要验证旧密码

```python
from app.core.security import hash_password, verify_password

# 密码哈希
hashed = hash_password("mysecretpassword")

# 密码验证
is_valid = verify_password("mysecretpassword", hashed)
```

---

## Token 安全

- Access Token 有效期：2 小时
- Refresh Token 有效期：7 天
- Token 存储在 localStorage
- 登出时清除 Token

```python
from app.core.security import create_access_token, decode_access_token

# 创建 Token
token = create_access_token(data={"user_id": user.id})

# 验证 Token
payload = decode_access_token(token)
```

---

## 输入验证

- 所有用户输入必须验证
- 使用 Pydantic 进行请求体验证
- 手机号格式验证：`^1[3-9]\d{9}$`
- 文件上传类型和大小限制

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=50)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
```

---

## SQL 注入防护

- 使用 SQLAlchemy ORM，禁止拼接 SQL
- 参数化查询
- 对用户输入进行过滤

```python
# ✅ 正确 - 使用 ORM
from sqlalchemy import select
result = await db.execute(select(User).where(User.phone == phone))

# ❌ 错误 - 禁止拼接 SQL
result = await db.execute(f"SELECT * FROM users WHERE phone = '{phone}'")
```

---

## XSS 防护

- 前端框架自动转义输出
- 富文本输入使用安全库处理
- Content-Security-Policy 头设置

---

## CSRF 防护

- 使用 JWT Token 而非 Session Cookie
- 前端请求通过 Header 传递 Token
- 不依赖 Cookie 进行认证

---

## 文件上传安全

- 限制文件类型：jpg、jpeg、png
- 单文件大小限制：5MB
- 文件名使用 UUID 重命名
- 存储路径与代码分离

```python
# 文件上传验证
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

---

## 权限控制

### 基于角色的访问控制 (RBAC)

| 角色 | 权限 |
|------|------|
| user | 浏览商家、下单、管理个人信息 |
| merchant | 管理商品、处理订单、店铺设置 |
| admin | 用户管理、商家审核、数据统计 |

### 依赖注入权限验证

```python
from fastapi import Depends
from app.core.dependencies import get_current_user, get_current_admin_user

# 普通用户接口
@router.get("/users/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

# 管理员接口
@router.get("/admin/users")
async def list_users(
    current_admin: User = Depends(get_current_admin_user)
):
    return await admin_service.list_users()

# 商家接口
@router.get("/merchants/me")
async def get_my_merchant(
    current_merchant: User = Depends(get_current_merchant_user)
):
    return await merchant_service.get_by_user_id(current_merchant.id)
```

### 资源所有权验证

```python
# 验证用户只能访问自己的资源
async def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    order = await order_service.get_by_id(order_id)
    if order.user_id != current_user.id:
        raise PermissionException("无权访问此订单")
    return order
```

---

## 限流保护

- 基于 IP 的滑动窗口限流
- 每秒/每分钟请求数限制
- 超限自动封禁机制

---

## 相关文档

- [API 设计规范](./api-design.md) - API 安全设计
- [后端代码规范](./backend-conventions.md) - 安全编码规范
