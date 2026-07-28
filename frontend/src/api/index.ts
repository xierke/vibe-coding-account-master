/**
 * Axios 实例 + 请求/响应拦截器
 *
 * 核心功能：
 * 1. 请求拦截：自动附加 Authorization Bearer Token
 * 2. 响应拦截：统一处理业务错误 + Token 过期自动刷新
 * 3. Token 刷新使用队列机制，防止并发请求同时刷新
 */

import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { getAccessToken, getRefreshToken, saveTokens, clearTokens } from '@/utils/storage'

// ===== 创建 Axios 实例 =====
const apiClient: AxiosInstance = axios.create({
  baseURL: '/v1',   // Vite 代理到后端
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json; charset=utf-8'
  }
})

// ===== Token 刷新队列机制 =====
// 防止多个并发请求同时触发 Token 刷新
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: Error) => void
}> = []

/** 处理刷新队列：全部 resolve 或全部 reject */
function processQueue(error: Error | null, token: string | null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else if (token) {
      resolve(token)
    }
  })
  failedQueue = []
}

// ===== 请求拦截器 =====
// 自动附加 access_token 到请求头
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken()
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ===== 响应拦截器 =====
// 统一处理：成功解包 -> 401 刷新 Token -> 其他错误
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 成功响应：code === 0 时直接返回 data
    const { data } = response
    if (data.code === 0) {
      return data.data
    }
    // 业务错误：返回 rejected Promise
    const errorMsg = data.message || '请求失败'
    return Promise.reject(new Error(errorMsg))
  },
  async (error: AxiosError) => {
    // 网络错误（无响应）
    if (!error.response) {
      return Promise.reject(new Error('网络连接异常，请检查网络'))
    }

    const { status, data } = error.response
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // HTTP 401 — Token 可能已过期，尝试刷新
    if (status === 401 && !originalRequest._retry) {
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        // 无 refresh_token，直接登出
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(new Error('登录已过期，请重新登录'))
      }

      // 如果正在刷新中，将当前请求加入等待队列
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (newToken: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${newToken}`
              }
              resolve(apiClient(originalRequest))
            },
            reject
          })
        })
      }

      // 开始刷新 Token
      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshResponse = await axios.post('/v1/auth/refresh', {
          refresh_token: refreshToken
        })
        const { access_token, refresh_token } = refreshResponse.data.data
        saveTokens(access_token, refresh_token)

        // 重试队列中的请求
        processQueue(null, access_token)

        // 重试当前请求
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        return apiClient(originalRequest)
      } catch (refreshError) {
        // 刷新失败：清空 Token，跳转登录页
        processQueue(new Error('Token 刷新失败'), null)
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(new Error('登录已过期，请重新登录'))
      } finally {
        isRefreshing = false
      }
    }

    // HTTP 422 — 后端参数校验错误
    if (status === 422) {
      const message = (data as any)?.detail || (data as any)?.message || '参数错误'
      return Promise.reject(new Error(message))
    }

    // HTTP 5xx — 服务器错误
    if (status >= 500) {
      return Promise.reject(new Error('服务器繁忙，请稍后重试'))
    }

    // 其他 HTTP 错误
    const errorMessage = (data as any)?.message || (data as any)?.detail || '请求失败'
    return Promise.reject(new Error(errorMessage))
  }
)

export default apiClient
