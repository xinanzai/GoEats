# 常见问题与故障排除

> **版本**: v1.0
> **更新日期**: 2026-05-24
> **适用范围**: GoEats 项目开发、部署、测试

---

## 目录

- [环境配置问题](#环境配置问题)
- [数据库问题](#数据库问题)
- [认证问题](#认证问题)
- [前端问题](#前端问题)
- [测试问题](#测试问题)
- [已知 Bug 修复记录](#已知-bug-修复记录)

---

## 环境配置问题

### Python 虚拟环境激活失败

**问题**: Windows PowerShell 中执行 `.\venv\Scripts\activate` 报错

**解决方案**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### npm 安装速度慢

**问题**: npm install 下载依赖速度慢或超时

**解决方案**:
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com
```

### 端口被占用

**问题**: 8000、5173、5174、5175 端口已被占用

**解决方案**:

**后端修改端口 (server.py)**:
```python
uvicorn.run("app.main:app", host="0.0.0.0", port=8001)
```

**前端修改端口 (vite.config.js)**:
```javascript
export default defineConfig({
  server: {
    port: 5176
  }
})
```

---

## 数据库问题

### SQLite 并发写入问题

**问题**: 多个请求同时写入数据库时报错

**说明**: 开发环境无影响，生产环境建议迁移到 PostgreSQL/MySQL

### 数据库初始化失败

**问题**: 运行 `seed_data.py` 时报错

**解决方案**:
```bash
# 删除现有数据库文件
del food_delivery.db        # Windows
rm food_delivery.db         # macOS/Linux

# 重新初始化
python seed_data.py
```

### 数据库连接错误

**问题**: 后端启动时数据库连接失败

**解决方案**:
1. 确保在 `backend/` 目录下运行
2. 检查 `app/config.py` 中的数据库配置
3. 确认 aiosqlite 已安装

---

## 认证问题

### Token 过期处理

**问题**: 前端请求返回 401 错误

**解决方案**:
- 前端拦截 401 响应，自动跳转登录页
- 实现 refresh endpoint，使用 refresh token 获取新 access token

### JWT Token sub 字段类型错误

**问题**: python-jose 要求 `sub` 为字符串，但传入的是整数

**修复方案**:
```python
# ✅ 正确
token = create_access_token(data={"sub": str(user.id)})

# ❌ 错误
token = create_access_token(data={"sub": user.id})
```

### 登录服务未检查用户状态

**问题**: 被禁用的用户仍可登录

**修复方案**:
```python
# 添加 is_active 检查
if not user.is_active:
    raise ValidationException("用户已被禁用")
```

---

## 前端问题

### 跨域问题 (CORS)

**问题**: 前端请求后端 API 时报 CORS 错误

**解决方案**: 后端配置 CORS 中间件
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 组件通信问题

**问题**: 父子组件间数据传递复杂

**解决方案**:
- 优先使用 Pinia 进行状态管理
- 简单场景使用 props/emit
- 避免使用 EventBus

### 分类 API 调用路径错误

**问题**: 用户端获取商家分类时 API 路径错误

**修复方案**:
```javascript
// ✅ 正确
axios.get('/categories', { params: { merchant_id: id } })

// ❌ 错误
axios.get(`/merchants/${id}/categories`)
```

---

## 测试问题

### 测试环境限流触发 429

**问题**: E2E 测试短时间内大量请求触发限流中间件

**修复方案**:
```python
# main.py 中添加 pytest 环境检测
if os.getenv("PYTEST_CURRENTLY") != "1":
    app.add_middleware(RateLimiter)
```

### 商品列表 API 分页响应结构

**问题**: API 返回分页对象，测试代码直接遍历导致错误

**修复方案**:
```python
# ✅ 正确
items = response.json()["items"]
for item in items:
    ...

# ❌ 错误
for item in response.json():
    ...
```

### Token 时间精度测试容差

**问题**: Token 过期时间测试因时间精度失败

**修复方案**:
```python
# 增加时间容差
assert abs(token_exp - expected_exp) < 5  # 5秒容差
```

### Schema 字段不匹配

**问题**: CategoryCreate/ProductCreate Schema 的 merchant_id 必填导致调用失败

**修复方案**:
- CategoryCreate: 移除 merchant_id 必填，由 API 层从 current_user 获取
- ProductCreate: 移除 merchant_id 必填，由 API 层从 current_user 获取

---

## 已知 Bug 修复记录

### 后端 Bug

| 日期 | 问题描述 | 修复方案 | 影响范围 |
|------|---------|---------|---------|
| 2026-05-23 | passlib/bcrypt 兼容性 | 改用 bcrypt 直接调用 | 安全模块 |
| 2026-05-23 | JWT Token sub 字段类型 | 整数转为字符串 | 认证 |
| 2026-05-23 | 登录未检查用户禁用状态 | 添加 is_active 检查 | 认证安全 |
| 2026-05-23 | auth_service flush()/commit() | 改为 commit() | E2E 测试 |
| 2026-05-23 | get_my_products response_model | 改为 dict 类型 | 商品 API |
| 2026-05-23 | MerchantResponse 缺少 approved_by | 添加字段 | Schema |
| 2026-05-23 | admin_service 日期处理 | 处理 SQLite 字符串日期 | 统计 |

### 前端 Bug

| 日期 | 问题描述 | 修复方案 | 影响范围 |
|------|---------|---------|---------|
| 2026-05-23 | 用户端分类 API 路径错误 | 修正 API 路径 | 用户端 |

### 测试 Bug

| 日期 | 问题描述 | 修复方案 | 影响范围 |
|------|---------|---------|---------|
| 2026-05-23 | 测试环境限流触发 429 | 添加 pytest 环境检测 | E2E 测试 |
| 2026-05-23 | 商品列表分页响应遍历错误 | 使用 items 字段 | 集成测试 |
| 2026-05-23 | Token 时间精度测试失败 | 增加时间容差 | 安全测试 |
| 2026-05-23 | conftest._create_product 缺参数 | 添加 description 参数 | 测试 fixtures |

---

## 相关文档

- [快速开始指南](./getting-started.md) - 环境配置指南
- [后端代码规范](../design/backend-conventions.md) - 后端开发规范
- [前端代码规范](../design/frontend-conventions.md) - 前端开发规范
