<!--
  BillRow.vue — 账单行组件
  显示单条账单：分类图标 + 名称 + 备注 + 金额 + 时间
  点击可展开详情
-->
<template>
  <div class="bill-row" :class="{ 'bill-row-expanded': expanded }" @click="$emit('click')">
    <!-- 主要信息行 -->
    <div class="bill-main">
      <!-- 分类图标（从 category 颜色生成背景） -->
      <div
        class="bill-category-icon"
        :style="{ backgroundColor: categoryColor + '26', color: categoryColor }"
      >
        {{ categoryIcon }}
      </div>
      <!-- 分类名称 + 备注 -->
      <div class="bill-info">
        <span class="bill-category-name">{{ categoryName }}</span>
        <span v-if="note" class="bill-note">{{ note }}</span>
      </div>
      <!-- 金额 + 时间 -->
      <div class="bill-amount-side">
        <span
          class="bill-amount"
          :class="type === 'income' ? 'text-income' : 'text-expense'"
        >
          {{ type === 'income' ? '+' : '-' }}{{ formattedAmount }}
        </span>
        <span class="bill-time">{{ billTime }}</span>
      </div>
    </div>
    <!-- 展开的详情区域（由父组件通过 slot 控制内容） -->
    <div v-if="expanded && $slots.detail" class="bill-detail">
      <slot name="detail" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatMoney, formatTime } from '@/utils/format'
import { truncateText } from '@/utils/format'

const props = defineProps<{
  /** 账单类型 */
  type: 'income' | 'expense'
  /** 金额 */
  amount: number
  /** 分类名称 */
  categoryName: string
  /** 分类图标 (emoji) */
  categoryIcon: string
  /** 分类颜色 */
  categoryColor: string
  /** 备注 */
  note?: string | null
  /** 创建时间 (ISO string) */
  createdAt: string
  /** 是否展开详情 */
  expanded?: boolean
}>()

defineEmits<{
  click: []
}>()

const formattedAmount = computed(() => formatMoney(props.amount, false))
const billTime = computed(() => formatTime(props.createdAt))

/** 截断备注文字（列表行最多显示 20 字） */
const displayNote = computed(() => {
  if (!props.note) return ''
  return truncateText(props.note, 20)
})
</script>

<style scoped>
.bill-row {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
}

.bill-row:last-child {
  border-bottom: none;
}

.bill-row:hover {
  background: var(--bg-hover);
}

.bill-main {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 36px;
}

/* 分类图标 */
.bill-category-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

/* 中间信息区 */
.bill-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.bill-category-name {
  font-size: var(--font-md);
  color: var(--text-primary);
}

.bill-note {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 金额 + 时间 */
.bill-amount-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
}

.bill-amount {
  font-size: var(--font-lg);
  font-weight: 600;
}

.bill-time {
  font-size: var(--font-xs);
  color: var(--text-disabled);
}

/* 展开详情区 */
.bill-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

@media (max-width: 767px) {
  .bill-row {
    padding: 10px 12px;
  }

  .bill-amount {
    font-size: var(--font-md);
  }
}
</style>
