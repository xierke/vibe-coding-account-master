/**
 * 认证 API 模块
 * 对应后端 /v1/auth/* 路由
 */

import apiClient from './index'
import type {
  LoginRequest,
  RegisterRequest,
  SmsLoginRequest,
  RefreshRequest,
  SendCodeRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
  TokenResponse
} from '@/types/auth'

/** 邮箱注册 */
export function register(data: RegisterRequest): Promise<TokenResponse> {
  return apiClient.post('/auth/register', data)
}

/** 密码登录 */
export function login(data: LoginRequest): Promise<TokenResponse> {
  return apiClient.post('/auth/login', data)
}

/** 短信验证码登录 */
export function loginBySms(data: SmsLoginRequest): Promise<TokenResponse> {
  return apiClient.post('/auth/login/sms', data)
}

/** 刷新 Token */
export function refreshToken(data: RefreshRequest): Promise<{ access_token: string; refresh_token: string; token_type: string }> {
  return apiClient.post('/auth/refresh', data)
}

/** 发送验证码（邮箱或短信） */
export function sendCode(data: SendCodeRequest): Promise<null> {
  return apiClient.post('/auth/send-code', data)
}

/** 重置密码（通过邮箱验证码） */
export function resetPassword(data: ResetPasswordRequest): Promise<null> {
  return apiClient.post('/auth/reset-password', data)
}

/** 已登录用户修改密码 */
export function changePassword(data: ChangePasswordRequest): Promise<null> {
  return apiClient.put('/auth/password', data)
}
