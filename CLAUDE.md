# CLAUDE.md — 品牌 AI 客服證據守門系統 MVP

## 這是什麼
驗證「證據分級內容 + 決策表 + 事後驗證」這套機制的 MVP，不是要接上 91APP
才算完成——91APP 整合是 Phase 3，現階段的重點是 Phase 1：把真實品牌內容
填進去、跑出第一份評估報告。詳見 `PRD.md`、`ARCHITECTURE.md`、`TASKS.md`。

## 重要慣例
- 決策表（`backend/app/decision_table.yaml`）是給非工程師也能審的規則，改規則
  優先改這個 YAML 檔，不要把規則寫死在 Python 程式碼裡
- LLM 呼叫全部集中在 `backend/app/llm_client.py`，預設用不需要金鑰的 Mock
  provider；真的要接模型時設環境變數 `GEMINI_API_KEY`，其他程式碼不用動
- 涉及「這類意圖一律不讓模型回答」的規則（例如客訴），要用 `always_fallback: true`
  而不是把 `min_evidence_tier` 設到最低——後者會被隨便什麼不相關內容打通過濾，
  等於沒有真的攔截（這是我們在建置時踩到的真實 bug，教訓記在這裡）
- 中文檢索：`retrieval.py` 用的是字元 n-gram TF-IDF（`analyzer="char_wb"`），
  不是預設的英文斷詞方式——如果之後有人「優化」把它改回預設設定，中文檢索會
  整個失效且不會報錯，只會安靜地檢索不到任何內容

## 已知環境限制
SQLite 資料庫檔案不能放在雲端同步監控的資料夾內跑（會出現 `disk I/O error`），
如果这個專案資料夾被 OneDrive 之類的軟體同步，把 `app/db.py` 的 `DATABASE_URL`
改到本機非同步路徑。

## 常用指令
```bash
# 後端
cd backend
pip install -r requirements.txt
python seed_data.py
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 文件更新原則
決策規則變了先改 `decision_table.yaml`；填了新的真實內容或跑了新的評估報告，
回來更新 `TASKS.md` 的 Phase 1 進度跟準確率數字。
