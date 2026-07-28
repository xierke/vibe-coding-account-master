<!--
  OverviewCard.vue — 概览统计卡片
  用于 Dashboard、报表页展示关键指标
  支持多列均分布局
-->
<template>
  <div class="overview-card card">
    <div class="overview-grid" :style="{ gridTemplateColumns: `repeat(${items.length}, 1fr)` }">
      <div
        v-for="item in items"
        :key="item.label"
        class="overview-item"
      >
        <span class="overview-label">{{ item.label }}</span>
        <span class="overview-value" :style="{ color: item.color || 'var(--text-primary)' }">
          {{ item.value }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/** 概览项 */
export interface OverviewItem {
  label: string
  value: string
  color?: string
}

defineProps<{
  items: OverviewItem[]
}>()
</script>

<style scoped>
.overview-card {
  padding: 20px 24px;
}

.overview-grid {
  display: grid;
  gap: 16px;
}

.overview-item {
  text-align: center;
}

.overview-label {
  display: block;
  font-size: var(--font-base);
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.overview-value {
  font-size: var(--font-3xl);
  font-weight: 600;
}

@media (max-width: 767px) {
  .overview-card {
    padding: 16px;
  }

  .overview-value {
    font-size: var(--font-xl);
  }
}
</style>
