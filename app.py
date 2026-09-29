"""
app.py
------
Streamlit web dashboard for Taiwan Weather Forecast.
Nationwide Overview, Regional Detail, and Taiwan Map tabs.

Architectural rule:
  No direct SQLite queries in app.py. All database access is routed through database.py.
"""

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from weather_map import TAIWAN_REGION_COORDINATES, build_weather_map
from database import (
    init_db,
    get_available_forecast_times,
    get_forecasts_by_time,
    get_all_regions,
    get_forecasts_by_region,
    get_latest_forecasts,
)

# Configure page settings
st.set_page_config(
    page_title="Taiwan Weather Forecast",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Main title and caption
st.title("🌤️ 台灣天氣預報 Web Dashboard")
st.caption("基於中央氣象署 (CWA) Open Data API 與 SQLite 歷史預報資料庫")

# 1. Fetch all regions dynamically from database
init_db()
regions = get_all_regions()

if not regions:
    st.error("⚠️ 資料庫中尚無任何地區資料，請先執行 main.py 同步氣象預報資料。")
    st.stop()

# 2. Sidebar region selector (globally visible across tabs)
st.sidebar.header("📍 地區選擇 / Region Filter")
default_index = regions.index("臺北市") if "臺北市" in regions else 0
selected_region = st.sidebar.selectbox(
    "請選擇縣市 / Select City or County",
    options=regions,
    index=default_index,
    help="此選項會控制「縣市查詢」分頁中的詳細氣象資料。",
)

# 3. Create Navigation Tabs
tab_overview, tab_detail, tab_map = st.tabs(["🗺️ 全台總覽", "🏙️ 縣市查詢", "🌏 台灣地圖"])

# ==========================================
# Tab 1: 全台總覽 (Nationwide Overview)
# ==========================================
with tab_overview:
    # Fetch latest forecast for all regions (1 period)
    overview_df = get_latest_forecasts(periods=1)

    # Constraint 1: Empty-data guard
    if overview_df.empty:
        st.warning("⚠️ 目前資料庫中查無全台最新預報資料。")
    else:
        # Constraint 2: Verify exactly one distinct startTime
        distinct_times = overview_df["startTime"].unique()
        if len(distinct_times) != 1:
            st.warning(f"⚠️ 預期單一時段資料，但取得 {len(distinct_times)} 個時段。")

        latest_time = distinct_times[0] if len(distinct_times) > 0 else "未知"
        st.info(f"🕒 最新預報時段：**{latest_time}**（共 {len(overview_df)} 個縣市資料）")

        # Constraint: Handle hottest / coldest ties properly
        max_t_val = overview_df["maxT"].max()
        min_t_val = overview_df["minT"].min()

        hottest_regions = overview_df[overview_df["maxT"] == max_t_val]["regionName"].tolist()
        coldest_regions = overview_df[overview_df["minT"] == min_t_val]["regionName"].tolist()

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="🔥 全台最高溫 (Highest Temp)",
                value=f"{max_t_val} °C",
            )
            st.caption(f"**最高溫縣市**: {', '.join(hottest_regions)}")

        with col2:
            st.metric(
                label="❄️ 全台最低溫 (Lowest Temp)",
                value=f"{min_t_val} °C",
            )
            st.caption(f"**最低溫縣市**: {', '.join(coldest_regions)}")

        st.divider()

        # Constraint 3: Comparison chart across regions (st.bar_chart)
        st.subheader("📊 各縣市氣溫比較 (Regional Temperature Comparison)")
        chart_data = overview_df.set_index("regionName")[["minT", "maxT"]].rename(
            columns={"minT": "最低溫 (°C)", "maxT": "最高溫 (°C)"}
        )
        st.bar_chart(chart_data, height=380)

        st.divider()

        # Table of all 22 regions
        st.subheader("📋 全台各縣市預報清單 (All Regions Forecast Table)")
        display_overview = overview_df[["regionName", "minT", "maxT", "startTime", "created_at"]].copy()
        display_overview = display_overview.rename(
            columns={
                "regionName": "縣市",
                "minT": "最低溫 (°C)",
                "maxT": "最高溫 (°C)",
                "startTime": "預報開始時間",
                "created_at": "建立時間 (Created At)",
            }
        )
        st.dataframe(display_overview, width="stretch", hide_index=True)


# ==========================================
# Tab 2: 縣市查詢 (Regional Detail)
# ==========================================
with tab_detail:
    df = get_forecasts_by_region(selected_region)

    if df.empty:
        st.warning(f"目前查無 {selected_region} 的預報資料。")
    else:
        # Latest forecast period is explicitly df.iloc[-1]
        latest_row = df.iloc[-1]

        st.markdown(f"### 📍 {selected_region} 最新天氣概況")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="🕒 最新預報時段 (Latest Period)",
                value=str(latest_row["startTime"]),
            )
        with col2:
            st.metric(
                label="❄️ 最低氣溫 (Min Temp)",
                value=f"{latest_row['minT']} °C",
            )
        with col3:
            st.metric(
                label="☀️ 最高氣溫 (Max Temp)",
                value=f"{latest_row['maxT']} °C",
            )

        st.divider()

        # Temperature Trend Line Chart
        st.subheader("📈 氣溫變化趨勢 (Temperature Trend)")

        # Convert startTime to pandas datetime before charting
        chart_df = df.copy()
        chart_df["startTime_dt"] = pd.to_datetime(chart_df["startTime"])
        chart_df = chart_df.rename(columns={"minT": "最低溫 (MinT °C)", "maxT": "最高溫 (MaxT °C)"})
        chart_df = chart_df.set_index("startTime_dt")[["最低溫 (MinT °C)", "最高溫 (MaxT °C)"]]

        st.line_chart(chart_df, height=350)

        st.divider()

        # Detailed Forecast Data Table
        st.subheader("📋 詳細預報資料 (Forecast Details)")

        display_df = df[["startTime", "minT", "maxT", "created_at"]].copy()
        display_df = display_df.rename(
            columns={
                "startTime": "預報開始時間 (Start Time)",
                "minT": "最低溫 (°C)",
                "maxT": "最高溫 (°C)",
                "created_at": "建立時間 (Created At)",
            }
        )

        st.dataframe(display_df, width="stretch", hide_index=True)


with tab_map:
    st.subheader("🌏 台灣各縣市預報地圖")
    available_times = get_available_forecast_times()
    if not available_times:
        st.info("目前沒有可顯示的預報時段，請先同步資料。")
    else:
        selected_time = st.selectbox(
            "🕒 請選擇預報時段 / Select Forecast Period",
            options=available_times,
            key="map_forecast_time",
        )
        map_df = get_forecasts_by_time(selected_time)
        if map_df.empty:
            st.warning("此時段沒有預報資料，請選擇其他時段。")
        else:
            known = set(TAIWAN_REGION_COORDINATES)
            present = set(map_df["regionName"])
            missing = sorted(known - present)
            unknown = sorted(present - known)
            if missing:
                st.warning(f"此時段缺少縣市資料：{'、'.join(missing)}")
            if unknown:
                st.warning(f"以下地區沒有對應座標，未顯示標記：{'、'.join(unknown)}")
            st.caption(
                "依最高溫配色：🔴 炎熱 ≥32°C｜🟠 溫暖 28–<32°C｜"
                "🟢 舒適 24–<28°C｜🔵 涼爽 <24°C｜灰色：最高溫無資料"
            )
            st.caption(
                f"預報開始時間：{selected_time}（臺灣時間）｜"
                f"顯示 {len(present & known)} / 22 縣市。"
                "標記為縣市代表位置，非測站位置；可縮放並點擊查看氣溫。"
            )
            st_folium(
                build_weather_map(map_df),
                use_container_width=True,
                height=550,
                returned_objects=[],
                key=f"weather_map_{selected_time}",
            )
