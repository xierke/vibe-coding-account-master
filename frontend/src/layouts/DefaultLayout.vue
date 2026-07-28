<!--
  DefaultLayout.vue — 主应用布局
  结构：顶部导航栏（桌面端） + 内容区 + 底部 Tab 栏（移动端）
-->
<template>
  <div class="default-layout">
    <!-- 顶部导航栏 — 桌面端 -->
    <AppHeader />

    <!-- 主内容区 -->
    <main class="layout-main">
      <router-view />
    </main>

    <!-- 底部 Tab 导航 — 移动端 -->
    <AppTabBar />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
import AppTabBar from '@/components/layout/AppTabBar.vue'
</script>

<style scoped>
.default-layout {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
}

.layout-main {
  flex: 1;
  padding-bottom: var(--space-xl);
}

/* 移动端：为底部 Tab 栏留出空间 */
@media (max-width: 767px) {
  .layout-main {
    padding-bottom: calc(var(--tabbar-height) + var(--space-lg));
  }
}
</style>
