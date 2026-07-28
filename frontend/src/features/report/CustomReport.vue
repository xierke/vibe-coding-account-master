<!--
  CustomReport.vue — 自定义时间范围报表

  与月报格式相同（无热力图和环比）
  用户选择起止日期生成报表
-->
<template>
  <div class="page-container">
    <PageHeader title="自定义报表" />

    <!-- 日期范围选择 -->
    <div class="date-range card">
      <div class="range-field">
        <label class="form-label">起始日期</label>
        <input v-model="startDate" type="date" class="form-input" />
      </div>
      <span class="range-sep">至</span>
      <div class="range-field">
        <label class="form-label">结束日期</label>
        <input v-model="endDate" type="date" class="form-input" />
      </div>
      <button class="btn btn-primary range-btn" :disabled="loading" @click="fetchReport">
        查询
      </button>
    </div>

    <!-- 加载 / 错误 -->
    <LoadingState v-if="loading" text="加载报表中..." />
    <ErrorState v-if="error" :description="error" show-retry @retry="fetchReport" />
    <EmptyState
      v-if="!loading && !error && !reportData"
      icon="📊"
      title="选择日期范围后查询报表"
      description="选择起止日期，点击「查询」按钮生成报表"
    />

    <!-- 报表内容 -->
    <template v-if="reportData">
      <!-- 概览卡片 -->
      <OverviewCard :items="overviewItems" />

      <!-- 每日收支柱状图 -->
      <div class="chart-section card">
        <h3 class="chart-title">每日收支</h3>
        <v-chart class="chart" :option="barChartOption" autoresize />
      </div>

      <!-- 分类排行 -->
      <div v-if="reportData.category_ranks.length > 0" class="chart-section card">
        <h3 class="chart-title">支出排行</h3>
        <v-chart class="chart chart-rank" :option="rankChartOption" autoresize />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { getCustomReport } from '@/api/reports'
import { formatMoney, formatDate, getToday } from '@/utils/format'
import type { CustomReport } from '@/types/report'
import type { OverviewItem } from '@/components/ui/OverviewCard.vue'

import PageHeader from '@/components/ui/PageHeader.vue'
import OverviewCard from '@/components/ui/OverviewCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'

// 注册 ECharts 模块
use([BarChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

// ===== 数据 =====
const reportData = ref<CustomReport | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// 默认日期范围：本月第一天 ~ 今天
const today = new Date()
const startDate = ref(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`)
const endDate = ref(getToday())

// ===== 概览卡片 =====
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

// ===== 柱状图 =====
const barChartOption = computed(() => {
  if (!reportData.value) return {}
  const dailyData = reportData.value.daily_data

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
        type: 'bar',
        data: dailyData.map(d => d.expense),
        itemStyle: { color: '#E07B5A' },
        barMaxWidth: 16
      },
      {
        name: '收入',
        type: 'bar',
        data: dailyData.map(d => d.income),
        itemStyle: { color: '#7BA587' },
        barMaxWidth: 16
      }
    ]
  }
})

// ===== 排行图 =====
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
    xAxis: { type: 'value', axisLabel: { color: '#8B7E75' } },
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

// ===== 方法 =====
async function fetchReport() {
  if (!startDate.value || !endDate.value) return
  if (startDate.value > endDate.value) {
    error.value = '起始日期不能晚于结束日期'
    return
  }

  loading.value = true
  error.value = null
  try {
    reportData.value = await getCustomReport(startDate.value, endDate.value)
  } catch (e: any) {
    error.value = e.message || '加载报表失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.date-range {
  padding: 20px 24px;
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 16px;
}

.range-field {
  flex: 1;
}

.range-sep {
  color: var(--text-secondary);
  padding-bottom: 10px;
}

.range-btn {
  height: 40px;
  flex-shrink: 0;
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
  height: 300px;
}

@media (max-width: 767px) {
  .date-range {
    flex-direction: column;
    align-items: stretch;
    padding: 16px;
  }

  .range-sep {
    text-align: center;
    padding-bottom: 0;
  }

  .chart-section {
    padding: 12px 16px;
  }

  .chart {
    height: 240px;
  }
}
</style>
