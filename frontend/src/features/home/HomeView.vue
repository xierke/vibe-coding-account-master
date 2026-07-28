<!--
  HomeView.vue — 记账首页
  桌面端：两栏布局（左：记账表单 + 右：近期账单）
  移动端：单列布局
  键盘操作：Enter 快捷提交
-->
<template>
  <div class="page-container">
    <!-- 本月收支概览卡片（全宽） -->
    <OverviewCard v-if="homeData" :items="overviewItems" :style="{ marginBottom: 'var(--space-lg)' }" />

    <!-- 主内容区：两栏布局 -->
    <div class="home-grid">
      <!-- 左栏：记账表单 -->
      <div class="bill-entry card">
        <div class="bill-entry-title">记一笔</div>

        <!-- 类型切换 -->
        <TypeToggle v-model="billType" class="mb-lg" />

        <!-- 金额输入 -->
        <div class="amount-area mb-lg">
          <span class="amount-label">金额</span>
          <div class="amount-display">
            <span class="currency">¥</span>
            <input
              ref="amountInputRef"
              v-model="amountRaw"
              type="text"
              inputmode="decimal"
              class="amount-input-field"
              placeholder="0.00"
              @keydown="onAmountKeydown"
            />
          </div>
        </div>

        <!-- 分类选择 -->
        <label class="form-label mb-sm">选择分类</label>
        <div class="category-grid mb-lg">
          <button
            v-for="cat in currentCategories"
            :key="cat.id"
            class="cat-chip"
            :class="{ selected: selectedCategoryId === cat.id, 'income-cat': billType === 'income' }"
            @click="selectedCategoryId = cat.id"
          >
            <span class="cat-icon">{{ cat.icon }}</span>
            <span class="cat-name">{{ cat.name }}</span>
          </button>
        </div>

        <!-- 日期 + 备注 -->
        <div class="entry-row mb-lg">
          <div class="form-group" style="flex:1;">
            <label class="form-label">日期</label>
            <input v-model="billDate" type="date" class="form-input" />
          </div>
          <div class="form-group" style="flex:2;">
            <label class="form-label">备注 <span class="text-disabled" style="font-weight:400;">（选填）</span></label>
            <input v-model="note" type="text" class="form-input" placeholder="例如：午餐外卖" maxlength="200" />
          </div>
        </div>

        <button class="btn btn-primary submit-btn" :disabled="submitting || !isFormValid" @click="handleSubmit">
          确认记账 ↵
        </button>
      </div>

      <!-- 右栏：近期账单 -->
      <div class="recent-bills card">
        <div class="recent-bills-title">近期账单</div>

        <LoadingState v-if="dashboardLoading" text="加载中..." />
        <EmptyState
          v-else-if="homeData && homeData.recent_bills.length === 0"
          icon="📝"
          title="暂无账单"
          description="开始记下你的第一笔账吧"
        />
        <template v-else-if="homeData">
          <div v-for="group in recentGroups" :key="group.date" class="day-group">
            <div class="day-header">
              <span class="day-label">{{ group.dayLabel }}</span>
              <span class="day-summary">
                支 <span class="sum-out">{{ formatMoney(group.dayExpense, false) }}</span>
                &nbsp;收 <span class="sum-in">{{ formatMoney(group.dayIncome, false) }}</span>
              </span>
            </div>
            <div v-for="bill in group.bills" :key="bill.id" class="bill-item" @click="$router.push(`/bills/${bill.id}`)">
              <span class="bill-cat-icon">{{ bill.category_icon }}</span>
              <div class="bill-info">
                <div class="bill-cat-name">{{ bill.category_name }}</div>
                <div class="bill-note">{{ bill.note || '' }}</div>
              </div>
              <span class="bill-amount" :class="bill.type === 'income' ? 'income' : 'expense'">
                {{ bill.type === 'income' ? '+' : '-' }}{{ formatMoney(bill.amount, false) }}
              </span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { getHomeDashboard } from '@/api/home'
import { createBill } from '@/api/bills'
import { useCategoryStore } from '@/stores/categories'
import { getToday, formatMoney, dateToDayLabel } from '@/utils/format'
import type { HomeDashboard, RecentBillItem } from '@/types/home'
import type { BillType } from '@/types/bill'
import type { OverviewItem } from '@/components/ui/OverviewCard.vue'

import OverviewCard from '@/components/ui/OverviewCard.vue'
import TypeToggle from '@/components/ui/TypeToggle.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

const router = useRouter()
const toast = useToast()
const categoryStore = useCategoryStore()

// ===== Dashboard 数据 =====
const homeData = ref<HomeDashboard | null>(null)
const dashboardLoading = ref(false)

const overviewItems = computed<OverviewItem[]>(() => {
  if (!homeData.value) return []
  return [
    { label: '总收入', value: formatMoney(homeData.value.month_income), color: 'var(--color-income)' },
    { label: '总支出', value: formatMoney(homeData.value.month_expense), color: 'var(--color-primary)' },
    { label: '结余', value: formatMoney(homeData.value.month_balance), color: homeData.value.month_balance >= 0 ? 'var(--color-income)' : 'var(--color-warning)' }
  ]
})

/** 近期账单按日期分组 */
const recentGroups = computed(() => {
  if (!homeData.value || homeData.value.recent_bills.length === 0) return []
  const map = new Map<string, { date: string; dayLabel: string; bills: RecentBillItem[]; dayIncome: number; dayExpense: number }>()
  for (const bill of homeData.value.recent_bills) {
    const d = bill.bill_date
    if (!map.has(d)) map.set(d, { date: d, dayLabel: dateToDayLabel(d), bills: [], dayIncome: 0, dayExpense: 0 })
    const g = map.get(d)!
    g.bills.push(bill)
    if (bill.type === 'income') g.dayIncome += bill.amount
    else g.dayExpense += bill.amount
  }
  return Array.from(map.values()).sort((a, b) => b.date.localeCompare(a.date))
})

// ===== 记账表单 =====
const amountInputRef = ref<HTMLInputElement | null>(null)
const billType = ref<BillType>('expense')
const amountRaw = ref('')
const amount = ref<number | null>(null)
const selectedCategoryId = ref<number | null>(null)
const billDate = ref(getToday())
const note = ref('')
const submitting = ref(false)

/** 解析用户输入的金额字符串 */
function parseAmount(raw: string): number | null {
  const cleaned = raw.replace(/[^0-9.]/g, '')
  const num = parseFloat(cleaned)
  return isNaN(num) || num <= 0 ? null : num
}

const currentCategories = computed(() =>
  billType.value === 'expense' ? categoryStore.expenseCategories : categoryStore.incomeCategories
)

const isFormValid = computed(() => amount.value !== null && selectedCategoryId.value !== null)

function onAmountKeydown(e: KeyboardEvent) {
  // Enter 快捷提交
  if (e.key === 'Enter') {
    e.preventDefault()
    handleSubmit()
  }
}

async function handleSubmit() {
  if (!isFormValid.value || submitting.value) return
  submitting.value = true
  try {
    await createBill({ type: billType.value, amount: amount.value!, category_id: selectedCategoryId.value!, bill_date: billDate.value, note: note.value.trim() || undefined })
    toast.success('✓ 记账成功')
    amountRaw.value = ''
    amount.value = null
    note.value = ''
    billDate.value = getToday()
    await fetchDashboard()
    nextTick(() => amountInputRef.value?.focus())
  } catch (e: any) { toast.error(e.message || '记账失败') }
  finally { submitting.value = false }
}

// 监听原始输入变化，实时解析金额
watch(amountRaw, (val) => { amount.value = parseAmount(val) })

// 切换类型时更新默认分类
watch(billType, () => {
  if (currentCategories.value.length > 0) selectedCategoryId.value = currentCategories.value[0].id
})

async function fetchDashboard() {
  dashboardLoading.value = true
  try { homeData.value = await getHomeDashboard() }
  catch { /* 不阻塞 */ }
  finally { dashboardLoading.value = false }
}

onMounted(async () => {
  await Promise.all([fetchDashboard(), categoryStore.fetchCategories()])
  if (currentCategories.value.length > 0) selectedCategoryId.value = currentCategories.value[0].id
  nextTick(() => amountInputRef.value?.focus())
})
</script>

<style scoped>
/* 两栏布局 */
.home-grid { display: grid; grid-template-columns: 1fr 360px; gap: var(--space-lg); }
@media (max-width: 920px) { .home-grid { grid-template-columns: 1fr; } }

/* 记账卡片 */
.bill-entry { padding: var(--space-lg); }
.bill-entry-title { font-size: 18px; font-weight: 700; margin-bottom: var(--space-md); }

.mb-sm { margin-bottom: var(--space-sm); }
.mb-lg { margin-bottom: var(--space-lg); }

/* 金额区域 */
.amount-area { text-align: center; }
.amount-label { font-size: 13px; color: var(--text-secondary); display: block; }
.amount-display { display: flex; align-items: baseline; justify-content: center; gap: 2px; padding: var(--space-md) 0; }
.currency { font-size: 20px; color: var(--text-secondary); font-weight: 500; }
.amount-input-field {
  width: 200px; border: none; background: transparent;
  font-size: 42px; font-weight: 700; font-family: ui-monospace, monospace;
  color: var(--text-primary); text-align: center; outline: none;
}
.amount-input-field::placeholder { color: var(--text-disabled); }

/* 分类 */
.category-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-sm); }
.cat-chip {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 10px 6px; border-radius: var(--radius-sm);
  border: 1px solid var(--border); background: transparent;
  font-size: 13px; color: var(--text-primary); cursor: pointer;
}
.cat-chip:hover { background: var(--bg-hover); }
.cat-chip.selected { border-color: var(--color-primary); background: var(--color-primary-light); }
.cat-chip.selected.income-cat { border-color: var(--color-income); background: color-mix(in oklch, var(--color-income) 12%, transparent); }
.cat-icon { font-size: 24px; }
.cat-name { font-size: 12px; }

.entry-row { display: flex; gap: var(--space-md); }
.form-group { display: flex; flex-direction: column; flex: 1; }
.form-input { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg-card); font-size: 14px; color: var(--text-primary); font-family: inherit; }
.form-input:focus { outline: none; border-color: var(--color-primary); }
.form-input::placeholder { color: var(--text-disabled); }

.submit-btn { width: 100%; font-size: 15px; }

/* 近期账单 */
.recent-bills { padding: var(--space-lg); max-height: 700px; overflow-y: auto; }
.recent-bills-title { font-size: 16px; font-weight: 700; margin-bottom: var(--space-md); }
.day-group { margin-bottom: var(--space-lg); }
.day-header { display: flex; justify-content: space-between; align-items: baseline; padding-bottom: var(--space-sm); margin-bottom: var(--space-sm); border-bottom: 1px solid var(--border); }
.day-label { font-size: 14px; font-weight: 600; }
.day-summary { font-size: 13px; }
.sum-out { color: var(--color-primary); font-family: ui-monospace, monospace; }
.sum-in { color: var(--color-income); font-family: ui-monospace, monospace; }
.bill-item {
  display: flex; align-items: center; gap: var(--space-sm);
  padding: 10px 0; border-bottom: 1px solid var(--border); cursor: pointer;
}
.bill-item:last-child { border-bottom: none; }
.bill-item:hover { background: var(--bg-hover); margin: 0 -8px; padding-left: 8px; padding-right: 8px; border-radius: var(--radius-sm); }
.bill-cat-icon { font-size: 22px; width: 32px; text-align: center; flex-shrink: 0; }
.bill-info { flex: 1; min-width: 0; }
.bill-cat-name { font-size: 14px; font-weight: 500; }
.bill-note { font-size: 12px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bill-amount { font-family: ui-monospace, monospace; font-weight: 600; font-size: 15px; white-space: nowrap; }
.bill-amount.expense { color: var(--color-primary); }
.bill-amount.income { color: var(--color-income); }

@media (max-width: 640px) {
  .entry-row { flex-direction: column; gap: var(--space-sm); }
  .category-grid { gap: 6px; }
  .cat-chip { padding: 8px 4px; }
  .cat-icon { font-size: 20px; }
  .amount-input-field { font-size: 32px; width: 160px; }
  .bill-entry, .recent-bills { padding: var(--space-md); }
}
</style>
