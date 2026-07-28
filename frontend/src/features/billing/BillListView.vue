<!--
  BillListView.vue — 账单列表页（对齐原型 app-bills.html）
  功能：
  - 筛选：全部 / 近7天 / 近30天 / 本月
  - 搜索：按备注搜索
  - 批量管理模式：checkbox + 批量操作栏
  - 行内编辑/删除按钮
  - 分页器
  - 删除确认弹窗
-->
<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">账单列表</h1>
      <div style="display:flex;gap:8px;">
        <button class="btn btn-ghost" @click="toggleBatchMode">{{ batchMode ? '退出管理' : '批量管理' }}</button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <button v-for="f in filters" :key="f.key" class="filter-pill" :class="{ active: activeFilter === f.key }" @click="applyFilter(f.key)">{{ f.label }}</button>
      <span class="filter-spacer"></span>
      <input v-model="searchKeyword" type="text" class="search-input" placeholder="搜索备注..." @input="onSearchInput" />
    </div>

    <!-- 批量操作栏 -->
    <div v-if="batchMode" class="batch-bar">
      <span class="batch-count">已选 {{ selectedIds.size }} 项</span>
      <span style="flex:1;"></span>
      <button class="btn btn-ghost" @click="toggleBatchMode">取消</button>
      <button class="btn btn-danger" :disabled="selectedIds.size === 0" @click="showBatchDeleteDialog">批量删除</button>
    </div>

    <!-- 加载 / 错误 / 空状态 -->
    <LoadingState v-if="loading && bills.length === 0" text="加载中..." />
    <ErrorState v-else-if="error && bills.length === 0" :description="error" show-retry @retry="fetchBills(true)" />
    <EmptyState v-else-if="!loading && bills.length === 0" icon="📋" title="暂无账单记录" description="开始记下你的第一笔账吧" action-text="去记账" @action="$router.push('/')" />

    <!-- 账单列表 -->
    <div v-else>
      <div v-for="group in groups" :key="group.date" class="day-group">
        <div class="day-header">
          <span class="day-label">{{ group.dayLabel }}</span>
          <span class="day-summary">支出 <span class="sum-out">{{ formatMoney(group.dayExpense, false) }}</span> &nbsp;收入 <span class="sum-in">{{ formatMoney(group.dayIncome, false) }}</span></span>
        </div>
        <div v-for="bill in group.bills" :key="bill.id" class="bill-item">
          <!-- 批量模式下的 checkbox -->
          <input v-if="batchMode" type="checkbox" class="bill-checkbox" :checked="selectedIds.has(bill.id)" @change="toggleSelect(bill.id)" />
          <span class="bill-cat-icon">{{ bill.category?.icon || '📌' }}</span>
          <div class="bill-info">
            <div class="bill-cat-name">{{ bill.category?.name || '未知' }}</div>
            <div class="bill-note">{{ bill.note || '' }}</div>
            <div class="bill-meta">{{ formatTime(bill.created_at) }}</div>
          </div>
          <span class="bill-amount" :class="bill.type">{{ bill.type === 'income' ? '+' : '-' }}{{ formatMoney(bill.amount, false) }}</span>
          <div v-if="!batchMode" class="bill-actions">
            <button class="bill-action-btn" title="编辑" @click="$router.push(`/bills/${bill.id}`)">✎</button>
            <button class="bill-action-btn danger" title="删除" @click="confirmSingleDelete(bill.id)">✕</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页器 -->
    <Pagination :current-page="page" :total-pages="totalPages" @change="goToPage" />
  </div>

  <!-- 删除确认弹窗 -->
  <ConfirmDialog :visible="showDeleteDialog" :title="deleteDialogTitle" description="此操作不可撤销。" confirm-text="确认删除" cancel-text="取消" @confirm="handleDelete" @cancel="showDeleteDialog = false" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import * as billsApi from '@/api/bills'
import { formatMoney, formatTime, groupBillsByDate } from '@/utils/format'
import type { Bill } from '@/types/bill'

import EmptyState from '@/components/ui/EmptyState.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import Pagination from '@/components/ui/Pagination.vue'

const router = useRouter()
const toast = useToast()

// ==== 筛选 ====
const filters = [
  { key: 'all', label: '全部' },
  { key: 'week', label: '近 7 天' },
  { key: 'month30', label: '近 30 天' },
  { key: 'month', label: '本月' }
]
const activeFilter = ref('all')
const searchKeyword = ref('')

// ==== 列表数据 ====
const bills = ref<Bill[]>([])
const page = ref(1)
const total = ref(0)
const pageSize = 20
const loading = ref(false)
const error = ref<string | null>(null)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const groups = computed(() => groupBillsByDate(bills.value))

// ==== 批量管理 ====
const batchMode = ref(false)
const selectedIds = ref(new Set<number>())

function toggleBatchMode() {
  batchMode.value = !batchMode.value
  selectedIds.value = new Set()
}
function toggleSelect(id: number) {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id); else s.add(id)
  selectedIds.value = s
}

// ==== 删除 ====
const showDeleteDialog = ref(false)
const deletingIds = ref<number[]>([])
const deleteDialogTitle = ref('')

function confirmSingleDelete(id: number) {
  deletingIds.value = [id]; deleteDialogTitle.value = '确认删除这笔账单？'; showDeleteDialog.value = true
}
function showBatchDeleteDialog() {
  if (selectedIds.value.size === 0) return
  deletingIds.value = Array.from(selectedIds.value); deleteDialogTitle.value = `确定要删除选中的 ${deletingIds.value.length} 笔账单吗？`; showDeleteDialog.value = true
}

async function handleDelete() {
  try {
    if (deletingIds.value.length === 1) {
      await billsApi.deleteBill(deletingIds.value[0])
    } else {
      await billsApi.batchDeleteBills({ ids: deletingIds.value })
    }
    toast.success('删除成功')
    showDeleteDialog.value = false
    if (batchMode.value) toggleBatchMode()
    await fetchBills(true)
  } catch (e: any) { toast.error(e.message || '删除失败') }
}

// ==== 数据 =====
let searchTimer: ReturnType<typeof setTimeout> | null = null

function buildParams() {
  const params: any = { page: page.value, page_size: pageSize }
  const now = new Date()
  if (activeFilter.value === 'week') {
    const d = new Date(); params.start_date = formatDateStr(new Date(d.setDate(d.getDate() - 7))); params.end_date = formatDateStr(now)
  } else if (activeFilter.value === 'month30') {
    const d = new Date(); params.start_date = formatDateStr(new Date(d.setDate(d.getDate() - 30))); params.end_date = formatDateStr(now)
  } else if (activeFilter.value === 'month') {
    params.start_date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`; params.end_date = formatDateStr(now)
  }
  return params
}

async function fetchBills(reset = false) {
  if (loading.value) return
  if (reset) { page.value = 1; bills.value = [] }
  loading.value = true; error.value = null
  try {
    const params = buildParams()
    let result
    if (searchKeyword.value.trim()) {
      result = await billsApi.searchBills({ keyword: searchKeyword.value.trim(), page: page.value, page_size: pageSize })
    } else {
      result = await billsApi.getBills(params)
    }
    if (reset) bills.value = result.items; else bills.value.push(...result.items)
    total.value = result.total; page.value++
  } catch (e: any) { error.value = e.message || '加载失败' }
  finally { loading.value = false }
}

function applyFilter(key: string) { activeFilter.value = key; fetchBills(true) }
function onSearchInput() { if (searchTimer) clearTimeout(searchTimer); searchTimer = setTimeout(() => fetchBills(true), 500) }
function goToPage(p: number) { page.value = p; fetchBills(true); window.scrollTo({ top: 0, behavior: 'auto' }) }
function formatDateStr(d: Date) { return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` }

onMounted(() => fetchBills(true))
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-lg); }
.page-title { font-size: 22px; font-weight: 700; }

/* 筛选 */
.filter-bar { display: flex; gap: var(--space-sm); margin-bottom: var(--space-lg); flex-wrap: wrap; align-items: center; }
.filter-pill { padding: 7px 14px; border-radius: 999px; border: 1px solid var(--border); background: transparent; color: var(--text-secondary); font-size: 13px; font-weight: 500; cursor: pointer; }
.filter-pill:hover { border-color: var(--color-primary); color: var(--color-primary); }
.filter-pill.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.filter-spacer { flex: 1; }
.search-input { padding: 8px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg-card); font-size: 14px; width: 200px; color: var(--text-primary); font-family: inherit; }
.search-input:focus { outline: none; border-color: var(--color-primary); }
.search-input::placeholder { color: var(--text-disabled); }

/* 批量栏 */
.batch-bar { display: flex; align-items: center; gap: var(--space-md); padding: 10px var(--space-md); background: var(--color-primary-light); border-radius: var(--radius-sm); margin-bottom: var(--space-md); }
.batch-count { font-size: 14px; font-weight: 500; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 9px 18px; border-radius: var(--radius-sm); border: 1px solid transparent; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-danger { background: var(--color-warning); color: #fff; border-color: var(--color-warning); }
.btn-ghost { background: transparent; color: var(--text-primary); border-color: var(--border); }
.btn-ghost:hover { border-color: var(--text-primary); }

/* 日分组 */
.day-group { margin-bottom: var(--space-xl); }
.day-header { display: flex; justify-content: space-between; align-items: baseline; padding-bottom: var(--space-sm); margin-bottom: var(--space-sm); border-bottom: 1px solid var(--border); }
.day-label { font-size: 15px; font-weight: 600; }
.day-summary { font-size: 13px; }
.sum-out { color: var(--color-primary); font-family: ui-monospace, monospace; }
.sum-in { color: var(--color-income); font-family: ui-monospace, monospace; }

/* 账单行 */
.bill-item { display: flex; align-items: center; gap: var(--space-sm); padding: 12px var(--space-sm); border-radius: var(--radius-sm); }
.bill-item:hover { background: var(--bg-hover); }
.bill-checkbox { width: 18px; height: 18px; accent-color: var(--color-primary); flex-shrink: 0; }
.bill-cat-icon { font-size: 24px; width: 36px; text-align: center; flex-shrink: 0; }
.bill-info { flex: 1; min-width: 0; }
.bill-cat-name { font-size: 14px; font-weight: 500; }
.bill-meta { font-size: 12px; color: var(--text-secondary); }
.bill-note { font-size: 13px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bill-amount { font-family: ui-monospace, monospace; font-weight: 600; font-size: 16px; white-space: nowrap; }
.bill-amount.expense { color: var(--color-primary); }
.bill-amount.income { color: var(--color-income); }
.bill-actions { display: flex; gap: 4px; }
.bill-action-btn { width: 32px; height: 32px; border-radius: var(--radius-sm); border: none; background: transparent; color: var(--text-secondary); display: grid; place-items: center; font-size: 16px; cursor: pointer; }
.bill-action-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
.bill-action-btn.danger:hover { color: var(--color-warning); }

@media (max-width: 640px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: var(--space-sm); }
  .filter-pill { padding: 6px 10px; font-size: 12px; }
  .bill-item { padding: 10px 4px; }
}
</style>
