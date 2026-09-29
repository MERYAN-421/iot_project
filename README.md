# 🌤️ Taiwan Weather Forecast｜台灣天氣預報

使用中央氣象署 F-C0032-001 的 36 小時預報，呈現全台 22 縣市最低／最高氣溫。

- **全台總覽**：極端溫度（含並列縣市）、氣溫比較圖與資料表。
- **縣市查詢**：地區選擇、各預報時段指標與趨勢折線圖。
- **台灣地圖**：預報時段選擇、22 縣市代表座標、溫度配色、提示與點擊視窗，含離島。

## 本機啟動（PowerShell）

在專案資料夾執行；已驗證環境為 Python 3.14。

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
# 編輯 .env，填入自己的 CWA_API_KEY；已有 .env 時不要覆蓋。
.\.venv\Scripts\python -X utf8 main.py
.\.venv\Scripts\python -m streamlit run app.py
```

瀏覽器開啟 <http://localhost:8501>。之後執行 `main.py` 同步，再重新整理頁面。
API Key 可向 [中央氣象署開放資料平台](https://opendata.cwa.gov.tw/) 申請。
資料庫未初始化或沒有資料時，介面會提示同步，不會顯示空白地圖。

## 公開網址：Streamlit Community Cloud

1. 將程式碼推送到 `MERYAN-421/iot_project` 的 `main` 分支。
2. 登入 [Streamlit Community Cloud](https://share.streamlit.io/)，選擇 **Create app**。
3. Repository 填 `MERYAN-421/iot_project`；Branch 填 `main`；Main file path 填 **`cloud_app.py`**。
4. Advanced settings 選 Python **3.14**，Secrets 填入下列 TOML（填入真實 Key，勿提交到 Git）：

   ```toml
   CWA_API_KEY = "你的中央氣象署 API Key"
   ```

5. 部署後使用平台實際產生的 `https://….streamlit.app` 網址；於分享設定確認開放給所有人。

`cloud_app.py` 會在首次開啟時同步資料。成功結果快取一小時，過期後於下一次頁面執行再同步；
這不是無人造訪也運行的排程。同步失敗時保留已儲存資料，下一次頁面執行可重試。
無 API Key 且無既有資料時，必須先完成 Secrets 設定才會有天氣資料。

Community Cloud 作為展示環境：SQLite 不作永久保存保證，重啟或重新部署後歷史可能遺失。
需要永久歷史時，改用具持久磁碟的主機／Docker volume。
目前倉庫不含正式公開網址，須完成登入與部署後才會產生。

官方操作說明：[部署](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)、
[Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)。

## Docker

需先安裝並啟動 Docker Engine／Docker Desktop；本次開發環境未安裝 Docker，容器尚未實際建置驗證。

```powershell
docker compose build
docker compose run --rm sync
docker compose up -d dashboard
```

開啟 <http://localhost:8501>。更新資料使用 `docker compose run --rm sync`。
`weather-data` volume 保存 SQLite；`docker compose down` 不會刪除它，請勿使用 `down -v`，除非要清除歷史。
API Key 僅注入 sync 容器，不放入映像檔。網站容器使用非 root 帳號並提供健康檢查。
Docker 預設是本機服務；公開部署仍需主機、HTTPS 與網路入口。

## 架構與資料語意

```text
CWA API → cwa_api.py → data_parser.py → database.py → SQLite
                                                        ↓
                                         app.py → weather_map.py
cloud_app.py → sync_service.py → 同一套 API／解析／資料庫流程
```

- 所有 SQL 均位於 `database.py`；地圖模組只接收 DataFrame。
- `(regionName, startTime)` 唯一；同時段修訂原地更新，舊時段持續保留，不保存修訂版本。
- 預報時間採 CWA 的臺灣時間；「最新」代表資料庫中最大的預報開始時間，非 API 發布時間。
- SQLite `created_at` 為首次建立紀錄時間（SQLite 預設 UTC），不等於最新同步時間。
- `WEATHER_DB_PATH` 環境變數可指定資料庫檔案；預設位於程式所在目錄，指定的父目錄須存在。
- 地圖座標為代表點，非氣象測站或行政區邊界。
- 配色依最高溫：紅 ≥32、橘 28–<32、綠 24–<28、藍 <24°C；最高溫缺值為灰色。
- 底圖與地圖前端資源需要網路；資料不齊時會列出缺少的縣市。
- 不包含 AI 或行政區多邊形。

## 測試

```powershell
python -X utf8 -m unittest discover -s tests -v
```

測試使用臨時 SQLite，不修改本機 `weather.db`，涵蓋時段去重／排序、22 縣市、配色邊界、
缺值、標記內容、三分頁、時段切換資料更新、縣市選擇互不干擾、空資料庫與雲端快取／失敗處理。

## 已知限制

既有 `cwa_api.py` 在憑證驗證失敗後會改用 `verify=False` 並印出警告；本次真實 API 測試也走到此後備路徑。
這會略過伺服器憑證驗證，並非正式環境的理想安全設定。後續應修正憑證鏈／信任設定並恢復完整驗證；
目前未改動前階段的 SSL 決策。不要將 `.env`、`.streamlit/secrets.toml` 或 API Key 加入版本控制。
