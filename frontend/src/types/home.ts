// ===== 首页 Dashboard 类型 =====
// 与后端 schemas/user.py HomeDashboardResponse 对齐

/** 最近账单条目（Dashboard 精简版） */
export interface RecentBillItem {
  id: number
  type: string
  amount: number
  category_name: string
  category_icon: string
  category_color: string
  bill_date: string
  note: string
}

/** 首页 Dashboard 数据 */
export interface HomeDashboard {
  month_income: number
  month_expense: number
  month_balance: number
  today_bill_count: number
  today_expense: number
  budget_total: number | null
  budget_spent: number
  budget_usage_rate: number
  budget_warning: boolean
  recent_bills: RecentBillItem[]
}
