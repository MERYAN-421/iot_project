# 🌤️ Taiwan Weather Forecast｜台灣天氣預報

公開展示：[開啟台灣天氣預報](https://iotproject-hpwvgzzmi2zm7wbuxkerht.streamlit.app/)

使用中央氣象署 F-C0032-001 的 36 小時預報，呈現全台 22 縣市最低／最高氣溫。

## 功能

- **天氣地圖**：22 縣市行政邊界、點選連動資訊卡、選取縣市高亮與聚焦；可切換預報或真實測站圖層。
- **全台總覽**：最低到最高溫區間圖（不堆疊）、降雨機率排序、資料表與 CSV 下載。
- **縣市預報**：氣溫、天氣描述、降雨機率、舒適度與完整起訖時間，三時段卡片及歷史趨勢。
- **即時測站**：CWA O-A0001-001 全測站逐時資料；本次同步 876 站（數量依 API 回應變動），含氣溫、濕度、風速與當日累積雨量。
- 測站支援縣市篩選、站名／代碼／鄉鎮搜尋、詳細資訊與 CSV 下載。測站圖層自動群集，放大可看到各站。
- 預報與觀測分開顯示；缺值顯示「—」、雨跡獨立標記；超過兩小時或時間無法解析的觀測有提示，地圖預設排除。

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

`cloud_app.py` 會在首次開啟時同步資料。預報成功結果快取一小時，測站結果快取十分鐘，過期後於下一次頁面執行再同步；
這不是無人造訪也運行的排程。兩個來源獨立同步：預報失敗可於下一次頁面執行重試；測站失敗亦快取十分鐘，避免反覆請求，並保留上次快照。
無 API Key 且無既有資料時，必須先完成 Secrets 設定才會有天氣資料。

Community Cloud 作為展示環境：SQLite 不作永久保存保證，重啟或重新部署後歷史可能遺失。
需要永久歷史時，改用具持久磁碟的主機／Docker volume。
已於 2026-09-30 部署完成；公開網址見本文件頂端。

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
- 預報標記為縣市代表點；測站模式使用 API 的 WGS84 真實座標。行政邊界由 Taiwan Atlas 提供，僅供視覺化。
- 配色依最高溫：紅 ≥32、橘 28–<32、綠 24–<28、藍 <24°C；最高溫缺值為灰色。
- 底圖與地圖前端資源需要網路；資料不齊時會列出缺少的縣市。
- 已加入行政區多邊形；不包含 AI。
- `StationObservations` 保存最近一次成功同步的測站快照，不累積測站歷史。
- 舊預報表會自動增補 `endTime`、`weather`、`pop`、`comfort` 欄位；既有資料保留，下一次同步補齊新欄位。

## 測試

```powershell
python -X utf8 -m unittest discover -s tests -v
```

測試使用臨時 SQLite，不修改本機 `weather.db`。17 項測試涵蓋舊表遷移、時間對齊解析、22 縣市邊界閉合、測站缺值與座標、快照原子替換、HTML 跳脫、地圖點選連動、測站搜尋、四分頁與雲端失敗處理。

## 已知限制

既有 `cwa_api.py` 在憑證驗證失敗後會改用 `verify=False` 並印出警告；本次真實 API 測試也走到此後備路徑。
這會略過伺服器憑證驗證，並非正式環境的理想安全設定。後續應修正憑證鏈／信任設定並恢復完整驗證；
目前未改動前階段的 SSL 決策。不要將 `.env`、`.streamlit/secrets.toml` 或 API Key 加入版本控制。

## 邊界與資料來源

- 氣象觀測：[中央氣象署 O-A0001-001 標準文件](https://opendata.cwa.gov.tw/opendatadoc/Observation/O-A0001-001.pdf)。
- 行政邊界：[Taiwan Atlas](https://github.com/dkaoster/taiwan-atlas)，由內政部縣市界線簡化產生。
- 專案附 `assets/counties.topo.json`，MIT 授權全文與來源／檔案雜湊位於同目錄。圖資不是即時行政界線公告，不可用於法律界址認定。
- 底圖 © OpenStreetMap contributors；瀏覽器需網路載入底圖與 Leaflet 資源。
