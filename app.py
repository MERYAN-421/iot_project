"""
app.py
------
Streamlit web dashboard for Taiwan Weather Forecast.
Phase 3 Milestone 1: Regional forecasts, metrics, trend line charts, and data tables.

Architectural rule:
  No direct SQLite queries in app.py. All database access is routed through database.py.
"""

import streamlit as st
import pandas as pd
from database import get_all_regions, get_forecasts_by_region

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
regions = get_all_regions()

if not regions:
    st.error("⚠️ 資料庫中尚無任何地區資料，請先執行 main.py 同步氣象預報資料。")
    st.stop()

# 2. Sidebar region selector
st.sidebar.header("📍 地區選擇 / Region Filter")
default_index = regions.index("臺北市") if "臺北市" in regions else 0
selected_region = st.sidebar.selectbox(
    "請選擇縣市 / Select City or County",
    options=regions,
    index=default_index,
)

# 3. Fetch forecasts for the selected region
df = get_forecasts_by_region(selected_region)

if df.empty:
    st.warning(f"目前查無 {selected_region} 的預報資料。")
    st.stop()

# 4. Display Key Metrics for the latest forecast period
# Since get_forecasts_by_region() returns startTime ASC, latest period is explicitly df.iloc[-1]
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

# 5. Temperature Trend Line Chart
st.subheader("📈 氣溫變化趨勢 (Temperature Trend)")

# Convert startTime to pandas datetime before charting
chart_df = df.copy()
chart_df["startTime_dt"] = pd.to_datetime(chart_df["startTime"])
chart_df = chart_df.rename(columns={"minT": "最低溫 (MinT °C)", "maxT": "最高溫 (MaxT °C)"})
chart_df = chart_df.set_index("startTime_dt")[["最低溫 (MinT °C)", "最高溫 (MaxT °C)"]]

st.line_chart(chart_df, height=350)

st.divider()

# 6. Detailed Forecast Data Table
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

st.dataframe(display_df, use_container_width=True, hide_index=True)
