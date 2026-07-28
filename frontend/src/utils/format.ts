/**
 * 格式化工具函数
 * 金额、日期、百分比等格式化
 */

/**
 * 格式化金额为人民币显示
 * @param amount 金额数值
 * @param showSymbol 是否显示 ¥ 符号，默认 true
 * @returns 格式化后的金额字符串，如 "¥1,234.56" 或 "-¥1,234.56"
 */
export function formatMoney(amount: number, showSymbol = true): string {
  const abs = Math.abs(amount)
  const formatted = abs.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
  const prefix = showSymbol ? '¥' : ''
  return amount < 0 ? `-${prefix}${formatted}` : `${prefix}${formatted}`
}

/**
 * 格式化百分比
 * @param rate 比例值，如 0.42
 * @param decimals 小数位数，默认 1
 * @returns 如 "42.0%"
 */
export function formatPercent(rate: number, decimals = 1): string {
  return (rate * 100).toFixed(decimals) + '%'
}

/**
 * 将日期字符串转换为中文日标签
 * @param dateStr YYYY-MM-DD 格式的日期字符串
 * @returns 中文日标签，如 "今天"、"昨天"、"07月28日 周一"
 */
export function dateToDayLabel(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00')
  const today = new Date()
  const todayStr = formatDate(today)

  if (dateStr === todayStr) return '今天'

  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  if (dateStr === formatDate(yesterday)) return '昨天'

  const dayOfWeek = date.getDay()
  const weekNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const month = date.getMonth() + 1
  const day = date.getDate()

  return `${String(month).padStart(2, '0')}月${String(day).padStart(2, '0')}日 ${weekNames[dayOfWeek]}`
}

/**
 * 格式化日期为 YYYY-MM-DD
 */
export function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * 获取今天的日期字符串 YYYY-MM-DD
 */
export function getToday(): string {
  return formatDate(new Date())
}

/**
 * 获取当前月份字符串 YYYY-MM
 */
export function getCurrentMonth(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

/**
 * 获取指定日期所在周的周一日期
 * @param dateStr 参考日期 YYYY-MM-DD
 * @returns 周一日期 YYYY-MM-DD
 */
export function getMondayOfWeek(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00')
  const day = date.getDay()
  // 周日(0) 需要回退 6 天，周一(1) 回退 0 天
  const diff = day === 0 ? -6 : 1 - day
  date.setDate(date.getDate() + diff)
  return formatDate(date)
}

/**
 * 格式化 ISO datetime 为时间字符串
 * @param isoStr ISO 格式时间字符串
 * @returns 如 "12:30"
 */
export function formatTime(isoStr: string): string {
  const date = new Date(isoStr)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

/**
 * 将账单列表按日期分组
 * @param bills 账单列表（已按日期排序）
 * @returns 按日期分组的账单数据
 */
export function groupBillsByDate(bills: import('@/types/bill').Bill[]): import('@/types/bill').BillGroup[] {
  const groupMap = new Map<string, import('@/types/bill').BillGroup>()

  for (const bill of bills) {
    const date = bill.bill_date
    if (!groupMap.has(date)) {
      groupMap.set(date, {
        date,
        dayLabel: dateToDayLabel(date),
        bills: [],
        dayIncome: 0,
        dayExpense: 0
      })
    }

    const group = groupMap.get(date)!
    group.bills.push(bill)

    if (bill.type === 'income') {
      group.dayIncome += bill.amount
    } else {
      group.dayExpense += bill.amount
    }
  }

  // 按日期降序排列
  return Array.from(groupMap.values()).sort((a, b) => b.date.localeCompare(a.date))
}

/**
 * 截断文本，超出长度添加省略号
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * 获取环比变化的方向和颜色
 * @param changePct 变化百分比
 * @returns { text: 显示文本, color: CSS 颜色变量, isUp: 是否上升 }
 */
export function getChangeDisplay(changePct: number): { text: string; color: string; isUp: boolean } {
  const isUp = changePct > 0
  const absValue = Math.abs(changePct)
  const text = `${isUp ? '↑' : '↓'} ${absValue.toFixed(1)}%`
  // 支出上升 = 红色，收入上升 = 绿色（调用方决定）
  return { text, color: '', isUp }
}
