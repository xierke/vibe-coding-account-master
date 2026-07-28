/**
 * 认证状态管理 (Pinia Store)
 *
 * 管理：
 * - JWT Token 的存储和读取
 * - 用户登录/注册/登出
 * - Token 刷新
 * - 用户个人信息
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { saveTokens, clearTokens, getAccessToken, getRefreshToken } from '@/utils/storage'
import * as authApi from '@/api/auth'
import * as usersApi from '@/api/users'
import type { UserProfile, LoginRequest, RegisterRequest, TokenResponse } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // ===== 状态 =====
  const user = ref<UserProfile | null>(null)
  const accessToken = ref<string | null>(getAccessToken())
  const refreshToken = ref<string | null>(getRefreshToken())

  // ===== 计算属性 =====
  /** 是否已登录 */
  const isAuthenticated = computed(() => !!accessToken.value)

  /** 当前用户名 */
  const username = computed(() => user.value?.username || '')

  // ===== 操作方法 =====

  /**
   * 保存 Token 到 state 和 localStorage
   */
  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    saveTokens(access, refresh)
  }

  /**
   * 密码登录
   */
  async function login(data: LoginRequest) {
    const response: TokenResponse = await authApi.login(data)
    setTokens(response.access_token, response.refresh_token)
    // 登录后获取用户信息
    await fetchProfile()
  }

  /**
   * 邮箱注册（成功后自动登录）
   */
  async function register(data: RegisterRequest) {
    const response: TokenResponse = await authApi.register(data)
    setTokens(response.access_token, response.refresh_token)
    await fetchProfile()
  }

  /**
   * 获取用户个人信息
   */
  async function fetchProfile() {
    const profile = await usersApi.getUserProfile()
    user.value = profile
  }

  /**
   * 更新个人信息
   */
  async function updateProfile(data: { username?: string; avatar_url?: string }) {
    const profile = await usersApi.updateUserProfile(data)
    user.value = profile
  }

  /**
   * 修改密码
   */
  async function changePassword(oldPassword: string, newPassword: string, confirmPassword: string) {
    await authApi.changePassword({
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  }

  /**
   * 登出：清除 Token 和用户信息
   */
  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    clearTokens()
  }

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    // 计算属性
    isAuthenticated,
    username,
    // 方法
    login,
    register,
    fetchProfile,
    updateProfile,
    changePassword,
    logout
  }
})
