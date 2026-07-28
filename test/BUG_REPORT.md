# BUG_REPORT.md

## 项目质量审查 — 第四阶段：Bug 发现

**审查日期**: 2026-07-29  
**项目**: DailyTracker — 日常记账APP  

---

## Bug 概览

| Severity | Count | Description |
|----------|-------|-------------|
| 🔴 Critical | 0 | — |
| 🟠 High | 3 | 环境变量泄露、XSS、验证码脆弱性 |
| 🟡 Medium | 4 | CORS 过宽、login tab 冲突、密码校验不一致、类型错误 |
| 🟢 Low | 3 | 输入框类型、金额精度、WARNING: code 重复 |

---

## 🔴 Critical

（无）

---

## 🟠 High — 3 个

### BUG-H01: `.env` 文件提交到 Git 仓库

**ID**: BUG-H01  
**严重等级**: 🟠 High  
**位置**: `backend/.env` (已提交), `backend/.env.example`  
**发现时间**: 2026-07-29  

**复现步骤**:
1. 查看 `git log -- backend/.env`
2. 或直接打开 `backend/.env`

**实际结果**:
```
DATABASE_URL=mysql+aiomysql://root:wyx4022@127.0.0.1:3306/account
JWT_SECRET=dailytracker-dev-secret-key-change-in-production
```
数据库密码 `wyx4022` 和 JWT Secret 以明文形式存储在仓库中。

**预期结果**: `.env` 文件仅在 `.env.example` 模板中提供占位值，真实凭据不应提交。

**修复建议**:
1. 立即从 Git 历史中清除 `.env` 文件: `git filter-branch` 或 `git rebase`
2. 更换数据库密码和 JWT Secret
3. 确认 `.gitignore` 已包含 `*.env` 规则（当前已包含）
4. 执行 `git rm --cached backend/.env` 并提交

---

### BUG-H02: XSS — 用户输入未做 HTML 转义

**ID**: BUG-H02  
**严重等级**: 🟠 High  
**位置**: `backend/app/schemas/bill.py`, `backend/app/services/bill_service.py`  
**发现时间**: 2026-07-29  

**复现步骤**:
1. POST `/v1/bills` 传入 `{"note": "<script>alert(1)</script>"}`
2. 查询 GET `/v1/bills` 查看返回

**实际结果**:
```json
{"note": "<script>alert(1)</script>"}
```
HTML/JS 标签原样存入数据库并返回前端。前端若使用 `v-html` 或 `innerHTML` 渲染将执行脚本。

**预期结果**: 后端应对用户输入做 HTML 实体编码（如 `<` → `&lt;`），或前端渲染时使用 `{{ }}`（Vue 默认转义）。

**修复建议**:
1. 后端: 在 Schema 的 `field_validator` 中对 `note` 字段做 HTML 转义: `v.replace("<", "&lt;").replace(">", "&gt;")`
2. 前端: 确认所有用户内容使用 `{{ }}` 插值而非 `v-html`
3. 考虑使用 `bleach` 或 `nh3` 库做更严格的内容净化

---

### BUG-H03: Redis 不可用时验证码完全失效

**ID**: BUG-H03  
**严重等级**: 🟠 High  
**位置**: `backend/app/services/auth_service.py:252-275` (`send_verify_code`)  
**发现时间**: 2026-07-29  

**复现步骤**:
1. 确保 Redis 服务未运行
2. POST `/v1/auth/register` 注册新用户
3. POST `/v1/auth/send-code` 请求邮箱验证码
4. 尝试用验证码完成注册/密码重置

**实际结果**:
```python
# 代码第 267-269 行
except Exception:
    logger.warning("Redis 不可用，验证码仅打印到日志，无法用于实际验证")
```
验证码打印到后端控制台日志，但未存储到任何可查询位置。实际用户无法获取验证码。

**预期结果**: Redis 不可用时应有备选方案（如内存存储），或返回明确错误告知用户服务不可用。

**修复建议**:
1. 短期: 使用进程内存字典 `{key: (code, expires_at)}` 作为 Redis 不可用时的 fallback
2. 长期: 确保生产环境 Redis 高可用
3. 前端: 显示明确错误"验证码服务暂时不可用"

---

## 🟡 Medium — 4 个

### BUG-M01: CORS 配置过于宽松

**ID**: BUG-M01  
**严重等级**: 🟡 Medium  
**位置**: `backend/app/main.py:99-105`  
**发现时间**: 2026-07-29  

**复现步骤**: 查看 CORS 中间件配置

**实际结果**:
```python
allow_methods=["*"],
allow_headers=["*"],
```

**预期结果**: 生产环境应限定具体的 methods (`GET, POST, PUT, DELETE`) 和 headers。

**修复建议**:
1. 生产环境配置: `allow_methods=["GET", "POST", "PUT", "DELETE"]`
2. `allow_headers` 限定为 `["Content-Type", "Authorization"]`
3. 根据 `DEBUG` 环境变量切换 CORS 严格程度

---

### BUG-M02: LoginView 中 Tab 按钮与 Submit 按钮名称冲突

**ID**: BUG-M02  
**严重等级**: 🟡 Medium  
**位置**: `frontend/src/features/auth/LoginView.vue`  
**发现时间**: 2026-07-29  

**复现步骤**:
1. 使用 Playwright 测试登录页
2. 执行 `page.getByRole('button', { name: '登录' })`

**实际结果**:
```html
<!-- Tab 按钮 -->
<button class="auth-tab active">登录</button>
<!-- Submit 按钮 -->
<button class="btn btn-primary btn-full">登录</button>
```
两个按钮有相同的 accessible name "登录"，导致 Playwright strict mode 报错。

**预期结果**: 每个交互元素的 accessible name 应该是唯一的。

**修复建议**:
1. 给 Submit 按钮添加 `aria-label="登录提交"` 或使用不同的文本如 "登录系统"
2. 或者 Tab 按钮使用 `role="tab"` 而非 `role="button"`

---

### BUG-M03: 密码校验规则前后端不一致

**ID**: BUG-M03  
**严重等级**: 🟡 Medium  
**位置**:
- 后端: `backend/app/schemas/auth.py:28-37` (RegisterRequest)
- 前端: `frontend/src/features/auth/LoginView.vue:211-213`

**发现时间**: 2026-07-29  

**实际结果**:
- 后端校验: 8-20 位，包含字母和数字（`[A-Za-z]` + `\d`）
- 前端校验: 仅检查 `regForm.password.length < 8`
- `ResetPasswordRequest` (line 133-140) 的密码校验比 `RegisterRequest` (line 28-37) 宽松——不检查字母

**预期结果**:
1. 前端和后端使用相同的密码强度规则
2. `RegisterRequest` 和 `ResetPasswordRequest` 使用一致的密码校验逻辑

**修复建议**:
1. 前端增加正则校验: `/[A-Za-z]/.test(pwd) && /\d/.test(pwd)`
2. 抽取公共密码校验函数 `validate_password_strength()` 在 Register/Reset/Change 中复用

---

### BUG-M04: 异常处理器中的类型注解错误

**ID**: BUG-M04  
**严重等级**: 🟡 Medium  
**位置**: `backend/app/exceptions/handlers.py:41`  
**发现时间**: 2026-07-29  

**实际结果**:
```python
async def unhandled_exception_handler(request: requests.Request, exc: Exception):
```
`requests.Request` 应为 `fastapi.Request`。这是类型注解错误，运行时不会报错因为 Python 不做运行时类型检查，但会导致 IDE 类型提示错误。

**预期结果**: `request: Request`（已从 fastapi 导入）

**修复建议**: 将 `requests.Request` 改为 `Request`（即 `fastapi.Request`）

---

## 🟢 Low — 3 个

### BUG-L01: LoginView 邮箱输入框 type 属性不正确

**ID**: BUG-L01  
**严重等级**: 🟢 Low  
**位置**: `frontend/src/features/auth/LoginView.vue:35`  
**发现时间**: 2026-07-29  

**实际结果**:
```html
<input type="text" ... placeholder="your@email.com" autocomplete="email" />
```
`type="text"` 而非 `type="email"`。

**预期结果**: `type="email"` 可触发浏览器的邮箱格式校验和移动端键盘优化。

**修复建议**: 改为 `type="email"`

---

### BUG-L02: 分类名 "其他支出" 和 "其他收入" 在列表中图标相同

**ID**: BUG-L02  
**严重等级**: 🟢 Low  
**位置**: `backend/app/services/category_service.py:31,37`  
**发现时间**: 2026-07-29  

**实际结果**:
```python
{"name": "其他支出", "icon": "📌", ...},   # sort_order=8
{"name": "其他收入", "icon": "📌", ...},   # sort_order=5
```
两个不同的分类使用了相同图标 📌。

**预期结果**: 不同分类应有不同图标以便区分。

**修复建议**: 改变其中一个图标，如"其他支出"使用 💸，"其他收入"使用 💵

---

### BUG-L03: 金额 `round()` 在 Schema 层和 Service 层重复执行

**ID**: BUG-L03  
**严重等级**: 🟢 Low  
**位置**:
- `backend/app/schemas/bill.py:33` (`round(v, 2)`)
- `backend/app/services/bill_service.py:51` (`round(float(amount), 2)`)

**发现时间**: 2026-07-29  

**实际结果**: 金额在 Pydantic Schema 的 `field_validator` 中 round 一次，在 Service 层又 round 一次。虽然不造成功能问题，但重复逻辑。

**预期结果**: 仅在 Schema 层或 Service 层做一次 round。

**修复建议**: 移除 Service 层中的 `round()`，仅保留 Schema 层校验

---

## Bug 分布统计

| 层级 | Critical | High | Medium | Low | Total |
|------|----------|------|--------|-----|-------|
| 后端 | 0 | 2 | 2 | 2 | 6 |
| 前端 | 0 | 0 | 1 | 1 | 2 |
| 安全/配置 | 0 | 1 | 1 | 0 | 2 |
| **合计** | **0** | **3** | **4** | **3** | **10** |
