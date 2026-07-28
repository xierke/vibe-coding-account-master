<!--
  LoadingState.vue — 加载状态组件
  简单的加载指示器 + 文字提示
  设计规范允许加载图标的 CSS animation（功能性需要，不影响其他元素）
-->
<template>
  <div class="loading-state">
    <span class="loading-spinner"></span>
    <p class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text?: string
}>()
</script>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

/* 加载动画仅用于功能性指示器 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: var(--font-base);
  color: var(--text-secondary);
}
</style>
