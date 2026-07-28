# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: DailyTracker — 日常记账APP

A personal expense/income tracking web application (V1.0 Web) with weekly and monthly reports. Warm-tone, clean design with zero animations. Responsive layout ready for future mobile expansion.

**Source of truth:** [docs/PRD-日常记账APP.md](docs/PRD-日常记账APP.md)

---

## Tech Stack

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端框架** | Vue 3 + Vite | Composition API + `<script setup>` + TypeScript |
| **状态管理** | Pinia | Vue 官方推荐 |
| **路由** | Vue Router 4 | SPA 路由，导航守卫 |
| **HTTP 客户端** | Axios | 请求/响应拦截器，Token 自动刷新 |
| **图表** | ECharts (vue-echarts) | 柱状图、饼图、折线图、热力图 |
| **UI 组件** | 自定义（无第三方组件库） | 保持暖色调风格统一，避免覆盖默认样式的成本 |
| **图标** | Lucide Icons / Heroicons | 线性风格 |
| **后端框架** | FastAPI (Python 3.12+) | 异步、自动 OpenAPI 文档、Pydantic 校验 |
| **ORM** | SQLAlchemy 2.0 (async) | Python 生态最成熟 ORM |
| **数据库迁移** | Alembic | SQLAlchemy 配套 |
| **认证** | PyJWT + bcrypt | JWT access_token(15min) + refresh_token(7d) |
| **数据库** | MySQL 8.0 | 关系型数据库 |
| **缓存** | Redis (可选) | 热点数据缓存、限流计数 |
| **部署** | Docker + Nginx | 容器化部署 |

---

## Design System (Critical — Must Follow)

### Colors — Warm & Clean

| 色阶 | 色值 | 用途 |
|------|------|------|
| 主色（暖珊瑚） | `#E07B5A` | 主按钮、支出标识 |
| 主色-hover | `#C96A4C` | 按钮悬停 |
| 主色-light | `#FDF0EB` | 主色浅底背景 |
| 辅助色（暖绿） | `#7BA587` | 收入标识、正向指标 |
| 辅助色（暖蓝） | `#6B9EB3` | 链接、信息提示 |
| 文字-主要 | `#4A3F3A` | 标题、正文 |
| 文字-次要 | `#8B7E75` | 辅助说明 |
| 文字-禁用 | `#BFB5AD` | 禁用状态 |
| 背景-页面 | `#FAF7F4` | 页面底色（暖白） |
| 背景-卡片 | `#FFFFFF` | 卡片/列表项背景 |
| 背景-悬停 | `#FDF5F0` | 列表悬停态 |
| 边框 | `#EBE3DC` | 分割线、边框 |
| 警告 | `#D4786E` | 超支、删除等警示 |

### Design Rules

- **NO animations** — no `transition`, `animation`, or CSS motion of any kind. Page changes are instant.
- **Shadows** — only single light card shadow: `0 1px 3px rgba(74,63,58,0.08)`. No layered shadows.
- **Border radius** — cards 12px, buttons/inputs 8px.
- **Spacing** — 8px grid: 8, 12, 16, 24, 32, 48px.
- **Font** — system default: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif`.
- **Layout** — Flexbox/Grid, max-width 1200px centered on desktop, full-width single-column on mobile (<768px).
- **Icons** — linear style only, no filled/solid variants.

---

## Current Phase

**Pre-implementation / planning.** No application code exists yet. The PRD at [docs/PRD-日常记账APP.md](docs/PRD-日常记账APP.md) is the authoritative source for requirements, architecture, data model, and API design.

---

## Planned Project Structure

```
daily-tracker/
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 调用层 (axios 实例 + 拦截器)
│   │   │   ├── index.ts        #   axios 实例 + Token 刷新逻辑
│   │   │   ├── auth.ts         #   认证接口
│   │   │   ├── bills.ts        #   账单接口
│   │   │   ├── categories.ts   #   分类接口
│   │   │   ├── reports.ts      #   报表接口
│   │   │   └── budgets.ts      #   预算接口
│   │   ├── components/         # 通用组件
│   │   │   ├── AppHeader.vue   #   顶部导航栏 (桌面端)
│   │   │   ├── AppTabBar.vue   #   底部 Tab 导航 (移动端)
│   │   │   ├── AmountInput.vue #   金额输入组件
│   │   │   ├── CategoryIcon.vue#   分类图标
│   │   │   ├── OverviewCard.vue#   概览卡片
│   │   │   ├── Toast.vue       #   即时提示 (无动画)
│   │   │   └── ConfirmDialog.vue#  确认弹窗
│   │   ├── composables/        # 组合式函数
│   │   │   ├── useAuth.ts      #   认证逻辑
│   │   │   └── usePagination.ts#   分页逻辑
│   │   ├── features/           # 功能模块 (feature-first)
│   │   │   ├── auth/           #   认证模块
│   │   │   ├── billing/        #   记账模块 (记一笔/列表/搜索)
│   │   │   ├── report/         #   报表模块 (周报/月报/自定义)
│   │   │   └── settings/       #   设置模块 (预算/导出/个人信息)
│   │   ├── layouts/
│   │   │   └── DefaultLayout.vue  # 默认布局
│   │   ├── router/
│   │   │   └── index.ts        # 路由 + 导航守卫
│   │   ├── stores/             # Pinia stores
│   │   │   ├── auth.ts
│   │   │   ├── bills.ts
│   │   │   └── categories.ts
│   │   ├── styles/
│   │   │   ├── variables.css   #   CSS 变量 (颜色/间距/圆角)
│   │   │   ├── reset.css       #   样式重置
│   │   │   └── global.css      #   全局样式
│   │   ├── types/              # TypeScript 类型定义
│   │   └── utils/
│   │       ├── format.ts       #   金额/日期格式化
│   │       └── storage.ts      #   localStorage 封装
│   ├── index.html
│   └── vite.config.ts
├── server/                      # Python 后端
│   ├── app/
│   │   ├── api/                # API 路由 (按模块分)
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   ├── schemas/            # Pydantic 请求/响应 schema
│   │   ├── services/           # 业务逻辑层
│   │   ├── core/
│   │   │   ├── config.py       #   应用配置 (环境变量)
│   │   │   ├── security.py     #   JWT + 密码哈希
│   │   │   ├── database.py     #   数据库引擎 + session
│   │   │   └── deps.py         #   FastAPI 依赖注入
│   │   ├── exceptions/         # 自定义异常
│   │   └── main.py             # FastAPI 入口
│   ├── alembic/                # 数据库迁移
│   └── requirements.txt
├── docs/
│   └── PRD-日常记账APP.md      # 产品需求文档
├── docker-compose.yml
└── README.md
```

---

## Feature Modules (from PRD)

```
日常记账APP
├── 1. 用户模块 (auth) — P0
│   ├── 注册 (邮箱)
│   ├── 登录 (邮箱+密码)
│   └── 密码找回 (邮箱验证码)
├── 2. 记账模块 (billing) — P0 (核心)
│   ├── 记一笔 (收入/支出, ≤3秒完成)
│   ├── 账单列表 (按天分组, 分页, 筛选)
│   ├── 账单详情/编辑/删除/批量删除
│   └── 分类管理 (8支出+5收入默认, 可自定义)
├── 3. 报表模块 (report) — P0 (核心)
│   ├── 周报表 (柱状图+饼图+周对比+日明细)
│   ├── 月报表 (趋势线+热力图+排行+月对比)
│   └── 自定义时间范围报表 (P2)
├── 4. 设置模块 (settings)
│   ├── 预算设置 (总额/分类预算, 80%提醒) — P1
│   └── 数据导出 (CSV/Excel) — P2
```

---

## Data Model (core entities)

- **users**: `id, username, email, password_hash, avatar_url, created_at, updated_at`
- **bills**: `id, user_id(FK), type(ENUM income/expense), amount DECIMAL(12,2), category_id(FK), bill_date, note VARCHAR(200), created_at, updated_at`
  - INDEX: `(user_id, bill_date)`, `(user_id, category_id)`
- **categories**: `id, user_id(FK, NULL=系统默认), name, icon, color, type(ENUM), is_default, sort_order, created_at`
- **budgets**: `id, user_id(FK), category_id(FK, NULL=总预算), amount DECIMAL(12,2), month VARCHAR(7)`
  - UNIQUE: `(user_id, month, category_id)`

---

## Key Design Decisions

- **Feature-first** project organization (not layer-first)
- API base: `https://api.dailytracker.com/v1`
- API response: `{ "code": 0, "message": "success", "data": {...} }`
- Error response: `{ "code": 40001, "message": "...", "detail": "..." }`
- Money is always `DECIMAL(12,2)` — **never float**
- JWT dual-token: access_token (15min) + refresh_token (7 days)
- Password: bcrypt hashing
- Default categories: 8 expense + 5 income (see PRD §2.3.2 for names/icons/colors)
- System default categories (`user_id=NULL`) cannot be deleted
- Categories with active bills cannot be deleted
- V1.0: 邮箱注册 only, CNY only, single ledger, no voice input

---

## API Summary

| Module | Key Endpoints |
|--------|--------------|
| Auth | `POST /auth/{register,login,refresh,send-code,reset-password}`, `PUT /auth/password` |
| Bills | `POST /bills`, `GET /bills`, `GET/PUT/DELETE /bills/{id}`, `POST /bills/batch-delete`, `GET /bills/search` |
| Categories | `GET /categories`, `POST /categories`, `PUT/DELETE /categories/{id}` |
| Reports | `GET /reports/{weekly,monthly,custom}` |
| Budgets | `GET /budgets`, `PUT /budgets` |
| Users | `GET/PUT /users/profile` |

---

## Development Order

1. **Backend first**: auth system → bill CRUD → category management → report APIs
2. **Frontend**: pages + chart integration
3. **Integration testing**
4. **Deploy**

---

## Custom Constraints

- 删除文件时，必须给我提示，经过我同意才能删除
- 每次 review 之后，告知我任务完成了，ACK 内容为"当前任务已完成"
- 用户对 Vue 生态不太精通，代码需有清晰注释，避免过度抽象
