# API 设计规范

> **版本**: v1.0
> **更新日期**: 2026-05-24
> **适用范围**: GoEats 后端 API

---

## 目录

- [统一响应格式](#统一响应格式)
- [响应码规范](#响应码规范)
- [RESTful 规范](#restful-规范)
- [认证与授权](#认证与授权)
- [分页规范](#分页规范)
- [API 端点总览](#api-端点总览)

---

## 统一响应格式

### 成功响应

```json
{
    "code": 200,
    "message": "success",
    "data": { }
}
```

### 分页响应

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

### 错误响应

```json
{
    "code": 400,
    "message": "错误信息",
    "data": null
}
```

---

## 响应码规范

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

---

## RESTful 规范

| 操作 | 方法 | 路径 | 示例 |
|------|------|------|------|
| 获取列表 | GET | /resources | GET /api/v1/merchants |
| 获取详情 | GET | /resources/{id} | GET /api/v1/merchants/1 |
| 创建 | POST | /resources | POST /api/v1/orders |
| 更新 | PUT | /resources/{id} | PUT /api/v1/users/profile |
| 部分更新 | PATCH | /resources/{id} | PATCH /api/v1/orders/1/status |
| 删除 | DELETE | /resources/{id} | DELETE /api/v1/products/1 |

---

## 认证与授权

### JWT Token

- **Access Token 有效期**: 2 小时
- **Refresh Token 有效期**: 7 天
- **存储方式**: localStorage (前端)

### 请求头

```
Authorization: Bearer <access_token>
```

### 角色权限

| 角色 | 可访问端点 |
|------|-----------|
| 公开 | /auth/*, /merchants, /products |
| user | /users/*, /orders/users/* |
| merchant | /merchants/me/*, /orders/merchant/* |
| admin | /admin/* |

---

## 分页规范

### 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 (从 1 开始) |
| page_size | int | 20 | 每页数量 (最大 100) |

### 示例

```
GET /api/v1/merchants?page=1&page_size=10
```

---

## API 端点总览

### 认证接口 (/api/v1/auth)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /auth/login | 用户登录 | 公开 |
| POST | /auth/register | 用户注册 | 公开 |
| POST | /auth/merchant/register | 商家注册 | 公开 |
| POST | /auth/refresh | 刷新令牌 | 已登录 |
| GET | /auth/me | 获取当前用户信息 | 已登录 |

### 用户接口 (/api/v1/users)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /users/profile | 获取个人信息 | 已登录 |
| PUT | /users/profile | 更新个人信息 | 已登录 |
| PUT | /users/password | 修改密码 | 已登录 |
| GET | /users/addresses | 获取地址列表 | 已登录 |
| POST | /users/addresses | 添加地址 | 已登录 |
| PUT | /users/addresses/{id} | 更新地址 | 已登录 |
| DELETE | /users/addresses/{id} | 删除地址 | 已登录 |
| PUT | /users/addresses/{id}/set-default | 设为默认地址 | 已登录 |

### 商家接口 (/api/v1/merchants)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /merchants | 商家列表 | 公开 |
| GET | /merchants/{id} | 商家详情 | 公开 |
| GET | /merchants/me | 当前商家信息 | 商家 |
| PUT | /merchants/me | 更新商家信息 | 商家 |
| GET | /merchants/me/categories | 获取分类列表 | 商家 |
| POST | /merchants/me/categories | 添加分类 | 商家 |
| PUT | /merchants/me/categories/{id} | 更新分类 | 商家 |
| DELETE | /merchants/me/categories/{id} | 删除分类 | 商家 |

### 商品接口 (/api/v1/products)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /products | 商品列表 | 公开 |
| GET | /products/{id} | 商品详情 | 公开 |
| GET | /products/merchant/me | 我的商品列表 | 商家 |
| POST | /products/merchant/me | 添加商品 | 商家 |
| PUT | /products/merchant/me/{id} | 更新商品 | 商家 |
| DELETE | /products/merchant/me/{id} | 删除商品 | 商家 |
| PUT | /products/merchant/me/{id}/toggle | 上架/下架商品 | 商家 |

### 订单接口 (/api/v1/orders)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /orders | 创建订单 | 已登录用户 |
| GET | /orders/users/me | 我的订单列表 | 已登录用户 |
| GET | /orders/users/me/{id} | 订单详情 | 已登录用户 |
| POST | /orders/users/me/{id}/cancel | 取消订单 | 已登录用户 |
| POST | /orders/users/me/{id}/pay | 支付订单 | 已登录用户 |
| GET | /orders/merchant/me | 商家订单列表 | 商家 |
| POST | /orders/merchant/me/{id}/prepare | 开始制作 | 商家 |
| POST | /orders/merchant/me/{id}/deliver | 开始配送 | 商家 |
| POST | /orders/merchant/me/{id}/complete | 完成订单 | 商家 |

### 管理接口 (/api/v1/admin)

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
| GET | /admin/statistics | 统计数据 | 管理员 |

---

## 相关文档

- [数据模型](../architecture/data-models.md) - 数据库模型设计
- [后端代码规范](./backend-conventions.md) - 后端开发规范
- [测试规范](./testing-standards.md) - API 测试规范
