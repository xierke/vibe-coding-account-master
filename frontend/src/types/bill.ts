// ===== 账单相关类型 =====
// 与后端 schemas/bill.py 对齐

/** 账单类型 */
export type BillType = 'income' | 'expense'

/** 分类简要信息（内嵌在账单响应中） */
export interface CategoryBrief {
  id: number
  name: string
  icon: string
  color: string
}

/** 账单记录 */
export interface Bill {
  id: number
  type: BillType
  amount: number
  category: CategoryBrief | null
  bill_date: string       // YYYY-MM-DD
  note: string | null
  created_at: string      // ISO datetime
  updated_at: string
}

/** 创建账单请求 */
export interface BillCreateRequest {
  type: BillType
  amount: number         // 0.01 ~ 999999999.99
  category_id: number
  bill_date?: string     // 不传默认当天
  note?: string          // 最多 200 字
}

/** 编辑账单请求（所有字段可选） */
export interface BillUpdateRequest {
  type?: BillType
  amount?: number
  category_id?: number
  bill_date?: string
  note?: string
}

/** 批量删除请求 */
export interface BatchDeleteRequest {
  ids: number[]
}

/** 账单列表查询参数 */
export interface BillQueryParams {
  page?: number
  page_size?: number
  type?: BillType
  category_id?: number
  start_date?: string
  end_date?: string
}

/** 账单搜索参数 */
export interface BillSearchParams {
  keyword?: string
  page?: number
  page_size?: number
}

/** 按日期分组的账单分组 */
export interface BillGroup {
  date: string           // YYYY-MM-DD
  dayLabel: string       // "今天" / "昨天" / "07月28日 周一"
  bills: Bill[]
  dayIncome: number
  dayExpense: number
}
