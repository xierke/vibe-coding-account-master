// ===== API 通用类型定义 =====
// 与后端 FastAPI schemas/common.py 对齐

/** 统一 API 响应外层包装 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/** 分页数据 */
export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
