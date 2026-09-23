# PROJECT_CONTENT

## 1. Project Name

Taiwan Weather Forecast

## 2. Project Goal

建立一個台灣天氣預報資料應用。

使用中央氣象署 CWA Open Data API 取得天氣預報資料，
使用 Python Requests 取得 JSON，
解析並整理各地區的最低氣溫與最高氣溫，
使用 Pandas 進行資料整理，
使用 SQLite 儲存歷史資料，
最後使用 Streamlit 建立互動式 Web Dashboard。

後續將加入 Folium 台灣地圖視覺化，
並探索 AI 分析與其他氣象應用。


## 3. Main Technology Stack

- Python
- CWA Open Data API
- Requests
- JSON
- Pandas
- SQLite
- Streamlit
- Folium
- Git
- GitHub


## 4. System Architecture

CWA Open Data API
→ Requests
→ JSON
→ Data Processing
→ Pandas DataFrame
→ SQLite
→ SQL Query
→ Streamlit
→ Charts / Tables / Maps


## 5. Development Phases

### Phase 1 - CWA API

- 註冊 CWA Open Data
- 取得 API Key
- 選擇氣象資料集
- 使用 Requests 呼叫 API
- 取得 JSON


### Phase 2 - Data Processing

- 分析 JSON 結構
- 找到 location
- 找到 weatherElement
- 提取 MinT
- 提取 MaxT
- 將資料轉為 Pandas DataFrame


### Phase 3 - Database

建立 SQLite：

weather.db

資料表：

TemperatureForecasts

預計欄位：

- id
- regionName
- dataDate
- minT
- maxT


### Phase 4 - Streamlit Web App

建立互動式 Web App。

功能：

- 選擇地區
- 顯示最低 / 最高溫
- 顯示資料表
- 顯示折線圖
- 查詢 SQLite 資料


### Phase 5 - Taiwan Map

使用 Folium + Streamlit：

- 台灣地圖
- 各地區氣溫標記
- 顏色代表不同溫度區間
- 日期選擇
- 顯示指定日期天氣


### Phase 6 - Future Extensions

- 更多 CWA API
- 天氣提醒
- Line Bot
- 旅遊行程建議
- 農業 / 防災應用
- AI 天氣資料分析
- AI 預測模型


## 6. Current Milestone

目前先完成 MVP 1：

CWA API
→ JSON
→ 提取 MinT / MaxT
→ Pandas DataFrame

目前不要先實作：

- SQLite
- Streamlit
- Folium
- AI


## 7. AI Development Rules

Antigravity 在修改程式前應先閱讀本文件。

開發原則：

1. 一次只完成一個 milestone。
2. 不要一次產生整個完整系統。
3. 每個 Python module 保持單一職責。
4. API Key 不得直接寫入 Git repository。
5. API Key 應存放於 .env。
6. .env 必須加入 .gitignore。
7. 每完成一階段先測試，再進入下一階段。
8. 新增重要架構或決策後，更新本文件。


## 8. Current Progress

Completed:

- Local Git repository
- GitHub remote repository
- Antigravity local project
- PROJECT_CONTENT.md
- Overall project plan

Current:

Phase 1 - CWA API integration


## 9. Current Task

取得 CWA API 天氣預報 JSON，
了解 API response 的資料結構。

接著提取：

- regionName
- date/time
- MinT
- MaxT

並轉換成 Pandas DataFrame。


## 10. Source of Truth

PROJECT_CONTENT.md 是本專案主要 AI context。

ChatGPT：
- Architecture
- Explanation
- Planning
- Code review
- Debugging

Antigravity：
- Implementation
- File modification
- Local testing assistance

GitHub：
- Version control
- Project source code