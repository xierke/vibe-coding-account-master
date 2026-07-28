<!--
  CategoryIcon.vue — 单个分类图标组件
  显示 emoji 图标 + 分类名称
  支持选中态和点击事件
-->
<template>
  <button
    class="category-icon"
    :class="{ 'category-selected': selected }"
    @click="$emit('select')"
    type="button"
  >
    <span class="category-emoji">{{ category.icon }}</span>
    <span class="category-label">{{ category.name }}</span>
  </button>
</template>

<script setup lang="ts">
import type { Category } from '@/types/category'

defineProps<{
  /** 分类数据 */
  category: Category | { id: number; name: string; icon: string; color: string }
  /** 是否选中 */
  selected?: boolean
}>()

defineEmits<{
  select: []
}>()
</script>

<style scoped>
.category-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 72px;
  border-radius: var(--radius-sm);
  background: var(--bg-page);
  border: 1.5px solid transparent;
  cursor: pointer;
  gap: 6px;
}

.category-icon:hover {
  background: var(--bg-hover);
}

.category-selected {
  background: var(--color-primary-light) !important;
  border-color: var(--color-primary) !important;
}

.category-emoji {
  font-size: 28px;
  line-height: 1;
}

.category-label {
  font-size: var(--font-sm);
  color: var(--text-primary);
}
</style>
