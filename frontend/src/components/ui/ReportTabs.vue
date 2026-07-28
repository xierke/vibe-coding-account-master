<!--
  ReportTabs.vue — 报表类型 Tab 切换
  用于周报/月报页面顶部的 Tab 导航
-->
<template>
  <div class="report-tabs">
    <router-link
      v-for="tab in tabs"
      :key="tab.path"
      :to="tab.path"
      class="report-tab"
      :class="{ active: currentPath === tab.path }"
    >
      {{ tab.label }}
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const tabs = [
  { path: '/reports/weekly', label: '周报' },
  { path: '/reports/monthly', label: '月报' }
]

const currentPath = route.path
</script>

<style scoped>
.report-tabs {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}
.report-tab {
  padding: 8px 18px;
  border-radius: var(--radius-sm);
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
}
.report-tab:hover { border-color: var(--color-primary); color: var(--color-primary); }
.report-tab.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
</style>
