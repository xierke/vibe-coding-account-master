/**
 * 预算 API 模块
 * 对应后端 /v1/budgets 路由
 */

import apiClient from './index'
import type { BudgetData, BudgetUpdateRequest } from '@/types/budget'

/** 获取指定月份的预算（含执行情况） */
export function getBudgets(month: string): Promise<BudgetData> {
  return apiClient.get('/budgets', { params: { month } })
}

/** 设置/更新月度预算 */
export function setBudgets(data: BudgetUpdateRequest): Promise<BudgetData> {
  return apiClient.put('/budgets', data)
}
