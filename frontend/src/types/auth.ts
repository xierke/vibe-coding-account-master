// ===== 认证相关类型 =====
// 与后端 schemas/auth.py 对齐

/** 密码登录请求 */
export interface LoginRequest {
  account: string        // 用户名或邮箱
  password: string
  remember_me?: boolean
}

/** 邮箱注册请求 */
export interface RegisterRequest {
  username: string       // 2-20 字符
  email: string
  password: string       // 8-20 位，须含字母+数字
  confirm_password: string
}

/** 短信登录请求 */
export interface SmsLoginRequest {
  phone: string        // 11 位中国大陆手机号
  code: string         // 6 位验证码
}

/** Token 刷新请求 */
export interface RefreshRequest {
  refresh_token: string
}

/** 发送验证码请求 */
export interface SendCodeRequest {
  type: 'email' | 'sms'
  target: string       // 邮箱地址或手机号
}

/** 重置密码请求 */
export interface ResetPasswordRequest {
  email: string
  code: string         // 6 位验证码
  new_password: string
  confirm_password: string
}

/** 修改密码请求（已登录） */
export interface ChangePasswordRequest {
  old_password: string
  new_password: string
  confirm_password: string
}

/** Token 响应（登录/注册/刷新 共用） */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user_id: number
  username: string
}

/** 用户个人信息 */
export interface UserProfile {
  id: number
  username: string
  email: string
  phone: string | null
  avatar_url: string | null
  created_at: string
}

/** 更新个人信息请求 */
export interface UpdateProfileRequest {
  username?: string    // 2-20 字符，须唯一
  avatar_url?: string
}
