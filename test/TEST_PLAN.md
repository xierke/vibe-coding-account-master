# TEST_PLAN.md

## 项目质量审查 — 第二阶段：测试计划

**审查日期**: 2026-07-29  
**项目**: DailyTracker — 日常记账APP

---

## 测试环境

| 项目 | 值 |
|------|-----|
| 操作系统 | Windows 11 Home China 10.0.26200 |
| Python | 3.14.6 |
| Node.js | v24.18.0 |
| MySQL | 8.0.44 (127.0.0.1:3306) |
| Redis | 未运行（应用有降级处理） |
| 后端地址 | http://localhost:8000 |
| 前端地址 | http://localhost:5173 |
| 浏览器 | Chromium (Playwright) |

---

## 测试范围

### 一、前端测试 (Frontend)

#### 1.1 页面加载测试
- [x] Landing 页面加载
- [x] Login 页面加载（3 个 Tab：登录/注册/忘记密码）
- [x] Home 首页加载（记账表单 + 近期账单）
- [x] Bills 账单列表页加载
- [x] Bill Detail 账单详情页加载
- [x] Categories 分类管理页加载
- [x] Reports 报表页加载（周报/月报/自定义）
- [x] Settings 设置页加载
- [x] 404 页面兜底

#### 1.2 路由测试
- [x] 公开路由可正常访问（/landing, /login）
- [x] 未登录访问受保护路由跳转到登录页
- [x] 已登录访问登录页重定向到首页
- [x] 路由 meta.title 正确设置页面标题
- [x] /reports 重定向到 /reports/weekly

#### 1.3 用户交互测试
- [x] 登录 Tab 切换（登录 ↔ 注册 ↔ 忘记密码）
- [x] 收支类型切换 (TypeToggle)
- [x] 金额输入和实时解析
- [x] 分类选择点击
- [x] 记账表单提交
- [x] 账单列表滚动加载
- [x] 账单详情返回

#### 1.4 表单验证测试
- [x] 登录表单：空邮箱/空密码提示
- [x] 注册表单：用户名长度、邮箱格式、密码强度、确认密码
- [x] 忘记密码：邮箱必填、验证码必填、新密码验证
- [x] 记账表单：金额必填、分类必选、备注长度限制

#### 1.5 状态管理测试
- [x] Pinia auth store 登录/登出状态
- [x] Token localStorage 持久化
- [x] 分类 store 数据获取
- [x] Token 刷新队列机制

#### 1.6 UI 异常测试
- [x] Loading 状态展示
- [x] Empty 空数据状态
- [x] Error 网络错误状态
- [x] Toast 提示展示
- [x] 浏览器后退/前进

#### 1.7 浏览器兼容性
- [x] Chromium 渲染测试
- [x] 桌面端 (1920x1080) 布局
- [x] 平板端 (768px) 布局
- [x] 移动端 (375px) 布局

---

### 二、后端测试 (Backend)

#### 2.1 API 接口测试
- [x] `POST /v1/auth/register` — 用户注册
- [x] `POST /v1/auth/login` — 密码登录
- [x] `POST /v1/auth/refresh` — Token 刷新
- [x] `POST /v1/auth/send-code` — 发送验证码
- [x] `POST /v1/auth/reset-password` — 密码重置
- [x] `PUT /v1/auth/password` — 修改密码（需登录）
- [x] `POST /v1/bills` — 创建账单
- [x] `GET /v1/bills` — 账单列表（分页+筛选）
- [x] `GET /v1/bills/search` — 账单搜索
- [x] `GET /v1/bills/{id}` — 账单详情
- [x] `PUT /v1/bills/{id}` — 编辑账单
- [x] `DELETE /v1/bills/{id}` — 删除账单
- [x] `POST /v1/bills/batch-delete` — 批量删除
- [x] `GET /v1/categories` — 分类列表
- [x] `POST /v1/categories` — 创建分类
- [x] `GET /v1/reports/weekly` — 周报表
- [x] `GET /v1/reports/monthly` — 月报表
- [x] `GET /v1/budgets` — 预算查询
- [x] `PUT /v1/budgets` — 预算设置
- [x] `GET /v1/users/profile` — 用户信息
- [x] `GET /health` — 健康检查
- [x] `GET /` — 根路径

#### 2.2 参数验证测试
- [x] bill type 必须是 income/expense
- [x] amount 范围 0.01 ~ 999,999,999.99
- [x] amount 自动四舍五入到 2 位小数
- [x] 用户名 2-20 字符
- [x] 密码 8-20 字符，含字母+数字
- [x] 邮箱格式校验 (EmailStr)
- [x] 手机号格式校验
- [x] note 最大 200 字符
- [x] 分页参数范围校验

#### 2.3 CRUD 流程测试
- [x] 注册 → 登录 → 创建账单 → 查看列表 → 详情 → 编辑 → 删除
- [x] 批量删除流程
- [x] 搜索流程（文本匹配 + 金额匹配）

#### 2.4 权限控制测试
- [x] 未登录访问 API → 401
- [x] 无效 Token 访问 API → 401
- [x] 跨用户访问账单 → 404（隐藏资源存在性）
- [x] 跨用户编辑账单 → 403
- [x] 系统默认分类不可删除
- [x] ccess Token 过期 → 401

#### 2.5 异常处理测试
- [x] 用户名重复注册 → 409
- [x] 邮箱重复注册 → 409
- [x] 密码错误 → 401 + 剩余次数提示
- [x] 连续 5 次密码错误 → 账号锁定
- [x] 分类不存在 → 404
- [x] 账单不存在 → 404

#### 2.6 数据库操作验证
- [x] 事务回滚（异常时数据不写入）
- [x] 数据隔离（user_id 过滤）
- [x] 金额 DECIMAL 精度保持

---

### 三、端到端测试 (E2E)

模拟真实用户完整流程：

```
用户注册
  ↓
用户登录
  ↓
查看首页（空数据状态）
  ↓
记一笔支出（餐饮 ¥35.50）
  ↓
记一笔收入（工资 ¥5000）
  ↓
查看首页概览（本月收支自动更新）
  ↓
查看账单列表
  ↓
搜索账单
  ↓
编辑账单
  ↓
查看周报表
  ↓
查看月报表
  ↓
删除账单
  ↓
用户登出
```

---

## 测试执行计划

| 阶段 | 测试类型 | 工具 | 预计时间 |
|------|----------|------|----------|
| Phase 3a | Backend API 测试 | curl + httpx + pytest | 20 min |
| Phase 3b | Frontend 组件测试 | Playwright (可见浏览器) | 15 min |
| Phase 3c | E2E 完整流程 | Playwright | 10 min |
| Phase 4 | Bug 收集 | 手动汇总 | 10 min |
| Phase 5 | 安全检查 | 代码审查 + 工具扫描 | 10 min |
| Phase 6 | 最终报告 | 汇总 | 10 min |
