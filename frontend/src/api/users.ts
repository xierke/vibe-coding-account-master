/**
 * 用户信息 API 模块
 * 对应后端 /v1/users/* 路由
 */

import apiClient from './index'
import type { UserProfile, UpdateProfileRequest } from '@/types/auth'

/** 获取当前登录用户的个人信息 */
export function getUserProfile(): Promise<UserProfile> {
  return apiClient.get('/users/profile')
}

/** 更新个人信息（用户名、头像） */
export function updateUserProfile(data: UpdateProfileRequest): Promise<UserProfile> {
  return apiClient.put('/users/profile', data)
}
