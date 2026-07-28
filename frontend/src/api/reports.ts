/**
 * 报表 API 模块
 * 对应后端 /v1/reports/* 路由
 */

import apiClient from './index'
import type { WeeklyReport, MonthlyReport, CustomReport } from '@/types/report'

/** 获取周报表 */
export function getWeeklyReport(date: string): Promise<WeeklyReport> {
  return apiClient.get('/reports/weekly', { params: { date } })
}

/** 获取月报表 */
export function getMonthlyReport(month: string): Promise<MonthlyReport> {
  return apiClient.get('/reports/monthly', { params: { month } })
}

/** 获取自定义时间范围报表 */
export function getCustomReport(startDate: string, endDate: string): Promise<CustomReport> {
  return apiClient.get('/reports/custom', { params: { start_date: startDate, end_date: endDate } })
}
