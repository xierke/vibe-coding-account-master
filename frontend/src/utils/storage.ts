/**
 * localStorage 封装
 * 管理 JWT Token 的本地持久化存储
 */

const ACCESS_TOKEN_KEY = 'dailytracker_access_token'
const REFRESH_TOKEN_KEY = 'dailytracker_refresh_token'

/** 获取 access_token */
export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

/** 设置 access_token */
export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

/** 获取 refresh_token */
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

/** 设置 refresh_token */
export function setRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token)
}

/** 保存 Token 对（登录/刷新后调用） */
export function saveTokens(accessToken: string, refreshToken: string): void {
  setAccessToken(accessToken)
  setRefreshToken(refreshToken)
}

/** 清除所有 Token（登出时调用） */
export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

/** 检查是否有有效的 Token */
export function hasToken(): boolean {
  return !!getAccessToken()
}
