"""Taiwan weather explorer. Weather persistence is exclusively in database.py."""
from datetime import datetime, timedelta, timezone
import pandas as pd
import altair as alt
import streamlit as st
from streamlit_folium import st_folium
from database import (init_db, get_all_regions, get_available_forecast_times,
                      get_forecasts_by_time, get_forecasts_by_region, get_observations)
from geography import region_from_tooltip
from weather_map import build_weather_map
from ui import THEME, forecast_card, observation_card, value, text

st.set_page_config(page_title="島嶼氣象 Island Weather", page_icon="🌤️", layout="wide")
st.markdown(THEME, unsafe_allow_html=True)
init_db()
regions = get_all_regions()
times = get_available_forecast_times()
if not regions or not times:
    st.info("尚無預報資料，請先執行 main.py 同步；雲端管理者請確認 CWA_API_KEY 設定。")
    st.stop()

# Apply a map selection before creating the corresponding widget.
if st.session_state.get("pending_region") in regions:
    st.session_state["region_picker"] = st.session_state.pop("pending_region")
if st.session_state.get("region_picker") not in regions:
    st.session_state["region_picker"] = "臺北市" if "臺北市" in regions else regions[0]

st.sidebar.markdown("### 🌤️ 島嶼氣象")
st.sidebar.caption("ISLAND WEATHER / TAIWAN")
st.sidebar.divider()
selected_region = st.sidebar.selectbox("探索縣市", regions, key="region_picker")
now = datetime.now(timezone(timedelta(hours=8)))
now_string = now.strftime("%Y-%m-%d %H:%M:%S")
current = [time for time in times if time <= now_string]
default_time = max(current) if current else min(times)
selected_time = st.sidebar.selectbox("預報時段（臺灣時間）", times,
                                    index=times.index(default_time), key="map_forecast_time")
focus = st.sidebar.toggle("聚焦選取縣市", value=False, key="focus_region")
st.sidebar.caption("點選地圖邊界或縣市標記，也能切換縣市。")
st.sidebar.divider()
st.sidebar.markdown("**資料來源**  中央氣象署")
st.sidebar.caption("縣市預報：今明 36 小時\n\n測站實況：各站最新觀測\n\n預報代表點不等於觀測站。")

forecasts = get_forecasts_by_time(selected_time)
observations = get_observations()
region_forecasts = get_forecasts_by_region(selected_region)
if forecasts.empty:
    st.warning("此時段沒有資料，請選擇其他時段。")
    st.stop()
selected_rows = forecasts[forecasts.regionName == selected_region]
selected = selected_rows.iloc[0].to_dict() if not selected_rows.empty else None
region_stations = observations[observations.regionName == selected_region] if not observations.empty else observations
if not observations.empty:
    obs_times = pd.to_datetime(observations.observedAt, utc=True, errors="coerce")
    observations = observations.assign(stale=obs_times.isna() | (obs_times < pd.Timestamp(now) - pd.Timedelta(hours=2)))
    region_stations = observations[observations.regionName == selected_region]

st.markdown('''<div class="hero"><div><div class="eyebrow">ISLAND WEATHER · TAIWAN</div>
<h1>看見島嶼的每一種天氣</h1><div class="muted">從縣市預報到在地測站，探索你關心的地方。</div></div>
<div class="badge">中央氣象署開放資料</div></div>''', unsafe_allow_html=True)
ends = pd.to_datetime(forecasts.endTime, errors="coerce")
if ends.notna().any() and ends.max() < now.replace(tzinfo=None):
    st.warning("所選預報時段已結束，以下顯示歷史預報，並非目前天氣。")
cols = st.columns(4)
cols[0].metric("預報涵蓋縣市", f"{len(forecasts)} / 22")
cols[1].metric("最高預報氣溫", value(forecasts.maxT.max(), " °C"))
cols[2].metric("最高降雨機率", value(forecasts['pop'].max(), "%"))
cols[3].metric("已載入觀測站", f"{len(observations):,}")

map_tab, overview_tab, detail_tab, stations_tab = st.tabs(["🌏 天氣地圖", "☀️ 全台總覽", "📍 縣市預報", "📡 即時測站"])
with map_tab:
    mode = st.radio("地圖資料", ["縣市預報", "測站實況"], horizontal=True, key="map_mode")
    st.caption(f"預報時段 {selected_time} · {len(forecasts)} / 22 縣市｜紅 ≥32°C · 橘 28–<32°C · 綠 24–<28°C · 藍 <24°C · 灰 缺值")
    shown_stations = observations
    if mode == "測站實況":
        include_stale = st.checkbox("包含超過 2 小時或時間不明的觀測", value=False)
        if not observations.empty and not include_stale:
            shown_stations = observations[~observations.stale]
        if focus and not shown_stations.empty:
            shown_stations = shown_stations[shown_stations.regionName == selected_region]
        st.caption(f"地圖顯示 {len(shown_stations)} 站；圓形數字是測站群集，放大可看個別測站。實況時間以各站資訊卡為準。")
        if shown_stations.empty:
            st.info("目前沒有符合條件的測站資料；仍可查看縣市邊界與預報。")
    left, right = st.columns([2.6, 1], gap="large")
    with left:
        result = st_folium(
            build_weather_map(forecasts, selected_region, shown_stations,
                              "forecast" if mode == "縣市預報" else "observations", focus),
            use_container_width=True, height=610,
            returned_objects=["last_object_clicked_tooltip", "last_object_clicked"],
            key=f"explorer_{mode}_{selected_time}_{focus}_{selected_region}",
        )
        if result:
            picked = region_from_tooltip(result.get("last_object_clicked_tooltip"), regions)
            if picked and picked != selected_region and (mode == "縣市預報" or str(result.get("last_object_clicked_tooltip")).strip() == picked):
                st.session_state["pending_region"] = picked
                st.rerun()
    with right:
        if selected:
            st.markdown(forecast_card(selected), unsafe_allow_html=True)
        else:
            st.info(f"{selected_region} 在所選時段沒有預報資料。")
        st.markdown("#### 在地觀測")
        st.caption(f"{selected_region} · {len(region_stations)} 個已載入測站")
        if not region_stations.empty:
            fresh = region_stations[~region_stations.stale & region_stations.temperature.notna()]
            if not fresh.empty:
                low, high = value(fresh.temperature.min()), value(fresh.temperature.max())
                st.markdown(f'<div style="background:white;border:1px solid #dce6ec;border-radius:16px;padding:18px"><div class="section-note">有效測站氣溫範圍</div><div style="font-size:24px;font-weight:700;color:#176678">{low}–{high}°C</div></div>', unsafe_allow_html=True)
                st.caption("範圍取自 2 小時內有效觀測，並非全縣市平均。")
            else:
                st.caption("暫無 2 小時內的有效溫度觀測。")
        st.markdown('<div class="section-note">操作提示<br>① 點選縣市邊界，切換資訊卡<br>② 開啟「聚焦選取縣市」放大<br>③ 切換「測站實況」探索附近觀測</div>', unsafe_allow_html=True)
    st.caption("行政界線：內政部圖資 / Taiwan Atlas（簡化邊界，僅供視覺化）。底圖 © OpenStreetMap。")

with overview_tab:
    st.subheader("全台氣溫，一眼比較")
    st.caption("線段表示最低到最高預報氣溫，兩者不相加。滑鼠移至圖表可看詳細數值。")
    order = st.selectbox("排序方式", ["最高溫由高到低", "降雨機率由高到低", "縣市名稱"])
    sort_key = {"最高溫由高到低": "maxT", "降雨機率由高到低": "pop", "縣市名稱": "regionName"}[order]
    ranked = forecasts.sort_values(sort_key, ascending=(sort_key == "regionName"), na_position="last")
    base = alt.Chart(ranked).encode(y=alt.Y("regionName:N", sort=ranked.regionName.tolist(), title=None),
        tooltip=[alt.Tooltip("regionName:N", title="縣市"), alt.Tooltip("minT:Q", title="最低溫"),
                 alt.Tooltip("maxT:Q", title="最高溫"), alt.Tooltip("pop:Q", title="降雨機率 %")])
    band = base.mark_rule(strokeWidth=6, color="#b6d9e0").encode(x=alt.X("minT:Q", title="預報氣溫 °C", scale=alt.Scale(zero=False)), x2="maxT:Q")
    low = base.mark_circle(size=65, color="#258ba4").encode(x="minT:Q")
    high = base.mark_circle(size=65, color="#df8c52").encode(x="maxT:Q")
    st.altair_chart((band + low + high).properties(height=570), width="stretch")
    st.dataframe(ranked[["regionName", "weather", "minT", "maxT", "pop", "comfort"]].rename(columns={
        "regionName":"縣市", "weather":"天氣", "minT":"最低 °C", "maxT":"最高 °C", "pop":"降雨機率 %", "comfort":"舒適度"}), hide_index=True, width="stretch")
    st.download_button("下載所選時段 CSV", forecasts.to_csv(index=False).encode("utf-8-sig"), "taiwan_forecast.csv", "text/csv")

with detail_tab:
    st.subheader(f"{selected_region} · 天氣行事曆")
    if region_forecasts.empty:
        st.info("此縣市尚無預報。")
    else:
        upcoming = region_forecasts[region_forecasts.startTime >= selected_time].head(3)
        if not upcoming.empty:
            for col, row in zip(st.columns(len(upcoming)), upcoming.to_dict("records")):
                with col:
                    st.markdown(forecast_card(row, True), unsafe_allow_html=True)
        st.markdown("#### 預報氣溫趨勢")
        chart = region_forecasts.copy()
        chart["startTime"] = pd.to_datetime(chart.startTime)
        st.line_chart(chart.set_index("startTime")[["minT", "maxT"]].rename(columns={"minT":"最低溫", "maxT":"最高溫"}), color=["#278da4", "#dc9157"], height=300)
        with st.expander("查看完整預報與歷史資料"):
            st.dataframe(region_forecasts, hide_index=True, width="stretch")
            st.download_button("下載此縣市 CSV", region_forecasts.to_csv(index=False).encode("utf-8-sig"), "region_forecast.csv", "text/csv")

with stations_tab:
    st.subheader("探索真實觀測站")
    st.caption("氣溫、濕度、風速與當日累積雨量來自各測站實測，不是預報。各站時間可能不同。")
    if observations.empty:
        st.info("尚未同步測站。雲端會自動嘗試同步；本機可執行 python main.py。")
    else:
        a, b = st.columns([1, 2])
        county_filter = a.selectbox("測站縣市", ["全台"] + sorted(observations.regionName.unique()), key="station_county")
        query = b.text_input("搜尋站名、代碼或鄉鎮", placeholder="例如：玉山、C0、信義")
        filtered = observations if county_filter == "全台" else observations[observations.regionName == county_filter]
        if query:
            matched = filtered[["stationName", "stationId", "townName"]].fillna("").agg(" ".join, axis=1).str.contains(query, case=False, regex=False)
            filtered = filtered[matched]
        st.caption(f"找到 {len(filtered)} 站；其中 {int(filtered.stale.sum())} 站已超過 2 小時或觀測時間不明。— 表示缺值；雨跡保留為獨立欄位。")
        if not filtered.empty:
            station_id = st.selectbox("測站詳細資訊", filtered.stationId.tolist(),
                format_func=lambda sid: f"{filtered.set_index('stationId').loc[sid, 'stationName']} · {sid}")
            station_row = filtered[filtered.stationId == station_id].iloc[0].to_dict()
            if station_row["stale"]:
                st.warning("此站觀測已過期或時間不明，請勿視為即時天氣。")
            st.markdown(observation_card(station_row), unsafe_allow_html=True)
        display = filtered[["stationName", "regionName", "townName", "temperature", "humidity", "windSpeed", "precipitation", "rainTrace", "observedAt", "stale"]].rename(columns={
            "stationName":"測站", "regionName":"縣市", "townName":"鄉鎮", "temperature":"氣溫 °C", "humidity":"濕度 %", "windSpeed":"風速 m/s", "precipitation":"當日雨量 mm", "rainTrace":"雨跡", "observedAt":"觀測時間", "stale":"過期 / 時間不明"})
        st.dataframe(display, hide_index=True, width="stretch")
        st.download_button("下載篩選測站 CSV", filtered.to_csv(index=False).encode("utf-8-sig"), "weather_stations.csv", "text/csv")
st.caption("ISLAND WEATHER · 資料以中央氣象署最新發布為準。雲端展示的歷史資料不保證永久保存。")
