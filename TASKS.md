# TASKS：品牌 AI 客服證據守門系統 MVP

## Phase 0 — 骨架（已完成，不依賴 91APP）
- [x] PRD.md / ARCHITECTURE.md
- [x] 後端：FastAPI + SQLite，ContentChunk / EvalQuestion 資料模型
- [x] 決策表（decision_table.yaml + decision_table.py），意圖 -> 最低證據等級/語氣/fallback 規則
- [x] 意圖分類（關鍵字規則）
- [x] TF-IDF 檢索 + 證據等級過濾（**已修正中文斷詞 bug**，改用字元 n-gram）
- [x] 事後驗證（禁用詞檢查）
- [x] Pipeline 串接，回傳完整 trace
- [x] REST API：內容 CRUD、問答測試、評估報告
- [x] 前端：問答測試頁（攤開完整過程）、內容管理頁、評估報告頁
- [x] 範例資料（4 條範例內容、4 條測試問題）
- [x] 本機驗證：4 個測試案例（含醫療聲明陷阱題、一般問題、客訴）全部通過
- [x] 發現並修正設計漏洞：COMPLAINT（客訴）原本會因為檢索到不相關內容而被模型接手回答，
      已加上 `always_fallback` 規則，客訴一律轉真人

## Phase 1 — 填入真實內容（下一步，你可以現在開始）
- [ ] 挑一個現有客戶（建議醫之方或 Dr's Formula，因為你已經有審核過的內容跟信任關係）
- [ ] 把該品牌至少 10-20 條實際內容，依證據等級（A/B/C/D）標記後填入「內容管理」頁面
- [ ] 從真實客服紀錄或常見問題裡，整理 10-20 題測試問題（含至少 3-5 題「陷阱題」——
      故意問超出現有證據等級的問題，驗證系統會不會正確攔截）
- [ ] 跑一次評估報告，記錄準確率，這份報告是你對外談合作/談客戶的第一份實證

## Phase 2 — 品質提升（視 Phase 1 結果決定優先順序）
- [ ] 如果 TF-IDF 檢索準確度不夠，換成真的 embedding（例如用 Gemini 的 embedding API）
- [ ] 如果關鍵字意圖分類漏判太多，換成用 LLM 做結構化分類（function calling / JSON schema）
- [ ] 申請 GEMINI_API_KEY，把 Mock 模型換成真實模型，重新跑一次評估報告比較

## Phase 3 — 接 91APP（等 Partner Program 有回覆再開始）
- [ ] 把 `llm_client.py` 的介面模式，套用到「91APP webhook 轉接層」——寫一個新的
      adapter，把 AgentOne 的訊息事件轉成呼叫這裡的 pipeline，回傳結果送回去
- [ ] 在 91APP 沙盒環境測試

## 環境限制記錄
- SQLite 資料庫檔案不能放在雲端同步監控的資料夾內跑，會出現 `disk I/O error`
  （已在 README.md 記錄，需要的話把 `app/db.py` 的路徑改到非同步資料夾）
