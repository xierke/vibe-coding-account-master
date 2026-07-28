/**
 * 账单 API 模块
 * 对应后端 /v1/bills/* 路由
 */

import apiClient from './index'
import type { ApiResponse, PaginatedData } from '@/types/api'
import type {
  Bill,
  BillCreateRequest,
  BillUpdateRequest,
  BatchDeleteRequest,
  BillQueryParams,
  BillSearchParams
} from '@/types/bill'

/** 记一笔 — 创建账单 */
export function createBill(data: BillCreateRequest): Promise<Bill> {
  return apiClient.post('/bills', data)
}

/** 账单列表（分页 + 多条件筛选） */
export function getBills(params: BillQueryParams): Promise<PaginatedData<Bill>> {
  return apiClient.get('/bills', { params })
}

/** 搜索账单 */
export function searchBills(params: BillSearchParams): Promise<PaginatedData<Bill>> {
  return apiClient.get('/bills/search', { params })
}

/** 获取单条账单详情 */
export function getBillById(id: number): Promise<Bill> {
  return apiClient.get(`/bills/${id}`)
}

/** 编辑账单 */
export function updateBill(id: number, data: BillUpdateRequest): Promise<Bill> {
  return apiClient.put(`/bills/${id}`, data)
}

/** 删除单条账单 */
export function deleteBill(id: number): Promise<null> {
  return apiClient.delete(`/bills/${id}`)
}

/** 批量删除账单 */
export function batchDeleteBills(data: BatchDeleteRequest): Promise<null> {
  return apiClient.post('/bills/batch-delete', data)
}
