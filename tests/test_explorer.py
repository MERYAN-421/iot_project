import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from database import init_db, save_forecasts, get_forecasts_by_time, save_observations, get_observations
from data_parser import parse_temperature_forecast, parse_observations
from geography import county_boundaries, region_from_tooltip
from weather_map import TAIWAN_REGION_COORDINATES, build_weather_map
from ui import forecast_card, observation_card


def station(station_id="A", temp="22.5", rain="T"):
    return {"StationId": station_id, "StationName": "測試站", "ObsTime": {"DateTime": "2026-09-30T02:00:00+08:00"},
            "GeoInfo": {"CountyName": "台北市", "TownName": "中正區", "Coordinates": [
                {"CoordinateName":"TWD67", "StationLatitude":"0", "StationLongitude":"0"},
                {"CoordinateName":"WGS84", "StationLatitude":"25.03", "StationLongitude":"121.56"}]},
            "WeatherElement": {"AirTemperature": temp, "RelativeHumidity":"-99", "WindSpeed":"X",
                               "Now":{"Precipitation": rain}, "Weather":"晴"}}


class ExplorerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = str(Path(self.temp.name) / "test.db")

    def test_migrate_old_schema_without_losing_forecasts(self):
        conn = sqlite3.connect(self.db)
        conn.execute("CREATE TABLE TemperatureForecasts (id INTEGER PRIMARY KEY, regionName TEXT, startTime TEXT, minT INTEGER, maxT INTEGER, created_at TEXT)")
        conn.execute("INSERT INTO TemperatureForecasts VALUES (1,'臺北市','2026-09-30 06:00:00',20,30,'old')")
        conn.commit(); conn.close()
        init_db(self.db)
        init_db(self.db)
        rows = get_forecasts_by_time("2026-09-30 06:00:00", self.db)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows.iloc[0].minT, 20)
        self.assertIsNone(rows.iloc[0].weather)
        self.assertTrue(get_observations(db_path=self.db).empty)

    def test_forecast_joins_by_timestamp_not_position(self):
        def period(time, val):
            return {"startTime":time,"endTime":"end","parameter":{"parameterName":val}}
        data = {"records":{"location":[{"locationName":"臺北市","weatherElement":[
            {"elementName":"MinT","time":[period("A","20"),period("B","21")]},
            {"elementName":"MaxT","time":[period("B","31"),period("A","30")]},
            {"elementName":"PoP","time":[period("A","70")]},
            {"elementName":"Wx","time":[period("A","短暫雨")]}]}]}}
        rows = parse_temperature_forecast(data).set_index("startTime")
        self.assertEqual(rows.loc["A", "maxT"], 30)
        self.assertEqual(rows.loc["B", "maxT"], 31)
        self.assertEqual(rows.loc["A", "pop"], 70)
        self.assertTrue(pd.isna(rows.loc["B", "pop"]))

    def test_station_missing_values_and_wgs84(self):
        rows = parse_observations({"records":{"Station":[station(temp="-99")]}})
        row = rows.iloc[0]
        self.assertIsNone(row.temperature)
        self.assertIsNone(row.humidity)
        self.assertIsNone(row.windSpeed)
        self.assertIsNone(row.precipitation)
        self.assertEqual(row.rainTrace, 1)
        self.assertEqual(row.latitude, 25.03)
        self.assertEqual(row.regionName, "臺北市")

    def test_invalid_coordinates_skipped(self):
        entry = station()
        entry["GeoInfo"]["Coordinates"][1]["StationLatitude"] = "-99"
        self.assertTrue(parse_observations({"records":{"Station":[entry]}}).empty)

    def test_snapshot_replacement_empty_failure_retains_data(self):
        init_db(self.db)
        rows = parse_observations({"records":{"Station":[station("A"), station("B")]}})
        self.assertEqual(save_observations(rows, self.db), 2)
        with self.assertRaises(ValueError):
            save_observations(rows.iloc[0:0], self.db)
        self.assertEqual(len(get_observations(db_path=self.db)), 2)
        save_observations(rows.iloc[:1], self.db)
        self.assertEqual(get_observations("臺北市", self.db).stationId.tolist(), ["A"])

    def test_all_22_boundaries_closed_and_valid_range(self):
        boundaries = county_boundaries()
        self.assertEqual({f["properties"]["regionName"] for f in boundaries["features"]}, set(TAIWAN_REGION_COORDINATES))
        for feature in boundaries["features"]:
            geom = feature["geometry"]
            polygons = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
            for polygon in polygons:
                for ring in polygon:
                    self.assertEqual(ring[0], ring[-1])
                    self.assertGreaterEqual(len(ring), 4)
                    for lon, lat in ring:
                        self.assertTrue(117 < lon < 123 and 21 < lat < 27)

    def test_html_escaped_and_map_selection(self):
        card = forecast_card(dict(regionName="<script>alert(1)</script>",minT=20,maxT=30,weather="<b>x</b>"))
        self.assertNotIn("<script>", card)
        self.assertIn("&lt;script&gt;", card)
        self.assertEqual(region_from_tooltip("臺北市 · 臺北", TAIWAN_REGION_COORDINATES), "臺北市")
        self.assertIsNone(region_from_tooltip("Unknown", TAIWAN_REGION_COORDINATES))

    def test_station_layer_and_selected_boundary(self):
        rows = parse_observations({"records":{"Station":[station()]}})
        forecasts = pd.DataFrame([dict(regionName="臺北市", minT=20,maxT=30,startTime="now")])
        m = build_weather_map(forecasts, "臺北市", rows, "observations", True)
        html = m.get_root().render()
        self.assertIn("markerClusterGroup", html)
        self.assertIn("測試站", html)
        self.assertIn("雨跡", html)
        self.assertIn("3.5", html)


if __name__ == "__main__":
    unittest.main()
