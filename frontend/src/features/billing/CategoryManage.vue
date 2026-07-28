<!--
  CategoryManage.vue — 分类管理页

  功能：
  - 支出/收入分类切换
  - 分类列表（含账单数量徽章）
  - 添加/编辑分类（Modal 弹窗）
  - 删除自定义分类（系统默认不可删除）
-->
<template>
  <div class="page-container">
    <PageHeader title="分类管理">
      <template #actions>
        <button class="btn btn-primary btn-sm" @click="openAddModal">
          添加分类
        </button>
      </template>
    </PageHeader>

    <!-- 类型切换 -->
    <div class="type-section">
      <TypeToggle v-model="activeType" />
    </div>

    <!-- 加载中 -->
    <LoadingState v-if="categoryStore.loading" text="加载中..." />

    <!-- 分类列表 -->
    <div v-else class="category-list card">
      <div
        v-for="cat in currentCategories"
        :key="cat.id"
        class="category-row"
      >
        <div
          class="category-row-icon"
          :style="{ backgroundColor: cat.color + '26' }"
        >
          {{ cat.icon }}
        </div>
        <div class="category-row-info">
          <span class="category-row-name">{{ cat.name }}</span>
          <span class="category-row-meta">
            {{ cat.bill_count }} 笔账单
            <span v-if="cat.is_default" class="badge-default">系统默认</span>
          </span>
        </div>
        <div class="category-row-actions">
          <button class="btn-text" @click="openEditModal(cat)">编辑</button>
          <button
            v-if="!cat.is_default"
            class="btn-text text-danger"
            :disabled="cat.bill_count > 0"
            :title="cat.bill_count > 0 ? `该分类下有 ${cat.bill_count} 笔账单，无法删除` : '删除'"
            @click="confirmDeleteCategory(cat)"
          >
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑 Modal -->
    <Modal
      :visible="showModal"
      :title="isEditing ? '编辑分类' : '添加分类'"
      show-close
      @close="closeModal"
    >
      <div class="modal-form">
        <div class="form-group">
          <label class="form-label">名称</label>
          <input
            v-model="form.name"
            type="text"
            class="form-input"
            placeholder="分类名称"
            maxlength="30"
          />
        </div>
        <div class="form-group">
          <label class="form-label">图标（Emoji）</label>
          <div class="emoji-picker">
            <button
              v-for="emoji in emojiOptions"
              :key="emoji"
              type="button"
              class="emoji-option"
              :class="{ 'emoji-selected': form.icon === emoji }"
              @click="form.icon = emoji"
            >
              {{ emoji }}
            </button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">颜色</label>
          <input v-model="form.color" type="color" class="color-input" />
        </div>
        <div v-if="!isEditing" class="form-group">
          <label class="form-label">类型</label>
          <TypeToggle v-model="form.type" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closeModal">取消</button>
          <button class="btn btn-primary" :disabled="submitting" @click="handleSave">
            {{ submitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </Modal>

    <!-- 删除确认 -->
    <ConfirmDialog
      :visible="showDeleteDialog"
      :title="`确认删除分类「${deletingCat?.name}」？`"
      description="删除后不可恢复"
      confirm-text="确认删除"
      cancel-text="取消"
      @confirm="handleDelete"
      @cancel="showDeleteDialog = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useCategoryStore } from '@/stores/categories'
import type { Category, CategoryType } from '@/types/category'

import PageHeader from '@/components/ui/PageHeader.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import Modal from '@/components/ui/Modal.vue'
import TypeToggle from '@/components/ui/TypeToggle.vue'

const toast = useToast()
const categoryStore = useCategoryStore()

// ===== 类型切换 =====
const activeType = ref<CategoryType>('expense')

/** 当前类型的分类列表 */
const currentCategories = computed(() => {
  return activeType.value === 'expense'
    ? categoryStore.expenseCategories
    : categoryStore.incomeCategories
})

// ===== Modal =====
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)

const form = reactive({
  name: '',
  icon: '📌',
  color: '#E07B5A',
  type: 'expense' as CategoryType
})

/** 常用 Emoji 列表 */
const emojiOptions = [
  '🍽️', '🚗', '🛒', '🏠', '🎮', '💊', '📚', '📌',
  '💰', '💼', '📈', '🧧', '🐱', '🐶', '✈️', '🎓',
  '💻', '📱', '🎂', '🎁', '🏥', '🎬', '🎵', '☕',
  '🍺', '👗', '💄', '🏋️', '🚇', '⛽', '📦', '🔧'
]

/** 打开添加弹窗 */
function openAddModal() {
  isEditing.value = false
  editingId.value = null
  form.name = ''
  form.icon = '📌'
  form.color = '#E07B5A'
  form.type = activeType.value
  showModal.value = true
}

/** 打开编辑弹窗 */
function openEditModal(cat: Category) {
  isEditing.value = true
  editingId.value = cat.id
  form.name = cat.name
  form.icon = cat.icon
  form.color = cat.color
  form.type = cat.type
  showModal.value = true
}

/** 关闭弹窗 */
function closeModal() {
  showModal.value = false
}

/** 保存分类 */
async function handleSave() {
  if (!form.name.trim()) {
    toast.error('请输入分类名称')
    return
  }

  submitting.value = true
  try {
    if (isEditing.value && editingId.value) {
      await categoryStore.updateCategory(editingId.value, {
        name: form.name.trim(),
        icon: form.icon,
        color: form.color,
        sort_order: 0
      })
      toast.success('编辑成功')
    } else {
      await categoryStore.createCategory({
        name: form.name.trim(),
        icon: form.icon,
        color: form.color,
        type: form.type
      })
      toast.success('添加成功')
    }
    closeModal()
  } catch (e: any) {
    toast.error(e.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// ===== 删除 =====
const showDeleteDialog = ref(false)
const deletingCat = ref<Category | null>(null)

function confirmDeleteCategory(cat: Category) {
  if (cat.bill_count > 0) {
    toast.error(`该分类下有 ${cat.bill_count} 笔账单，无法删除`)
    return
  }
  deletingCat.value = cat
  showDeleteDialog.value = true
}

async function handleDelete() {
  if (!deletingCat.value) return

  try {
    await categoryStore.deleteCategory(deletingCat.value.id)
    toast.success('删除成功')
    showDeleteDialog.value = false
    deletingCat.value = null
  } catch (e: any) {
    toast.error(e.message || '删除失败')
  }
}

// ===== 初始化 =====
onMounted(() => {
  categoryStore.fetchCategories()
})
</script>

<style scoped>
.type-section {
  margin-bottom: 16px;
}

.category-list {
  overflow: hidden;
}

.category-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}

.category-row:last-child {
  border-bottom: none;
}

.category-row-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.category-row-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.category-row-name {
  font-size: var(--font-md);
  color: var(--text-primary);
}

.category-row-meta {
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.badge-default {
  display: inline-block;
  padding: 1px 6px;
  font-size: var(--font-xs);
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: 4px;
  margin-left: 6px;
}

.category-row-actions {
  display: flex;
  gap: 4px;
}

/* Modal 表单 */
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.emoji-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.emoji-option {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  border-radius: var(--radius-sm);
  background: var(--bg-page);
  border: 1.5px solid transparent;
  cursor: pointer;
}

.emoji-option:hover {
  background: var(--bg-hover);
}

.emoji-selected {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.color-input {
  width: 80px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  padding: 2px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.modal-actions .btn {
  flex: 1;
}

.btn-sm {
  height: 36px;
  padding: 6px 16px;
  font-size: var(--font-sm);
}
</style>
