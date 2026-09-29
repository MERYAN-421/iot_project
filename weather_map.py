"""Representative county/city points and forecast map rendering (no database access)."""

from html import escape

import folium
import pandas as pd


TAIWAN_REGION_COORDINATES = {
    "基隆市": [25.1322, 121.7444],
    "臺北市": [25.0375, 121.5637],
    "新北市": [25.0143, 121.4625],
    "桃園市": [24.9936, 121.3010],
    "新竹市": [24.8039, 120.9647],
    "新竹縣": [24.8383, 121.0177],
    "宜蘭縣": [24.7570, 121.7530],
    "苗栗縣": [24.5650, 120.8208],
    "臺中市": [24.1632, 120.6403],
    "彰化縣": [24.0818, 120.5385],
    "南投縣": [23.9099, 120.6848],
    "雲林縣": [23.7092, 120.4313],
    "嘉義市": [23.4800, 120.4491],
    "嘉義縣": [23.4518, 120.2559],
    "臺南市": [22.9997, 120.2270],
    "高雄市": [22.6273, 120.3014],
    "屏東縣": [22.6830, 120.4879],
    "花蓮縣": [23.9912, 121.6111],
    "臺東縣": [22.7583, 121.1444],
    "澎湖縣": [23.5711, 119.5793],
    "金門縣": [24.4490, 118.3766],
    "連江縣": [26.1557, 119.9519],
}


def temperature_color(max_t: float) -> str:
    """Color by forecast maximum; missing values remain visibly distinct."""
    if pd.isna(max_t):
        return "gray"
    if max_t >= 32:
        return "red"
    if max_t >= 28:
        return "orange"
    if max_t >= 24:
        return "green"
    return "blue"


def format_temperature(value: float) -> str:
    return "無資料" if pd.isna(value) else f"{value:g} °C"


def build_weather_map(forecasts: pd.DataFrame) -> folium.Map:
    """Render one marker per known region from a single forecast slice."""
    weather_map = folium.Map(location=[23.7, 120.95], zoom_start=7)
    for row in forecasts.itertuples(index=False):
        coordinates = TAIWAN_REGION_COORDINATES.get(row.regionName)
        if coordinates is None:
            continue
        region = escape(str(row.regionName))
        period = escape(str(row.startTime))
        temperatures = f"{format_temperature(row.minT)} ~ {format_temperature(row.maxT)}"
        folium.Marker(
            location=coordinates,
            tooltip=f"{region}: {temperatures}",
            popup=folium.Popup(
                f"<b>{region}</b><br>預報時段: {period}<br>氣溫範圍: {temperatures}",
                max_width=320,
            ),
            icon=folium.Icon(color=temperature_color(row.maxT), icon="info-sign"),
        ).add_to(weather_map)
    # Include Kinmen and Matsu in the initial viewport, including on narrow screens.
    weather_map.fit_bounds([[22.0, 118.15], [26.4, 122.1]])
    return weather_map
