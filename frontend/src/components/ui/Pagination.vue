<!--
  Pagination.vue — 分页器组件
  Props: currentPage, totalPages
  Events: @change(page)
-->
<template>
  <div class="pagination" v-if="totalPages > 1">
    <button class="page-btn" :disabled="currentPage <= 1" @click="$emit('change', currentPage - 1)">‹</button>
    <button
      v-for="p in displayPages"
      :key="p"
      class="page-btn"
      :class="{ active: p === currentPage }"
      @click="$emit('change', p)"
    >{{ p }}</button>
    <button class="page-btn" :disabled="currentPage >= totalPages" @click="$emit('change', currentPage + 1)">›</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentPage: number
  totalPages: number
}>()

defineEmits<{
  change: [page: number]
}>()

/** 展示的页码列表（最多显示 5 个） */
const displayPages = computed(() => {
  const pages: number[] = []
  let start = Math.max(1, props.currentPage - 2)
  let end = Math.min(props.totalPages, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-lg) 0;
}
.page-btn {
  width: 36px; height: 36px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-primary);
  display: grid;
  place-items: center;
  font-size: 14px;
  cursor: pointer;
}
.page-btn:hover { border-color: var(--color-primary); }
.page-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.page-btn:disabled { color: var(--text-disabled); pointer-events: none; }
</style>
