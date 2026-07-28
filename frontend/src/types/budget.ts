// ===== 预算相关类型 =====
// 与后端 schemas/budget.py 对齐

/** 预算项（含执行情况） */
export interface BudgetItem {
  category_id: number | null   // null = 总预算
  category_name: string
  amount: number
  spent: number
  usage_rate: number           // 0.0 ~ 1.0+（超支可超过 1.0）
}

/** 预算数据 */
export interface BudgetData {
  month: string
  total_budget: BudgetItem | null
  category_budgets: BudgetItem[]
}

/** 设置/更新预算请求 */
export interface BudgetUpdateRequest {
  month: string                // YYYY-MM
  total_budget?: number | null
  category_budgets?: CategoryBudgetItem[]
}

export interface CategoryBudgetItem {
  category_id: number
  amount: number
}
