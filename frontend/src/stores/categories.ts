/**
 * 分类状态管理 (Pinia Store)
 *
 * 管理分类列表的获取和缓存。
 * 分类数据相对稳定，在应用生命周期内缓存。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as categoriesApi from '@/api/categories'
import type { Category, CategoryCreateRequest, CategoryUpdateRequest } from '@/types/category'

export const useCategoryStore = defineStore('categories', () => {
  // ===== 状态 =====
  const expenseCategories = ref<Category[]>([])
  const incomeCategories = ref<Category[]>([])
  const loading = ref(false)

  // ===== 计算属性 =====
  /** 所有分类的扁平列表 */
  const allCategories = computed(() => [
    ...expenseCategories.value,
    ...incomeCategories.value
  ])

  /** 按分类 ID 查找 */
  function getCategoryById(id: number): Category | undefined {
    return allCategories.value.find(c => c.id === id)
  }

  // ===== 操作方法 =====

  /** 获取分类列表 */
  async function fetchCategories(type?: 'income' | 'expense') {
    loading.value = true
    try {
      if (!type || type === 'expense') {
        expenseCategories.value = await categoriesApi.getCategories('expense')
      }
      if (!type || type === 'income') {
        incomeCategories.value = await categoriesApi.getCategories('income')
      }
    } finally {
      loading.value = false
    }
  }

  /** 创建自定义分类 */
  async function createCategory(data: CategoryCreateRequest): Promise<Category> {
    const category = await categoriesApi.createCategory(data)
    // 创建成功后刷新对应类型的分类列表
    await fetchCategories(data.type)
    return category
  }

  /** 编辑分类 */
  async function updateCategory(id: number, data: CategoryUpdateRequest): Promise<Category> {
    const category = await categoriesApi.updateCategory(id, data)
    // 刷新分类列表以获取最新数据
    await fetchCategories()
    return category
  }

  /** 删除分类 */
  async function deleteCategory(id: number) {
    await categoriesApi.deleteCategory(id)
    // 刷新分类列表
    await fetchCategories()
  }

  return {
    // 状态
    expenseCategories,
    incomeCategories,
    loading,
    // 计算属性
    allCategories,
    // 方法
    getCategoryById,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory
  }
})
