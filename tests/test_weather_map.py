"""Offline regression tests using isolated SQLite databases."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import folium
import pandas as pd
from streamlit.testing.v1 import AppTest

import database
from weather_map import TAIWAN_REGION_COORDINATES, build_weather_map, temperature_color

APP = Path(__file__).resolve().parents[1] / "app.py"
REGIONS = "基隆市 臺北市 新北市 桃園市 新竹市 新竹縣 宜蘭縣 苗栗縣 臺中市 彰化縣 南投縣 雲林縣 嘉義市 嘉義縣 臺南市 高雄市 屏東縣 花蓮縣 臺東縣 澎湖縣 金門縣 連江縣".split()


class ForecastMapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = str(Path(self.temp.name) / "test.db")
        database.init_db(self.db)
        self.times = ["2026-09-30 06:00:00", "2026-09-30 18:00:00"]
        self.df = pd.DataFrame([
            dict(regionName=region, startTime=time, minT=20 + i, maxT=27 + i * 6)
            for i, time in enumerate(self.times) for region in REGIONS
        ])
        database.save_forecasts(self.df, self.db)

    def test_distinct_times_and_exact_slices(self):
        self.assertEqual(database.get_available_forecast_times(self.db), self.times[::-1])
        for time in self.times:
            rows = database.get_forecasts_by_time(time, self.db)
            self.assertEqual(len(rows), 22)
            self.assertEqual(set(rows.startTime), {time})
            self.assertEqual(set(rows.regionName), set(TAIWAN_REGION_COORDINATES))
        self.assertTrue(database.get_forecasts_by_time("missing", self.db).empty)

    def test_upsert_keeps_periods_unique(self):
        result = database.save_forecasts(self.df, self.db)
        self.assertEqual(result, dict(inserted=0, changed=0, unchanged=44, total=44))

    def test_temperature_boundaries(self):
        for value, expected in [(23.9, "blue"), (24, "green"), (27.9, "green"),
                                (28, "orange"), (31.9, "orange"), (32, "red"),
                                (None, "gray"), (float("nan"), "gray")]:
            with self.subTest(value=value):
                self.assertEqual(temperature_color(value), expected)

    def test_map_markers_content_and_missing_values(self):
        rows = database.get_forecasts_by_time(self.times[0], self.db)
        rows.loc[0, "maxT"] = float("nan")
        weather_map = build_weather_map(rows)
        markers = [v for v in weather_map._children.values() if isinstance(v, folium.Marker)]
        self.assertEqual(len(markers), 22)
        html = weather_map.get_root().render()
        for region in REGIONS:
            self.assertIn(region, html)
        self.assertIn(self.times[0], html)
        self.assertIn("無資料", html)
        self.assertIn("gray", html)
        self.assertIn("fitBounds", html)

    def run_app(self, callback):
        names = ["init_db", "get_all_regions", "get_forecasts_by_region",
                 "get_latest_forecasts", "get_forecasts_by_time", "get_available_forecast_times"]
        from contextlib import ExitStack
        with ExitStack() as stack:
            for name in names:
                original = getattr(database, name)
                stack.enter_context(patch.object(database, name,
                    side_effect=lambda *a, _fn=original, **kw: _fn(*a, db_path=self.db, **kw)))
            callback(AppTest.from_file(str(APP), default_timeout=30))

    def test_app_tabs_time_change_and_region_independence(self):
        def check(app):
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual([t.label for t in app.tabs], ["🗺️ 全台總覽", "🏙️ 縣市查詢", "🌏 台灣地圖"])
            self.assertEqual(app.selectbox(key="map_forecast_time").value, self.times[-1])
            app.selectbox(key="map_forecast_time").select(self.times[0]).run()
            self.assertFalse(app.exception)
            self.assertTrue(any(self.times[0] in c.value and "22 / 22" in c.value for c in app.caption))
            # Component receives the selected period and corresponding temperatures.
            import json
            component = app.get("component_instance")[0]
            payload = json.loads(component.proto.json_args)
            self.assertIn(self.times[0], payload["script"])
            self.assertNotIn(self.times[1], payload["script"])
            self.assertIn("27 °C", payload["script"])
            app.sidebar.selectbox[0].select("金門縣").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.selectbox(key="map_forecast_time").value, self.times[0])
        self.run_app(check)

    def test_empty_database_shows_instructions(self):
        self.db = str(Path(self.temp.name) / "empty.db")
        def check(app):
            app.run()
            self.assertFalse(app.exception)
            self.assertIn("main.py", app.error[0].value)
        self.run_app(check)

    def test_cloud_entrypoint_and_failed_sync_keep_dashboard(self):
        import streamlit as st
        cloud = APP.with_name("cloud_app.py")
        def check(_app):
            st.cache_data.clear()
            with patch("sync_service.sync_forecasts", return_value={}) as sync:
                app = AppTest.from_file(str(cloud), default_timeout=30).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.tabs), 3)
                app.run()
                self.assertEqual(sync.call_count, 1)
            st.cache_data.clear()
            with patch("sync_service.sync_forecasts", side_effect=RuntimeError("SECRET_REQUEST_URL")):
                app = AppTest.from_file(str(cloud), default_timeout=30).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.tabs), 3)
                self.assertIn("同步暫時失敗", app.warning[0].value)
                self.assertNotIn("SECRET_REQUEST_URL", app.warning[0].value)
            st.cache_data.clear()
        self.run_app(check)


if __name__ == "__main__":
    unittest.main()
