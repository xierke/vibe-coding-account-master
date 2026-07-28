/**
 * main.ts — 应用入口
 *
 * 初始化顺序：
 * 1. 全局 CSS（变量 → 重置 → 全局样式）
 * 2. 创建 Vue 应用
 * 3. 注册 Pinia（状态管理）
 * 4. 注册 Vue Router（路由）
 * 5. 挂载到 #app
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '@/router'
import App from '@/App.vue'

// ===== 全局样式（按优先级加载） =====
import '@/styles/variables.css'   // CSS 变量定义（最先加载，供后续引用）
import '@/styles/reset.css'       // 浏览器样式重置
import '@/styles/global.css'      // 全局工具类 + 响应式

// ===== 创建应用 =====
const app = createApp(App)

// ===== 注册 Pinia（状态管理） =====
const pinia = createPinia()
app.use(pinia)

// ===== 注册 Vue Router（路由 + 导航守卫） =====
app.use(router)

// ===== 挂载应用 =====
app.mount('#app')
