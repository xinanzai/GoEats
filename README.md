<div align="center">

# 🍔 GoEats - Food Delivery System / 外卖点餐系统

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.3-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Element Plus](https://img.shields.io/badge/Element%20Plus-2.4-409EFF)](https://element-plus.org/)
[![Vant](https://img.shields.io/badge/Vant-4.8-07c160)](https://vant-ui.github.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**GoEats** 是一个全功能的外卖点餐系统，包含三个独立前端（管理后台、商家端、用户端）和健壮的 RESTful API 后端。

</div>

---

## 📋 快速开始

```bash
# 后端启动
cd backend
python -m venv venv && .\venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py
python server.py

# 前端启动
cd frontend/admin && npm install && npm run dev  # 管理后台 :5173
cd frontend/merchant && npm install && npm run dev  # 商家端 :5174
cd frontend/user && npm install && npm run dev  # 用户端 :5175
```

**默认账号**:
| 角色 | 用户名 | 密码 |
|------|--------|------|
| Admin | `admin` | `admin123` |
| Merchant | `merchant1` | `merchant123` |
| User | `user1` | `user123` |

---

## 📚 文档

详细文档请查看 [doc/](./doc/) 目录：

### 项目概览
- [项目介绍](./doc/overview/README.md) - 完整的项目概览、技术栈、功能特性

### 架构设计
- [系统架构](./doc/architecture/system-architecture.md) - 整体架构设计、数据流图
- [项目结构](./doc/architecture/project-structure.md) - 详细的目录结构说明
- [数据模型](./doc/architecture/data-models.md) - 数据库模型设计、ER 图

### 开发计划
- [开发计划](./doc/planning/development-plan.md) - 开发阶段规划、里程碑
- [实施进度](./doc/planning/implementation-tracker.md) - 任务进度跟踪、Bug 修复记录

### 设计规范
- [后端规范](./doc/design/backend-conventions.md) - Python/FastAPI 代码规范
- [前端规范](./doc/design/frontend-conventions.md) - Vue 3 代码规范
- [API 设计](./doc/design/api-design.md) - RESTful API 接口规范
- [数据库设计](./doc/design/database-design.md) - SQLite 表结构设计
- [测试规范](./doc/design/testing-standards.md) - 测试编写规范、覆盖率要求
- [安全规范](./doc/design/security-standards.md) - 安全设计原则

### 开发指南
- [快速开始](./doc/guides/getting-started.md) - 详细的环境配置和部署指南
- [故障排除](./doc/guides/troubleshooting.md) - 常见问题与解决方案

---

## 🧪 测试

```bash
# 后端测试（403 个测试）
cd backend && pytest -v

# 前端测试（129 个测试）
cd frontend/admin && npm run test:run
cd frontend/merchant && npm run test:run
cd frontend/user && npm run test:run
```

**测试总数**: 532+ 个测试，全部通过 ✅

---

## 📄 License

MIT License

---

<div align="center">
  Made with ❤️ by GoEats Team
</div>
