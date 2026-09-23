# Project Context

## 1. Project Goal

建立一個台灣天氣預報資料應用 (Taiwan Weather Forecast)。

使用中央氣象署 CWA Open Data API 取得天氣預報資料，
使用 Python Requests 取得 JSON，
解析並整理各地區的最低氣溫與最高氣溫，
使用 Pandas 進行資料整理，
使用 SQLite 儲存歷史資料，
最後使用 Streamlit 建立互動式 Web Dashboard。

後續將加入 Folium 台灣地圖視覺化，並探索 AI 分析與其他氣象應用。

專案資料夾：`D:\AIlot\L3_CWA`
GitHub Repository：`MERYAN-421/iot_project`

---

## 2. Development Environment

* OS: Windows
* Language: Python 3.14
* Version Control: Git
* Remote Repository: GitHub
* AI Coding Tool: Antigravity
* AI Planning / Review: ChatGPT

---

## 3. Project Workflow

主要開發流程：

ChatGPT
→ 討論架構、演算法、需求與 Debug

Antigravity
→ 實際修改本機程式碼

Local Git
→ 管理版本

GitHub
→ 保存與同步專案

流程：

1. 與 ChatGPT 討論需求
2. 更新 `project_content.md`
3. Antigravity 讀取此文件
4. Antigravity 修改程式
5. 本機執行與測試
6. Git commit
7. Git push
8. ChatGPT review 最新版本
9. 繼續下一階段

---

## 4. AI Instructions

在開始修改程式碼之前：

1. 先閱讀 `project_content.md`
2. 了解目前專案目標與架構
3. 不要任意修改已確定的架構
4. 若需要大幅修改架構，先說明原因
5. 每次完成任務後，更新 Current Progress
6. 保持程式碼簡單、可讀、模組化
7. 不要把 API key、password 或其他敏感資訊寫入 Git repository

---

## 5. Current Project Structure

```text
L3_CWA/
├── .env                  ← API Key (本機存放，不進 Git)
├── .env.example          ← Key 格式範本 (可進 Git)
├── .gitignore
├── requirements.txt      ← requests, pandas, python-dotenv, certifi, truststore
├── config.py             ← 從 .env 載入 CWA_API_KEY
├── cwa_api.py            ← 呼叫 CWA F-C0032-001 API，回傳 JSON
├── data_parser.py        ← 解析 JSON，提取 MinT/MaxT → Pandas DataFrame
├── main.py               ← 程式進入點
├── PROJECT_CONTENT.md    ← AI context 文件 (本文件)
└── myPlan/
    └── project_plan.md   ← 整體專案計畫
```

---

## 6. Current Progress

已完成：

* 建立本機專案資料夾
* 建立 Git repository
* GitHub repository 建立完成
* 本機 Git 與 GitHub 已連接
* Antigravity 已連接本機 Project
* 建立 `project_content.md` 與 `project_plan.md`
* **Phase 1 完成：** CWA API → JSON → Pandas DataFrame (66 rows, 22 regions)
* **Phase 1.5 完成：** SSL 調查與修正、程式碼清理、文件更新

---

## 7. Current Task

Phase 1 與 Phase 1.5 已完成。
下一步：Phase 2 — SQLite 資料庫整合。

---

## 8. TODO

* [x] 定義專案最終目標
* [x] 決定資料來源 (CWA F-C0032-001)
* [x] 設計 Python 專案結構
* [x] 建立第一版可執行程式 (Phase 1)
* [x] 測試資料流程 (66 rows, 22 regions 驗證通過)
* [ ] Phase 2: SQLite 儲存 (weather.db / TemperatureForecasts)
* [ ] Phase 3: Streamlit Web App
* [ ] Phase 4: Folium 台灣地圖
* [ ] 建立 Docker 環境
* [ ] 撰寫 README
* [ ] 建立 GitHub Demo / deployment

---

## 9. Important Decisions

目前已確定：

* Git 預設 branch 使用 `main`
* GitHub 作為主要 remote repository
* Antigravity 負責主要 coding
* ChatGPT 負責規劃、解釋、review 與 debugging
* `project_content.md` 作為 AI 之間共享專案上下文的主要文件
* API Endpoint：`F-C0032-001`（36小時天氣預報，含 MinT / MaxT）
* API Key 存放於本機 `.env`，不進 Git
* Windows 終端機需使用 `python -X utf8` 執行以正確顯示中文
* SSL 處理策略：先嘗試 certifi，失敗後 fallback 至 `verify=False` 並印出警告
  * 測試結果：`verify=True`、`certifi`、`truststore` 皆因 CWA 憑證缺少 SKI (RFC 5280) 而失敗
  * `verify=False` 為目前唯一可用方案，待 CWA 更新憑證後應改回 `verify=True`

---

## 10. Change Log

### Initial
* 建立 Git / GitHub workflow
* 建立 Antigravity local project
* 建立 project context 文件

### Phase 1 — CWA API Integration
* 建立 `config.py`、`cwa_api.py`、`data_parser.py`、`main.py`
* 成功呼叫 CWA F-C0032-001 API
* 解析 66 筆資料（22 地區 × 3 時段），MinT / MaxT 正確提取
* 修正 Windows 終端機中文顯示問題（UTF-8 encoding）

### Phase 1.5 — Code Quality & SSL Investigation
* 調查並測試三種 SSL 方案（verify=True、certifi、truststore）
* 確認 CWA 憑證缺少 SKI (RFC 5280)，所有標準驗證方案均失敗
* 重構 `cwa_api.py`：移除不準確描述、改為 try/except fallback 結構、移除全域警告抑制
* 修正 `data_parser.py`：移除未使用的變數 `i`
* 更新 `PROJECT_CONTENT.md` 以反映實際進度
