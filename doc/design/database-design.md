# 数据库设计规范

> **版本**: v1.0
> **更新日期**: 2026-05-24
> **适用范围**: GoEats 后端数据库设计

---

## 目录

- [表设计规范](#表设计规范)
- [字段类型选择](#字段类型选择)
- [索引设计规范](#索引设计规范)
- [外键约束](#外键约束)
- [SQL 表结构](#sql-表结构)

---

## 表设计规范

### 必须字段

每个表必须包含以下字段：

```sql
id INTEGER PRIMARY KEY AUTOINCREMENT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### 命名规范

| 规则 | 示例 |
|------|------|
| 表名复数 | `users`, `orders`, `products` |
| 外键命名 | `{表名单数}_id` → `user_id`, `merchant_id` |
| 索引命名 | `idx_{表名}_{字段名}` → `idx_users_phone` |
| 唯一索引 | `uq_{表名}_{字段名}` → `uq_users_username` |

---

## 字段类型选择

| 数据类型 | SQLite 类型 | 说明 |
|---------|------------|------|
| 整数ID | `INTEGER` | 自增主键 |
| 字符串(短) | `VARCHAR(n)` | 用户名、手机号等 |
| 字符串(长) | `TEXT` | 描述、备注等 |
| 金额 | `DECIMAL(10, 2)` | 价格相关 |
| 布尔值 | `BOOLEAN` | 状态标志 |
| 时间 | `TIMESTAMP` | 日期时间 |
| 枚举 | `VARCHAR + CHECK` | 状态、角色等 |

---

## 索引设计规范

**索引原则**：

- WHERE、JOIN、ORDER BY 频繁使用的字段建立索引
- 高区分度的字段适合建索引
- 避免过多索引影响写入性能
- 联合索引遵循最左前缀原则

---

## 外键约束

**外键删除策略**：

| 策略 | 说明 | 使用场景 |
|------|------|---------|
| CASCADE | 级联删除 | 订单项随订单删除 |
| RESTRICT | 禁止删除 | 有订单时不能删除商家 |
| SET NULL | 设为 NULL | 用户删除时相关字段设为NULL |

---

## SQL 表结构

### 用户表

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'merchant', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_phone ON users(phone);
```

### 商家表

```sql
CREATE TABLE merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    business_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    description TEXT,
    logo VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
    rejection_reason VARCHAR(255),
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_merchants_business_name ON merchants(business_name);
CREATE INDEX idx_merchants_status ON merchants(status);
```

### 分类表

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    name VARCHAR(50) NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_merchant_id ON categories(merchant_id);
```

### 商品表

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2),
    image_url VARCHAR(255),
    images TEXT,
    stock INTEGER NOT NULL DEFAULT 0,
    is_available BOOLEAN NOT NULL DEFAULT 1,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_merchant_id ON products(merchant_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_available ON products(is_available);
```

### 用户地址表

```sql
CREATE TABLE addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    receiver VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    detail_address VARCHAR(255) NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_addresses_user_id ON addresses(user_id);
```

### 订单表

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    address_id INTEGER NOT NULL REFERENCES addresses(id),
    receiver VARCHAR(50) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    receiver_address VARCHAR(500) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    delivery_fee DECIMAL(10, 2) NOT NULL DEFAULT 0,
    pay_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK(status IN ('pending', 'paid', 'preparing', 'delivering', 'completed', 'cancelled', 'refunded')),
    paid_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancel_reason VARCHAR(255),
    remark VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_merchant_id ON orders(merchant_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

### 订单项表

```sql
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    product_name VARCHAR(100) NOT NULL,
    product_image VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    subtotal DECIMAL(10, 2) NOT NULL
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
```

---

## 相关文档

- [数据模型](../architecture/data-models.md) - ORM 模型设计
- [后端代码规范](./backend-conventions.md) - SQLAlchemy 使用规范
