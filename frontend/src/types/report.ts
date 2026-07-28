// ===== 报表相关类型 =====
// 与后端 schemas/report.py 对齐

/** 报表概览数据 */
export interface ReportOverview {
  total_income: number
  total_expense: number
  balance: number
  avg_daily_expense: number
  budget_usage_rate: number | null
}

/** 每日收支汇总 */
export interface DailySummary {
  date: string
  income: number
  expense: number
}

/** 分类饼图数据项 */
export interface CategoryPieItem {
  category_id: number
  category_name: string
  icon: string
  color: string
  amount: number
  percentage: number
}

/** 分类排行数据项 */
export interface CategoryRankItem {
  rank: number
  category_id: number
  category_name: string
  icon: string
  color: string
  amount: number
  percentage: number
}

/** 日历热力图数据项 */
export interface CalendarDay {
  date: string
  day_of_month: number
  day_of_week: number    // 0=周一 ... 6=周日
  amount: number
  intensity: number      // 0.0 ~ 1.0
}

/** 环比数据 */
export interface PeriodComparison {
  prev_income: number
  prev_expense: number
  income_change_pct: number
  expense_change_pct: number
}

/** 周报表数据 */
export interface WeeklyReport {
  week_start: string
  week_end: string
  overview: ReportOverview
  daily_data: DailySummary[]
  category_pie: CategoryPieItem[]
  comparison: PeriodComparison | null
}

/** 月报表数据 */
export interface MonthlyReport {
  month: string
  overview: ReportOverview
  daily_data: DailySummary[]
  category_ranks: CategoryRankItem[]
  calendar_data: CalendarDay[]
  comparison: PeriodComparison | null
}

/** 自定义时间报表数据 */
export interface CustomReport {
  start_date: string
  end_date: string
  overview: ReportOverview
  daily_data: DailySummary[]
  category_ranks: CategoryRankItem[]
}
