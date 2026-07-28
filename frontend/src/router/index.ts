/**
 * Vue Router 路由配置 + 导航守卫
 *
 * 路由结构：
 * - 公开路由（无需登录）：/landing, /login
 * - 受保护路由（需登录）：/ (首页), /bills, /reports/*, /settings, /categories
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { hasToken } from '@/utils/storage'

// ===== 路由定义 =====
const routes: RouteRecordRaw[] = [
  // 公开路由
  {
    path: '/landing',
    name: 'Landing',
    component: () => import('@/features/landing/LandingView.vue'),
    meta: { requiresAuth: false, title: 'DailyTracker' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/features/auth/LoginView.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },

  // 受保护路由 — 主应用（DefaultLayout 包裹）
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/features/home/HomeView.vue'),
        meta: { title: '记账' }
      },
      {
        path: 'bills',
        name: 'Bills',
        component: () => import('@/features/billing/BillListView.vue'),
        meta: { title: '账单' }
      },
      {
        path: 'bills/:id',
        name: 'BillDetail',
        component: () => import('@/features/billing/BillDetailView.vue'),
        meta: { title: '账单详情' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/features/billing/CategoryManage.vue'),
        meta: { title: '分类管理' }
      },
      {
        path: 'reports',
        redirect: '/reports/weekly'
      },
      {
        path: 'reports/weekly',
        name: 'WeeklyReport',
        component: () => import('@/features/report/WeeklyReport.vue'),
        meta: { title: '周报表' }
      },
      {
        path: 'reports/monthly',
        name: 'MonthlyReport',
        component: () => import('@/features/report/MonthlyReport.vue'),
        meta: { title: '月报表' }
      },
      {
        path: 'reports/custom',
        name: 'CustomReport',
        component: () => import('@/features/report/CustomReport.vue'),
        meta: { title: '自定义报表' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/features/settings/SettingsView.vue'),
        meta: { title: '设置' }
      }
    ]
  },

  // 404 兜底 — 重定向到首页
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

// ===== 创建路由实例 =====
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// ===== 全局前置导航守卫 =====
router.beforeEach(async (to, _from, next) => {
  // 更新页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - DailyTracker`
  }

  // 公开路由：已登录用户访问登录/落地页时重定向到首页
  if (to.meta.requiresAuth === false) {
    if (hasToken() && (to.name === 'Login' || to.name === 'Landing')) {
      next('/')
      return
    }
    next()
    return
  }

  // 受保护路由：未登录用户访问根路径 → 展示落地页
  if (!hasToken() && to.path === '/') {
    next('/landing')
    return
  }

  // 受保护路由：检查登录状态
  if (to.meta.requiresAuth) {
    if (!hasToken()) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    // 有 Token 但无用户信息 — 尝试获取用户信息
    const authStore = useAuthStore()
    if (!authStore.user) {
      try {
        await authStore.fetchProfile()
        next()
      } catch {
        authStore.logout()
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }

    next()
    return
  }

  next()
})

export default router
