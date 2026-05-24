# 系统架构设计

> **版本**: v1.0
> **更新日期**: 2026-05-24
> **适用范围**: GoEats 外卖点餐系统

---

## 目录

- [整体架构](#整体架构)
- [数据流图](#数据流图)
- [技术栈](#技术栈)
- [架构分层](#架构分层)
- [核心组件](#核心组件)

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
├──────────────┬──────────────────┬───────────────────────────┤
│  Admin       │   Merchant       │   User                    │
│  (Vue+Elem)  │   (Vue+Elem)     │   (Vue+Vant)             │
└──────┬───────┴────────┬─────────┴──────────┬────────────────┘
       │                │                    │
       └────────────────┼────────────────────┘
                        │
┌───────────────────────┼─────────────────────────────────────┐
│              API Gateway (FastAPI)                          │
├───────────────────────┼─────────────────────────────────────┤
│               Business Logic (Services)                     │
├───────────────────────┼─────────────────────────────────────┤
│                Data Access (SQLAlchemy)                      │
├───────────────────────┼─────────────────────────────────────┤
│                    SQLite Database                           │
└───────────────────────┴─────────────────────────────────────┘
```

### 架构特点

- **前后端分离**: 三个独立的前端应用通过 RESTful API 与后端通信
- **分层架构**: API 层、业务逻辑层、数据访问层清晰分离
- **异步处理**: 全栈异步支持，提高并发处理能力
- **角色权限**: 基于 JWT 的 RBAC 权限控制

---

## 数据流图

### 用户下单流程

```
User Frontend          Backend API          Service Layer        Database
     │                    │                    │                    │
     │──POST /orders────▶│                    │                    │
     │                    │──validate()───────▶│                    │
     │                    │◀──validation───────│                    │
     │                    │                    │──check stock─────▶│
     │                    │                    │◀──stock info──────│
     │                    │                    │──create order────▶│
     │                    │                    │◀──order created───│
     │                    │◀──200 OK───────────│                    │
     │◀──order data───────│                    │                    │
```

### 商家审批流程

```
Admin Frontend         Backend API        Service Layer         Database
     │                    │                    │                    │
     │──GET /merchants───▶│                    │                    │
     │                    │                    │──query pending───▶│
     │                    │◀──merchant list────│                    │
     │◀──response────────│                    │                    │
     │                    │                    │                    │
     │──PUT /approve─────▶│                    │                    │
     │                    │──update status───▶│                    │
     │                    │                    │──UPDATE status───▶│
     │                    │◀──200 OK───────────│                    │
     │◀──response────────│                    │                    │
```

---

## 技术栈

### 后端技术

| 类别 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| Web 框架 | FastAPI | 0.104+ | 高性能异步 API 框架 |
| ORM | SQLAlchemy | 2.0+ | 异步 ORM 支持 |
| 数据库 | SQLite | 3.x | 开发环境，生产可替换为 PostgreSQL |
| 认证 | python-jose | 3.3.0 | JWT Token 处理 |
| 密码哈希 | bcrypt | 4.0+ | 安全的密码存储 |
| 数据验证 | Pydantic | 2.5+ | 请求数据验证 |
| 服务器 | Uvicorn | 0.24+ | ASGI 服务器 |
| 测试 | pytest | 7.4+ | Python 测试框架 |
| 异步测试 | pytest-asyncio | 0.21+ | 异步测试支持 |
| HTTP 测试客户端 | httpx | 0.26+ | 异步 HTTP 测试 |

### 前端技术

| 端 | 框架 | UI 库 | 状态管理 | 路由 | HTTP 客户端 | 图表 |
|---|------|-------|---------|------|------------|------|
| Admin | Vue 3 + Vite | Element Plus | Pinia | Vue Router | Axios | ECharts |
| Merchant | Vue 3 + Vite | Element Plus | Pinia | Vue Router | Axios | ECharts |
| User | Vue 3 + Vite | Vant 4 | Pinia | Vue Router | Axios | — |

### 测试技术

| 层级 | 工具 | 说明 |
|------|------|------|
| 后端单元测试 | pytest | Service 层、Schema 验证 |
| 后端集成测试 | pytest + httpx | API 端点测试 |
| 后端 E2E 测试 | pytest | 完整业务流程 |
| 前端组件测试 | Vitest + Vue Test Utils | 组件功能测试 |
| 覆盖率统计 | coverage.py / vitest | 代码覆盖率报告 |

---

## 架构分层

### 1. 前端层 (Frontend Layer)

三个独立的前端应用，每个应用负责特定的用户角色：

- **Admin**: 平台管理后台，管理用户、商家、订单
- **Merchant**: 商家端，管理商品、分类、订单处理
- **User**: 用户端（移动端），浏览商家、下单、跟踪订单

### 2. API 网关层 (API Gateway)

FastAPI 应用作为统一的 API 网关：

- **路由分发**: 将请求分发到对应的端点处理器
- **认证中间件**: JWT Token 验证
- **限流中间件**: 基于 IP 的请求限流
- **日志中间件**: 请求日志记录
- **CORS 处理**: 跨域请求处理
- **异常处理**: 全局异常捕获和统一响应格式

### 3. 业务逻辑层 (Service Layer)

独立的 Service 类处理业务逻辑：

| Service | 职责 |
|---------|------|
| AuthService | 用户注册、登录、Token 管理 |
| UserService | 用户信息管理、地址管理 |
| MerchantService | 商家信息 CRUD、审批流程 |
| CategoryService | 商品分类管理 |
| ProductService | 商品 CRUD、库存管理 |
| OrderService | 订单创建、状态流转、支付 |
| AddressService | 用户地址管理 |
| AdminService | 数据统计、仪表盘数据聚合 |

### 4. 数据访问层 (Data Access Layer)

SQLAlchemy ORM 提供数据访问：

- **Models**: SQLAlchemy 模型定义
- **Schemas**: Pydantic 数据验证模型
- **Database**: 异步数据库会话管理

### 5. 数据库层 (Database Layer)

SQLite 数据库存储所有业务数据：

- users: 用户表
- merchants: 商家表
- categories: 商品分类表
- products: 商品表
- addresses: 用户地址表
- orders: 订单表
- order_items: 订单项表

---

## 核心组件

### 认证系统

```
┌─────────────────────────────────────────────────────────┐
│                    Authentication Flow                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Client ──▶ POST /auth/login ──▶ AuthService            │
│                       │                                   │
│                       ├── Verify credentials             │
│                       ├── Check user status              │
│                       ├── Generate JWT Token             │
│                       └── Return token + user info       │
│                                                          │
│  Client ──▶ GET /protected ──▶ Dependency Injection     │
│                       │                                   │
│                       ├── Validate Token                 │
│                       ├── Get user from DB               │
│                       └── Return current_user            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 中间件链

```
Request ──▶ CORS Middleware
           ──▶ Rate Limiter Middleware
           ──▶ Logging Middleware
           ──▶ Authentication (if required)
           ──▶ API Endpoint
           ──▶ Response
```

### 依赖注入

```python
# 依赖注入链
get_current_user ──▶ get_current_admin_user
                ──▶ get_current_merchant_user

# 数据库会话
get_db ──▶ AsyncSession ──▶ Service Methods
```

---

## 相关文档

- [项目结构](./project-structure.md) - 详细的目录结构说明
- [数据模型](./data-models.md) - 数据库模型设计
- [API 设计](../design/api-design.md) - API 接口规范
