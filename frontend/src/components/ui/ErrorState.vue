<!--
  ErrorState.vue — 错误状态提示组件
  显示错误信息 + 重试按钮
-->
<template>
  <div class="error-state">
    <AlertTriangle :size="32" class="error-icon" />
    <h3 class="error-title">{{ title }}</h3>
    <p v-if="description" class="error-desc">{{ description }}</p>
    <button v-if="showRetry" class="btn btn-primary error-btn" @click="$emit('retry')">
      重新加载
    </button>
  </div>
</template>

<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'

defineProps<{
  title?: string
  description?: string
  showRetry?: boolean
}>()

defineEmits<{
  retry: []
}>()
</script>

<style scoped>
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.error-icon {
  color: var(--color-warning);
  margin-bottom: 16px;
}

.error-title {
  font-size: var(--font-lg);
  color: var(--text-primary);
  margin-bottom: 8px;
}

.error-desc {
  font-size: var(--font-base);
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.error-btn {
  min-width: 120px;
}
</style>
