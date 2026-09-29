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


PALETTE = {"red": "#dd654f", "orange": "#e4a346", "green": "#48a58d", "blue": "#4b95c8", "gray": "#8396a1"}


def build_weather_map(forecasts: pd.DataFrame, selected_region=None, observations=None,
                      mode="forecast", focus=False) -> folium.Map:
    from geography import county_boundaries
    from ui import forecast_card, observation_card, value
    from folium.plugins import MarkerCluster, Fullscreen

    weather_map = folium.Map(location=[23.7, 120.95], zoom_start=7, tiles="OpenStreetMap", control_scale=True)
    Fullscreen(position="topright").add_to(weather_map)
    rows = {row["regionName"]: row for row in forecasts.to_dict("records")}
    selected_bounds = None
    for feature in county_boundaries()["features"]:
        name = feature["properties"]["regionName"]
        row = rows.get(name)
        selected = name == selected_region
        color = PALETTE[temperature_color(row.get("maxT"))] if row else "#bdccd4"
        layer = folium.GeoJson(
            feature, name=name,
            style_function=lambda f, c=color, active=selected: {
                "fillColor": c, "color": "#0c6378" if active else "#7895a4",
                "weight": 3.5 if active else 1, "fillOpacity": .33 if active else .10,
            },
            highlight_function=lambda f: {"weight": 3, "color": "#127e91", "fillOpacity": .38},
            tooltip=folium.Tooltip(name, sticky=True),
            popup=folium.Popup(forecast_card(row, True), max_width=320) if row else folium.Popup(name),
        ).add_to(weather_map)
        if selected:
            selected_bounds = layer.get_bounds()
    if mode == "forecast":
        for name, row in rows.items():
            coordinates = TAIWAN_REGION_COORDINATES.get(name)
            if not coordinates:
                continue
            color = PALETTE[temperature_color(row.get("maxT"))]
            label = escape(name)
            folium.Marker(
                coordinates, tooltip=label,
                popup=folium.Popup(forecast_card(row, True), max_width=320),
                icon=folium.DivIcon(icon_size=(74, 40), icon_anchor=(37, 20), html=f'''<div style="background:white;border:2px solid {color};border-radius:12px;box-shadow:0 3px 12px #1b394333;text-align:center;padding:4px 3px;font-family:sans-serif;color:#234452;font-size:10px;line-height:1.4">{label}<br><b style="font-size:15px;color:{color}">{value(row.get('maxT'))}°</b></div>'''),
            ).add_to(weather_map)
    elif observations is not None and not observations.empty:
        cluster = MarkerCluster(name="中央氣象署觀測站", options={"maxClusterRadius": 38, "disableClusteringAtZoom": 11}).add_to(weather_map)
        for row in observations.to_dict("records"):
            color = PALETTE[temperature_color(row.get("temperature"))]
            folium.Marker(
                [row["latitude"], row["longitude"]],
                tooltip=f"{escape(row['regionName'])} · {escape(row['stationName'])} · {value(row['temperature'], '°C')}",
                popup=folium.Popup(observation_card(row), max_width=310),
                icon=folium.DivIcon(icon_size=(36, 28), icon_anchor=(18, 14), html=f'''<div style="border-radius:9px;padding:4px 1px;background:{color};border:2px solid white;box-shadow:0 2px 8px #17344640;color:white;text-align:center;font:bold 11px sans-serif">{value(row['temperature'])}</div>'''),
            ).add_to(cluster)
    weather_map.fit_bounds(selected_bounds if focus and selected_bounds else [[21.85, 118.15], [26.4, 122.1]], padding=(20, 20))
    return weather_map
