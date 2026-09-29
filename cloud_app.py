"""Streamlit Community Cloud entrypoint; refresh on visits, at most once/hour."""
from datetime import datetime
from pathlib import Path
import runpy

import streamlit as st

from sync_service import sync_forecasts

st.set_page_config(page_title="Taiwan Weather Forecast", page_icon="🌤️", layout="wide")


@st.cache_data(ttl=3600, show_spinner="正在同步中央氣象署天氣預報…")
def refresh_forecasts():
    # Errors are not cached; an upcoming visit can retry. Do not display request
    # exception strings: requests may include the Authorization query parameter.
    sync_forecasts()
    return datetime.now().isoformat(timespec="seconds")


try:
    refresh_forecasts()
except Exception:
    st.warning("氣象資料同步暫時失敗，將顯示已儲存的資料。管理者請確認 CWA_API_KEY、網路與 API 狀態。")

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
