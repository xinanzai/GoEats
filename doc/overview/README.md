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
- [Features / 功能特性](#features--功能特性)
- [Quick Start / 快速启动](#quick-start--快速启动)
- [Documentation / 文档](#documentation--文档)
- [Testing / 测试](#testing--测试)
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

详见 [Getting Started Guide](../guides/getting-started.md)

### Prerequisites / 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

### Backend Setup / 后端启动

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py
python server.py
```

### Frontend Setup / 前端启动

```bash
# Admin Portal
cd frontend/admin && npm install && npm run dev

# Merchant Portal
cd frontend/merchant && npm install && npm run dev

# User App
cd frontend/user && npm install && npm run dev
```

### Default Accounts / 默认账号

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Merchant | `merchant1` | `merchant123` |
| User | `user1` | `user123` |

---

## Documentation / 文档

- [System Architecture](../architecture/system-architecture.md) - 系统架构设计
- [Project Structure](../architecture/project-structure.md) - 项目目录结构
- [Data Models](../architecture/data-models.md) - 数据模型设计
- [Development Plan](../planning/development-plan.md) - 开发计划
- [Implementation Tracker](../planning/implementation-tracker.md) - 实施进度跟踪
- [Backend Conventions](../design/backend-conventions.md) - 后端代码规范
- [Frontend Conventions](../design/frontend-conventions.md) - 前端代码规范
- [API Design](../design/api-design.md) - API 设计规范
- [Database Design](../design/database-design.md) - 数据库设计规范
- [Testing Standards](../design/testing-standards.md) - 测试规范
- [Security Standards](../design/security-standards.md) - 安全规范
- [Getting Started](../guides/getting-started.md) - 快速开始指南
- [Troubleshooting](../guides/troubleshooting.md) - 常见问题与修复记录

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

## License / 许可

This project is licensed under the MIT License.

本项目采用 MIT 许可证。

---

<div align="center">
  Made with ❤️ by GoEats Team
</div>
