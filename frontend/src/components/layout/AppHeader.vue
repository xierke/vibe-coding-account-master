<!--
  AppHeader.vue — 顶部导航栏（桌面端）
  显示 Logo + 导航菜单项 + 用户头像/下拉
  仅在 ≥768px 时显示
-->
<template>
  <header class="app-header desktop-only">
    <div class="header-inner">
      <!-- Logo -->
      <div class="header-logo">
        <span class="logo-icon">💰</span>
        <span class="logo-text">DailyTracker</span>
      </div>

      <!-- 导航菜单 -->
      <nav class="header-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ 'nav-active': isActive(item.path) }"
        >
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- 用户区 -->
      <div class="header-user">
        <div class="user-avatar">
          {{ avatarLetter }}
        </div>
        <span class="user-name">{{ authStore.username || '用户' }}</span>
        <!-- 下拉菜单触发器（预留） -->
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Home, FileText, BarChart3, Settings } from 'lucide-vue-next'
import type { Component } from 'vue'

const route = useRoute()
const authStore = useAuthStore()

/** 导航菜单项 */
interface NavItem {
  path: string
  label: string
  icon: Component
}
const navItems: NavItem[] = [
  { path: '/', label: '记账', icon: Home },
  { path: '/bills', label: '账单', icon: FileText },
  { path: '/reports/weekly', label: '报表', icon: BarChart3 },
  { path: '/settings', label: '我的', icon: Settings }
]

/** 判断当前路由是否匹配导航项 */
function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

/** 用户头像首字母 */
const avatarLetter = computed(() => {
  const name = authStore.username || 'U'
  return name.charAt(0).toUpperCase()
})
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  height: var(--header-height);
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-card);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 24px;
}

/* Logo */
.header-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 48px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: var(--font-lg);
  font-weight: 700;
  color: var(--text-primary);
}

/* 导航菜单 */
.header-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: var(--font-base);
  text-decoration: none;
}

.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-active {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

/* 用户区 */
.header-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 24px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-base);
  font-weight: 600;
}

.user-name {
  font-size: var(--font-base);
  color: var(--text-primary);
}
</style>
