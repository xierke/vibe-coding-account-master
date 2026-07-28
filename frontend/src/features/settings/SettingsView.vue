<!--
  SettingsView.vue — 设置中心（侧栏布局）
  原型 app-settings.html 的 Vue 实现
  四个子模块：个人信息 / 预算设置 / 分类管理 / 数据导出
-->
<template>
  <div class="page-container">
    <PageHeader title="设置" />

    <div class="settings-grid">
      <!-- 左侧导航 -->
      <div class="settings-nav">
        <button
          v-for="item in navItems"
          :key="item.key"
          class="settings-nav-item"
          :class="{ active: activeSection === item.key }"
          @click="activeSection = item.key"
        >{{ item.label }}</button>
      </div>

      <!-- 右侧内容 -->
      <div class="settings-content">
        <!-- === 个人信息 === -->
        <div v-if="activeSection === 'profile'" class="settings-section">
          <h2>个人信息</h2>
          <p class="desc">管理你的账户基本信息与安全设置</p>

          <div class="profile-card">
            <div class="profile-avatar">{{ avatarLetter }}</div>
            <div>
              <div class="profile-name">{{ authStore.user?.username || 'User' }}</div>
              <div class="profile-email">{{ authStore.user?.email || '' }}</div>
              <div class="profile-meta">注册于 {{ formatDateStr(authStore.user?.created_at || '') }}</div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">用户名</label>
            <input v-model="profileUsername" class="form-input" type="text" maxlength="20" />
            <p class="form-hint">2–20 个字符，修改后其他用户可见</p>
          </div>
          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input :value="authStore.user?.email" class="form-input" type="email" disabled />
          </div>
          <button class="btn btn-primary" :disabled="savingProfile" @click="saveProfile">保存修改</button>

          <hr />
          <h3 class="section-subtitle">修改密码</h3>
          <div class="form-group">
            <label class="form-label">当前密码</label>
            <input v-model="pwdForm.old" class="form-input" type="password" placeholder="输入当前密码" />
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">新密码</label><input v-model="pwdForm.newPwd" class="form-input" type="password" placeholder="8-20 位" /></div>
            <div class="form-group"><label class="form-label">确认新密码</label><input v-model="pwdForm.confirm" class="form-input" type="password" placeholder="再次输入" /></div>
          </div>
          <p v-if="pwdError" class="form-error">{{ pwdError }}</p>
          <p v-if="pwdSuccess" class="form-success">{{ pwdSuccess }}</p>
          <button class="btn btn-primary" :disabled="savingPwd" @click="changePwd">修改密码</button>

          <div class="logout-section">
            <button class="btn btn-danger" @click="handleLogout">退出登录</button>
          </div>
        </div>

        <!-- === 预算设置 === -->
        <div v-if="activeSection === 'budget'" class="settings-section">
          <h2>预算设置</h2>
          <p class="desc">设置月度预算，当支出达 80% 时及时提醒</p>

          <!-- 预算状态提醒 -->
          <div class="budget-alert" :class="budgetWarning ? 'warn' : 'info'">
            {{ budgetAlertText }}
          </div>

          <!-- 月度总预算 -->
          <div class="budget-box">
            <h3>月度总预算</h3>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">预算金额</label>
                <input v-model.number="totalBudgetVal" class="form-input" type="number" min="0" step="0.01" placeholder="0.00" />
              </div>
              <div class="form-group">
                <label class="form-label">月份</label>
                <input v-model="budgetMonth" class="form-input" type="month" />
              </div>
            </div>
          </div>

          <!-- 分类预算 -->
          <div class="budget-box">
            <h3>分类预算（选填）</h3>
            <p class="hint-text">为高频分类设置单独预算，更精细地控制支出</p>
            <div class="form-row" style="margin-bottom:12px;">
              <select v-model="addCatBudgetId" class="form-input" style="flex:1;">
                <option :value="null" disabled>选择分类</option>
                <option v-for="cat in categoryStore.expenseCategories" :key="cat.id" :value="cat.id">{{ cat.icon }} {{ cat.name }}</option>
              </select>
              <input v-model.number="addCatBudgetAmount" class="form-input" type="number" placeholder="预算金额" style="flex:1;" />
              <button class="btn btn-primary btn-sm" style="flex:none;" @click="addCatBudget">添加</button>
            </div>
            <!-- 已设置分类预算列表 -->
            <div v-for="cb in catBudgetList" :key="cb.category_id" class="cat-budget-row">
              <span class="cat-budget-name">{{ getCatEmoji(cb.category_id) }} {{ getCatName(cb.category_id) }}</span>
              <span class="cat-budget-amount">{{ formatMoney(cb.amount) }} / 月</span>
              <div class="mini-progress"><div class="mini-progress-fill" :class="{ warn: cb.usage_rate >= 0.8 }" :style="{ width: Math.min(cb.usage_rate * 100, 100) + '%' }" /></div>
              <span class="cat-budget-pct">{{ (cb.usage_rate * 100).toFixed(0) }}%</span>
              <button class="cat-remove-btn" @click="removeCatBudget(cb.category_id)">✕</button>
            </div>
            <p v-if="catBudgetList.length === 0" class="text-disabled" style="font-size:13px;">暂无分类预算</p>
          </div>

          <button class="btn btn-primary" :disabled="savingBudget" @click="saveBudget">保存预算</button>
        </div>

        <!-- === 分类管理 === -->
        <div v-if="activeSection === 'categories'" class="settings-section">
          <h2>分类管理</h2>
          <p class="desc">管理你的收支分类，系统默认分类不可删除</p>

          <h3 class="section-subtitle">支出分类</h3>
          <div v-for="cat in categoryStore.expenseCategories" :key="cat.id" class="cat-item">
            <span class="cat-icon">{{ cat.icon }}</span>
            <div class="cat-info">
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-meta">{{ cat.is_default ? '系统默认' : '自定义' }}</span>
            </div>
            <span class="cat-color-dot" :style="{ background: cat.color }" />
            <div class="cat-actions">
              <button class="cat-action-btn" title="编辑" @click="openCatEdit(cat)">✎</button>
            </div>
          </div>

          <h3 class="section-subtitle">收入分类</h3>
          <div v-for="cat in categoryStore.incomeCategories" :key="cat.id" class="cat-item">
            <span class="cat-icon">{{ cat.icon }}</span>
            <div class="cat-info">
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-meta">{{ cat.is_default ? '系统默认' : '自定义' }}</span>
            </div>
            <span class="cat-color-dot" :style="{ background: cat.color }" />
            <div class="cat-actions">
              <button class="cat-action-btn" title="编辑" @click="openCatEdit(cat)">✎</button>
            </div>
          </div>

          <h3 class="section-subtitle">添加自定义分类</h3>
          <div class="form-row" style="margin-bottom:12px;">
            <input v-model="catForm.name" class="form-input" type="text" placeholder="分类名称" style="flex:2;" />
            <input v-model="catForm.icon" class="form-input" type="text" placeholder="图标 emoji" style="flex:1;" maxlength="2" />
            <input v-model="catForm.color" class="form-input" type="color" style="flex:1;padding:4px 8px;" />
          </div>
          <div class="form-group">
            <select v-model="catForm.type" class="form-input">
              <option value="expense">支出</option>
              <option value="income">收入</option>
            </select>
          </div>
          <button class="btn btn-primary btn-sm" :disabled="addingCat" @click="addCategory">
            {{ editingCatId ? '保存修改' : '添加分类' }}
          </button>
        </div>

        <!-- === 数据导出 === -->
        <div v-if="activeSection === 'export'" class="settings-section">
          <h2>数据导出</h2>
          <p class="desc">将你的账单数据导出为文件，支持 CSV 和 Excel 格式</p>

          <div class="form-group">
            <label class="form-label">导出格式</label>
            <div class="export-options">
              <button class="export-option" :class="{ active: exportFormat === 'csv' }" @click="exportFormat = 'csv'">
                CSV (.csv)<br><span class="export-hint">通用格式，Excel 可打开</span>
              </button>
              <button class="export-option" :class="{ active: exportFormat === 'xlsx' }" @click="exportFormat = 'xlsx'">
                Excel (.xlsx)<br><span class="export-hint">原生 Excel 格式</span>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">导出范围</label>
            <select v-model="exportRange" class="form-input">
              <option value="all">全部数据</option>
              <option value="currentMonth">本月（7月）</option>
              <option value="lastMonth">上月（6月）</option>
              <option value="custom">自定义日期范围</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">导出字段</label>
            <p class="form-hint">将导出：日期、类型、分类、金额、备注</p>
          </div>

          <button class="btn btn-primary" :disabled="exporting" @click="doExport">
            {{ exporting ? '导出中...' : '导出数据' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useCategoryStore } from '@/stores/categories'
import { getBudgets, setBudgets } from '@/api/budgets'
import { getBills } from '@/api/bills'
import { formatMoney, getCurrentMonth } from '@/utils/format'
import type { BudgetData, CategoryBudgetItem } from '@/types/budget'
import type { Category, CategoryType, CategoryUpdateRequest } from '@/types/category'

import PageHeader from '@/components/ui/PageHeader.vue'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const categoryStore = useCategoryStore()

// ==== 导航 ====
const navItems = [
  { key: 'profile', label: '个人信息' },
  { key: 'budget', label: '预算设置' },
  { key: 'categories', label: '分类管理' },
  { key: 'export', label: '数据导出' }
]
const activeSection = ref('profile')

// ==== 个人信息 ====
const profileUsername = ref('')
const savingProfile = ref(false)
const avatarLetter = computed(() => (authStore.user?.username || 'U').charAt(0).toUpperCase())

watch(() => authStore.user?.username, (v) => { profileUsername.value = v || '' })
function formatDateStr(iso: string) { return iso ? iso.slice(0, 7) : '' }

async function saveProfile() {
  if (!profileUsername.value.trim()) { toast.error('用户名不能为空'); return }
  savingProfile.value = true
  try { await authStore.updateProfile({ username: profileUsername.value.trim() }); toast.success('保存成功') }
  catch (e: any) { toast.error(e.message || '保存失败') }
  finally { savingProfile.value = false }
}

const pwdForm = reactive({ old: '', newPwd: '', confirm: '' })
const savingPwd = ref(false); const pwdError = ref(''); const pwdSuccess = ref('')
async function changePwd() {
  pwdError.value = ''; pwdSuccess.value = ''
  if (!pwdForm.old) { pwdError.value = '请输入当前密码'; return }
  if (pwdForm.newPwd.length < 8) { pwdError.value = '新密码至少 8 位'; return }
  if (pwdForm.newPwd !== pwdForm.confirm) { pwdError.value = '两次密码不一致'; return }
  savingPwd.value = true
  try { await authStore.changePassword(pwdForm.old, pwdForm.newPwd, pwdForm.confirm); pwdSuccess.value = '密码修改成功'; pwdForm.old = ''; pwdForm.newPwd = ''; pwdForm.confirm = ''; toast.success('密码修改成功') }
  catch (e: any) { pwdError.value = e.message || '修改失败' }
  finally { savingPwd.value = false }
}

function handleLogout() { authStore.logout(); toast.success('已退出登录'); router.replace('/login') }

// ==== 预算 ====
const budgetMonth = ref(getCurrentMonth())
const totalBudgetVal = ref<number | null>(null)
const budgetData = ref<BudgetData | null>(null)
const savingBudget = ref(false)
const budgetWarning = computed(() => (budgetData.value?.total_budget?.usage_rate || 0) >= 0.8)
const budgetAlertText = computed(() => {
  if (!budgetData.value?.total_budget) return '💡 当前月暂无预算数据，设置预算以跟踪支出进度。'
  const rate = budgetData.value.total_budget.usage_rate
  return `💡 当前月已支出 ${formatMoney(budgetData.value.total_budget.spent)}，预算使用率 ${(rate * 100).toFixed(0)}%，${rate >= 0.8 ? '接近预算上限！' : '状态正常。'}`
})

const addCatBudgetId = ref<number | null>(null); const addCatBudgetAmount = ref<number | null>(null)
const catBudgetList = ref<(CategoryBudgetItem & { usage_rate: number; spent: number })[]>([])

function getCatName(id: number) { return categoryStore.expenseCategories.find(c => c.id === id)?.name || '' }
function getCatEmoji(id: number) { return categoryStore.expenseCategories.find(c => c.id === id)?.icon || '' }

function addCatBudget() {
  if (!addCatBudgetId.value || !addCatBudgetAmount.value || addCatBudgetAmount.value <= 0) return
  const existing = catBudgetList.value.find(b => b.category_id === addCatBudgetId.value)
  if (existing) { existing.amount = addCatBudgetAmount.value! }
  else { catBudgetList.value.push({ category_id: addCatBudgetId.value!, amount: addCatBudgetAmount.value!, usage_rate: 0, spent: 0 }) }
  addCatBudgetId.value = null; addCatBudgetAmount.value = null
}
function removeCatBudget(id: number) { catBudgetList.value = catBudgetList.value.filter(b => b.category_id !== id) }

async function fetchBudgets() {
  try {
    budgetData.value = await getBudgets(budgetMonth.value)
    totalBudgetVal.value = budgetData.value.total_budget?.amount || null
    catBudgetList.value = (budgetData.value.category_budgets || []).map(b => ({
      category_id: b.category_id!, amount: b.amount, usage_rate: b.usage_rate, spent: b.spent
    }))
  } catch { /* ignore */ }
}
watch(budgetMonth, fetchBudgets)

async function saveBudget() {
  savingBudget.value = true
  try {
    await setBudgets({ month: budgetMonth.value, total_budget: totalBudgetVal.value || undefined, category_budgets: catBudgetList.value.map(b => ({ category_id: b.category_id, amount: b.amount })) })
    toast.success('预算保存成功'); await fetchBudgets()
  } catch (e: any) { toast.error(e.message || '保存失败') }
  finally { savingBudget.value = false }
}

// ==== 分类管理 ====
const catForm = reactive({ name: '', icon: '📌', color: '#E07B5A', type: 'expense' as CategoryType })
const addingCat = ref(false); const editingCatId = ref<number | null>(null)

function openCatEdit(cat: Category) {
  editingCatId.value = cat.id; catForm.name = cat.name; catForm.icon = cat.icon; catForm.color = cat.color; catForm.type = cat.type
}
async function addCategory() {
  if (!catForm.name.trim()) { toast.error('请输入分类名称'); return }
  addingCat.value = true
  try {
    if (editingCatId.value) {
      await categoryStore.updateCategory(editingCatId.value, { name: catForm.name.trim(), icon: catForm.icon, color: catForm.color } as CategoryUpdateRequest)
      toast.success('编辑成功')
    } else {
      await categoryStore.createCategory({ name: catForm.name.trim(), icon: catForm.icon, color: catForm.color, type: catForm.type })
      toast.success('添加成功')
    }
    editingCatId.value = null; catForm.name = ''; catForm.icon = '📌'; catForm.color = '#E07B5A'
  } catch (e: any) { toast.error(e.message || '操作失败') }
  finally { addingCat.value = false }
}

// ==== 数据导出 ====
const exportFormat = ref('csv'); const exportRange = ref('all'); const exporting = ref(false)
async function doExport() {
  exporting.value = true
  try {
    const params: any = { page: 1, page_size: 1000 }
    const now = new Date()
    if (exportRange.value === 'currentMonth') params.start_date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
    else if (exportRange.value === 'lastMonth') { params.start_date = `${now.getFullYear()}-${String(now.getMonth()).padStart(2, '0')}-01`; const ld = new Date(now.getFullYear(), now.getMonth(), 0).getDate(); params.end_date = `${now.getFullYear()}-${String(now.getMonth()).padStart(2, '0')}-${ld}` }

    const result = await getBills(params)
    if (result.items.length === 0) { toast.info('没有可导出的账单数据'); return }

    // CSV 导出
    const headers = ['日期', '类型', '分类', '金额', '备注']
    const rows = result.items.map(b => [b.bill_date, b.type === 'income' ? '收入' : '支出', b.category?.name || '', b.amount.toFixed(2), b.note || ''])
    const bom = '﻿'
    const csv = bom + [headers.join(','), ...rows.map(r => r.map(c => `"${c}"`).join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = `DailyTracker_导出_${new Date().toISOString().slice(0, 10)}.csv`; a.click()
    URL.revokeObjectURL(url)
    toast.success(`成功导出 ${result.items.length} 条账单`)
  } catch (e: any) { toast.error(e.message || '导出失败') }
  finally { exporting.value = false }
}

// ==== 初始化 ====
onMounted(async () => {
  await categoryStore.fetchCategories()
  if (!authStore.user) await authStore.fetchProfile()
})
</script>

<style scoped>
.settings-grid { display: grid; grid-template-columns: 200px 1fr; gap: var(--space-lg); }
@media (max-width: 640px) { .settings-grid { grid-template-columns: 1fr; } }

/* 侧栏导航 */
.settings-nav { display: flex; flex-direction: column; gap: 2px; position: sticky; top: 80px; }
.settings-nav-item { padding: 10px 14px; border-radius: var(--radius-sm); font-size: 14px; font-weight: 500; color: var(--text-secondary); border: none; background: transparent; text-align: left; cursor: pointer; }
.settings-nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.settings-nav-item.active { background: var(--color-primary-light); color: var(--color-primary); }
@media (max-width: 640px) { .settings-nav { flex-direction: row; overflow-x: auto; position: static; padding-bottom: var(--space-sm); }
  .settings-nav-item { white-space: nowrap; font-size: 13px; padding: 8px 12px; } }

.settings-section h2 { font-size: 20px; font-weight: 700; margin-bottom: var(--space-sm); }
.settings-section .desc { font-size: 14px; color: var(--text-secondary); margin-bottom: var(--space-lg); }

/* 个人信息 */
.profile-card { display: flex; align-items: center; gap: var(--space-md); padding: var(--space-lg); background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); box-shadow: var(--shadow-card); margin-bottom: var(--space-lg); }
.profile-avatar { width: 64px; height: 64px; border-radius: 50%; background: var(--color-primary-light); color: var(--color-primary); display: grid; place-items: center; font-size: 24px; font-weight: 700; }
.profile-name { font-size: 18px; font-weight: 600; }
.profile-email { font-size: 14px; color: var(--text-secondary); }
.profile-meta { font-size: 13px; color: var(--text-secondary); }

.form-group { margin-bottom: var(--space-md); }
.form-label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 6px; }
.form-hint { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.form-input { width: 100%; padding: 11px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg-card); color: var(--text-primary); font-size: 15px; font-family: inherit; }
.form-input:focus { outline: none; border-color: var(--color-primary); }
.form-input::placeholder { color: var(--text-disabled); }
.form-row { display: flex; gap: var(--space-sm); }
.form-row > * { flex: 1; }
.form-error { color: var(--color-warning); font-size: 13px; }
.form-success { color: var(--color-income); font-size: 13px; }
hr { border: 0; border-top: 1px solid var(--border); margin: var(--space-xl) 0; }
.section-subtitle { font-size: 16px; font-weight: 600; margin-bottom: var(--space-sm); }
.hint-text { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; }

.btn { display: inline-flex; align-items: center; gap: 8px; padding: 11px 22px; border-radius: var(--radius-sm); border: 1px solid transparent; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn-primary { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.btn-primary:hover { background: var(--color-primary-hover); }
.btn-danger { background: transparent; color: var(--color-warning); border-color: var(--color-warning); }
.btn-danger:hover { background: var(--color-warning); color: #fff; }
.btn-sm { padding: 6px 12px; font-size: 13px; }
.logout-section { margin-top: var(--space-xl); padding-top: var(--space-lg); border-top: 1px solid var(--border); }

/* 预算 */
.budget-box { margin-bottom: var(--space-lg); }
.budget-box h3 { font-size: 16px; font-weight: 600; margin-bottom: var(--space-sm); }
.budget-alert { padding: 14px var(--space-md); border-radius: var(--radius-sm); margin-bottom: var(--space-lg); font-size: 14px; }
.budget-alert.warn { background: rgba(212,120,110,0.12); color: var(--color-warning); border: 1px solid rgba(212,120,110,0.25); }
.budget-alert.info { background: rgba(107,158,179,0.12); color: #4A7F8A; border: 1px solid rgba(107,158,179,0.2); }

.cat-budget-row { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm); margin-bottom: 8px; }
.cat-budget-name { flex: 0 0 auto; min-width: 80px; font-size: 14px; }
.cat-budget-amount { font-family: ui-monospace, monospace; font-size: 13px; color: var(--text-secondary); }
.mini-progress { width: 80px; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.mini-progress-fill { height: 100%; background: var(--color-primary); border-radius: 3px; }
.mini-progress-fill.warn { background: var(--color-warning); }
.cat-budget-pct { font-size: 13px; color: var(--text-secondary); min-width: 30px; }
.cat-remove-btn { width: 24px; height: 24px; border-radius: var(--radius-sm); border: none; background: transparent; color: var(--text-secondary); cursor: pointer; font-size: 14px; display: grid; place-items: center; }
.cat-remove-btn:hover { background: var(--bg-hover); color: var(--text-primary); }

/* 分类 */
.cat-item { display: flex; align-items: center; gap: var(--space-sm); padding: 10px var(--space-sm); border-bottom: 1px solid var(--border); }
.cat-item:hover { background: var(--bg-hover); }
.cat-icon { font-size: 22px; width: 32px; text-align: center; }
.cat-info { flex: 1; }
.cat-name { font-size: 14px; font-weight: 500; display: block; }
.cat-meta { font-size: 12px; color: var(--text-secondary); }
.cat-color-dot { width: 16px; height: 16px; border-radius: 50%; border: 1px solid var(--border); }
.cat-actions { display: flex; gap: 4px; }
.cat-action-btn { width: 30px; height: 30px; border-radius: var(--radius-sm); border: none; background: transparent; color: var(--text-secondary); display: grid; place-items: center; font-size: 14px; cursor: pointer; }
.cat-action-btn:hover { background: var(--bg-hover); color: var(--text-primary); }

/* 导出 */
.export-options { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md); margin-bottom: var(--space-lg); }
.export-option { padding: var(--space-md); border: 1px solid var(--border); border-radius: var(--radius-sm); text-align: center; font-size: 14px; font-weight: 500; background: transparent; cursor: pointer; }
.export-option.active { border-color: var(--color-primary); background: var(--color-primary-light); }
.export-option:hover { border-color: var(--color-primary); }
.export-hint { font-size: 11px; color: var(--text-secondary); }
@media (max-width: 640px) { .export-options { grid-template-columns: 1fr; } }
</style>
