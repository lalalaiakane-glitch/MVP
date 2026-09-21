# ARCHITECTURE：品牌 AI 客服證據守門系統（Phase 0 MVP）

## 總覽

```
[Vue3 前端]  <-- REST/JSON -->  [FastAPI 後端]
                                      |
                    +-----------------+-----------------+
                    |                 |                 |
              [SQLite 資料庫]   [決策表 YAML]      [LLM Client]
              (內容+證據等級)   (意圖->規則)      (mock 或 Gemini，可抽換)
```

- 後端用 Python + FastAPI：這一層做的是檢索、意圖判斷、決策表查詢、prompt 組裝、事後驗證，這些都是資料處理跟規則邏輯，Python 生態（後續要換真的 embedding 模型）比較順手
- 前端用 Vue3：跟你其他專案一致的技術棧
- 資料庫先用 SQLite（單一檔案，零安裝），之後要多人共用再換 PostgreSQL
- 檢索先用 TF-IDF（scikit-learn），不用任何外部 API，MVP 階段重點是驗證「證據等級過濾」這個邏輯有沒有用，不是驗證檢索演算法多先進
- LLM 呼叫做成介面（`LLMClient`），預設是 `mock` provider（不用任何金鑰，回傳固定格式的假回答方便測試整條流程），可以切換成 `gemini` provider（沿用之前討論過的 Google AI Studio 免卡免費額度）

## 核心模組

```
backend/app/
  main.py              # FastAPI 進入點
  db.py                # SQLite + SQLAlchemy 設定
  models.py            # ContentChunk、EvalQuestion 等資料模型
  retrieval.py         # TF-IDF 檢索 + 依證據等級過濾
  intent.py            # 關鍵字規則判斷問題意圖
  decision_table.py    # 讀取 decision_table.yaml，依意圖查規則
  decision_table.yaml  # 決策表本體（意圖 -> 最低證據等級/語氣/找不到證據時的行為）
  llm_client.py        # LLMClient 介面：mock / gemini 兩種實作
  validation.py        # 事後驗證：禁用詞檢查、引用來源檢查
  pipeline.py           # 串起 intent -> retrieval -> decision -> prompt -> llm -> validation，回傳完整 trace
  routers/
    content.py         # 內容 CRUD API
    chat.py             # POST /api/chat，執行 pipeline，回傳完整過程
    eval.py             # POST /api/eval/run，跑一批測試問題，回傳報告
  seed_data.py          # 灌入範例內容（標記為範例，非真實品牌資料）
```

## 資料模型

**ContentChunk**（對應 PRD 裡的證據分級內容）

| 欄位 | 說明 |
|---|---|
| id | 主鍵 |
| brand_id | 品牌代碼（MVP 先固定一個範例品牌） |
| product_id | 適用產品 |
| text | 內容本文 |
| evidence_tier | A/B/C/D |
| claim_type | efficacy_claim / ingredient_fact / anecdotal / usage_instruction |
| source_citation | 來源引用 |
| last_reviewed_at | 最後審核日期 |

**EvalQuestion**（評估用測試問題）

| 欄位 | 說明 |
|---|---|
| id | 主鍵 |
| question | 測試問題文字 |
| expected_intent | 預期應該被判斷成什麼意圖 |
| expect_blocked | 預期是否應該被擋下來（true/false） |
| notes | 備註（例如：這是個容易誘導模型亂講的陷阱題） |

## Pipeline 流程（對應之前聊過的 Step 1-5）

1. `intent.classify(question)` → 回傳意圖分類（關鍵字規則，MVP 先不用 ML 分類器）
2. `decision_table.lookup(intent)` → 回傳規則：`min_evidence_tier`、`allowed_tone`、`fallback_action`
3. `retrieval.search(question, product_id, min_evidence_tier)` → TF-IDF 檢索，只回傳符合最低證據等級的內容
4. 如果檢索不到符合等級的內容 → 直接執行 `fallback_action`（拒答/轉真人），不呼叫 LLM
5. 否則組出限定內容的 prompt → `llm_client.generate(prompt)` → 呼叫模型
6. `validation.check(response, chunks_used, intent)` → 檢查禁用詞、檢查有沒有引用來源
7. 回傳完整 trace 給前端：意圖、檢索到的內容與等級、決策表規則、最終 prompt、模型回答、驗證結果

前端的問答測試頁面，就是把這個 trace 完整攤開顯示——這是對外展示「這不是黑箱」的關鍵畫面。

## 已知限制（刻意先不解決）

- TF-IDF 檢索在內容量大、用詞差異大時會抓不準，之後要換成真的 embedding + 向量資料庫
- 意圖分類用關鍵字規則，遇到隱晦問法會漏判，之後可以換成一個小分類模型或用 LLM 做結構化分類
- 目前是單一品牌、單一語言，沒有多租戶
