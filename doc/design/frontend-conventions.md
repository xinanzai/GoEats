# 前端代码规范

> **版本**: v1.0
> **更新日期**: 2026-05-24
> **适用范围**: GoEats 前端三端 (frontend/admin, frontend/merchant, frontend/user)

---

## 目录

- [命名规范](#命名规范)
- [目录结构规范](#目录结构规范)
- [Vue 组件规范](#vue-组件规范)
- [API 请求规范](#api-请求规范)
- [Pinia Store 规范](#pinia-store-规范)
- [路由规范](#路由规范)

---

## 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件夹名 | kebab-case | `user-profile`, `order-list` |
| 组件文件名 | PascalCase | `UserProfile.vue`, `OrderCard.vue` |
| 组合式函数 | camelCase, use 前缀 | `useAuth.js`, `useCart.js` |
| 变量/函数名 | camelCase | `userName`, `fetchOrders()` |
| 常量名 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| CSS 类名 | BEM 命名 | `.order-card__title`, `.btn--primary` |

---

## 目录结构规范

### 实际目录结构

```
src/
├── api/                    # API 请求模块
│   ├── auth.js             # 认证 API
│   ├── *.js                # 按业务模块拆分
│   └── ...
├── layouts/                # 布局组件
│   └── MainLayout.vue
├── router/                 # 路由配置
│   └── index.js
├── store/                  # Pinia 状态管理
│   ├── auth.js             # 认证状态
│   └── cart.js             # 购物车状态（user 端）
├── utils/                  # 工具函数
│   └── request.js          # Axios 封装
├── views/                  # 页面组件
│   ├── Login.vue
│   ├── Dashboard.vue
│   └── ...
├── App.vue                 # 根组件
└── main.js                 # 入口文件
```

### 各端 API 模块差异

| 模块 | Admin | Merchant | User |
|------|-------|----------|------|
| auth.js | ✅ | ✅ | ✅ |
| admin.js | ✅ | - | - |
| merchants.js | ✅ | ✅ | ✅ |
| products.js | - | ✅ | ✅ |
| orders.js | ✅ | ✅ | ✅ |
| upload.js | ✅ | ✅ | ✅ |
| dashboard.js | - | ✅ | - |
| users.js | - | - | ✅ |

### 各端 UI 框架

| 端 | UI 框架 | 说明 |
|---|---------|------|
| **Admin** | Element Plus | 桌面端管理后台，使用 Element Plus 组件库 |
| **Merchant** | Element Plus | 桌面端商家后台，使用 Element Plus 组件库 |
| **User** | Vant | 移动端用户端，使用 Vant 组件库（自动导入） |

---

## Vue 组件规范

### 单文件组件结构顺序

```vue
<template>
  <!-- 1. 模板部分 -->
</template>

<script setup>
// 2. 导入
// 3. Props 定义
// 4. Emits 定义
// 5. 响应式数据
// 6. 计算属性
// 7. 方法
// 8. 生命周期钩子
</script>

<style scoped>
/* 9. 样式部分 */
</style>
```

### 组件 Props 规范

```javascript
// ✅ 正确 - 完整定义 Props
const props = defineProps({
  title: {
    type: String,
    required: true,
    default: ''
  },
  count: {
    type: Number,
    default: 0
  }
})
```

---

## API 请求规范

- 所有 API 请求必须通过 `utils/request.js` 封装的 axios 实例
- 每个业务模块独立的 API 文件
- API 函数必须有 JSDoc 注释说明参数和返回值
- 统一的错误处理在 axios 拦截器中处理

---

## Pinia Store 规范

- 使用 Composition API 风格 (`setup` 函数)
- State 使用 `ref`/`reactive`
- Getters 使用 `computed`
- Actions 使用普通函数
- Store 文件按业务模块拆分

---

## 路由规范

- 使用懒加载：`component: () => import('...')`
- 所有页面路由必须配置 `meta.title`
- 需要认证的路由配置 `meta.requiresAuth: true`
- 路由守卫统一在 `router/index.js` 中处理

---

## 相关文档

- [后端代码规范](./backend-conventions.md) - 后端开发规范
- [测试规范](./testing-standards.md) - 测试编写规范
