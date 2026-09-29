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

專案資料夾：`C:\master\cloud_course\iot_project`
GitHub Repository：`MERYAN-421/iot_project`

---

## 2. Development Environment

* OS: Windows
* Language: Python 3.14
* Version Control: Git
* Remote Repository: GitHub
* AI Coding Tool: Codex（接續 Antigravity 既有成果）
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
├── requirements.txt      ← requests, pandas, python-dotenv, certifi, truststore, streamlit
├── config.py             ← 從 .env 載入 CWA_API_KEY
├── cwa_api.py            ← 呼叫 CWA F-C0032-001 API，回傳 JSON
├── data_parser.py        ← 解析 JSON，提取 MinT/MaxT → Pandas DataFrame
├── database.py           ← SQLite 資料庫操作 (init_db, save_forecasts, get_forecasts, get_total_count)
├── weather.db            ← 本機 SQLite 資料庫 (不進 Git)
├── main.py               ← 後端資料同步進入點 (ETL / Sync Pipeline)
├── app.py                ← 前端 Streamlit Web Dashboard 進入點
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
* **Phase 2 Milestone 1 完成：** SQLite 整合 (`database.py`、`weather.db`、`TemperatureForecasts` 表建立、66 筆資料存入與查詢驗證)
* **Phase 2.1 完成：** SQLite 重複資料處理與 UPSERT 機制 (UNIQUE constraint、`idx_forecast_unique` 索引、`ON CONFLICT DO UPDATE`、分開回報新增/更新/總筆數)
* **Phase 2.2 完成：** 資料語意精確化與查詢模組建置 (4-part metrics: inserted / changed / unchanged / total；實作支援 Phase 3 的查詢函式)
* **Phase 3 Milestone 1 完成：** Streamlit Web App (`app.py`、sidebar 22 地區下拉選單、最新預報指標卡片、氣溫趨勢折線圖、詳細資料表，全程透過 `database.py` 存取)
* **Phase 3.1 完成：** 全台總覽與分頁整合 (`app.py` 整合「全台總覽」與「縣市查詢」雙分頁、極端溫指標卡片支援多地區並列、全台 22 縣市氣溫比較長條圖與總覽表格)

---

## 7. Current Task

Phase 4 Milestone 2：介面改版、行政邊界與真實測站已完成本機實作／測試，待部署驗證。
Streamlit Community Cloud 公開展示已部署並完成瀏覽器驗證：https://iotproject-hpwvgzzmi2zm7wbuxkerht.streamlit.app/
使用 cloud_app.py 作為雲端入口；接受展示環境 SQLite 歷史資料不永久保存。

---

## 8. TODO

* [x] 定義專案最終目標
* [x] 決定資料來源 (CWA F-C0032-001)
* [x] 設計 Python 專案結構
* [x] 建立第一版可執行程式 (Phase 1)
* [x] 測試資料流程 (66 rows, 22 regions 驗證通過)
* [x] Phase 2: SQLite 儲存 (weather.db / TemperatureForecasts - Milestone 1, 2.1 & 2.2 完成)
* [x] Phase 3: Streamlit Web App (Milestone 1 & 3.1 全台總覽完成)
* [x] Phase 4: Folium 台灣地圖
* [ ] Docker 實機驗證（Dockerfile / compose.yaml 已完成；本機尚無 Docker）
* [x] 撰寫 README
* [x] 建立 GitHub Demo / deployment（Streamlit Community Cloud）

---

## 9. Important Decisions

目前已確定：

* Git 預設 branch 使用 `main`
* GitHub 作為主要 remote repository
* Codex 接續 Antigravity，負責本機實作、測試與部署準備
* ChatGPT 負責規劃、解釋、review 與 debugging
* `project_content.md` 作為 AI 之間共享專案上下文的主要文件
* API Endpoint：`F-C0032-001`（36小時天氣預報，含 MinT / MaxT）
* API Key 存放於本機 `.env`，不進 Git
* Windows 終端機需使用 `python -X utf8` 執行以正確顯示中文
* SSL 處理策略：先嘗試 certifi，失敗後 fallback 至 `verify=False` 並印出警告
  * 測試結果：`verify=True`、`certifi`、`truststore` 皆因 CWA 憑證缺少 SKI (RFC 5280) 而失敗
  * `verify=False` 為目前唯一可用方案，待 CWA 更新憑證後應改回 `verify=True`
* 資料庫與資料模型設計（Data Model Semantics）：
  * 資料庫檔案：`weather.db`（已列入 `.gitignore`）
  * 主鍵 (Primary Key)：`id INTEGER PRIMARY KEY AUTOINCREMENT`，維持單一自增主鍵
  * 複合唯一限制 (Composite Unique Constraint)：`UNIQUE(regionName, startTime)`，確保同一地區與同一預報時段僅有一筆最新紀錄
  * 唯一索引：`idx_forecast_unique ON TemperatureForecasts (regionName, startTime)`，向下相容現有資料庫
  * 歷史累積性：舊預報時段持續保留於資料庫中，隨著時間推移自然形成歷史預報資料庫
  * 無版本歷程 (No Revision Versioning)：當 CWA 針對同一預報時段更新 `minT` 或 `maxT` 時，以 UPSERT 原地覆寫更新，不保留同一時段修訂前之歷史舊版本
  * 同步指標 (Sync Metrics)：精準劃分「新插入筆數 (inserted)」、「溫度實質變更筆數 (changed)」、「溫度未變更筆數 (unchanged)」與「同步後總筆數 (total)」
  * 查詢介面模組化：提供 `get_forecasts_by_region`、`get_latest_forecasts(periods=3)`、`get_all_regions` 與 `get_forecasts_by_time`，為 Phase 3 Streamlit 奠定標準資料存取層
* Web Dashboard 架構設計（Phase 3 & 3.1）：
  * `app.py` 為 Streamlit 應用進入點
  * 雙分頁架構：`st.tabs(["🗺️ 全台總覽", "🏙️ 縣市查詢"])`，側邊欄地區選單維持全域可見
  * 嚴格遵守架構分層：`app.py` 完全不含原生 SQL，全數經由 `database.py` 存取
  * 全台總覽防禦性設計：具備空資料檢查 (empty guard) 與單一時段唯一性驗證 (`len(distinct_times) == 1`)
  * 極端溫處理：支援多縣市並列 (ties)，以字串列表清楚標註所有最高溫與最低溫縣市
  * 比較圖表：跨縣市離散比較採用原生 `st.bar_chart`，維持輕量無額外依賴
  * 縣市查詢時序分析：折線圖 X 軸預先轉為 Pandas datetime (`pd.to_datetime`)，詳細預報表格時間明確標記為「建立時間 (Created At)」

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

### Phase 2 Milestone 1 — SQLite Integration
* 建立 `database.py`，封裝 `init_db`、`save_forecasts`、`get_forecasts` 與 `get_total_count`
* 建立資料庫 `weather.db` 與資料表 `TemperatureForecasts` (含自動遞增 `id` 與 `created_at` timestamp)
* 更新 `main.py` 整合端到端流程：API 取得 → 解析 → 存入 SQLite → 查詢最新 5 筆 sample 驗證
* 實施 append 模式並驗證 66 筆資料成功寫入與讀出 (`ORDER BY id DESC`)
* 確認 `weather.db` 已被 `.gitignore` 排除不進 Git

### Phase 2.1 — SQLite UPSERT & Deduplication
* 在 `database.py` 的 `init_db()` 加入 `UNIQUE(regionName, startTime)` constraint 與 `idx_forecast_unique` 索引，並在建立索引前自動檢查既有重複 key
* 重構 `save_forecasts()` 為 SQLite UPSERT 語法 (`ON CONFLICT DO UPDATE SET minT, maxT`)，保持氣溫預測為 CWA 最新版本
* 實作分類比對機制，獨立統計並回傳 `inserted`、`updated` 與 `total` 筆數
* 更新 `main.py` 輸出，清楚呈現同步統計
* 實測二次執行：確認 0 筆新增、66 筆更新、資料庫總數維持 66 筆不膨脹

### Phase 2.2 — Data Semantics & Query Functions
* 優化同步指標：精確區分 `inserted`、`changed`（`minT` 或 `maxT` 實際有異動）、`unchanged`（完全一致）與 `total`
* 實作 Phase 3 查詢函式：
  * `get_forecasts_by_region(region_name)`：按 `startTime ASC` 查詢單一地區時序預報
  * `get_latest_forecasts(periods=3)`：取得最新 N 個時段的所有地區預報，按 `startTime ASC, regionName ASC` 排序
  * `get_all_regions()`：取得排序後的不重複地區清單（供 Streamlit 下拉選單使用）
  * `get_forecasts_by_time(start_time)`：按指定時段切片查詢全台預報（供地圖或時段篩選使用）
* 明確界定資料模型語意：複合唯一限制 (composite unique constraint) 非複合主鍵；舊時段累加保存；同一時段修訂採原地更新不留歷程版本
* 通過全方位測試（實測同步、重複同步、手動變更溫度、查詢函式驗證、Git ignore 狀態確認）

### Phase 3 Milestone 1 — Streamlit Web App
* 將 `streamlit` 加入 `requirements.txt`
* 建立 `app.py` 作為 Web Dashboard 進入點，嚴格禁止原生 SQL，全數呼叫 `database.py` 模組
* 實作側邊欄 22 地區 `st.sidebar.selectbox` 下拉選單（預設臺北市）
* 實作最新時段天氣指標卡片（`df.iloc[-1]` 取得預報時段、最低溫、最高溫）
* 實作氣溫趨勢折線圖（`pd.to_datetime` 轉換 X 軸）與預報詳細資料表格（時間標記為 Created At）
* 通過自動化驗證：服務成功啟動 (HTTP 200)、22 個地區選單切換正常、圖表與指標動態更新、無 Traceback

### Phase 3.1 — Nationwide Overview Tab
* 在 `app.py` 實作 `st.tabs(["🗺️ 全台總覽", "🏙️ 縣市查詢"])` 雙分頁佈局
* 全台總覽分頁整合 `get_latest_forecasts(periods=1)`，加入空資料防護與單一時段驗證
* 實作全台最高溫與最低溫指標卡，並完整支援多縣市同溫並列 (ties) 顯示
* 實作全台 22 縣市氣溫比較長條圖 (`st.bar_chart`) 與全台最新預報表格
* 驗證縣市切換不影響全台總覽，服務運作正常且無任何 Traceback






### Phase 4 Milestone 1 — Taiwan Map（2026-09-30）
* 新增 weather_map.py，保存 22 縣市代表座標並建立 Folium 地圖，含離島初始視野、Tooltip / Popup、最高溫四色分級與缺值灰色。
* app.py 新增「🌏 台灣地圖」第三分頁，使用 get_available_forecast_times / get_forecasts_by_time 選取時段；列出缺少或無座標的縣市。
* database.py 新增時段清單查詢；連線改以 closing 確實關閉，修正 Windows 檔案鎖；預設 DB 路徑固定在程式目錄，支援 WEATHER_DB_PATH。
* 已確認 folium / streamlit-folium 依賴存在；未加入多邊形與 AI。
* 7 項 unittest / Streamlit AppTest 通過：時段與 22 縣市、溫度边界與缺值、標記、分頁切換、空資料與雲端快取／失敗處理。
* HTTP 200，瀏覽器確認底圖、標記與 Popup 正常；真實 CWA → 臨時 SQLite 同步 66 筆成功，未覆寫本機資料。

### 部署準備（2026-09-30）
* README.md 包含本機、Docker、Cloud 操作步驟與資料語意。
* cloud_app.py / sync_service.py 支援雲端首次造訪同步；成功結果快取一小時，後續造訪再觸發更新；失敗時顯示既有資料且不輸出含金鑰的請求例外。
* Dockerfile / compose.yaml / .dockerignore：非 root 容器、持久 volume、獨立同步服務與健康檢查；Docker 未安装，尚未實際建置。
* 使用者選擇 Streamlit Community Cloud 展示，接受歷史 SQLite 在重啟後可能遺失；公開網址已完成：https://iotproject-hpwvgzzmi2zm7wbuxkerht.streamlit.app/
* 既有 SSL fallback 保留：本次 CWA 驗證失敗後以 verify=False 成功，這仍是待改善的既有限制，不能視為完整驗證連線。

### 公開部署驗證（2026-09-30）
* 使用者完成 Streamlit Community Cloud 部署；未登入的瀏覽器可直接開啟公開網址。
* 全台總覽顯示 22 縣市；三個分頁存在；地圖 22 個標記、底圖與 Popup 正常。
* 實測時段由 18:00 切換為 06:00，南投最高溫由 31°C 更新為 35°C，標記與 Popup 同步更新。
* Docker 實機建置仍未驗證，既有 SSL fallback 限制仍保留。

### Phase 4 Milestone 2 — 島嶼氣象（2026-09-30）
* 使用者要求擴充觀測站、行政區邊界、美化資訊框；此需求取代 Milestone 1 的「不加入多邊形」限制。
* 四分頁重設：天氣地圖／全台總覽／縣市預報／即時測站；新增 ui.py 管理一致卡片與視覺風格。
* 接入 O-A0001-001 全測站逐時觀測，實測取得 876 站；保留 WGS84 真實座標、氣溫、濕度、風速、當日雨量、觀測時間。
* 預報加入 Wx / PoP / CI / endTime，改為依 startTime 對齊元素，避免依陣列位置配錯時段。
* database.py 原地增欄且保留既有預報；StationObservations 原子替換最新有效快照，空回應不清除舊資料。SQL 仍全部集中於 database.py。
* geography.py 解碼隨附 Taiwan Atlas 縣市界線，台／臺名稱正規化；22 縣市皆有閉合多邊形，含離島。
* 地圖點選連動縣市選單與資訊卡、邊界高亮／聚焦；測站群集與站點 Popup；實測與預報明確分開。
* 新增全台溫度區間圖（修正原本堆疊氣溫）、降雨排序、測站搜尋與 CSV 下載。
* 雲端預報快取 1 小時，測站快取 10 分鐘（含失敗冷卻）；超過 2 小時或未知時間觀測顯示過期，圖層預設排除。
* 17 項離線 unittest / AppTest 通過；本機真實同步 66 筆預報與 876 個測站；正式部署前進行瀏覽器點選檢查。
* Docker 加入 assets 與主題設定；本機 Docker 不可用，容器建置仍未驗證。
