<!--
  BillDetailView.vue — 账单详情 / 编辑页

  支持两个模式：
  - 查看模式：显示账单所有字段（只读）
  - 编辑模式：可编辑所有字段，保存后返回
-->
<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <PageHeader :title="isEditing ? '编辑账单' : '账单详情'" show-back>
      <template #actions>
        <button
          v-if="!isEditing"
          class="btn btn-secondary btn-sm"
          @click="enterEditMode"
        >
          编辑
        </button>
      </template>
    </PageHeader>

    <!-- 加载状态 -->
    <LoadingState v-if="loading" text="加载中..." />

    <!-- 错误状态 -->
    <ErrorState
      v-else-if="error"
      :description="error"
      show-retry
      @retry="fetchBill"
    />

    <!-- 账单内容 -->
    <div v-if="bill" class="card detail-card">
      <!-- 查看模式 -->
      <template v-if="!isEditing">
        <div class="detail-header">
          <div
            class="detail-category-icon"
            :style="{ backgroundColor: (bill.category?.color || '#B0A090') + '26' }"
          >
            {{ bill.category?.icon || '📌' }}
          </div>
          <div class="detail-header-info">
            <h3 class="detail-category-name">{{ bill.category?.name || '未知分类' }}</h3>
            <p class="detail-type">{{ bill.type === 'income' ? '收入' : '支出' }}</p>
          </div>
          <div class="detail-amount-side">
            <span class="detail-amount" :class="bill.type === 'income' ? 'text-income' : 'text-expense'">
              {{ bill.type === 'income' ? '+' : '-' }}{{ formatMoney(bill.amount, false) }}
            </span>
          </div>
        </div>

        <div class="detail-divider" />

        <div class="detail-fields-view">
          <div class="detail-field-row">
            <span class="field-label">日期</span>
            <span class="field-value">{{ bill.bill_date }}</span>
          </div>
          <div class="detail-field-row">
            <span class="field-label">备注</span>
            <span class="field-value">{{ bill.note || '无' }}</span>
          </div>
          <div class="detail-field-row">
            <span class="field-label">创建时间</span>
            <span class="field-value">{{ formatDateTime(bill.created_at) }}</span>
          </div>
        </div>

        <div class="detail-divider" />

        <div class="detail-actions-bottom">
          <button class="btn btn-secondary" @click="enterEditMode">
            编辑
          </button>
          <button class="btn btn-danger" @click="confirmDeleteBill">
            删除
          </button>
        </div>
      </template>

      <!-- 编辑模式 -->
      <template v-if="isEditing">
        <!-- 类型切换 -->
        <div class="form-row">
          <label class="form-label">类型</label>
          <TypeToggle v-model="editForm.type" />
        </div>

        <!-- 金额 -->
        <div class="form-row">
          <label class="form-label">金额</label>
          <AmountInput v-model="editForm.amount" />
        </div>

        <!-- 分类 -->
        <div class="form-row">
          <label class="form-label">分类</label>
          <div class="category-grid">
            <CategoryIcon
              v-for="cat in editCategories"
              :key="cat.id"
              :category="cat"
              :selected="editForm.categoryId === cat.id"
              @select="editForm.categoryId = cat.id"
            />
          </div>
        </div>

        <!-- 日期 -->
        <div class="form-row">
          <label class="form-label">日期</label>
          <input v-model="editForm.date" type="date" class="form-input" />
        </div>

        <!-- 备注 -->
        <div class="form-row">
          <label class="form-label">备注（选填）</label>
          <input v-model="editForm.note" type="text" class="form-input" placeholder="请输入备注..." maxlength="200" />
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button class="btn btn-secondary" @click="cancelEdit">取消</button>
          <button class="btn btn-primary" :disabled="saving" @click="saveEdit">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </template>
    </div>

    <!-- 删除确认弹窗 -->
    <ConfirmDialog
      :visible="showDeleteDialog"
      title="确认删除该账单？"
      description="删除后数据不可恢复"
      confirm-text="确认删除"
      cancel-text="取消"
      @confirm="handleDelete"
      @cancel="showDeleteDialog = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useCategoryStore } from '@/stores/categories'
import * as billsApi from '@/api/bills'
import { formatMoney, formatDate, formatTime } from '@/utils/format'
import type { Bill, BillType } from '@/types/bill'

import PageHeader from '@/components/ui/PageHeader.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import TypeToggle from '@/components/ui/TypeToggle.vue'
import AmountInput from '@/components/ui/AmountInput.vue'
import CategoryIcon from '@/components/ui/CategoryIcon.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const categoryStore = useCategoryStore()

// ===== 数据 =====
const bill = ref<Bill | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// ===== 编辑态 =====
const isEditing = ref(false)
const saving = ref(false)
const editForm = reactive({
  type: 'expense' as BillType,
  amount: null as number | null,
  categoryId: null as number | null,
  date: formatDate(new Date()),
  note: ''
})

/** 编辑模式下的分类列表 */
const editCategories = computed(() => {
  return editForm.type === 'expense'
    ? categoryStore.expenseCategories
    : categoryStore.incomeCategories
})

// ===== 删除 =====
const showDeleteDialog = ref(false)

// ===== 方法 =====

/** 获取账单详情 */
async function fetchBill() {
  const id = Number(route.params.id)
  if (!id) {
    error.value = '无效的账单 ID'
    return
  }

  loading.value = true
  error.value = null

  try {
    bill.value = await billsApi.getBillById(id)
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

/** 进入编辑模式 */
function enterEditMode() {
  if (!bill.value) return
  editForm.type = bill.value.type
  editForm.amount = bill.value.amount
  editForm.categoryId = bill.value.category?.id || null
  editForm.date = bill.value.bill_date
  editForm.note = bill.value.note || ''
  isEditing.value = true
}

/** 取消编辑 */
function cancelEdit() {
  isEditing.value = false
  // 重新加载最新数据
  fetchBill()
}

/** 保存编辑 */
async function saveEdit() {
  if (!bill.value || saving.value) return
  if (!editForm.amount || editForm.amount <= 0) {
    toast.error('请输入有效金额')
    return
  }
  if (!editForm.categoryId) {
    toast.error('请选择分类')
    return
  }

  saving.value = true
  try {
    const updated = await billsApi.updateBill(bill.value.id, {
      type: editForm.type,
      amount: editForm.amount,
      category_id: editForm.categoryId,
      bill_date: editForm.date,
      note: editForm.note.trim() || undefined
    })
    bill.value = updated
    isEditing.value = false
    toast.success('保存成功')
  } catch (e: any) {
    toast.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

/** 弹出删除确认 */
function confirmDeleteBill() {
  showDeleteDialog.value = true
}

/** 执行删除 */
async function handleDelete() {
  if (!bill.value) return
  try {
    await billsApi.deleteBill(bill.value.id)
    toast.success('删除成功')
    showDeleteDialog.value = false
    router.replace('/bills')
  } catch (e: any) {
    toast.error(e.message || '删除失败')
  }
}

/** 格式化日期时间 */
function formatDateTime(iso: string): string {
  const d = new Date(iso)
  return `${formatDate(d)} ${formatTime(iso)}`
}

// ===== 初始化 =====
onMounted(async () => {
  await categoryStore.fetchCategories()
  fetchBill()
})
</script>

<style scoped>
.detail-card {
  padding: 24px;
  max-width: 600px;
}

/* 查看模式 */
.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-category-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.detail-header-info {
  flex: 1;
}

.detail-category-name {
  font-size: var(--font-xl);
  color: var(--text-primary);
}

.detail-type {
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.detail-amount-side {
  flex-shrink: 0;
}

.detail-amount {
  font-size: var(--font-2xl);
  font-weight: 700;
}

.detail-divider {
  height: 1px;
  background: var(--border);
  margin: 20px 0;
}

.detail-fields-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-field-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.field-label {
  font-size: var(--font-base);
  color: var(--text-secondary);
}

.field-value {
  font-size: var(--font-base);
  color: var(--text-primary);
}

.detail-actions-bottom {
  display: flex;
  gap: 12px;
}

.detail-actions-bottom .btn {
  flex: 1;
}

/* 编辑模式 */
.form-row {
  margin-bottom: 20px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  max-width: 400px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.form-actions .btn {
  flex: 1;
}

.btn-sm {
  height: 36px;
  padding: 6px 16px;
  font-size: var(--font-sm);
}

@media (max-width: 767px) {
  .detail-card {
    padding: 16px;
  }

  .detail-amount {
    font-size: var(--font-xl);
  }

  .category-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
}
</style>
