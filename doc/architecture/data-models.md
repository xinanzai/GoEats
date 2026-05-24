# 数据模型设计

> **版本**: v1.0
> **更新日期**: 2026-05-24

---

## 目录

- [ER 关系图](#er-关系图)
- [数据模型详情](#数据模型详情)
- [模型关系说明](#模型关系说明)
- [枚举类型](#枚举类型)

---

## ER 关系图

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   User      │     │   Merchant       │     │  Category   │
├─────────────┤     ├──────────────────┤     ├─────────────┤
│ id          │     │ id               │     │ id          │
│ username    │     │ user_id (FK)     │     │ name        │
│ phone       │─────│ business_name    │     │ merchant_id │
│ password    │     │ contact_phone    │     │   (FK)      │
│ avatar      │     │ address          │     │ sort_order  │
│ role        │     │ status           │     └─────────────┘
│ created_at  │     │ created_at       │              ▲
│ updated_at  │     │ approved_at      │              │
└─────────────┘     │ approved_by      │     ┌────────┴────────┐
                    └──────────────────┘     │   Product       │
┌─────────────┐                              ├─────────────────┤
│   Address   │     ┌──────────────┐        │ id              │
├─────────────┤     │    Order     │        │ name            │
│ id          │     ├──────────────┤        │ description     │
│ user_id(FK) │─────│ id           │        │ category_id(FK) │
│ receiver    │     │ user_id(FK)  │        │ merchant_id(FK) │
│ phone       │     │ merchant_id  │        │ price           │
│ address     │     │   (FK)       │        │ image_url       │
│ is_default  │     │ address_id   │        │ stock           │
└─────────────┘     │   (FK)       │        │ is_available    │
                    │ total_price  │        │ sort_order      │
                    │ status       │        │ created_at      │
                    │ created_at   │        │ updated_at      │
                    │ updated_at   │        └─────────────────┘
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │  OrderItem   │
                    ├──────────────┤
                    │ id           │
                    │ order_id(FK) │
                    │ product_id   │
                    │   (FK)       │
                    │ quantity     │
                    │ price        │
                    └──────────────┘
```

---

## 数据模型详情

### User (用户模型)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto Increment | 主键 |
| username | String(50) | Unique, Not Null, Indexed | 用户名 |
| phone | String(20) | Unique, Not Null, Indexed | 手机号 |
| password_hash | String(255) | Not Null | 密码哈希 |
| avatar | String(255) | Nullable | 头像 URL |
| role | Enum | Not Null, Default: 'user' | 角色: user/merchant/admin |
| is_active | Boolean | Not Null, Default: True | 是否启用 |
| created_at | DateTime | Not Null, Default: now | 创建时间 |
| updated_at | DateTime | Not Null, Default: now | 更新时间 |

**关系**:
- 1 → 1 Merchant (通过 user_id)
- 1 → N Address (通过 user_id)
- 1 → N Order (通过 user_id)

---

### Merchant (商家模型)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto Increment | 主键 |
| user_id | Integer | FK(users.id), Unique, Not Null | 关联用户 |
| business_name | String(100) | Not Null, Indexed | 店铺名称 |
| contact_phone | String(20) | Not Null | 联系电话 |
| address | String(255) | Not Null | 店铺地址 |
| description | Text | Nullable | 店铺描述 |
| logo | String(255) | Nullable | Logo URL |
| status | Enum | Not Null, Default: 'pending' | 状态: pending/approved/rejected |
| rejection_reason | String(255) | Nullable | 拒绝原因 |
| approved_at | DateTime | Nullable | 审批时间 |
| approved_by | Integer | FK(users.id), Nullable | 审批人 |
| created_at | DateTime | Not Null, Default: now | 创建时间 |
| updated_at | DateTime | Not Null, Default: now | 更新时间 |

**关系**:
- 1 ← 1 User (通过 user_id)
- 1 → N Category (通过 merchant_id)
- 1 → N Product (通过 merchant_id)
- 1 → N Order (通过 merchant_id)

---

### Category (分类模型)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto Increment | 主键 |
| merchant_id | Integer | FK(merchants.id), Not Null, Indexed | 关联商家 |
| name | String(50) | Not Null | 分类名称 |
| sort_order | Integer | Not Null, Default: 0 | 排序 |
| created_at | DateTime | Not Null, Default: now | 创建时间 |

**关系**:
- 1 ← 1 Merchant (通过 merchant_id)
- 1 → N Product (通过 category_id)

---

### Product (商品模型)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto Increment | 主键 |
| merchant_id | Integer | FK(merchants.id), Not Null, Indexed | 关联商家 |
| category_id | Integer | FK(categories.id), Not Null, Indexed | 关联分类 |
| name | String(100) | Not Null | 商品名称 |
| description | Text | Nullable | 商品描述 |
| price | Decimal(10,2) | Not Null | 价格 |
| original_price | Decimal(10,2) | Nullable | 原价（用于折扣展示） |
| image_url | String(255) | Nullable | 主图 URL |
| images | Text | Nullable | 多图 JSON 数组 |
| stock | Integer | Not Null, Default: 0 | 库存 (0=不限) |
| is_available | Boolean | Not Null, Default: True | 是否上架 |
| sort_order | Integer | Not Null, Default: 0 | 排序 |
| created_at | DateTime | Not Null, Default: now | 创建时间 |
| updated_at | DateTime | Not Null, Default: now | 更新时间 |

**关系**:
- 1 ← 1 Merchant (通过 merchant_id)
- 1 ← 1 Category (通过 category_id)
- 1 → N OrderItem (通过 product_id)

---

### Address (地址模型)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto Increment | 主键 |
| user_id | Integer | FK(users.id), Not Null, Indexed | 关联用户 |
| receiver | String(50) | Not Null | 收货人 |
| phone | String(20) | Not Null | 联系电话 |
| province | String(50) | Not Null | 省份 |
| city | String(50) | Not Null | 城市 |
| district | String(50) | Not Null | 区域 |
| detail_address | String(255) | Not Null | 详细地址 |
| is_default | Boolean | Not Null, Default: False | 是否默认 |
| created_at | DateTime | Not Null, Default: now | 创建时间 |
| updated_at | DateTime | Not Null, Default: now | 更新时间 |

**关系**:
- 1 ← 1 User (通过 user_id)
- 1 → N Order (通过 address_id)

---

### Order (订单模型)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto Increment | 主键 |
| order_no | String(32) | Unique, Not Null, Indexed | 订单编号 |
| user_id | Integer | FK(users.id), Not Null, Indexed | 下单用户 |
| merchant_id | Integer | FK(merchants.id), Not Null, Indexed | 关联商家 |
| address_id | Integer | FK(addresses.id), Not Null | 收货地址 |
| receiver | String(50) | Not Null | 收货人快照 |
| receiver_phone | String(20) | Not Null | 联系电话快照 |
| receiver_address | String(500) | Not Null | 地址快照 |
| total_price | Decimal(10,2) | Not Null | 商品总价 |
| discount_amount | Decimal(10,2) | Default: 0 | 优惠金额 |
| delivery_fee | Decimal(10,2) | Default: 0 | 配送费 |
| pay_amount | Decimal(10,2) | Not Null | 实付金额 |
| status | Enum | Not Null, Default: 'pending' | 订单状态 |
| paid_at | DateTime | Nullable | 支付时间 |
| completed_at | DateTime | Nullable | 完成时间 |
| cancel_reason | String(255) | Nullable | 取消原因 |
| remark | String(500) | Nullable | 用户备注 |
| created_at | DateTime | Not Null, Default: now, Indexed | 创建时间 |
| updated_at | DateTime | Not Null, Default: now | 更新时间 |

**关系**:
- 1 ← 1 User (通过 user_id)
- 1 ← 1 Merchant (通过 merchant_id)
- 1 ← 1 Address (通过 address_id)
- 1 → N OrderItem (通过 order_id)

---

### OrderItem (订单项模型)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto Increment | 主键 |
| order_id | Integer | FK(orders.id), Not Null, Indexed | 关联订单 |
| product_id | Integer | FK(products.id), Not Null | 关联商品 |
| product_name | String(100) | Not Null | 商品名称快照 |
| product_image | String(255) | Nullable | 商品图片快照 |
| price | Decimal(10,2) | Not Null | 下单时价格快照 |
| quantity | Integer | Not Null, Default: 1 | 数量 |
| subtotal | Decimal(10,2) | Not Null | 小计金额 |

**关系**:
- 1 ← 1 Order (通过 order_id)
- 1 ← 1 Product (通过 product_id)

---

## 模型关系说明

### 一对一关系

| 关系 | 外键位置 | 说明 |
|------|---------|------|
| User ↔ Merchant | Merchant.user_id | 一个用户只能有一个商家店铺 |

### 一对多关系

| 关系 | 外键位置 | 删除策略 | 说明 |
|------|---------|---------|------|
| Merchant → Category | Category.merchant_id | CASCADE | 商家删除时分类级联删除 |
| Merchant → Product | Product.merchant_id | CASCADE | 商家删除时商品级联删除 |
| Category → Product | Product.category_id | CASCADE | 分类删除时商品级联删除 |
| User → Address | Address.user_id | CASCADE | 用户删除时地址级联删除 |
| User → Order | Order.user_id | RESTRICT | 有订单时不能删除用户 |
| Merchant → Order | Order.merchant_id | RESTRICT | 有订单时不能删除商家 |
| Order → OrderItem | OrderItem.order_id | CASCADE | 订单删除时订单项级联删除 |

---

## 枚举类型

### 用户角色 (User.role)

| 值 | 说明 |
|---|------|
| user | 普通用户 |
| merchant | 商家 |
| admin | 管理员 |

### 商家状态 (Merchant.status)

| 值 | 说明 |
|---|------|
| pending | 待审核 |
| approved | 已通过 |
| rejected | 已拒绝 |

### 订单状态 (Order.status)

| 值 | 说明 | 流转方向 |
|---|------|---------|
| pending | 待付款 | 初始状态 |
| paid | 已付款 | pending → paid |
| preparing | 制作中 | paid → preparing |
| delivering | 配送中 | preparing → delivering |
| completed | 已完成 | delivering → completed |
| cancelled | 已取消 | pending/paid → cancelled |
| refunded | 已退款 | cancelled → refunded |

---

## 相关文档

- [系统架构](./system-architecture.md) - 系统整体架构
- [数据库设计规范](../design/database-design.md) - 数据库设计原则
- [API 设计](../design/api-design.md) - API 接口规范
