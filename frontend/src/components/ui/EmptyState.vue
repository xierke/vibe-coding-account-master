<!--
  EmptyState.vue — 空状态占位组件
  用于列表/页面无数据时展示
-->
<template>
  <div class="empty-state">
    <span class="empty-icon">{{ icon }}</span>
    <h3 class="empty-title">{{ title }}</h3>
    <p v-if="description" class="empty-desc">{{ description }}</p>
    <button v-if="actionText" class="btn btn-primary empty-btn" @click="$emit('action')">
      {{ actionText }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon?: string
  title?: string
  description?: string
  actionText?: string
}>()

defineEmits<{
  action: []
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  line-height: 1;
  margin-bottom: 16px;
}

.empty-title {
  font-size: var(--font-lg);
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: var(--font-base);
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.empty-btn {
  min-width: 120px;
}
</style>
