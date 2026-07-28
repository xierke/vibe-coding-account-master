<!--
  AppTabBar.vue — 底部 Tab 导航栏（移动端）
  4 个 Tab：记账 | 账单 | 报表 | 我的
  仅在 <768px 时显示
-->
<template>
  <nav class="app-tabbar mobile-only">
    <router-link
      v-for="tab in tabs"
      :key="tab.path"
      :to="tab.path"
      class="tab-item"
      :class="{ 'tab-active': isActive(tab.path) }"
    >
      <component :is="tab.icon" :size="22" />
      <span class="tab-label">{{ tab.label }}</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { Home, FileText, BarChart3, User } from 'lucide-vue-next'
import type { Component } from 'vue'

const route = useRoute()

interface TabItem {
  path: string
  label: string
  icon: Component
}

const tabs: TabItem[] = [
  { path: '/', label: '记账', icon: Home },
  { path: '/bills', label: '账单', icon: FileText },
  { path: '/reports/weekly', label: '报表', icon: BarChart3 },
  { path: '/settings', label: '我的', icon: User }
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.app-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: var(--tabbar-height);
  background: var(--bg-card);
  border-top: 1px solid var(--border);
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: var(--text-secondary);
  text-decoration: none;
  padding: 4px 0;
}

.tab-active {
  color: var(--color-primary);
}

.tab-label {
  font-size: var(--font-xs);
}
</style>
