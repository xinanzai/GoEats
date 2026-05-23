<div align="center">

# 🍔 GoEats - Food Delivery System / 外卖点餐系统

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.3-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Element Plus](https://img.shields.io/badge/Element%20Plus-2.4-409EFF)](https://element-plus.org/)
[![Vant](https://img.shields.io/badge/Vant-4.8-07c160)](https://vant-ui.github.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**GoEats** is a full-featured food delivery system with three separate frontends (Admin, Merchant, User) and a robust RESTful API backend.

**GoEats** 是一个全功能的外卖点餐系统，包含三个独立前端（管理后台、商家端、用户端）和健壮的 RESTful API 后端。

</div>

---

## 📋 Table of Contents / 目录

- [Overview / 项目概览](#overview--项目概览)
- [Tech Stack / 技术栈](#tech-stack--技术栈)
- [System Architecture / 系统架构](#system-architecture--系统架构)
- [Project Structure / 项目结构](#project-structure--项目结构)
- [Features / 功能特性](#features--功能特性)
- [Quick Start / 快速启动](#quick-start--快速启动)
- [API Documentation / API 文档](#api-documentation--api-文档)
- [Testing / 测试](#testing--测试)
- [Preview / 界面预览](#preview--界面预览)
- [License / 许可](#license--许可)

---

## Overview / 项目概览

**English**

GoEats is a complete food delivery ordering system designed for three types of users:

- **Platform Administrators** - Manage users, review merchants, view statistics and order management
- **Merchants** - Register shop, manage products/categories, process orders
- **Consumers** - Browse restaurants, place orders, track delivery, manage addresses

The project includes comprehensive test coverage with **532+ tests** ensuring reliability and code quality.

**中文**

GoEats 是一个完整的外卖点餐系统，为三类用户设计：

- **平台管理员** - 用户管理、商家审核、数据统计、订单管理
- **商家** - 店铺注册、商品/分类管理、订单处理
- **消费者** - 浏览商家、下单点餐、订单追踪、地址管理

项目拥有全面的测试覆盖，**532+ 个测试用例**确保可靠性与代码质量。

---

## Tech Stack / 技术栈

### Backend / 后端

| Category | Technology |
|----------|-----------|
| Framework | Python 3.10+ / FastAPI 0.104 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite (via aiosqlite) |
| Authentication | JWT (python-jose) |
| Validation | Pydantic 2.5 |
| Password Hashing | bcrypt |
| Server | Uvicorn |

### Frontend / 前端

| Portal | Framework | UI Library | Charts |
|--------|-----------|------------|--------|
| **Admin** (管理后台) | Vue 3 + Vite | Element Plus | ECharts |
| **Merchant** (商家端) | Vue 3 + Vite | Element Plus | ECharts |
| **User** (用户端) | Vue 3 + Vite | Vant 4 (Mobile) | — |

### Testing / 测试

| Layer | Tool | Count |
|-------|------|-------|
| Backend Unit Tests | pytest + pytest-asyncio | 245 ✅ |
| Backend Integration Tests | pytest + httpx | 143 ✅ |
| Backend E2E Tests | pytest | 15 ✅ |
| Admin Frontend Tests | Vitest + Vue Test Utils | 42 ✅ |
| Merchant Frontend Tests | Vitest + Vue Test Utils | 36 ✅ |
| User Frontend Tests | Vitest + Vue Test Utils | 51 ✅ |

---

## System Architecture / 系统架构

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

### Data Model / 数据模型

```
User (1) ──── (1) Merchant
  │                    │
  │                    ├─── (N) Category ──── (N) Product
  │                    │
  │                    └─── (N) Order ──── (N) OrderItem
  │
  └─── (N) Address
```

---

## Project Structure / 项目结构

```
GoEats/
├── backend/                          # Backend application
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry
│   │   ├── config.py                 # Configuration
│   │   ├── database.py               # DB connection
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── api/
│   │   │   ├── router.py             # Route aggregation
│   │   │   └── endpoints/            # API endpoints
│   │   │       ├── auth.py           # Authentication
│   │   │       ├── users.py          # User management
│   │   │       ├── merchants.py      # Merchant management
│   │   │       ├── products.py       # Product management
│   │   │       ├── categories.py     # Category management
│   │   │       ├── orders.py         # Order management
│   │   │       └── admin.py          # Admin operations
│   │   ├── services/                 # Business logic
│   │   ├── core/                     # Core (security, deps)
│   │   └── middleware/               # Middleware
│   │       ├── logging_middleware.py # Request logging
│   │       └── rate_limiter.py       # Rate limiting
│   ├── tests/                        # Tests
│   │   ├── conftest.py               # Test fixtures
│   │   ├── integration/              # Integration & E2E tests
│   │   ├── test_auth.py
│   │   ├── test_user_service.py
│   │   ├── test_merchant_service.py
│   │   ├── test_product_service.py
│   │   ├── test_order_service.py
│   │   └── ...
│   ├── seed_data.py                  # Database seeder
│   └── server.py                     # Server startup script
│
├── frontend/
│   ├── admin/                        # Admin Portal
│   │   └── src/
│   │       ├── views/                # Pages
│   │       ├── api/                  # API calls
│   │       ├── router/               # Routes
│   │       ├── store/                # State (Pinia)
│   │       └── layouts/              # Layouts
│   │
│   ├── merchant/                     # Merchant Portal
│   │   └── src/
│   │       ├── views/                # Pages
│   │       ├── api/                  # API calls
│   │       ├── router/               # Routes
│   │       ├── store/                # State (Pinia)
│   │       └── layouts/              # Layouts
│   │
│   └── user/                         # User App (Mobile)
│       └── src/
│           ├── views/                # Pages
│           ├── api/                  # API calls
│           ├── router/               # Routes
│           └── store/                # State (Pinia)
│
├── design-specification.md           # Design specifications
├── development-plan.md               # Development plan
└── IMPLEMENTATION-PLAN.md            # Implementation progress
```

---

## Features / 功能特性

### Authentication / 认证系统
- **User registration & login** - Phone number & password
- **Merchant registration** - Requires admin approval
- **JWT token** - Secure authentication, auto-refresh
- **Role-based access** - User / Merchant / Admin

### Admin Portal / 管理后台
- **Dashboard** - Statistics cards, charts, recent orders
- **User management** - Paginated list, search, role filter, enable/disable
- **Merchant review** - Approve/reject merchant registrations
- **Order management** - Full order list with status filter, date range
- **Statistics** - Order trends, revenue trends, top-selling products

### Merchant Portal / 商家端
- **Dashboard** - Business statistics, order distribution charts
- **Product management** - CRUD, toggle availability, image upload
- **Category management** - CRUD, sort order
- **Order processing** - Prepare, deliver, complete orders
- **Shop settings** - Edit info, upload logo, update contact

### User App / 用户端 (Mobile)
- **Home** - Search restaurants, browse by category, sort options
- **Restaurant detail** - Menu by category, add to cart, cart float
- **Shopping cart** - Adjust quantities, total calculation
- **Checkout** - Address selection, order summary, submit
- **Order tracking** - Status tabs (pending, preparing, delivering, completed)
- **Profile** - Edit profile, manage addresses, order history

---

## Quick Start / 快速启动

### Prerequisites / 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

### Backend Setup / 后端启动

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database & seed data
python seed_data.py

# 5. Start server
python server.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Setup / 前端启动

**Admin Portal / 管理后台:**
```bash
cd frontend/admin
npm install
npm run dev
# Runs at http://localhost:5173
```

**Merchant Portal / 商家端:**
```bash
cd frontend/merchant
npm install
npm run dev
# Runs at http://localhost:5174
```

**User App / 用户端:**
```bash
cd frontend/user
npm install
npm run dev
# Runs at http://localhost:5175
```

### Default Accounts / 默认账号

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Merchant | `merchant1` | `merchant123` |
| User | `user1` | `user123` |

---

## API Documentation / API 文档

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints Overview

| Module | Endpoints |
|--------|-----------|
| **Auth** | `POST /api/v1/auth/register`, `/login`, `/refresh`, `/me`, `/merchant/register` |
| **Users** | `GET/PUT /api/v1/users/profile`, `PUT /api/v1/users/password` |
| **Addresses** | `GET/POST /api/v1/users/addresses`, `PUT/DELETE .../{id}`, `.../{id}/set-default` |
| **Merchants** | `GET /api/v1/merchants`, `GET /api/v1/merchants/{id}`, `GET/PUT /api/v1/merchants/me` |
| **Categories** | `GET/POST /api/v1/merchants/me/categories`, `PUT/DELETE .../{id}` |
| **Products** | `GET /api/v1/products`, `GET .../{id}`, `GET/POST/PUT/DELETE .../merchant/me[/{id}]` |
| **Orders** | `POST /api/v1/orders`, `GET .../users/me`, `GET/POST .../users/me/{id}[/cancel/pay]` |
| **Admin** | `GET /api/v1/admin/dashboard`, `/users`, `/merchants`, `/orders`, `/statistics` |

---

## Testing / 测试

### Run All Backend Tests / 运行全部后端测试

```bash
cd backend
pytest -v
```

### Run with Coverage / 带覆盖率运行

```bash
pytest --cov=app -v
```

### Run Frontend Tests / 运行前端测试

```bash
# Admin
cd frontend/admin && npm run test:run

# Merchant
cd frontend/merchant && npm run test:run

# User
cd frontend/user && npm run test:run
```

---

## Preview / 界面预览

| Portal | Screenshots |
|--------|-------------|
| **Admin Dashboard** | 📊 Statistics cards, ECharts line/bar/pie charts, recent orders list |
| **Admin Users** | 👥 User list with pagination, search, role filter, enable/disable |
| **Admin Merchants** | 🏪 Merchant list with approval workflow |
| **Merchant Dashboard** | 📈 Business stats, order distribution charts |
| **Merchant Products** | 🛍️ Product CRUD, category filter, toggle availability |
| **Merchant Orders** | 📋 Order processing (prepare → deliver → complete) |
| **User Home** | 🏠 Restaurant browsing, search, category filter, sort |
| **User Cart** | 🛒 Cart management, quantity adjust, checkout |
| **User Orders** | 📦 Order tracking with status tabs |

---

## License / 许可

This project is licensed under the MIT License.

本项目采用 MIT 许可证。

---

<div align="center">
  Made with ❤️ by GoEats Team
</div>
