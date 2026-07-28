<!--
  LoginView.vue — 登录/注册/忘记密码（单页面 Tab 面板）
  原型 login.html 的三面板设计：
  - Tab「登录」：邮箱 + 密码 + 记住我 + 登录按钮
  - Tab「注册」：用户名 + 邮箱 + 密码 + 确认密码 + 验证码 + 用户协议
  - Tab「忘记密码」：邮箱 + 验证码 + 新密码 + 重置按钮
-->
<template>
  <div class="auth-wrapper">
    <div class="auth-page">
      <div class="auth-header">
        <div class="logo">DailyTracker</div>
        <p>温暖记账，清晰生活</p>
      </div>

      <div class="auth-card">
        <!-- Tab 切换 -->
        <div class="auth-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="auth-tab"
            :class="{ active: activeTab === tab.key }"
            @click="switchTab(tab.key)"
          >{{ tab.label }}</button>
        </div>

        <!-- === 登录面板 === -->
        <div v-if="activeTab === 'login'" class="auth-panel">
          <!-- 错误 -->
          <div v-if="loginError" class="alert alert-error">{{ loginError }}</div>

          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input v-model="loginForm.account" type="text" class="form-input" placeholder="your@email.com" autocomplete="email" />
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <input v-model="loginForm.password" type="password" class="form-input" placeholder="输入密码" autocomplete="current-password" />
          </div>
          <div class="checkbox-row">
            <input type="checkbox" id="remember" v-model="loginForm.remember" />
            <label for="remember">记住我（7 天免登录）</label>
          </div>
          <button class="btn btn-primary btn-full" :disabled="loginLoading" @click="handleLogin">
            {{ loginLoading ? '登录中...' : '登录' }}
          </button>
          <div class="form-footer" style="margin-top: 16px;">
            <a href="#" @click.prevent="switchTab('forgot')">忘记密码？</a>
          </div>
          <hr />
          <div class="form-footer">
            还没有账号？<a href="#" @click.prevent="switchTab('register')">立即注册</a>
          </div>
        </div>

        <!-- === 注册面板 === -->
        <div v-if="activeTab === 'register'" class="auth-panel">
          <div v-if="regError" class="alert alert-error">{{ regError }}</div>
          <div v-if="regSuccess" class="alert alert-success">{{ regSuccess }}</div>

          <div class="form-group">
            <label class="form-label">用户名</label>
            <input v-model="regForm.username" type="text" class="form-input" placeholder="2-20 个字符" maxlength="20" />
            <p class="form-hint">2–20 个字符</p>
          </div>
          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input v-model="regForm.email" type="email" class="form-input" placeholder="your@email.com" />
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <input v-model="regForm.password" type="password" class="form-input" placeholder="8-20 位，含字母+数字" />
            <p class="form-hint">8–20 位，需包含字母与数字</p>
          </div>
          <div class="form-group">
            <label class="form-label">确认密码</label>
            <input v-model="regForm.confirmPassword" type="password" class="form-input" placeholder="再次输入密码" />
          </div>
          <div class="form-group">
            <label class="form-label">邮箱验证码</label>
            <div class="form-row">
              <input v-model="regForm.code" type="text" class="form-input" placeholder="6 位验证码" maxlength="6" style="flex:2;" />
              <button class="btn btn-primary" style="flex:1;padding:12px 8px;font-size:13px;" :disabled="sendingCode" @click="sendRegCode">
                {{ sendingCode ? (countdown > 0 ? `${countdown}s` : '...') : '发送验证码' }}
              </button>
            </div>
            <p class="form-hint">验证码 5 分钟内有效</p>
          </div>
          <div class="checkbox-row">
            <input type="checkbox" id="agree" v-model="regForm.agreed" />
            <label for="agree">我已阅读并同意 <a href="#" style="color:var(--color-primary);">用户协议</a> 和 <a href="#" style="color:var(--color-primary);">隐私政策</a></label>
          </div>
          <button class="btn btn-primary btn-full" :disabled="regLoading" @click="handleRegister">
            {{ regLoading ? '注册中...' : '注册并登录' }}
          </button>
          <hr />
          <div class="form-footer">
            已有账号？<a href="#" @click.prevent="switchTab('login')">去登录</a>
          </div>
        </div>

        <!-- === 忘记密码面板 === -->
        <div v-if="activeTab === 'forgot'" class="auth-panel">
          <a class="back-link" href="#" @click.prevent="switchTab('login')">← 返回登录</a>
          <div class="alert alert-info">输入注册邮箱，我们将发送密码重置验证码。</div>

          <div v-if="forgotError" class="alert alert-error">{{ forgotError }}</div>
          <div v-if="forgotMsg" class="alert alert-success">{{ forgotMsg }}</div>

          <div class="form-group">
            <label class="form-label">注册邮箱</label>
            <input v-model="forgotForm.email" type="email" class="form-input" placeholder="your@email.com" />
          </div>
          <div class="form-group">
            <label class="form-label">验证码</label>
            <div class="form-row">
              <input v-model="forgotForm.code" type="text" class="form-input" placeholder="6 位验证码" maxlength="6" style="flex:2;" />
              <button class="btn btn-primary" style="flex:1;padding:12px 8px;font-size:13px;" :disabled="sendingForgotCode" @click="sendForgotCode">
                {{ sendingForgotCode ? (forgotCountdown > 0 ? `${forgotCountdown}s` : '...') : '发送验证码' }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">新密码</label>
            <input v-model="forgotForm.newPassword" type="password" class="form-input" placeholder="8-20 位" />
          </div>
          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <input v-model="forgotForm.confirmPassword" type="password" class="form-input" placeholder="再次输入新密码" />
          </div>
          <button class="btn btn-primary btn-full" :disabled="forgotLoading" @click="handleResetPassword">
            {{ forgotLoading ? '重置中...' : '重置密码' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { sendCode, resetPassword } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

// ==== Tab 切换 ====
type TabKey = 'login' | 'register' | 'forgot'
const tabs = [
  { key: 'login' as TabKey, label: '登录' },
  { key: 'register' as TabKey, label: '注册' }
]
const activeTab = ref<TabKey>('login')

function switchTab(key: TabKey) {
  activeTab.value = key
  // 清空表单错误
  loginError.value = ''
  regError.value = ''
  forgotError.value = ''
}

// ==== 登录 ====
const loginForm = reactive({ account: '', password: '', remember: true })
const loginLoading = ref(false)
const loginError = ref('')

async function handleLogin() {
  if (!loginForm.account.trim()) { loginError.value = '请输入邮箱'; return }
  if (!loginForm.password) { loginError.value = '请输入密码'; return }

  loginLoading.value = true; loginError.value = ''
  try {
    await authStore.login({ account: loginForm.account, password: loginForm.password, remember_me: loginForm.remember })
    toast.success('登录成功')
    const redirect = (route.query.redirect as string) || '/'
    router.replace(redirect)
  } catch (e: any) {
    loginError.value = e.message || '登录失败'
  } finally { loginLoading.value = false }
}

// ==== 注册 ====
const regForm = reactive({ username: '', email: '', password: '', confirmPassword: '', code: '', agreed: false })
const regLoading = ref(false)
const regError = ref('')
const regSuccess = ref('')
const sendingCode = ref(false)
const countdown = ref(0)

async function sendRegCode() {
  if (!regForm.email.trim()) { regError.value = '请先输入邮箱'; return }
  sendingCode.value = true; regError.value = ''
  try {
    await sendCode({ type: 'email', target: regForm.email.trim() })
    countdown.value = 60; const timer = setInterval(() => { countdown.value--; if (countdown.value <= 0) clearInterval(timer) }, 1000)
    toast.success('验证码已发送')
  } catch (e: any) { regError.value = e.message || '发送失败' }
  finally { sendingCode.value = false }
}

async function handleRegister() {
  if (!regForm.username.trim() || regForm.username.trim().length < 2) { regError.value = '用户名至少 2 个字符'; return }
  if (!regForm.email.trim()) { regError.value = '请输入邮箱'; return }
  if (regForm.password.length < 8) { regError.value = '密码至少 8 位'; return }
  if (regForm.password !== regForm.confirmPassword) { regError.value = '两次密码不一致'; return }
  if (!regForm.code.trim()) { regError.value = '请输入验证码'; return }
  if (!regForm.agreed) { regError.value = '请先同意用户协议'; return }

  regLoading.value = true; regError.value = ''
  try {
    await authStore.register({ username: regForm.username.trim(), email: regForm.email.trim(), password: regForm.password, confirm_password: regForm.confirmPassword })
    regSuccess.value = '注册成功！'
    toast.success('注册成功')
    router.replace('/')
  } catch (e: any) { regError.value = e.message || '注册失败' }
  finally { regLoading.value = false }
}

// ==== 忘记密码 ====
const forgotForm = reactive({ email: '', code: '', newPassword: '', confirmPassword: '' })
const forgotLoading = ref(false)
const forgotError = ref('')
const forgotMsg = ref('')
const sendingForgotCode = ref(false)
const forgotCountdown = ref(0)

async function sendForgotCode() {
  if (!forgotForm.email.trim()) { forgotError.value = '请输入邮箱'; return }
  sendingForgotCode.value = true; forgotError.value = ''
  try {
    await sendCode({ type: 'email', target: forgotForm.email.trim() })
    forgotCountdown.value = 60; const timer = setInterval(() => { forgotCountdown.value--; if (forgotCountdown.value <= 0) clearInterval(timer) }, 1000)
    toast.success('验证码已发送')
  } catch (e: any) { forgotError.value = e.message || '发送失败' }
  finally { sendingForgotCode.value = false }
}

async function handleResetPassword() {
  if (!forgotForm.email.trim()) { forgotError.value = '请输入邮箱'; return }
  if (!forgotForm.code.trim()) { forgotError.value = '请输入验证码'; return }
  if (forgotForm.newPassword.length < 8) { forgotError.value = '新密码至少 8 位'; return }
  if (forgotForm.newPassword !== forgotForm.confirmPassword) { forgotError.value = '两次密码不一致'; return }

  forgotLoading.value = true; forgotError.value = ''; forgotMsg.value = ''
  try {
    await resetPassword({ email: forgotForm.email.trim(), code: forgotForm.code.trim(), new_password: forgotForm.newPassword, confirm_password: forgotForm.confirmPassword })
    forgotMsg.value = '密码重置成功，请使用新密码登录'
    toast.success('密码重置成功')
    setTimeout(() => switchTab('login'), 1500)
  } catch (e: any) { forgotError.value = e.message || '重置失败' }
  finally { forgotLoading.value = false }
}
</script>

<style scoped>
/* 全屏居中 */
.auth-wrapper { min-height: 100dvh; display: flex; align-items: center; justify-content: center; background: var(--bg-page); padding: 24px; }
.auth-page { width: 100%; max-width: 420px; }
.auth-header { text-align: center; margin-bottom: var(--space-xl); }
.logo { font-size: 28px; font-weight: 700; color: var(--color-primary); letter-spacing: -0.01em; }
.auth-header p { color: var(--text-secondary); font-size: 15px; margin: 4px 0 0; }
.auth-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 32px; box-shadow: var(--shadow-card); }

/* Tabs */
.auth-tabs { display: flex; border-bottom: 1px solid var(--border); margin-bottom: var(--space-xl); }
.auth-tab { flex: 1; padding: 12px 0; text-align: center; font-size: 15px; font-weight: 600; color: var(--text-secondary); background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; }
.auth-tab.active { color: var(--color-primary); border-bottom-color: var(--color-primary); }

/* Form */
.auth-panel { display: flex; flex-direction: column; gap: 12px; }
.form-group { display: flex; flex-direction: column; }
.form-label { font-size: 14px; font-weight: 500; margin-bottom: 6px; }
.form-input { width: 100%; padding: 12px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg-card); font-size: 15px; color: var(--text-primary); font-family: inherit; }
.form-input:focus { outline: none; border-color: var(--color-primary); }
.form-input::placeholder { color: var(--text-disabled); }
.form-hint { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.form-row { display: flex; gap: 12px; }
.form-row > * { flex: 1; }
.checkbox-row { display: flex; align-items: center; gap: 8px; font-size: 14px; color: var(--text-secondary); }
.checkbox-row input { accent-color: var(--color-primary); }
.btn-full { width: 100%; }
.form-footer { text-align: center; font-size: 14px; color: var(--text-secondary); }
.form-footer a { color: var(--color-primary); font-weight: 500; }
.back-link { display: inline-flex; align-items: center; gap: 4px; color: var(--text-secondary); font-size: 14px; text-decoration: none; }
.back-link:hover { color: var(--text-primary); }
hr { border: 0; border-top: 1px solid var(--border); margin: 16px 0; }

/* Alerts */
.alert { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 14px; }
.alert-error { background: rgba(212,120,110,0.12); color: var(--color-warning); border: 1px solid rgba(212,120,110,0.25); }
.alert-success { background: rgba(122,165,135,0.12); color: var(--color-income); border: 1px solid rgba(122,165,135,0.25); }
.alert-info { background: rgba(107,158,179,0.12); color: #4A7F8A; border: 1px solid rgba(107,158,179,0.2); }
</style>
