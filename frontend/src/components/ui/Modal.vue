<!--
  Modal.vue — 通用模态弹窗容器
  遮罩 + 居中面板，支持标题和关闭按钮
-->
<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-card" :style="{ maxWidth: maxWidth }">
        <!-- 标题栏 -->
        <div v-if="title || showClose" class="modal-header">
          <h3 class="modal-title">{{ title }}</h3>
          <button v-if="showClose" class="modal-close" @click="$emit('close')">
            <X :size="20" />
          </button>
        </div>
        <!-- 内容区 -->
        <div class="modal-body">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'

defineProps<{
  visible: boolean
  title?: string
  showClose?: boolean
  maxWidth?: string
}>()

defineEmits<{
  close: []
}>()
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9980;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(74, 63, 58, 0.4);
  padding: 16px;
}

.modal-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
}

.modal-title {
  font-size: var(--font-lg);
  color: var(--text-primary);
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

.modal-close:hover {
  background: var(--bg-hover);
}

.modal-body {
  padding: 24px;
}
</style>
