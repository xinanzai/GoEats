# 项目目录结构

> **版本**: v1.0
> **更新日期**: 2026-05-24

---

## 目录

- [整体结构](#整体结构)
- [后端结构](#后端结构)
- [前端结构](#前端结构)
- [文档结构](#文档结构)
- [关键文件说明](#关键文件说明)

---

## 整体结构

```
GoEats/
├── backend/                      # 后端项目
├── frontend/                     # 前端项目
│   ├── admin/                    # 管理后台
│   ├── merchant/                 # 商家端
│   └── user/                     # 用户端
├── doc/                          # 项目文档
│   ├── overview/                 # 项目概览
│   ├── architecture/             # 架构设计
│   ├── planning/                 # 开发计划
│   ├── design/                   # 设计规范
│   └── guides/                   # 开发指南
├── .gitignore
├── README.md                     # 项目根目录入口
├── start_server.bat              # 启动服务器脚本
└── stop_server.bat               # 停止服务器脚本
```

---

## 后端结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI 应用入口
│   ├── config.py                 # 配置管理
│   ├── database.py               # 数据库连接
│   │
│   ├── models/                   # SQLAlchemy 数据模型
│   │   ├── __init__.py
│   │   ├── user.py               # 用户模型
│   │   ├── merchant.py           # 商家模型
│   │   ├── category.py           # 分类模型
│   │   ├── product.py            # 商品模型
│   │   ├── address.py            # 地址模型
│   │   ├── order.py              # 订单模型
│   │   └── order_item.py         # 订单项模型
│   │
│   ├── schemas/                  # Pydantic 数据验证模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── merchant.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── address.py
│   │
│   ├── api/                      # API 路由
│   │   ├── __init__.py
│   │   ├── router.py             # 路由聚合
│   │   └── endpoints/            # API 端点
│   │       ├── __init__.py
│   │       ├── auth.py           # 认证接口
│   │       ├── users.py          # 用户接口
│   │       ├── merchants.py      # 商家接口
│   │       ├── categories.py     # 分类接口
│   │       ├── products.py       # 商品接口
│   │       ├── orders.py         # 订单接口
│   │       ├── admin.py          # 管理接口
│   │       └── upload.py         # 文件上传接口
│   │
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── merchant_service.py
│   │   ├── category_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   ├── address_service.py
│   │   └── admin_service.py
│   │
│   ├── core/                     # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py           # 密码加密、JWT
│   │   ├── dependencies.py       # 依赖注入
│   │   └── exceptions.py         # 自定义异常
│   │
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── file_handler.py       # 文件处理
│   │   └── logger.py             # 日志配置
│   │
│   └── middleware/               # 中间件
│       ├── __init__.py
│       ├── logging_middleware.py # 请求日志中间件
│       └── rate_limiter.py       # 限流中间件
│
├── tests/                        # 测试文件
│   ├── __init__.py
│   ├── conftest.py               # 全局测试 fixtures
│   │
│   ├── integration/              # 集成测试
│   │   ├── __init__.py
│   │   ├── test_admin_flow.py
│   │   ├── test_merchant_integration.py
│   │   ├── test_merchant_category_product.py
│   │   ├── test_merchant_orders.py
│   │   └── test_user_flow.py
│   │
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_merchants.py
│   ├── test_products.py
│   ├── test_orders.py
│   ├── test_admin.py
│   ├── test_user_service.py
│   ├── test_merchant_service.py
│   ├── test_product_service.py
│   ├── test_order_service.py
│   ├── test_address_service.py
│   ├── test_schemas.py
│   ├── test_security.py
│   ├── test_register_flow.py
│   ├── test_order_flow.py
│   └── test_approval_flow.py
│
├── uploads/                      # 文件上传目录
│   ├── avatars/                  # 头像上传
│   ├── merchants/                # 商家 Logo
│   └── products/                 # 商品图片
│
├── requirements.txt              # Python 依赖
├── pytest.ini                    # 测试配置
├── seed_data.py                  # 测试数据种子
├── server.py                     # 服务器启动脚本
├── init_database.py              # 数据库初始化
└── init_database.bat             # 数据库初始化脚本
```

### 后端关键目录说明

| 目录 | 职责 |
|------|------|
| `app/models/` | SQLAlchemy ORM 模型定义，对应数据库表结构 |
| `app/schemas/` | Pydantic 数据验证模型，用于请求/响应数据验证 |
| `app/api/endpoints/` | API 路由端点，处理 HTTP 请求和响应 |
| `app/services/` | 业务逻辑层，包含核心业务规则 |
| `app/core/` | 核心功能：安全、依赖注入、异常处理 |
| `app/utils/` | 工具函数：文件处理、日志记录 |
| `app/middleware/` | 中间件：日志、限流 |
| `tests/` | 测试文件：单元测试、集成测试、E2E 测试 |

---

## 前端结构

### Admin / Merchant / User 通用结构

```
frontend/{admin|merchant|user}/
├── src/
│   ├── api/                      # API 请求模块
│   │   ├── auth.js               # 认证 API
│   │   ├── users.js              # 用户 API
│   │   ├── merchants.js          # 商家 API
│   │   ├── products.js           # 商品 API
│   │   ├── orders.js             # 订单 API
│   │   ├── upload.js             # 上传 API
│   │   └── ...
│   │
│   ├── views/                    # 页面组件
│   │   ├── Login.vue
│   │   ├── Dashboard.vue
│   │   └── ...
│   │
│   ├── router/                   # 路由配置
│   │   └── index.js
│   │
│   ├── store/                    # Pinia 状态管理
│   │   └── auth.js
│   │
│   ├── layouts/                  # 布局组件
│   │   └── MainLayout.vue
│   │
│   ├── utils/                    # 工具函数
│   │   └── request.js            # Axios 封装
│   │
│   ├── App.vue                   # 根组件
│   └── main.js                   # 入口文件
│
├── tests/                        # 前端测试
│   ├── setup.js                  # 测试配置
│   ├── views/                    # 页面测试
│   ├── store/                    # Store 测试
│   ├── layouts/                  # 布局测试
│   └── utils/                    # 工具测试
│
├── index.html                    # HTML 模板
├── package.json                  # 项目依赖
├── vite.config.js                # Vite 配置
└── ...
```

### 各端页面差异

| 端 | 特有页面 |
|---|---------|
| **Admin** | Users.vue, Merchants.vue, Orders.vue, Statistics.vue |
| **Merchant** | Products.vue, Categories.vue, Settings.vue, WaitingApproval.vue, Register.vue |
| **User** | Home.vue, Cart.vue, Checkout.vue, Orders.vue, OrderDetail.vue, Profile.vue, Addresses.vue, MerchantDetail.vue |

---

## 文档结构

```
doc/
├── overview/                     # 项目概览
│   └── README.md                 # 项目介绍、技术栈、快速开始
│
├── architecture/                 # 架构设计
│   ├── system-architecture.md    # 系统架构设计
│   ├── project-structure.md      # 项目目录结构（本文档）
│   └── data-models.md            # 数据模型设计
│
├── planning/                     # 开发计划
│   ├── development-plan.md       # 开发计划
│   └── implementation-tracker.md # 实施进度跟踪
│
├── design/                      # 设计规范
│   ├── backend-conventions.md    # 后端代码规范
│   ├── frontend-conventions.md   # 前端代码规范
│   ├── api-design.md             # API 设计规范
│   ├── database-design.md        # 数据库设计规范
│   ├── testing-standards.md      # 测试规范
│   └── security-standards.md     # 安全规范
│
└── guides/                      # 开发指南
    ├── getting-started.md        # 快速开始指南
    └── troubleshooting.md        # 常见问题与修复记录
```

---

## 关键文件说明

### 后端核心文件

| 文件 | 说明 |
|------|------|
| `app/main.py` | FastAPI 应用入口，配置中间件、CORS、路由 |
| `app/config.py` | 环境配置，读取环境变量 |
| `app/database.py` | 数据库连接配置，异步会话管理 |
| `app/core/security.py` | JWT Token 创建/验证、密码哈希 |
| `app/core/dependencies.py` | 依赖注入：当前用户、角色验证 |
| `app/core/exceptions.py` | 自定义异常类 |
| `app/api/router.py` | 路由聚合，注册所有端点 |

### 前端核心文件

| 文件 | 说明 |
|------|------|
| `src/main.js` | Vue 应用入口，注册 Pinia、Router |
| `src/router/index.js` | 路由配置，路由守卫 |
| `src/utils/request.js` | Axios 实例封装，请求/响应拦截器 |
| `src/store/auth.js` | 认证状态管理 |

### 测试核心文件

| 文件 | 说明 |
|------|------|
| `backend/tests/conftest.py` | 全局测试 fixtures：数据库、客户端、测试用户 |
| `frontend/*/tests/setup.js` | Vitest 测试配置 |

---

## 相关文档

- [系统架构](./system-architecture.md) - 系统整体架构设计
- [数据模型](./data-models.md) - 数据库模型设计详情
- [后端规范](../design/backend-conventions.md) - 后端代码规范
