// ===== 分类相关类型 =====
// 与后端 schemas/category.py 对齐

/** 分类类型 */
export type CategoryType = 'income' | 'expense'

/** 分类记录 */
export interface Category {
  id: number
  name: string           // 最多 30 字符
  icon: string           // emoji
  color: string          // #RRGGBB
  type: CategoryType
  is_default: boolean
  sort_order: number
  bill_count: number     // 该分类下的账单数量
}

/** 创建分类请求 */
export interface CategoryCreateRequest {
  name: string
  icon: string
  color: string          // #RRGGBB
  type: CategoryType
  sort_order?: number
}

/** 编辑分类请求（所有字段可选） */
export interface CategoryUpdateRequest {
  name?: string
  icon?: string
  color?: string
  sort_order?: number
}
