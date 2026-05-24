# 快速开始指南

本文档提供详细的步骤来本地部署和运行 GoEats 外卖点餐系统。

---

## 目录

- [环境准备](#环境准备)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [数据库初始化](#数据库初始化)
- [验证安装](#验证安装)
- [常见问题](#常见问题)

---

## 环境准备

### 必需软件

| 软件 | 版本要求 | 下载地址 |
|------|---------|---------|
| Python | 3.10+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| npm | 9+ | 随 Node.js 一起安装 |

### 验证安装

```bash
# 检查 Python 版本
python --version
# 预期输出: Python 3.10.x 或更高

# 检查 Node.js 版本
node --version
# 预期输出: v18.x.x 或更高

# 检查 npm 版本
npm --version
# 预期输出: 9.x.x 或更高
```

---

## 后端部署

### 1. 进入后端目录

```bash
cd backend
```

### 2. 创建虚拟环境

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python seed_data.py
```

此命令将：
- 创建所有数据库表
- 插入测试数据（管理员、商家、用户、商品、订单等）

### 5. 启动后端服务器

```bash
python server.py
```

服务器将在以下地址运行：
- **API 服务**: http://localhost:8000
- **Swagger 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc

---

## 前端部署

### 管理后台 (Admin)

```bash
cd frontend/admin
npm install
npm run dev
```

运行地址: http://localhost:5173

### 商家端 (Merchant)

```bash
cd frontend/merchant
npm install
npm run dev
```

运行地址: http://localhost:5174

### 用户端 (User)

```bash
cd frontend/user
npm install
npm run dev
```

运行地址: http://localhost:5175

---

## 数据库初始化

### 测试数据说明

`seed_data.py` 会创建以下测试数据：

| 数据类型 | 数量 | 说明 |
|---------|------|------|
| 管理员 | 1 | 用户名: admin |
| 商家 | 2 | merchant1, merchant2 |
| 普通用户 | 2 | user1, user2 |
| 商品分类 | 8 | 分布在两个商家下 |
| 商品 | 14 | 分布在各个分类下 |
| 用户地址 | 3 | 属于 user1 |
| 订单 | 5 | 包含多个订单项 |

### 默认账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| Admin | `admin` | `admin123` | 平台管理员 |
| Merchant | `merchant1` | `merchant123` | 商家1 |
| Merchant | `merchant2` | `merchant123` | 商家2 |
| User | `user1` | `user123` | 普通用户1 |
| User | `user2` | `user123` | 普通用户2 |

### 重新初始化数据库

如果需要重置数据库：

```bash
# 删除现有数据库文件
del food_delivery.db        # Windows
rm food_delivery.db         # macOS/Linux

# 重新初始化
python seed_data.py
```

---

## 验证安装

### 1. 检查后端 API

在浏览器中访问 http://localhost:8000/docs，您应该能看到 Swagger UI 界面，列出了所有可用的 API 端点。

### 2. 测试登录

**管理后台:**
1. 打开 http://localhost:5173
2. 使用 `admin` / `admin123` 登录
3. 应该能看到仪表盘页面

**商家端:**
1. 打开 http://localhost:5174
2. 使用 `merchant1` / `merchant123` 登录
3. 应该能看到商家仪表盘

**用户端:**
1. 打开 http://localhost:5175
2. 使用 `user1` / `user123` 登录
3. 应该能看到首页商家列表

### 3. 运行测试

```bash
# 后端测试
cd backend
pytest -v

# 前端测试
cd frontend/admin && npm run test:run
cd frontend/merchant && npm run test:run
cd frontend/user && npm run test:run
```

---

## 常见问题

### 端口被占用

如果 8000、5173、5174 或 5175 端口被占用：

**后端 (server.py):**
```python
# 修改端口
uvicorn.run("app.main:app", host="0.0.0.0", port=8001)
```

**前端 (vite.config.js):**
```javascript
export default defineConfig({
  server: {
    port: 5176  // 修改为其他端口
  }
})
```

### Python 虚拟环境激活失败

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### npm 安装速度慢

使用国内镜像：
```bash
npm config set registry https://registry.npmmirror.com
```

### 数据库连接错误

确保在 `backend/` 目录下运行，检查数据库配置文件 `app/config.py`。

---

## 下一步

- 查看 [系统架构](../architecture/system-architecture.md) 了解系统整体设计
- 查看 [API 设计规范](../design/api-design.md) 了解 API 接口详情
- 查看 [开发计划](../planning/development-plan.md) 了解项目开发进度
