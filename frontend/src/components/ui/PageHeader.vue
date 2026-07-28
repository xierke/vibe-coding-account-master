<!--
  PageHeader.vue — 页面标题栏
  可选的返回按钮 + 标题 + 右侧操作区
-->
<template>
  <div class="page-header">
    <div class="page-header-left">
      <button v-if="showBack" class="back-btn" @click="$router.back()">
        <ChevronLeft :size="20" />
      </button>
      <h2 class="page-title">{{ title }}</h2>
    </div>
    <div v-if="$slots.actions" class="page-header-right">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChevronLeft } from 'lucide-vue-next'

defineProps<{
  title: string
  showBack?: boolean
}>()
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
  min-height: 40px;
}

.page-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.back-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

.back-btn:hover {
  background: var(--bg-hover);
}

.page-title {
  font-size: var(--font-xl);
  color: var(--text-primary);
}
</style>
