<!--
  TypeToggle.vue — 收入/支出类型切换组件
  Segment control 样式，暖色调
-->
<template>
  <div class="type-toggle">
    <button
      class="type-option"
      :class="{ 'type-active': modelValue === 'expense' }"
      @click="$emit('update:modelValue', 'expense')"
    >
      支出
    </button>
    <button
      class="type-option"
      :class="{ 'type-active': modelValue === 'income' }"
      @click="$emit('update:modelValue', 'income')"
    >
      收入
    </button>
  </div>
</template>

<script setup lang="ts">
import type { BillType } from '@/types/bill'

defineProps<{
  modelValue: BillType
}>()

defineEmits<{
  'update:modelValue': [value: BillType]
}>()
</script>

<style scoped>
.type-toggle {
  display: flex;
  background: var(--bg-page);
  border-radius: var(--radius-sm);
  padding: 3px;
  height: 40px;
}

.type-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-size: var(--font-base);
  color: var(--text-secondary);
  border: none;
  cursor: pointer;
  background: transparent;
}

.type-active {
  background: var(--color-primary);
  color: #FFFFFF;
}
</style>
