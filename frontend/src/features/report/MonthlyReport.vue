<!--
  MonthlyReport.vue — 月报表

  包含：
  1. 概览卡片（收入、支出、结余、日均支出、预算使用率）
  2. 每日收支趋势折线图
  3. 支出分类排行（横向条形图）
  4. 消费日历热力图
  5. 环比对比
-->
<template>
  <div class="page-container">
    <PageHeader title="月报表" />

    <!-- 月份选择器 -->
    <div class="month-picker">
      <button class="btn btn-secondary btn-sm" @click="changeMonth(-1)">
        <ChevronLeft :size="16" /> 上一月
      </button>
      <span class="month-label">{{ currentMonth }}</span>
      <button class="btn btn-secondary btn-sm" @click="changeMonth(1)">
        下一月 <ChevronRight :size="16" />
      </button>
    </div>

    <!-- 加载 / 错误 -->
    <LoadingState v-if="loading" text="加载报表中..." />
    <ErrorState v-if="error" :description="error" show-retry @retry="fetchReport" />

    <!-- 报表内容 -->
    <template v-if="reportData">
      <!-- 概览卡片 -->
      <OverviewCard :items="overviewItems" />

      <!-- 每日趋势折线图 -->
      <div class="chart-section card">
        <h3 class="chart-title">每日支出趋势</h3>
        <v-chart class="chart" :option="lineChartOption" autoresize />
      </div>

      <!-- 分类排行 + 热力图（并排，桌面端） -->
      <div class="two-columns">
        <!-- 支出分类排行 -->
        <div v-if="reportData.category_ranks.length > 0" class="chart-section card">
          <h3 class="chart-title">支出排行 Top 10</h3>
          <v-chart class="chart chart-rank" :option="rankChartOption" autoresize />
        </div>

        <!-- 消费日历热力图 -->
        <div class="chart-section card">
          <h3 class="chart-title">消费日历</h3>
          <div class="calendar-heatmap">
            <div class="calendar-header">
              <span v-for="day in dayNames" :key="day" class="cal-day-name">{{ day }}</span>
            </div>
            <div class="calendar-grid">
              <!-- 填充空白格（月初天数偏移） -->
              <div
                v-for="i in firstDayOfWeek"
                :key="'empty-' + i"
                class="cal-cell cal-empty"
              />
              <!-- 每天的热力格子 -->
              <div
                v-for="day in reportData.calendar_data"
                :key="day.date"
                class="cal-cell"
                :style="{ backgroundColor: getHeatColor(day.intensity, day.amount) }"
                :title="`${day.date}: ¥${day.amount.toFixed(2)}`"
              >
                <span class="cal-day-num">{{ day.day_of_month }}</span>
              </div>
            </div>
            <!-- 热力图例 -->
            <div class="heat-legend">
              <span>低</span>
              <div class="heat-gradient" />
              <span>高</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 环比对比 -->
      <div v-if="reportData.comparison" class="chart-section card">
        <h3 class="chart-title">与上月对比</h3>
        <div class="comparison-grid">
          <div class="comparison-item">
            <span class="comparison-label">上月收入</span>
            <span class="comparison-value">{{ formatMoney(reportData.comparison.prev_income) }}</span>
          </div>
          <div class="comparison-item">
            <span class="comparison-label">收入变化</span>
            <span
              class="comparison-value"
              :class="reportData.comparison.income_change_pct >= 0 ? 'text-income' : 'text-expense'"
            >
              {{ reportData.comparison.income_change_pct >= 0 ? '↑' : '↓' }}
              {{ Math.abs(reportData.comparison.income_change_pct).toFixed(1) }}%
            </span>
          </div>
          <div class="comparison-item">
            <span class="comparison-label">上月支出</span>
            <span class="comparison-value">{{ formatMoney(reportData.comparison.prev_expense) }}</span>
          </div>
          <div class="comparison-item">
            <span class="comparison-label">支出变化</span>
            <span
              class="comparison-value"
              :class="reportData.comparison.expense_change_pct <= 0 ? 'text-income' : 'text-expense'"
            >
              {{ reportData.comparison.expense_change_pct <= 0 ? '↓' : '↑' }}
              {{ Math.abs(reportData.comparison.expense_change_pct).toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { use } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { getMonthlyReport } from '@/api/reports'
import { formatMoney, getCurrentMonth } from '@/utils/format'
import type { MonthlyReport } from '@/types/report'
import type { OverviewItem } from '@/components/ui/OverviewCard.vue'

import PageHeader from '@/components/ui/PageHeader.vue'
import OverviewCard from '@/components/ui/OverviewCard.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'

// 注册 ECharts 模块
use([LineChart, BarChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

// ===== 数据 =====
const reportData = ref<MonthlyReport | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const currentMonth = ref(getCurrentMonth())

const dayNames = ['一', '二', '三', '四', '五', '六', '日']

// ===== 概览卡片 =====
const overviewItems = computed<OverviewItem[]>(() => {
  if (!reportData.value) return []
  const d = reportData.value.overview
  const items: OverviewItem[] = [
    { label: '总收入', value: formatMoney(d.total_income), color: 'var(--color-income)' },
    { label: '总支出', value: formatMoney(d.total_expense), color: 'var(--color-primary)' },
    { label: '结余', value: formatMoney(d.balance), color: d.balance >= 0 ? 'var(--color-income)' : 'var(--color-warning)' },
    { label: '日均支出', value: formatMoney(d.avg_daily_expense) }
  ]
  if (d.budget_usage_rate !== null) {
    items.push({ label: '预算使用率', value: (d.budget_usage_rate * 100).toFixed(1) + '%', color: d.budget_usage_rate >= 0.8 ? 'var(--color-warning)' : 'var(--color-income)' })
  }
  return items
})

// ===== 折线图 =====
const lineChartOption = computed(() => {
  if (!reportData.value) return {}
  const dailyData = reportData.value.daily_data
  const avgExpense = reportData.value.overview.avg_daily_expense

  return {
    animation: false,
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#FFFFFF',
      borderColor: '#EBE3DC',
      textStyle: { color: '#4A3F3A' }
    },
    legend: {
      data: ['支出', '收入', '日均支出'],
      bottom: 0,
      textStyle: { color: '#8B7E75' }
    },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '15%' },
    xAxis: {
      type: 'category',
      data: dailyData.map(d => d.date.slice(-5)),
      axisLabel: { color: '#8B7E75' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#8B7E75' }
    },
    series: [
      {
        name: '支出',
        type: 'line',
        data: dailyData.map(d => d.expense),
        itemStyle: { color: '#E07B5A' },
        lineStyle: { color: '#E07B5A' },
        smooth: false
      },
      {
        name: '收入',
        type: 'line',
        data: dailyData.map(d => d.income),
        itemStyle: { color: '#7BA587' },
        lineStyle: { color: '#7BA587' },
        smooth: false
      },
      {
        name: '日均支出',
        type: 'line',
        data: dailyData.map(() => avgExpense),
        itemStyle: { color: '#BFB5AD' },
        lineStyle: { color: '#BFB5AD', type: 'dashed' },
        symbol: 'none'
      }
    ]
  }
})

// ===== 排行图（横向柱状图） =====
const rankChartOption = computed(() => {
  if (!reportData.value) return {}
  const ranks = [...reportData.value.category_ranks].reverse()

  return {
    animation: false,
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#FFFFFF',
      borderColor: '#EBE3DC',
      textStyle: { color: '#4A3F3A' }
    },
    grid: { left: '3%', right: '8%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#8B7E75' }
    },
    yAxis: {
      type: 'category',
      data: ranks.map(r => r.category_name),
      axisLabel: { color: '#4A3F3A' }
    },
    series: [{
      type: 'bar',
      data: ranks.map(r => ({
        value: r.amount,
        itemStyle: { color: r.color }
      })),
      barMaxWidth: 20
    }]
  }
})

// ===== 热力图 =====
/** 当月第一天是周几（0=周一...6=周日） */
const firstDayOfWeek = computed(() => {
  if (!reportData.value || reportData.value.calendar_data.length === 0) return 0
  return reportData.value.calendar_data[0].day_of_week
})

/** 根据强度获取热力颜色 */
function getHeatColor(intensity: number, amount: number): string {
  if (amount === 0) return '#F5F5F5'
  // 暖珊瑚色渐变：浅 -> 深
  const alpha = 0.05 + intensity * 0.7
  return `rgba(224, 123, 90, ${alpha})`
}

// ===== 方法 =====
function changeMonth(delta: number) {
  const [year, month] = currentMonth.value.split('-').map(Number)
  const date = new Date(year, month - 1 + delta, 1)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  currentMonth.value = `${y}-${m}`
}

async function fetchReport() {
  loading.value = true
  error.value = null
  try {
    reportData.value = await getMonthlyReport(currentMonth.value)
  } catch (e: any) {
    error.value = e.message || '加载报表失败'
  } finally {
    loading.value = false
  }
}

watch(currentMonth, () => fetchReport())
onMounted(() => fetchReport())
</script>

<style scoped>
.month-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.month-label {
  font-size: var(--font-md);
  color: var(--text-primary);
  font-weight: 500;
}

.btn-sm {
  height: 32px;
  padding: 4px 12px;
  font-size: var(--font-sm);
  display: flex;
  align-items: center;
  gap: 4px;
}

.chart-section {
  padding: 20px 24px;
  margin-top: 16px;
}

.chart-title {
  font-size: var(--font-md);
  color: var(--text-primary);
  margin-bottom: 16px;
}

.chart {
  height: 340px;
}

.chart-rank {
  height: 320px;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* 消费日历热力图 */
.calendar-heatmap {
  padding: 8px 0;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.cal-day-name {
  text-align: center;
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.cal-cell {
  aspect-ratio: 1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: default;
}

.cal-empty {
  background: transparent;
}

.cal-day-num {
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.heat-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.heat-gradient {
  width: 80px;
  height: 10px;
  border-radius: 2px;
  background: linear-gradient(to right, rgba(224, 123, 90, 0.05), rgba(224, 123, 90, 0.75));
}

/* 环比对比 */
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.comparison-item {
  text-align: center;
}

.comparison-label {
  display: block;
  font-size: var(--font-sm);
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.comparison-value {
  font-size: var(--font-lg);
  font-weight: 600;
  color: var(--text-primary);
}

@media (max-width: 767px) {
  .two-columns {
    grid-template-columns: 1fr;
  }

  .chart-section {
    padding: 12px 16px;
  }

  .chart {
    height: 240px;
  }

  .comparison-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
