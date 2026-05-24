# 测试规范

> **版本**: v1.0
> **更新日期**: 2026-05-24
> **适用范围**: GoEats 全项目测试

---

## 目录

- [测试框架与工具](#测试框架与工具)
- [测试目录结构](#测试目录结构)
- [后端测试规范](#后端测试规范)
- [前端测试规范](#前端测试规范)
- [测试覆盖率要求](#测试覆盖率要求)
- [测试编写原则](#测试编写原则)
- [测试运行命令](#测试运行命令)

---

## 测试框架与工具

| 层级 | 工具 | 说明 |
|------|------|------|
| 后端单元测试 | pytest | Python 标准测试框架 |
| 后端 API 测试 | pytest + httpx | 异步 HTTP 客户端测试 |
| 后端异步测试 | pytest-asyncio | 异步测试支持 |
| 前端单元测试 | Vitest | Vue 3 推荐的测试框架 |
| 前端组件测试 | @vue/test-utils | Vue 组件测试工具 |
| 覆盖率统计 | coverage.py (后端), vitest (前端) | 代码覆盖率 |

---

## 测试目录结构

### 后端测试

```
backend/tests/
├── __init__.py
├── conftest.py                  # 全局 fixture
├── integration/                 # 集成测试
│   ├── __init__.py
│   ├── test_admin_flow.py
│   ├── test_merchant_integration.py
│   ├── test_merchant_category_product.py
│   ├── test_merchant_orders.py
│   └── test_user_flow.py
├── test_auth.py                 # 认证测试
├── test_users.py                # 用户测试
├── test_merchants.py            # 商家测试
├── test_products.py             # 商品测试
├── test_orders.py               # 订单测试
├── test_admin.py                # 管理测试
├── test_user_service.py         # 用户服务测试
├── test_merchant_service.py     # 商家服务测试
├── test_product_service.py      # 商品服务测试
├── test_order_service.py        # 订单服务测试
├── test_address_service.py      # 地址服务测试
├── test_schemas.py              # Schema 验证测试
├── test_security.py             # 安全模块测试
├── test_register_flow.py        # 注册流程 E2E
├── test_order_flow.py           # 订单流程 E2E
└── test_approval_flow.py        # 审批流程 E2E
```

### 前端测试

```
frontend/{admin|merchant|user}/tests/
├── setup.js                     # 测试配置
├── views/                       # 页面测试
├── store/                       # Store 测试
├── layouts/                     # 布局测试
└── utils/                       # 工具测试
```

---

## 后端测试规范

### 测试命名规范

```
test_{方法名}_{场景}_{预期结果}
```

示例：
```python
def test_create_user_with_valid_data_should_return_user()
def test_get_user_with_invalid_id_should_raise_404()
def test_login_with_wrong_password_should_return_401()
```

### Service 层单元测试示例

```python
# tests/test_user_service.py
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
```

### Schema 验证测试示例

```python
# tests/test_schemas.py
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
```

### API 集成测试示例

```python
# tests/test_auth.py
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

    async def test_login_wrong_password(self, client, normal_user):
        """测试密码错误登录"""
        response = await client.post("/auth/login", json={
            "phone": normal_user.phone,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
```

---

## 前端测试规范

### Vitest 配置

```javascript
// vitest.config.js
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

### 组件测试示例

```javascript
// tests/views/Login.test.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Login from '@/views/Login.vue'

describe('Login', () => {
  it('应该正确渲染登录表单', () => {
    const wrapper = mount(Login)
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })

  it('点击登录按钮应该触发登录', async () => {
    const wrapper = mount(Login)
    await wrapper.find('button').trigger('click')
    // 验证登录逻辑
  })
})
```

### Store 测试示例

```javascript
// tests/store/auth.test.js
import { describe, it, expect } from 'vitest'
import { useAuthStore } from '@/store/auth'

describe('useAuthStore', () => {
  it('初始状态应该是未登录', () => {
    const store = useAuthStore()
    expect(store.isLoggedIn).toBe(false)
    expect(store.token).toBe(null)
  })

  it('登录成功后应该保存 token', () => {
    const store = useAuthStore()
    store.setToken('test-token')
    expect(store.token).toBe('test-token')
    expect(store.isLoggedIn).toBe(true)
  })
})
```

---

## 测试覆盖率要求

| 模块 | 最低覆盖率 | 说明 |
|------|-----------|------|
| Service 层 | ≥ 90% | 核心业务逻辑 |
| Schema 验证 | ≥ 95% | 数据验证 |
| API 端点 | ≥ 85% | 接口测试 |
| 工具函数 | ≥ 90% | 纯函数易于测试 |
| 前端组件 | ≥ 80% | UI 组件 |
| 前端 Store | ≥ 85% | 状态管理 |
| 整体项目 | ≥ 85% | 最低要求 |

---

## 测试编写原则

1. **AAA 模式**: Arrange(安排) → Act(执行) → Assert(断言)
2. **测试独立性**: 每个测试用例应独立运行，不依赖执行顺序
3. **测试可重复性**: 测试结果应该确定，不依赖外部状态
4. **测试命名清晰**: 从命名能知道测试什么场景
5. **一个测试一个断言**: 尽量保持测试的单一职责
6. **测试边界条件**: 空值、最大值、最小值、异常情况
7. **使用 Fixture**: 重复的测试数据使用 fixture 管理

---

## 测试运行命令

### 后端测试

```bash
# 运行所有测试
cd backend
pytest -v

# 运行特定测试文件
pytest tests/test_user_service.py -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html -v

# 运行失败的测试
pytest --lf
```

### 前端测试

```bash
# 运行所有测试
cd frontend/admin
npm run test:run

# 监听模式
npm run test

# 生成覆盖率报告
npm run test -- --coverage
```

---

## 相关文档

- [后端代码规范](./backend-conventions.md) - 后端开发规范
- [前端代码规范](./frontend-conventions.md) - 前端开发规范
- [快速开始指南](../guides/getting-started.md) - 测试环境配置
