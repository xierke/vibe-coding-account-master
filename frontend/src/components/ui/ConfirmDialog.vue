<!--
  ConfirmDialog.vue — 确认弹窗
  用于删除确认等需要二次确认的操作
  插槽：默认插槽放置触发元素
-->
<template>
  <Teleport to="body">
    <div v-if="visible" class="dialog-overlay" @click.self="onCancel">
      <div class="dialog-card">
        <div class="dialog-body">
          <AlertTriangle :size="32" class="dialog-icon" />
          <h3 class="dialog-title">{{ title }}</h3>
          <p v-if="description" class="dialog-desc">{{ description }}</p>
        </div>
        <div class="dialog-actions">
          <button class="btn btn-secondary" @click="onCancel">{{ cancelText }}</button>
          <button class="btn btn-danger" @click="onConfirm">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'

defineProps<{
  visible: boolean
  title?: string
  description?: string
  confirmText?: string
  cancelText?: string
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

function onConfirm() {
  emit('confirm')
}

function onCancel() {
  emit('cancel')
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 9990;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(74, 63, 58, 0.4);
  padding: 16px;
}

.dialog-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  width: 360px;
  max-width: 100%;
  padding: 24px;
}

.dialog-body {
  text-align: center;
  margin-bottom: 24px;
}

.dialog-icon {
  color: var(--color-warning);
  margin-bottom: 12px;
}

.dialog-title {
  font-size: var(--font-lg);
  color: var(--text-primary);
  margin-bottom: 8px;
}

.dialog-desc {
  font-size: var(--font-base);
  color: var(--text-secondary);
}

.dialog-actions {
  display: flex;
  gap: 12px;
}

.dialog-actions .btn {
  flex: 1;
}
</style>
