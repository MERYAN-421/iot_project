"""Shared escaped HTML cards and a lightweight visual theme."""
from html import escape
import pandas as pd


def text(value, fallback="—"):
    return fallback if value is None or pd.isna(value) or str(value) == "" else escape(str(value))


def value(number, suffix=""):
    return "—" if pd.isna(number) else f"{number:g}{suffix}"


def weather_icon(description):
    description = str(description or "")
    if "雷" in description:
        return "⛈️"
    if "雨" in description:
        return "🌦️"
    if "晴" in description:
        return "☀️"
    return "☁️"


def forecast_card(row, compact=False):
    name = text(row.get("regionName"))
    weather = text(row.get("weather"), "天氣描述尚未同步")
    low, high = value(row.get("minT")), value(row.get("maxT"))
    pop = value(row.get("pop"), "%")
    period = text(row.get("startTime"))
    end = text(row.get("endTime"))
    return f'''<div style="font-family:Inter,'Noto Sans TC',sans-serif;background:linear-gradient(135deg,#102f42,#176b77);color:#fff;border-radius:20px;padding:{'20' if compact else '28'}px;min-width:210px;box-sizing:border-box">
    <div style="font-size:11px;letter-spacing:2px;color:#a7d8de">COUNTY FORECAST · 縣市預報</div>
    <div style="font-size:27px;font-weight:750;margin:12px 0">{name} <span style="float:right">{weather_icon(row.get('weather'))}</span></div>
    <div style="font-size:36px;font-weight:700;line-height:1.4">{low}–{high}<span style="font-size:18px"> °C</span></div>
    <div style="color:#d2e8eb;margin:5px 0 20px">{weather}</div>
    <div style="display:flex;gap:24px;border-top:1px solid #ffffff30;padding-top:16px">
      <div><small style="color:#a7d8de">降雨機率</small><div style="font-size:22px;font-weight:650">{pop}</div></div>
      <div><small style="color:#a7d8de">舒適度</small><div style="font-size:15px;margin-top:5px">{text(row.get('comfort'))}</div></div>
    </div><div style="font-size:11px;color:#b8d7dd;margin-top:18px">{period}<br>至 {end} · 臺灣時間</div></div>'''


def observation_card(row):
    rain = "雨跡" if row.get("rainTrace") else value(row.get("precipitation"), " mm")
    return f'''<div style="font-family:sans-serif;width:245px;padding:20px;background:#fff;color:#183a47;border-radius:16px">
      <div style="font-size:11px;letter-spacing:1px;color:#17838c">LIVE OBSERVATION · 測站實況</div>
      <h2 style="margin:12px 0 4px">{text(row.get('stationName'))}</h2>
      <div style="font-size:12px;color:#6c8290">{text(row.get('regionName'))} · {text(row.get('townName'))} · {text(row.get('stationId'))}</div>
      <div style="font-size:38px;font-weight:750;margin:12px 0">{value(row.get('temperature'),'°C')}</div>
      <div>{text(row.get('weather'))}</div><hr style="border:0;border-top:1px solid #e1eaee;margin:16px 0">
      <div style="line-height:2">相對濕度 <b>{value(row.get('humidity'),'%')}</b><br>
      風速 <b>{value(row.get('windSpeed'),' m/s')}</b><br>當日累積雨量 <b>{rain}</b></div>
      <div style="font-size:11px;color:#6c8290;margin-top:12px">觀測 {text(row.get('observedAt'))}</div></div>'''


THEME = '''<style>
.stApp {background:#f4f7fa;color:#183447}
.block-container {padding-top:2.2rem;padding-bottom:3rem;max-width:1550px}
[data-testid="stSidebar"] {background:#eaf0f4;border-right:1px solid #d9e4eb}
h1,h2,h3 {letter-spacing:-.035em;color:#163b4b}
[data-testid="stMetric"] {background:#fff;border:1px solid #dce6ec;border-radius:18px;padding:18px 22px;box-shadow:0 5px 20px #18344705}
[data-testid="stMetricLabel"] {color:#657e8c;font-size:12px}
[data-testid="stMetricValue"] {color:#163f50}
button[data-baseweb="tab"] {font-weight:650;padding:12px 20px}
[data-testid="stTabs"] {margin-top:16px}
.hero {display:flex;justify-content:space-between;align-items:center;margin-bottom:22px;gap:16px;flex-wrap:wrap}
.hero h1 {font-size:38px;margin:6px 0 4px;font-weight:800;line-height:1.25}
.eyebrow {font-size:11px;font-weight:750;letter-spacing:3px;color:#208490}
.muted {color:#637e8d;font-size:14px}
.badge {background:#e2f1eb;color:#25715a;border:1px solid #c7e5d7;border-radius:100px;padding:8px 14px;font-size:12px}
.section-note {font-size:12px;color:#6d8390;line-height:1.8}
@media(max-width:640px){.block-container{padding:1.2rem 1rem}.hero h1{font-size:29px}}
</style>'''
