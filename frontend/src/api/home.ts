/**
 * 首页 Dashboard API 模块
 * 对应后端 /v1/home 路由
 */

import apiClient from './index'
import type { HomeDashboard } from '@/types/home'

/** 获取首页 Dashboard 数据（含 Redis 缓存） */
export function getHomeDashboard(): Promise<HomeDashboard> {
  return apiClient.get('/home')
}
