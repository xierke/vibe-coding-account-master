# DailyTracker API 文档

> **Base URL:** `https://api.dailytracker.com/v1`  
> **版本:** 1.0.0  
> **协议:** HTTP/1.1  
> **内容类型:** `application/json; charset=utf-8`  
> **认证方式:** JWT Bearer Token  
> **更新日期:** 2026-07-28

---

## 目录

1. [概述](#概述)
2. [通用约定](#通用约定)
   - [统一响应格式](#统一响应格式)
   - [错误码体系](#错误码体系)
   - [分页格式](#分页格式)
   - [认证机制](#认证机制)
3. [系统接口](#系统接口)
4. [认证模块 — `/v1/auth`](#认证模块)
5. [用户模块 — `/v1/users`](#用户模块)
6. [账单模块 — `/v1/bills`](#账单模块)
7. [分类模块 — `/v1/categories`](#分类模块)
8. [报表模块 — `/v1/reports`](#报表模块)
9. [预算模块 — `/v1/budgets`](#预算模块)
10. [数据模型](#数据模型)
11. [安全策略](#安全策略)
12. [环境变量](#环境变量)

---

## 概述

DailyTracker 是一个个人收支记账 App 的后端服务。基于 FastAPI 构建，提供用户认证、账单 CRUD、报表聚合、预算管理等 RESTful API。

| 特性 | 说明 |
|------|------|
| 认证 | JWT 双 Token（access 15min + refresh 7d） |
| 密码 | bcrypt 哈希，错误超限自动锁定 |
| 数据校验 | Pydantic v2，金额 Decimal(12,2) |
| 缓存 | Redis Cache-Aside（主页 Dashboard TTL 5min） |
| 日志 | JSON 结构化日志，含 request_id 追踪 |
| API 文档 | 自动生成 Swagger（`/docs`）+ ReDoc（`/redoc`） |

---

## 通用约定

### 统一响应格式

所有 API 返回统一 JSON 结构：

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | `int` | 业务状态码，`0` 表示成功 |
| `message` | `string` | 状态描述 |
| `data` | `object\|array\|null` | 响应数据，无数据时为 `null` |

### 错误码体系

```json
{
  "code": 40101,
  "message": "账号或密码错误",
  "detail": "详细错误说明"
}
```

| 错误码范围 | 含义 | HTTP 状态码 |
|-----------|------|-------------|
| `0` | 成功 | 200 |
| `40001-40099` | 客户端参数错误 | 400 |
| `40100-40199` | 认证/授权失败 | 401 |
| `40300-40399` | 无权限 | 403 |
| `40400-40499` | 资源不存在 | 404 |
| `40900-40999` | 资源冲突 | 409 |
| `42200-42299` | 业务规则校验失败 | 422 |
| `50000` | 服务器内部错误 | 500 |
| `50300` | 服务降级 | 503 |

### 分页格式

分页接口统一返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `items` | `array` | 当前页数据 |
| `total` | `int` | 总条数 |
| `page` | `int` | 当前页码（从 1 开始） |
| `page_size` | `int` | 每页条数（默认 20，最大 100） |

### 认证机制

- **access_token**: JWT，有效期 15 分钟，用于所有需要认证的请求
- **refresh_token**: JWT，有效期 7 天，用于刷新 Token

**请求头格式:**

```
Authorization: Bearer <access_token>
```

**Token 刷新流程:**

1. access_token 过期时返回 `40100`
2. 前端用 refresh_token 调用 `/v1/auth/refresh` 获取新 Token
3. 刷新失败则跳转登录页

---

## 系统接口

这些接口不需要 API 前缀和认证。

### GET `/`

**描述:** 服务信息，返回应用名称、版本和文档入口。

**响应示例:**

```json
{
  "name": "DailyTracker",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### GET `/health`

**描述:** 存活探针（Liveness Probe），供 K8s/负载均衡器使用。

**响应示例:**

```json
{ "status": "ok" }
```

---

### GET `/ready`

**描述:** 就绪探针（Readiness Probe），检查 DB + Redis 是否可用。

**成功响应 (200):**

```json
{
  "status": "ok",
  "checks": { "database": "ok", "redis": "ok" }
}
```

**降级响应 (503):**

```json
{
  "status": "degraded",
  "checks": {
    "database": "ok",
    "redis": "ConnectionRefusedError: ..."
  }
}
```

---

## 认证模块

`/v1/auth`

### POST `/v1/auth/register`

**描述:** 邮箱注册。注册成功自动登录，返回 Token。

**请求体:**

```json
{
  "username": "myusername",
  "email": "user@example.com",
  "password": "Pass1234",
  "confirm_password": "Pass1234"
}
```

| 字段 | 类型 | 必填 | 校验规则 |
|------|------|------|----------|
| `username` | `string` | 是 | 2-20 字符 |
| `email` | `string(email)` | 是 | 合法邮箱格式 |
| `password` | `string` | 是 | 8-20 位，须含字母+数字 |
| `confirm_password` | `string` | 是 | 须与 `password` 一致 |

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbG...",
    "refresh_token": "eyJhbG...",
    "token_type": "bearer",
    "user_id": 1,
    "username": "myusername"
  }
}
```

**错误码:**

| 错误码 | 说明 |
|--------|------|
| `40900` | 用户名或邮箱已被注册 |

---

### POST `/v1/auth/login`

**描述:** 密码登录。支持用户名或邮箱。密码错误超过 5 次锁定 15 分钟。

**请求体:**

```json
{
  "account": "user@example.com",
  "password": "Pass1234",
  "remember_me": false
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `account` | `string` | 是 | 用户名 或 邮箱 |
| `password` | `string` | 是 | 明文密码 |
| `remember_me` | `bool` | 否 | 默认 `false`（当前版本 Token 统一 7 天） |

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbG...",
    "refresh_token": "eyJhbG...",
    "token_type": "bearer",
    "user_id": 1,
    "username": "myusername"
  }
}
```

**错误码:**

| 错误码 | 说明 |
|--------|------|
| `40101` | 账号或密码错误（会提示剩余尝试次数） |
| `40101` | 账号已锁定（会提示剩余锁定分钟数） |

---

### POST `/v1/auth/login/sms`

**描述:** 短信验证码登录。首次登录自动创建账号并绑定手机号。

**请求体:**

```json
{
  "phone": "13800138000",
  "code": "123456"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `phone` | `string` | 是 | 11 位中国大陆手机号 |
| `code` | `string` | 是 | 6 位短信验证码 |

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbG...",
    "refresh_token": "eyJhbG...",
    "token_type": "bearer",
    "user_id": 2,
    "username": "user_138000"
  }
}
```

**说明:** 首次短信登录的用户名自动生成为 `user_<手机号后6位>`，密码默认为手机号。

---

### POST `/v1/auth/refresh`

**描述:** 刷新 Token。使用 refresh_token 获取新的 access_token + refresh_token。

**请求体:**

```json
{
  "refresh_token": "eyJhbG..."
}
```

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbG...",
    "refresh_token": "eyJhbG...",
    "token_type": "bearer"
  }
}
```

**错误码:**

| 错误码 | 说明 |
|--------|------|
| `40100` | refresh_token 无效或已过期 |
| `40101` | Token 类型不匹配（非 refresh token） |

---

### POST `/v1/auth/send-code`

**描述:** 发送验证码。支持邮箱和短信两种类型。

**请求体:**

```json
{
  "type": "email",
  "target": "user@example.com"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `string` | 是 | `"email"` 或 `"sms"` |
| `target` | `string` | 是 | 邮箱地址或手机号 |

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "验证码已发送",
  "data": null
}
```

**说明:**
- 验证码为 6 位数字，有效期 5 分钟
- 当前短信为 **Mock 实现**，验证码打印到服务端控制台日志
- 同一 target 重复发送会覆盖旧验证码

---

### POST `/v1/auth/reset-password`

**描述:** 通过邮箱验证码重置密码。重置后需重新登录（旧 Token 不失效）。

**请求体:**

```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "NewPass5678",
  "confirm_password": "NewPass5678"
}
```

| 字段 | 类型 | 必填 | 校验规则 |
|------|------|------|----------|
| `email` | `string(email)` | 是 | 已注册的邮箱 |
| `code` | `string` | 是 | 6 位验证码 |
| `new_password` | `string` | 是 | 8-20 位，须含数字 |
| `confirm_password` | `string` | 是 | 须与 `new_password` 一致 |

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "密码重置成功，请重新登录",
  "data": null
}
```

---

### PUT `/v1/auth/password`

**描述:** 已登录用户修改密码。

**认证:** Bearer Token

**请求体:**

```json
{
  "old_password": "OldPass1234",
  "new_password": "NewPass5678",
  "confirm_password": "NewPass5678"
}
```

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "密码修改成功",
  "data": null
}
```

**错误码:**

| 错误码 | 说明 |
|--------|------|
| `42200` | 原密码错误 或 新密码与原密码相同 |

---

## 用户模块

`/v1/users`

### GET `/v1/home`

**描述:** 主页 Dashboard。返回本月收支概览、今日统计、预算进度和最近 5 条账单。

**认证:** Bearer Token

**缓存策略:** Redis Cache-Aside，TTL 5 分钟。记一笔/编辑/删除后自动失效。

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "month_income": 16500.00,
    "month_expense": 8430.50,
    "month_balance": 8069.50,
    "today_bill_count": 5,
    "today_expense": 320.00,
    "budget_total": 20000.00,
    "budget_spent": 8430.50,
    "budget_usage_rate": 0.42,
    "budget_warning": false,
    "recent_bills": [
      {
        "id": 128,
        "type": "expense",
        "amount": 45.00,
        "category_name": "餐饮",
        "category_icon": "🍽️",
        "category_color": "#E07B5A",
        "bill_date": "2026-07-28",
        "note": "午餐外卖"
      }
    ]
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `month_income` | `float` | 本月总收入 |
| `month_expense` | `float` | 本月总支出 |
| `month_balance` | `float` | 本月结余 |
| `today_bill_count` | `int` | 今日记账笔数 |
| `today_expense` | `float` | 今日支出 |
| `budget_total` | `float\|null` | 月度总预算，未设置时为 `null` |
| `budget_spent` | `float` | 本月已支出 |
| `budget_usage_rate` | `float` | 预算使用率（0.0 ~ 1.0+） |
| `budget_warning` | `bool` | 是否超过 80% 预警线 |
| `recent_bills` | `array` | 最近 5 条账单 |

---

### GET `/v1/users/profile`

**描述:** 获取当前登录用户的个人信息。

**认证:** Bearer Token

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "myusername",
    "email": "user@example.com",
    "phone": "13800138000",
    "avatar_url": "https://example.com/avatar.png",
    "created_at": "2026-01-15T10:30:00"
  }
}
```

---

### PUT `/v1/users/profile`

**描述:** 更新个人信息（用户名、头像）。

**认证:** Bearer Token

**请求体:**

```json
{
  "username": "newusername",
  "avatar_url": "https://example.com/new-avatar.png"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | `string` | 否 | 2-20 字符，须唯一 |
| `avatar_url` | `string` | 否 | 头像 URL |

**错误码:**

| 错误码 | 说明 |
|--------|------|
| `40900` | 用户名已被占用 |

---

## 账单模块

`/v1/bills`

这是记账核心模块。金额全部使用 `DECIMAL(12,2)` 精度，范围 `0.01 ~ 999,999,999.99`。

### POST `/v1/bills`

**描述:** 记一笔 — 创建收支记录。bill_date 为空时默认当天。

**认证:** Bearer Token

**请求体:**

```json
{
  "type": "expense",
  "amount": 45.50,
  "category_id": 1,
  "bill_date": "2026-07-28",
  "note": "午餐外卖"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `string` | 是 | `"income"` 或 `"expense"` |
| `amount` | `float` | 是 | 金额，0.01 ~ 999,999,999.99 |
| `category_id` | `int` | 是 | 分类 ID |
| `bill_date` | `string(date)` | 否 | 账单日期，格式 `YYYY-MM-DD`，默认当天 |
| `note` | `string` | 否 | 备注，最多 200 字 |

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 129,
    "type": "expense",
    "amount": 45.50,
    "category": {
      "id": 1,
      "name": "餐饮",
      "icon": "🍽️",
      "color": "#E07B5A"
    },
    "bill_date": "2026-07-28",
    "note": "午餐外卖",
    "created_at": "2026-07-28T12:30:00",
    "updated_at": "2026-07-28T12:30:00"
  }
}
```

**副作用:** 清除当前用户的主页 Dashboard 缓存。

---

### GET `/v1/bills`

**描述:** 账单列表 — 分页 + 多条件筛选。按 `bill_date DESC, created_at DESC` 排序。

**认证:** Bearer Token

**查询参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | `int` | 否 | `1` | 页码，≥1 |
| `page_size` | `int` | 否 | `20` | 每页条数，1-100 |
| `type` | `string` | 否 | — | 筛选类型：`"income"` / `"expense"` |
| `category_id` | `int` | 否 | — | 筛选分类 ID |
| `start_date` | `string(date)` | 否 | — | 起始日期 `YYYY-MM-DD` |
| `end_date` | `string(date)` | 否 | — | 结束日期 `YYYY-MM-DD` |

**请求示例:**

```
GET /v1/bills?page=1&page_size=20&type=expense&start_date=2026-07-01&end_date=2026-07-31
```

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 129,
        "type": "expense",
        "amount": 45.50,
        "category": { "id": 1, "name": "餐饮", "icon": "🍽️", "color": "#E07B5A" },
        "bill_date": "2026-07-28",
        "note": "午餐外卖",
        "created_at": "2026-07-28T12:30:00",
        "updated_at": "2026-07-28T12:30:00"
      }
    ],
    "total": 84,
    "page": 1,
    "page_size": 20
  }
}
```

---

### GET `/v1/bills/search`

**描述:** 搜索账单 — 按备注文本模糊匹配 + 金额精确匹配。

**认证:** Bearer Token

> **注意:** 此路由必须在 `GET /v1/bills/{bill_id}` 之前定义，否则 FastAPI 会将 `search` 误解析为 `bill_id`。

**查询参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `keyword` | `string` | 否 | `""` | 搜索关键词 |
| `page` | `int` | 否 | `1` | 页码 |
| `page_size` | `int` | 否 | `20` | 每页条数 |

**搜索逻辑:**
- 备注文本模糊匹配
- 若 keyword 可解析为数字，同时匹配金额精确等于该值的账单

**请求示例:**

```
GET /v1/bills/search?keyword=午餐&page=1&page_size=20
```

---

### GET `/v1/bills/{bill_id}`

**描述:** 获取单条账单详情。

**认证:** Bearer Token

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `bill_id` | `int` | 账单 ID |

**错误码:**

| 错误码 | 说明 |
|--------|------|
| `40400` | 账单不存在 |
| `40300` | 无权访问此账单 |

---

### PUT `/v1/bills/{bill_id}`

**描述:** 编辑账单 — 仅更新传入的非空字段。

**认证:** Bearer Token

**请求体:**（所有字段可选）

```json
{
  "type": "expense",
  "amount": 50.00,
  "category_id": 2,
  "bill_date": "2026-07-28",
  "note": "修改后的备注"
}
```

**成功时返回完整账单对象（同创建响应）。**

**副作用:** 清除主页 Dashboard 缓存。

---

### DELETE `/v1/bills/{bill_id}`

**描述:** 删除单条账单。

**认证:** Bearer Token

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "删除成功",
  "data": null
}
```

**副作用:** 清除主页 Dashboard 缓存。

---

### POST `/v1/bills/batch-delete`

**描述:** 批量删除账单 — 仅删除属于当前用户的账单，其他人的账单自动跳过。

**认证:** Bearer Token

**请求体:**

```json
{
  "ids": [129, 130, 131, 999]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ids` | `array[int]` | 是 | 要删除的账单 ID 列表 |

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "成功删除 3 条账单",
  "data": null
}
```

> 示例中请求了 4 个 ID，但 ID=999 不属于当前用户，实际只删除 3 条。

**副作用:** 清除主页 Dashboard 缓存。

---

## 分类模块

`/v1/categories`

### GET `/v1/categories`

**描述:** 获取分类列表 — 包含系统默认 13 个分类 + 用户自定义分类。返回每个分类的账单数量。

**认证:** Bearer Token

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `string` | 否 | 筛选类型：`"income"` / `"expense"` |

**排序规则:**
1. 系统默认分类按 `sort_order` 排序
2. 用户自定义分类按创建时间排序

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "餐饮",
      "icon": "🍽️",
      "color": "#E07B5A",
      "type": "expense",
      "is_default": true,
      "sort_order": 1,
      "bill_count": 42
    },
    {
      "id": 14,
      "name": "宠物",
      "icon": "🐱",
      "color": "#FF8844",
      "type": "expense",
      "is_default": false,
      "sort_order": 0,
      "bill_count": 3
    }
  ]
}
```

**默认分类:**

| 支出 (8 个) | 图标 | 收入 (5 个) | 图标 |
|-------------|------|-------------|------|
| 餐饮 | 🍽️ | 工资 | 💰 |
| 交通 | 🚗 | 兼职 | 💼 |
| 购物 | 🛒 | 投资 | 📈 |
| 居住 | 🏠 | 红包 | 🧧 |
| 娱乐 | 🎮 | 其他收入 | 📌 |
| 医疗 | 💊 | | |
| 教育 | 📚 | | |
| 其他支出 | 📌 | | |

---

### POST `/v1/categories`

**描述:** 创建用户自定义分类。

**认证:** Bearer Token

**请求体:**

```json
{
  "name": "宠物",
  "icon": "🐱",
  "color": "#FF8844",
  "type": "expense",
  "sort_order": 0
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | `string` | 是 | 分类名称，最多 30 字符 |
| `icon` | `string` | 是 | 图标（emoji） |
| `color` | `string` | 是 | 颜色，格式 `#RRGGBB` |
| `type` | `string` | 是 | `"income"` 或 `"expense"` |
| `sort_order` | `int` | 否 | 排序值，默认 `0` |

**错误码:**

| 错误码 | 说明 |
|--------|------|
| `40900` | 同名分类已存在 |

---

### PUT `/v1/categories/{category_id}`

**描述:** 编辑分类 — 系统默认分类可编辑（但不能删除），用户自定义分类全部可编辑。

**认证:** Bearer Token

**请求体:**（所有字段可选）

```json
{
  "name": "宠物用品",
  "icon": "🐶",
  "color": "#FF6644",
  "sort_order": 5
}
```

---

### DELETE `/v1/categories/{category_id}`

**描述:** 删除分类。

**认证:** Bearer Token

**删除规则:**

| 条件 | 结果 |
|------|------|
| 系统默认分类（`is_default=true`） | ❌ 不可删除 |
| 有关联账单的分类 | ❌ 不可删除 |
| 用户自定义分类 + 无关联账单 | ✅ 可删除 |

**错误码:**

| 错误码 | 说明 |
|--------|------|
| `40300` | 系统默认分类不可删除 |
| `40900` | 该分类下有 N 笔账单，无法删除 |

---

## 报表模块

`/v1/reports`

所有报表数据为实时查询（不缓存），确保数据准确性。

### GET `/v1/reports/weekly`

**描述:** 周收支报表。返回给定日期所在周（周一 ~ 周日）的数据。

**认证:** Bearer Token

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `date` | `string(date)` | 是 | 参考日期 `YYYY-MM-DD`，取该日期所在周 |

**请求示例:**

```
GET /v1/reports/weekly?date=2026-07-28
```

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "week_start": "2026-07-21",
    "week_end": "2026-07-27",
    "overview": {
      "total_income": 8200.00,
      "total_expense": 3450.00,
      "balance": 4750.00,
      "avg_daily_expense": 492.86,
      "budget_usage_rate": null
    },
    "daily_data": [
      { "date": "2026-07-21", "income": 1500.00, "expense": 320.00 },
      { "date": "2026-07-22", "income": 0.00, "expense": 480.00 }
    ],
    "category_pie": [
      {
        "category_id": 1,
        "category_name": "餐饮",
        "icon": "🍽️",
        "color": "#E07B5A",
        "amount": 1276.50,
        "percentage": 37.0
      }
    ],
    "comparison": {
      "prev_income": 8000.00,
      "prev_expense": 3760.00,
      "income_change_pct": 2.5,
      "expense_change_pct": -8.2
    }
  }
}
```

**响应字段说明:**

| 字段 | 说明 |
|------|------|
| `overview.avg_daily_expense` | 日均支出 = 总支出 ÷ 天数 |
| `overview.budget_usage_rate` | 周报始终为 `null`（仅月报计算） |
| `daily_data` | 仅包含有记录的日期 |
| `category_pie` | 按支出金额降序排列，`percentage` 精确到 1 位小数 |
| `comparison` | 与上周对比。如果两周均无数据则为 `null` |

---

### GET `/v1/reports/monthly`

**描述:** 月收支报表。包含概览、趋势、排行、热力图、环比。

**认证:** Bearer Token

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `month` | `string` | 是 | 月份 `YYYY-MM` |

**请求示例:**

```
GET /v1/reports/monthly?month=2026-07
```

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "month": "2026-07",
    "overview": {
      "total_income": 28500.00,
      "total_expense": 12870.00,
      "balance": 15630.00,
      "avg_daily_expense": 435.00,
      "budget_usage_rate": 64.0
    },
    "daily_data": [
      { "date": "2026-07-01", "income": 0.00, "expense": 320.00 },
      { "date": "2026-07-02", "income": 0.00, "expense": 0.00 }
    ],
    "category_ranks": [
      {
        "rank": 1,
        "category_id": 1,
        "category_name": "餐饮",
        "icon": "🍽️",
        "color": "#E07B5A",
        "amount": 4520.00,
        "percentage": 35.1
      }
    ],
    "calendar_data": [
      {
        "date": "2026-07-01",
        "day_of_month": 1,
        "day_of_week": 2,
        "amount": 320.00,
        "intensity": 0.45
      }
    ],
    "comparison": {
      "prev_income": 27100.00,
      "prev_expense": 13285.00,
      "income_change_pct": 5.2,
      "expense_change_pct": -3.1
    }
  }
}
```

**响应字段说明:**

| 字段 | 说明 |
|------|------|
| `overview.budget_usage_rate` | 预算使用率 = 支出 / 总预算 × 100，无预算时为 `null` |
| `daily_data` | 补全当月所有日期，无数据的日期金额为 `0.00` |
| `category_ranks` | Top 10 分类排行，`percentage` 相对于排行内总支出 |
| `calendar_data` | 整个月的日历数据，`intensity` 为 0.0 ~ 1.0（相对最高支出） |
| `calendar_data[].day_of_week` | 0=周一 … 6=周日 |

---

### GET `/v1/reports/custom`

**描述:** 自定义时间范围报表，格式与月报一致（无热力图和环比）。

**认证:** Bearer Token

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `start_date` | `string(date)` | 是 | 起始日期 `YYYY-MM-DD` |
| `end_date` | `string(date)` | 是 | 结束日期 `YYYY-MM-DD` |

**请求示例:**

```
GET /v1/reports/custom?start_date=2026-07-01&end_date=2026-07-15
```

--- 

## 预算模块

`/v1/budgets`

### GET `/v1/budgets`

**描述:** 获取指定月份的预算 — 总预算 + 分类预算 + 各自执行情况。

**认证:** Bearer Token

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `month` | `string` | 是 | 月份 `YYYY-MM` |

**成功响应 (200):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "month": "2026-07",
    "total_budget": {
      "category_id": null,
      "category_name": "总预算",
      "amount": 20000.00,
      "spent": 12870.00,
      "usage_rate": 0.64
    },
    "category_budgets": [
      {
        "category_id": 1,
        "category_name": "餐饮",
        "amount": 5000.00,
        "spent": 4520.00,
        "usage_rate": 0.90
      }
    ]
  }
}
```

| 字段 | 说明 |
|------|------|
| `total_budget` | `null` 表示未设置总预算 |
| `category_budgets` | 空数组表示无分类预算 |
| `usage_rate` | 使用率 0.0 ~ 1.0（可能超过 1.0 表示超支） |

---

### PUT `/v1/budgets`

**描述:** 设置/更新月度预算。采用「先删后插」策略 — 更新时先清空该月全部预算数据再重新写入。

**认证:** Bearer Token

**请求体:**

```json
{
  "month": "2026-07",
  "total_budget": 20000.00,
  "category_budgets": [
    { "category_id": 1, "amount": 5000.00 },
    { "category_id": 3, "amount": 3000.00 }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `month` | `string` | 是 | 月份 `YYYY-MM` |
| `total_budget` | `float` | 否 | 总预算，`null` 或 ≤0 表示不设置 |
| `category_budgets` | `array` | 否 | 分类预算列表 |
| `category_budgets[].category_id` | `int` | 是 | 分类 ID |
| `category_budgets[].amount` | `float` | 是 | 预算金额 |

**响应:** 同 GET 响应，返回更新后的完整预算数据。

---

## 数据模型

### 数据库表结构

#### `users` — 用户表

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | `INT PK AUTO_INCREMENT` | 主键 |
| `username` | `VARCHAR(50) UNIQUE` | 用户名 |
| `email` | `VARCHAR(100) UNIQUE` | 邮箱 |
| `password_hash` | `VARCHAR(255)` | bcrypt 哈希 |
| `phone` | `VARCHAR(20) UNIQUE NULL` | 手机号（短信登录绑定） |
| `avatar_url` | `VARCHAR(500) NULL` | 头像 URL |
| `is_locked` | `BOOLEAN DEFAULT FALSE` | 是否锁定 |
| `locked_until` | `DATETIME NULL` | 锁定到期时间 |
| `failed_login_attempts` | `INT DEFAULT 0` | 连续失败次数 |
| `created_at` | `DATETIME` | 创建时间 |
| `updated_at` | `DATETIME` | 更新时间 |

#### `categories` — 收支分类表

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | `INT PK AUTO_INCREMENT` | 主键 |
| `user_id` | `INT FK NULL` | 所属用户，NULL=系统默认 |
| `name` | `VARCHAR(30)` | 分类名称 |
| `icon` | `VARCHAR(50)` | 图标（emoji） |
| `color` | `VARCHAR(7)` | 颜色 `#RRGGBB` |
| `type` | `ENUM('income','expense')` | 类型 |
| `is_default` | `BOOLEAN` | 是否系统默认 |
| `sort_order` | `INT DEFAULT 0` | 排序值 |
| `created_at` | `DATETIME` | 创建时间 |

外键：`user_id → users.id ON DELETE CASCADE`（删除用户时级联删除自定义分类）

#### `bills` — 账单表

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | `INT PK AUTO_INCREMENT` | 主键 |
| `user_id` | `INT FK` | 所属用户 |
| `type` | `ENUM('income','expense')` | 类型 |
| `amount` | `DECIMAL(12,2)` | 金额 |
| `category_id` | `INT FK` | 分类 |
| `bill_date` | `DATE` | 账单日期 |
| `note` | `VARCHAR(200) NULL` | 备注 |
| `created_at` | `DATETIME` | 创建时间 |
| `updated_at` | `DATETIME` | 更新时间 |

外键：
- `user_id → users.id ON DELETE CASCADE`
- `category_id → categories.id ON DELETE RESTRICT`（有关联账单的分类不可删除）

索引：
- `(user_id, bill_date)` — 加速按用户+日期的范围查询
- `(user_id, category_id)` — 加速按分类筛选

#### `budgets` — 预算表

| 列 | 类型 | 说明 |
|----|------|------|
| `id` | `INT PK AUTO_INCREMENT` | 主键 |
| `user_id` | `INT FK` | 所属用户 |
| `category_id` | `INT FK NULL` | 分类 NULL=总预算 |
| `amount` | `DECIMAL(12,2)` | 预算金额 |
| `month` | `VARCHAR(7)` | 月份 `YYYY-MM` |
| `created_at` | `DATETIME` | 创建时间 |
| `updated_at` | `DATETIME` | 更新时间 |

唯一约束：`(user_id, month, category_id)` — 同一用户同一月份每种预算仅一条

### ER 关系

```
users (1) ──────< (N) bills
  │
  ├── (1) ──────< (N) categories (user_id=NULL 为系统默认)
  │
  └── (1) ──────< (N) budgets

categories (1) ──────< (N) bills (ON DELETE RESTRICT)
```

---

## 安全策略

### 密码规则

| 规则 | 说明 |
|------|------|
| 哈希算法 | bcrypt（`rounds=12`） |
| 长度限制 | 8-20 字符 |
| 复杂度 | 须包含字母 + 数字 |
| 登录锁定 | 连续错误 ≥ 5 次锁定 15 分钟 |
| 锁定自动解除 | 到期后下次登录自动解锁并清零计数 |

### JWT Token

| Token 类型 | 有效期 | 用途 |
|-----------|--------|------|
| `access_token` | 15 分钟 | API 认证 |
| `refresh_token` | 7 天 | 刷新 Token |

Token payload 结构：
```json
{
  "sub": "1",
  "type": "access",
  "iat": 1753700000,
  "exp": 1753700900
}
```

### 接口限流

| 类型 | 限制 | 范围 |
|------|------|------|
| 通用 API | 100 次/分钟 | 按用户 |
| 登录接口 | 20 次/分钟 | 按 IP |

### CORS

| 配置 | 值 |
|------|-----|
| 允许来源 | `http://localhost:5173`, `http://localhost:3000` |
| 允许方法 | 全部 |
| 允许凭证 | 是 |

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_NAME` | `DailyTracker` | 应用名称 |
| `APP_VERSION` | `1.0.0` | 版本号 |
| `DEBUG` | `false` | 调试模式 |
| `API_V1_PREFIX` | `/v1` | API 前缀 |
| `DATABASE_URL` | `mysql+aiomysql://root:wyx4022@127.0.0.1:3306/account` | MySQL 连接串 |
| `DB_POOL_SIZE` | `10` | 连接池大小 |
| `DB_MAX_OVERFLOW` | `20` | 连接池溢出上限 |
| `DB_ECHO` | `false` | SQL 日志 |
| `REDIS_URL` | `redis://127.0.0.1:6379/0` | Redis 连接串 |
| `JWT_SECRET` | `dailytracker-dev-secret-key-change-in-production` | JWT 签名密钥 |
| `JWT_ALGORITHM` | `HS256` | JWT 算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access Token 有效期 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh Token 有效期 |
| `BCRYPT_ROUNDS` | `12` | bcrypt 加密轮数 |
| `MAX_LOGIN_ATTEMPTS` | `5` | 密码错误上限 |
| `LOCKOUT_DURATION_MINUTES` | `15` | 锁定时长 |
| `VERIFY_CODE_LENGTH` | `6` | 验证码位数 |
| `VERIFY_CODE_TTL_SECONDS` | `300` | 验证码有效期 |
| `RATE_LIMIT_PER_MINUTE` | `100` | API 限流 |
| `LOGIN_RATE_LIMIT_PER_MINUTE` | `20` | 登录限流 |
| `CORS_ORIGINS` | `["http://localhost:5173","http://localhost:3000"]` | 允许跨域来源 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

---

## API 全景图

```
认证 (无需 Token)
├── POST   /v1/auth/register        注册 → 返回 Token
├── POST   /v1/auth/login           密码登录 → 返回 Token
├── POST   /v1/auth/login/sms       短信登录 → 返回 Token
├── POST   /v1/auth/refresh         刷新 Token
├── POST   /v1/auth/send-code       发送验证码
└── POST   /v1/auth/reset-password  重置密码

认证 (需 Token)
├── PUT    /v1/auth/password        修改密码

用户 & 首页
├── GET    /v1/home                 主页 Dashboard (Redis 缓存)
├── GET    /v1/users/profile        个人信息
└── PUT    /v1/users/profile        更新个人信息

账单 (核心模块)
├── POST   /v1/bills                记一笔
├── GET    /v1/bills                账单列表 (分页+筛选)
├── GET    /v1/bills/search         搜索账单
├── GET    /v1/bills/{id}           账单详情
├── PUT    /v1/bills/{id}           编辑账单
├── DELETE /v1/bills/{id}           删除账单
└── POST   /v1/bills/batch-delete   批量删除

分类
├── GET    /v1/categories           分类列表
├── POST   /v1/categories           创建自定义分类
├── PUT    /v1/categories/{id}      编辑分类
└── DELETE /v1/categories/{id}      删除分类

报表 (实时计算，不缓存)
├── GET    /v1/reports/weekly       周报表
├── GET    /v1/reports/monthly      月报表
└── GET    /v1/reports/custom       自定义范围报表

预算
├── GET    /v1/budgets              查询预算
└── PUT    /v1/budgets              设置/更新预算

系统 (无需 Token)
├── GET    /                         服务信息
├── GET    /health                   存活探针
└── GET    /ready                    就绪探针
```
