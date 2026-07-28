# PROJECT_ANALYSIS.md

## 项目质量审查 — 第一阶段：项目分析

**审查日期**: 2026-07-29  
**审查人**: Senior QA Engineer (Claude Code)  
**项目名称**: DailyTracker — 日常记账APP  
**项目类型**: Vibe Coding 全栈应用 (V1.0 Web)

---

## 1. 技术栈分析

### 前端 (Frontend)
| 层级 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 (Composition API + `<script setup>`) | ^3.5.39 |
| 构建工具 | Vite | ^8.1.1 |
| 语言 | TypeScript | ~6.0.2 |
| 状态管理 | Pinia | ^4.0.2 |
| 路由 | Vue Router 4 | ^4.6.4 |
| HTTP 客户端 | Axios | ^1.18.1 |
| 图表库 | ECharts (vue-echarts) | ^6.1.0 / ^8.0.1 |
| 图标库 | Lucide Vue Next | ^1.0.0 |
| UI 组件库 | 无 — 完全自定义组件 |

### 后端 (Backend)
| 层级 | 技术 | 版本 |
|------|------|------|
| 框架 | FastAPI (Python 3.14) | 0.140.7 |
| ORM | SQLAlchemy 2.0 (async) | 2.0.51 |
| 数据库 | MySQL 8.0 | 8.0.44 |
| 缓存 | Redis (可选) | 8.0.1 |
| 认证 | PyJWT + bcrypt | 2.13.0 / 5.0.0 |
| 数据校验 | Pydantic v2 | 2.13.4 |
| 数据库迁移 | Alembic | 已配置 |
| 异步驱动 | aiomysql | 0.3.2 |
| 服务器 | Uvicorn | 0.51.0 |

---

## 2. 测试体系分析

### 已有测试
| 类型 | 数量 | 说明 |
|------|------|------|
| 单元测试 | **0** | 无任何 `*.test.*` 或 `*.spec.*` 文件 |
| 集成测试 | **0** | 无 API 测试 |
| E2E 测试 | **0** | 无端到端测试 |
| 测试配置 | **0** | 无 vitest.config.ts / pytest.ini / playwright.config.ts |

### 测试覆盖情况
- **前端覆盖率**: 0%
- **后端覆盖率**: 0%
- **E2E 覆盖率**: 0%
- **测试目录**: `test/` 目录已创建（含 `frontend-test/` 和 `backend-test/` 子目录），但均为空

---

## 3. 项目结构分析

### 前端组件统计
| 类别 | 数量 | 文件 |
|------|------|------|
| 布局组件 | 2 | AppHeader, AppTabBar |
| UI 组件 | 11 | AmountInput, BillRow, CategoryIcon, ConfirmDialog, EmptyState, ErrorState, LoadingState, Modal, OverviewCard, PageHeader, Pagination, ReportTabs, Toast, TypeToggle |
| 功能页面 | 9 | LoginView, LandingView, HomeView, BillListView, BillDetailView, CategoryManage, WeeklyReport, MonthlyReport, CustomReport, SettingsView |
| API 模块 | 7 | index, auth, bills, categories, reports, budgets, users, home |
| Store | 2 | auth, categories |
| 类型定义 | 6 | api, auth, bill, budget, category, home, report |

### 后端模块统计
| 类别 | 数量 | 文件 |
|------|------|------|
| API 路由 | 6 | auth, bills, categories, reports, budgets, users |
| 服务层 | 6 | auth, bill, category, budget, home, report |
| 数据模型 | 4 | user, bill, category, budget |
| Pydantic Schema | 6 | auth, bill, budget, category, common, report |
| 核心模块 | 5 | config, database, deps, redis, security |
| 中间件 | 2 | request_id, logging_mw |
| 异常处理 | 1 | handlers (7 种类型化异常) |

---

## 4. 数据库状态

| 表名 | 行数 | 状态 |
|------|------|------|
| users | 9 | 包含测试用户 |
| bills | 4 | 部分测试数据 |
| categories | 15 | 13 条默认分类 + 2 条自定义 |
| budgets | 3 | 测试预算数据 |

---

## 5. 基础设施可用性

| 服务 | 状态 | 备注 |
|------|------|------|
| MySQL 8.0 | ✅ 运行中 | 127.0.0.1:3306, 数据库 `account` |
| Redis | ❌ 未运行 | 应用有优雅降级处理 |
| Python 3.14 | ✅ 可用 | 所有依赖已安装 |
| Node.js v24.18.0 | ✅ 可用 | npm 11.16.0 |
| Playwright | ✅ 可用 | v1.62.0 (npm) |
| Pytest | ✅ 可用 | v9.1.1 + pytest-asyncio |

---

## 6. 代码质量初步观察

### 优点
- ✅ 后端异常体系完整（7 种类型化异常）
- ✅ Pydantic 参数校验覆盖所有 API 入参
- ✅ Axios 拦截器实现了 Token 自动刷新队列机制
- ✅ 路由导航守卫正确处理认证逻辑
- ✅ 数据隔离：所有账单操作基于 `user_id` 过滤
- ✅ 统一 API 响应格式（code + message + data）
- ✅ 账号锁定机制（5 次错误锁定 15 分钟）

### 需关注
- ⚠️ `.env` 文件提交到仓库（含数据库密码 `wyx4022`）
- ⚠️ JWT Secret 使用硬编码开发密钥
- ⚠️ XSS 输入未做 HTML 转义（`<script>` 标签直接存入数据库）
- ⚠️ 前端无输入校验（仅依赖后端 Pydantic 校验）
- ⚠️ 无任何自动化测试
- ⚠️ Redis 不可用时验证码直接丢失（Mock 模式）
- ⚠️ CORS 配置 `allow_origins=["*"]` 在生产中不安全
- ⚠️ `handlers.py:41` 有类型错误：`requests.Request` 应为 `Request`
