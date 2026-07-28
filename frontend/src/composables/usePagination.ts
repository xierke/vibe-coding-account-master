/**
 * 分页逻辑 composable
 *
 * 封装列表分页加载的通用逻辑：
 * - 自动管理 page/total/hasMore
 * - loadMore 追加数据
 * - refresh 重置并重新加载
 */

import { ref, computed } from 'vue'
import type { PaginatedData } from '@/types/api'

export function usePagination<T>(
  fetchFn: (page: number, pageSize: number) => Promise<PaginatedData<T>>,
  pageSize = 20
) {
  // ===== 状态 =====
  const items = ref<T[]>([])
  const page = ref(1)
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ===== 计算属性 =====
  const hasMore = computed(() => items.value.length < total.value)

  // ===== 方法 =====

  /** 加载下一页（追加到现有列表） */
  async function loadMore() {
    if (loading.value || !hasMore.value) return

    loading.value = true
    error.value = null

    try {
      const result = await fetchFn(page.value, pageSize)
      items.value.push(...result.items)
      total.value = result.total
      page.value++
    } catch (e: any) {
      error.value = e.message || '加载失败'
    } finally {
      loading.value = false
    }
  }

  /** 刷新列表（重置并重新加载第一页） */
  async function refresh() {
    loading.value = true
    error.value = null
    page.value = 1
    items.value = []

    try {
      const result = await fetchFn(1, pageSize)
      items.value = result.items
      total.value = result.total
      page.value = 2 // 下一页从第 2 页开始
    } catch (e: any) {
      error.value = e.message || '加载失败'
    } finally {
      loading.value = false
    }
  }

  /** 重置所有状态 */
  function reset() {
    items.value = []
    page.value = 1
    total.value = 0
    error.value = null
    loading.value = false
  }

  return {
    items,
    page,
    total,
    loading,
    error,
    hasMore,
    loadMore,
    refresh,
    reset
  }
}
