<!--
  Toast.vue — 全局即时提示组件
  固定在页面顶部居中，无动画，2.5 秒自动消失
  类型：success(绿色) / error(警告色) / info(蓝色)
-->
<template>
  <div class="toast-container" v-if="toastStore.messages.value.length > 0">
    <div
      v-for="msg in toastStore.messages.value"
      :key="msg.id"
      class="toast-item"
      :class="'toast-' + msg.type"
    >
      <!-- 图标 -->
      <span class="toast-icon">
        <CheckCircle v-if="msg.type === 'success'" :size="18" />
        <AlertCircle v-else-if="msg.type === 'error'" :size="18" />
        <Info v-else :size="18" />
      </span>
      <!-- 文字 -->
      <span class="toast-text">{{ msg.text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import { CheckCircle, AlertCircle, Info } from 'lucide-vue-next'
import { TOAST_KEY } from '@/composables/useToast'

const toastStore = inject(TOAST_KEY)
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-card);
  font-size: var(--font-base);
  color: var(--text-primary);
  min-width: 200px;
  max-width: 360px;
  pointer-events: auto;
  border-left: 3px solid transparent;
}

.toast-success {
  border-left-color: var(--color-income);
}

.toast-success .toast-icon {
  color: var(--color-income);
}

.toast-error {
  border-left-color: var(--color-warning);
}

.toast-error .toast-icon {
  color: var(--color-warning);
}

.toast-info {
  border-left-color: var(--color-info);
}

.toast-info .toast-icon {
  color: var(--color-info);
}

.toast-icon {
  flex-shrink: 0;
}

.toast-text {
  line-height: 1.4;
}
</style>
