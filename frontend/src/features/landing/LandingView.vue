<!--
  LandingView.vue — 产品落地页
  内容：Hero 区域 + 三大卖点 + 应用预览 + 关键指标 + CTA
-->
<template>
  <div class="landing">
    <!-- 顶部导航 -->
    <header class="topnav">
      <div class="topnav-inner container">
        <span class="logo">DailyTracker</span>
        <nav>
          <a href="#features">功能</a>
          <a href="#reports">报表</a>
          <a href="#design">设计</a>
        </nav>
        <router-link to="/login" class="btn btn-primary btn-sm">免费使用</router-link>
      </div>
    </header>

    <main>
      <!-- Hero -->
      <section class="hero" id="hero">
        <div class="hero-bg" aria-hidden="true"></div>
        <div class="container hero-inner">
          <div class="hero-split">
            <div class="hero-text">
              <p class="eyebrow">日常记账助手 · V1.0</p>
              <h1>像写日记一样记账。<br>温暖，安静，刚刚好。</h1>
              <p class="lead">打开就记，选分类、输金额、回车。没有弹窗和引导，没有眼花缭乱的图表动效 — 只在你需要的时候，告诉你钱都去哪儿了。</p>
              <div class="hero-cta">
                <router-link to="/login" class="btn btn-primary btn-lg">免费开始使用</router-link>
                <a href="#features" class="btn btn-secondary">看看怎么做到的</a>
              </div>
            </div>
            <div class="hero-visual">
              <div class="journal-frame">
                <div class="journal-inner">
                  <div class="journal-lines">
                    <div class="journal-entry"><span class="je-date">7月28日 周一</span></div>
                    <div class="journal-entry">🍽️ 午餐外卖 <span class="je-expense">-128.50</span></div>
                    <div class="journal-entry">🚗 地铁通勤 <span class="je-expense">-12.00</span></div>
                    <div class="journal-entry">🛒 超市采买 <span class="je-expense">-96.00</span></div>
                    <div class="journal-entry" style="margin-top:4px;"><span class="je-date">7月27日 周日</span></div>
                    <div class="journal-entry">🍽️ 朋友聚餐 <span class="je-expense">-312.00</span></div>
                    <div class="journal-entry">💰 兼职工资 <span class="je-income">+3,000</span></div>
                  </div>
                </div>
                <div class="journal-card">
                  <div class="jc-label">7月结余</div>
                  <div class="jc-value">¥15,630</div>
                  <div class="jc-sub">较上月 ↑ 8.2%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 卖点 -->
      <section class="section" id="features">
        <div class="container stack" style="gap: 56px;">
          <div style="max-width: 36ch;">
            <p class="eyebrow">为什么选择 DailyTracker</p>
            <h2>记一笔只需 3 秒，剩下的交给报表。</h2>
          </div>
          <div class="grid-3">
            <div class="feature">
              <div class="feature-mark">
                <PlusCircle :size="22" />
              </div>
              <h3>极简操作</h3>
              <p>打开即记账，选分类、输金额、回车确认。从打开到完成，不超过 5 秒。键盘与触摸均友好。</p>
            </div>
            <div class="feature">
              <div class="feature-mark">
                <LayoutGrid :size="22" />
              </div>
              <h3>清晰报表</h3>
              <p>周报柱状图 + 饼图看消费构成，月报趋势线 + 热力图看花钱节奏。你的消费习惯，一目了然。</p>
            </div>
            <div class="feature">
              <div class="feature-mark">
                <Shield :size="22" />
              </div>
              <h3>云端安全</h3>
              <p>数据加密存储于云端，换设备登录即同步。JWT 双 Token 认证保护你的财务隐私，永不丢失。</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 应用预览 -->
      <section class="section" id="design">
        <div class="container stack" style="gap: 48px;">
          <div class="row-between">
            <div style="max-width: 32ch;">
              <p class="eyebrow">温暖设计</p>
              <h2>暖珊瑚配色，像秋日午后阳光一样舒适。</h2>
            </div>
            <div class="row" style="gap: var(--gap-sm);">
              <span class="pill">暖珊瑚主色</span>
              <span class="pill pill-green">暖绿收入色</span>
            </div>
          </div>
          <div class="grid-2">
            <!-- 记账预览 -->
            <div class="app-preview">
              <div class="app-preview-header">
                <span class="app-preview-dot accent"></span><span class="app-preview-dot"></span><span class="app-preview-dot"></span>
                <span class="app-preview-label">记账首页</span>
              </div>
              <div class="app-preview-body">
                <div class="preview-toggle">
                  <button class="preview-toggle-btn active">支出</button>
                  <button class="preview-toggle-btn">收入</button>
                </div>
                <div class="preview-amount">
                  <span class="preview-amount-label">金额</span>
                  <div class="preview-amount-value">¥128.50</div>
                </div>
                <div class="preview-cat-grid">
                  <div class="preview-cat selected">🍽️<br>餐饮</div>
                  <div class="preview-cat">🚗<br>交通</div>
                  <div class="preview-cat">🛒<br>购物</div>
                  <div class="preview-cat">🏠<br>居住</div>
                </div>
                <button class="preview-submit">确认记账</button>
              </div>
            </div>
            <!-- 报表预览 -->
            <div class="app-preview">
              <div class="app-preview-header">
                <span class="app-preview-dot accent"></span><span class="app-preview-dot"></span><span class="app-preview-dot"></span>
                <span class="app-preview-label">周报表</span>
              </div>
              <div class="app-preview-body">
                <div class="preview-kpi-row">
                  <div class="preview-kpi"><span>总收入</span><b class="text-income">¥8,200</b></div>
                  <div class="preview-kpi"><span>总支出</span><b class="text-accent">¥3,450</b></div>
                  <div class="preview-kpi"><span>结余</span><b class="text-income">¥4,750</b></div>
                </div>
                <!-- 简易柱状图 -->
                <svg viewBox="0 0 280 100" class="preview-chart">
                  <line x1="0" y1="90" x2="280" y2="90" stroke="#EBE3DC" stroke-width="1"/>
                  <rect x="6" y="40" width="28" height="50" rx="2" fill="#E07B5A" opacity="0.8"/>
                  <rect x="42" y="55" width="28" height="35" rx="2" fill="#E07B5A" opacity="0.8"/>
                  <rect x="78" y="20" width="28" height="70" rx="2" fill="#E07B5A" opacity="0.8"/>
                  <rect x="114" y="30" width="28" height="60" rx="2" fill="#E07B5A" opacity="0.8"/>
                  <rect x="150" y="52" width="28" height="38" rx="2" fill="#E07B5A" opacity="0.8"/>
                  <rect x="186" y="10" width="28" height="80" rx="2" fill="#E07B5A" opacity="0.8"/>
                  <rect x="222" y="45" width="28" height="45" rx="2" fill="#E07B5A" opacity="0.8"/>
                  <text v-for="(d,i) in '一二三四五六日'" :key="i" :x="20+i*36" y="98" font-size="9" fill="#8B7E75" text-anchor="middle">{{ d }}</text>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 产品指标 -->
      <section class="section" id="stats">
        <div class="container">
          <p class="eyebrow" style="margin-bottom: 40px;">产品目标</p>
          <div class="grid-3">
            <div class="stat">
              <div class="stat-num">≤ 3<span class="stat-unit">秒</span></div>
              <p class="stat-label">记账操作耗时目标（P95），打开即记，无需多余步骤。</p>
            </div>
            <div class="stat">
              <div class="stat-num">13<span class="stat-unit">类</span></div>
              <p class="stat-label">预设收支分类，覆盖日常消费与收入场景，支持自定义扩展。</p>
            </div>
            <div class="stat">
              <div class="stat-num">≥ 40<span class="stat-unit">%</span></div>
              <p class="stat-label">用户次日留存率目标，温暖体验让记账成为习惯。</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="section cta-section">
        <div class="container cta-inner">
          <h2>准备好开始记账了吗？</h2>
          <p class="lead">完全免费，无需下载。浏览器打开即可使用，支持桌面端与平板。</p>
          <router-link to="/login" class="btn btn-primary btn-lg">免费注册 · 3 秒开始</router-link>
        </div>
      </section>
    </main>

    <footer class="pagefoot">
      <div class="container footer-inner">
        <span>© 2026 DailyTracker · 日常记账助手</span>
        <span class="meta">温暖记账 · 清晰生活 · hello@dailytracker.com</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { PlusCircle, LayoutGrid, Shield } from 'lucide-vue-next'
</script>

<style scoped>
/* === Design Tokens === */
.landing {
  --gap-xs: 8px; --gap-sm: 12px; --gap-md: 20px; --gap-lg: 32px; --gap-xl: 56px; --gap-2xl: 96px;
  --container: 1120px; --gutter: 32px;
  min-height: 100dvh; display: flex; flex-direction: column;
}
.container { max-width: var(--container); margin-inline: auto; padding-inline: var(--gutter); }
.section { padding-block: clamp(48px, 8vw, var(--gap-2xl)); }
.section + .section { border-top: 1px solid var(--border); }
.stack { display: flex; flex-direction: column; }
.row { display: flex; align-items: center; gap: var(--gap-md); }
.row-between { display: flex; align-items: center; justify-content: space-between; gap: var(--gap-md); }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--gap-lg); }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--gap-lg); }
h2 { font-size: clamp(28px, 4vw, 44px); font-weight: 700; line-height: 1.15; letter-spacing: -0.015em; margin: 0; }
.lead { font-size: 18px; line-height: 1.6; color: var(--text-secondary); max-width: 60ch; margin: 0; }
.eyebrow { font-family: ui-monospace, monospace; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--color-primary); margin: 0 0 var(--gap-md); }

/* === Top Nav === */
.topnav { position: sticky; top: 0; z-index: 10; background: rgba(250,247,244,0.94); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); }
.topnav-inner { display: flex; align-items: center; justify-content: space-between; padding-block: 14px; }
.logo { font-size: 20px; font-weight: 700; color: var(--color-primary); }
.topnav nav { display: flex; gap: var(--gap-lg); }
.topnav nav a { font-size: 15px; color: var(--text-secondary); font-weight: 500; text-decoration: none; }
.topnav nav a:hover { color: var(--text-primary); }
.btn-sm { padding: 8px 16px; font-size: 13px; height: auto; }

/* === Hero === */
.hero { padding-block: 0; min-height: 85vh; display: flex; align-items: center; position: relative; overflow: hidden; }
.hero-bg { position: absolute; inset: 0; z-index: 0;
  background: radial-gradient(ellipse 80% 60% at 25% 30%, rgba(224,123,90,0.08) 0%, transparent 60%),
              radial-gradient(ellipse 60% 50% at 75% 70%, rgba(122,165,135,0.06) 0%, transparent 50%),
              linear-gradient(180deg, #FDF8F4 0%, #FAF7F4 40%, #F8F3EE 100%); }
.hero-bg::before { content: ''; position: absolute; inset: 0;
  background-image: repeating-linear-gradient(0deg, transparent, transparent 31px, rgba(74,63,58,0.03) 31px, rgba(74,63,58,0.03) 32px);
  mask-image: linear-gradient(180deg, transparent 10%, black 30%, black 70%, transparent 90%); }
.hero-bg::after { content: ''; position: absolute; right: -60px; top: 50%; transform: translateY(-50%);
  width: 420px; height: 420px; border-radius: 50%;
  background: radial-gradient(circle at 60% 40%, rgba(224,123,90,0.06) 0%, transparent 70%); }
.hero-inner { position: relative; z-index: 1; width: 100%; }
.hero-split { display: grid; grid-template-columns: 1fr 1fr; gap: var(--gap-2xl); align-items: center; min-height: 85vh; }
.hero-text { padding-block: clamp(60px, 10vw, 120px); }
.hero-text h1 { font-size: clamp(40px, 5.5vw, 60px); line-height: 1.1; letter-spacing: -0.02em; margin-bottom: var(--gap-md); }
.hero-text .lead { margin-bottom: var(--gap-lg); }
.hero-cta { display: inline-flex; gap: var(--gap-sm); flex-wrap: wrap; }
.btn-lg { padding: 14px 32px; font-size: 17px; }
.hero-visual { display: flex; align-items: center; justify-content: center; padding-block: clamp(40px, 8vw, 80px); }

/* Journal Frame */
.journal-frame { position: relative; width: 340px; height: 400px; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 6px; box-shadow: 0 1px 2px rgba(74,63,58,0.06), 0 4px 16px rgba(74,63,58,0.1); transform: rotate(-2deg); }
.journal-frame::after { content: ''; position: absolute; inset: 8px; border: 1px solid rgba(74,63,58,0.06); border-radius: 2px; pointer-events: none; }
.journal-inner { position: absolute; inset: 16px; display: flex; flex-direction: column;
  background: linear-gradient(175deg, #FFFDF8 0%, #FEFAF5 100%); border-radius: 2px; overflow: hidden; }
.journal-lines { flex: 1; margin: 12px 16px;
  background: repeating-linear-gradient(0deg, transparent, transparent 27px, rgba(74,63,58,0.08) 27px, rgba(74,63,58,0.08) 28px); }
.journal-entry { padding: 0 4px; font-size: 13px; color: var(--text-primary); line-height: 28px; font-family: ui-monospace, monospace; }
.je-date { color: var(--color-primary); font-weight: 600; }
.je-expense { color: var(--color-primary); }
.je-income { color: var(--color-income); }
.journal-card { position: absolute; bottom: 20px; right: -30px; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 14px 18px; box-shadow: 0 2px 12px rgba(74,63,58,0.1);
  transform: rotate(3deg); z-index: 2; font-size: 12px; min-width: 140px; }
.jc-label { font-size: 10px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.06em; }
.jc-value { font-size: 20px; font-weight: 700; color: var(--color-income); margin: 2px 0; font-family: ui-monospace, monospace; }
.jc-sub { font-size: 10px; color: var(--text-secondary); }

/* === Features === */
.feature-mark { width: 44px; height: 44px; display: grid; place-items: center;
  background: var(--color-primary-light); border-radius: 10px; color: var(--color-primary); margin-bottom: var(--gap-md); }
.feature h3 { margin-bottom: 6px; font-size: 22px; }
.feature p { margin: 0; color: var(--text-secondary); font-size: 15px; line-height: 1.6; }

/* === App Preview === */
.app-preview { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg, 16px); overflow: hidden; box-shadow: var(--shadow-card); }
.app-preview-header { display: flex; align-items: center; gap: 8px; padding: 10px 16px; background: var(--bg-page); border-bottom: 1px solid var(--border); }
.app-preview-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--border); }
.app-preview-dot.accent { background: var(--color-primary); }
.app-preview-label { font-size: 12px; color: var(--text-secondary); margin-left: 8px; }
.app-preview-body { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.preview-toggle { display: flex; gap: 8px; }
.preview-toggle-btn { flex: 1; padding: 10px; border-radius: 8px; border: 1px solid var(--border); font-size: 14px; font-weight: 600; background: transparent; color: var(--text-secondary); }
.preview-toggle-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.preview-amount { text-align: center; padding: 16px; }
.preview-amount-label { font-size: 11px; color: var(--text-secondary); }
.preview-amount-value { font-size: 40px; font-weight: 700; font-family: ui-monospace, monospace; }
.preview-cat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.preview-cat { text-align: center; padding: 8px; border-radius: 8px; border: 1px solid var(--border); font-size: 12px; }
.preview-cat.selected { border: 2px solid var(--color-primary); background: var(--color-primary-light); }
.preview-submit { width: 100%; padding: 12px; border-radius: 8px; background: var(--color-primary); color: #fff; border: none; font-size: 15px; font-weight: 600; }
.preview-kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.preview-kpi { background: var(--color-primary-light); padding: 12px; border-radius: 8px; text-align: center; }
.preview-kpi span { font-size: 11px; color: var(--text-secondary); display: block; }
.preview-kpi b { font-size: 18px; font-weight: 700; }
.text-accent { color: var(--color-primary); }
.text-income { color: var(--color-income); }
.preview-chart { width: 100%; }

/* === Pill === */
.pill { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; background: var(--color-primary-light);
  color: var(--color-primary); border-radius: 999px; font-size: 11px; letter-spacing: 0.04em; text-transform: uppercase; font-family: ui-monospace, monospace; }
.pill-green { background: color-mix(in oklch, #7BA587 16%, transparent); color: #7BA587; }

/* === Stats === */
.stat-num { font-size: clamp(48px, 7vw, 72px); line-height: 0.95; letter-spacing: -0.03em; color: var(--color-primary); font-weight: 700; font-family: system-ui, sans-serif; }
.stat-unit { font-size: 0.45em; opacity: 0.6; margin-left: 2px; }
.stat-label { color: var(--text-secondary); font-size: 14px; margin-top: 8px; max-width: 24ch; }

/* === CTA === */
.cta-section { text-align: center; }
.cta-inner { max-width: 560px; }
.cta-inner .lead { margin: 16px auto 32px; }

/* === Footer === */
.pagefoot { padding-block: var(--gap-xl); color: var(--text-secondary); font-size: 14px; border-top: 1px solid var(--border); margin-top: auto; }
.footer-inner { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
.meta { font-size: 13px; }

/* === Buttons === */
.btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: var(--radius-sm); border: 1px solid transparent; font-size: 15px; font-weight: 600; }
.btn-primary { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.btn-primary:hover { background: var(--color-primary-hover); }
.btn-secondary { background: transparent; color: var(--text-primary); border-color: var(--border); }

@media (max-width: 920px) {
  .hero-split { grid-template-columns: 1fr; min-height: auto; }
  .hero { min-height: auto; }
  .hero-visual { padding-block: 0 40px; }
  .journal-frame { width: 260px; height: 320px; }
  .journal-card { right: -10px; bottom: 10px; }
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .topnav nav { display: none; }
  .container { padding-inline: 16px; }
}
</style>
