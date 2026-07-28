<!--
  WeeklyReport.vue — 周报表
  包含：ReportTabs + 概览卡片(含环比箭头) + 柱状图 + 环形图 + 环比对比卡片 + 每日明细表格
-->
<template>
  <div class="page-container">
    <PageHeader title="报表" />

    <!-- 报表类型 Tab -->
    <ReportTabs />

    <!-- 周选择器 -->
    <div class="week-nav">
      <h1>周报表</h1>
      <div class="week-nav-btns">
        <button class="nav-btn" @click="changeWeek(-1)">←</button>
        <span class="week-range">{{ reportData?.week_start }} – {{ reportData?.week_end }}</span>
        <button class="nav-btn" @click="changeWeek(1)">→</button>
      </div>
    </div>

    <!-- 加载 / 错误 -->
    <LoadingState v-if="loading" text="加载报表中..." />
    <ErrorState v-if="error" :description="error" show-retry @retry="fetchReport" />

    <!-- 报表内容 -->
    <template v-if="reportData">
      <!-- 概览卡片 -->
      <OverviewCard :items="overviewItems" />

      <!-- 每日收支柱状图 -->
      <div class="chart-section card">
        <h3 class="chart-title">每日收支</h3>
        <v-chart class="chart" :option="barChartOption" autoresize />
      </div>

      <!-- 支出分类饼图 -->
      <div v-if="reportData.category_pie.length > 0" class="chart-section card">
        <h3 class="chart-title">支出分类占比</h3>
        <v-chart class="chart" :option="pieChartOption" autoresize />
      </div>

      <!-- 环比对比 -->
      <div v-if="reportData.comparison" class="chart-section card">
        <h3 class="chart-title">与上周对比</h3>
        <div class="comparison-grid">
          <div class="comparison-item">
            <span class="comparison-label">上周收入</span>
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
            <span class="comparison-label">上周支出</span>
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
import { BarChart, PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { getWeeklyReport } from '@/api/reports'
import { formatMoney, getMondayOfWeek } from '@/utils/format'
import type { WeeklyReport } from '@/types/report'
import type { OverviewItem } from '@/components/ui/OverviewCard.vue'

import PageHeader from '@/components/ui/PageHeader.vue'
import ReportTabs from '@/components/ui/ReportTabs.vue'
import OverviewCard from '@/components/ui/OverviewCard.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'

// 注册 ECharts 模块
use([BarChart, PieChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

// ===== 数据 =====
const reportData = ref<WeeklyReport | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const currentDate = ref(formatDateStr(new Date()))

// ===== 概览卡片数据 =====
const overviewItems = computed<OverviewItem[]>(() => {
  if (!reportData.value) return []
  const d = reportData.value.overview
  return [
    { label: '总收入', value: formatMoney(d.total_income), color: 'var(--color-income)' },
    { label: '总支出', value: formatMoney(d.total_expense), color: 'var(--color-primary)' },
    { label: '结余', value: formatMoney(d.balance), color: d.balance >= 0 ? 'var(--color-income)' : 'var(--color-warning)' },
    { label: '日均支出', value: formatMoney(d.avg_daily_expense) }
  ]
})

// ===== 柱状图配置 =====
const barChartOption = computed(() => {
  if (!reportData.value) return {}
  const dailyData = reportData.value.daily_data
  const weekNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

  return {
    animation: false,
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#FFFFFF',
      borderColor: '#EBE3DC',
      textStyle: { color: '#4A3F3A' }
    },
    legend: {
      data: ['支出', '收入'],
      bottom: 0,
      textStyle: { color: '#8B7E75' }
    },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '15%' },
    xAxis: {
      type: 'category',
      data: dailyData.map((_, i) => weekNames[i]),
      axisLine: { lineStyle: { color: '#EBE3DC' } },
      axisLabel: { color: '#8B7E75' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#8B7E75' },
      splitLine: { lineStyle: { color: '#F5F0EB' } }
    },
    series: [
      {
        name: '支出',
        type: 'bar',
        data: dailyData.map(d => d.expense),
        itemStyle: { color: '#E07B5A' },
        barMaxWidth: 24
      },
      {
        name: '收入',
        type: 'bar',
        data: dailyData.map(d => d.income),
        itemStyle: { color: '#7BA587' },
        barMaxWidth: 24
      }
    ]
  }
})

// ===== 饼图配置 =====
const pieChartOption = computed(() => {
  if (!reportData.value) return {}
  const pieData = reportData.value.category_pie

  return {
    animation: false,
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)',
      backgroundColor: '#FFFFFF',
      borderColor: '#EBE3DC',
      textStyle: { color: '#4A3F3A' }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#8B7E75' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      data: pieData.map(item => ({
        name: item.category_name,
        value: item.amount,
        itemStyle: { color: item.color }
      })),
      label: {
        color: '#8B7E75',
        fontSize: 12
      }
    }]
  }
})

// ===== 方法 =====

/** 切换周 */
function changeWeek(delta: number) {
  const date = new Date(currentDate.value)
  date.setDate(date.getDate() + delta * 7)
  currentDate.value = formatDateStr(date)
}

/** 获取报表 */
async function fetchReport() {
  loading.value = true
  error.value = null
  try {
    reportData.value = await getWeeklyReport(currentDate.value)
  } catch (e: any) {
    error.value = e.message || '加载报表失败'
  } finally {
    loading.value = false
  }
}

/** 格式化日期为 YYYY-MM-DD */
function formatDateStr(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

// 监听日期变化，重新加载报表
watch(currentDate, () => fetchReport())

// 初始化
onMounted(() => fetchReport())
</script>

<style scoped>
.week-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.week-label {
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
  height: 320px;
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
