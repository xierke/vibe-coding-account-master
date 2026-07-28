/**
 * 分类 API 模块
 * 对应后端 /v1/categories/* 路由
 */

import apiClient from './index'
import type { Category, CategoryCreateRequest, CategoryUpdateRequest } from '@/types/category'

/** 获取分类列表（可选按类型筛选） */
export function getCategories(type?: 'income' | 'expense'): Promise<Category[]> {
  return apiClient.get('/categories', { params: type ? { type } : {} })
}

/** 创建用户自定义分类 */
export function createCategory(data: CategoryCreateRequest): Promise<Category> {
  return apiClient.post('/categories', data)
}

/** 编辑分类 */
export function updateCategory(id: number, data: CategoryUpdateRequest): Promise<Category> {
  return apiClient.put(`/categories/${id}`, data)
}

/** 删除分类（系统默认或有关联账单的分类不可删除） */
export function deleteCategory(id: number): Promise<null> {
  return apiClient.delete(`/categories/${id}`)
}
