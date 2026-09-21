<template>
  <div class="app">
    <header class="app-header">
      <h1>品牌 AI 客服證據守門系統</h1>
      <nav>
        <RouterLink to="/chat">問答測試</RouterLink>
        <RouterLink to="/content">內容管理</RouterLink>
        <RouterLink to="/eval">評估報告</RouterLink>
      </nav>
    </header>
    <main><RouterView /></main>
  </div>
</template>

<style>
body { margin: 0; font-family: -apple-system, "Segoe UI", "PingFang TC", "Microsoft JhengHei", sans-serif; background: #0f1115; color: #eaeaea; }
.app-header { padding: 16px 24px; border-bottom: 1px solid #262a33; display: flex; align-items: center; justify-content: space-between; }
.app-header h1 { font-size: 18px; }
.app-header nav a { margin-left: 16px; color: #9db4ff; text-decoration: none; }
main { max-width: 960px; margin: 0 auto; padding: 24px; }
table { width: 100%; border-collapse: collapse; margin-top: 12px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #262a33; font-size: 13px; vertical-align: top; }
input, select, textarea, button { font-family: inherit; }
input, select, textarea { width: 100%; box-sizing: border-box; padding: 8px 10px; background: #1a1d24; border: 1px solid #2c313c; border-radius: 6px; color: #eaeaea; font-size: 14px; }
button { padding: 8px 16px; background: #4c6fff; border: none; border-radius: 6px; color: white; cursor: pointer; font-size: 14px; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
.tier-A { color: #6bffa0; }
.tier-B { color: #8ac6e4; }
.tier-C { color: #e4e08a; }
.tier-D { color: #e48a8a; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; }
.badge.blocked { background: #3a1e1e; color: #e48a8a; }
.badge.answered { background: #1e3a24; color: #8ae4a0; }
</style>
