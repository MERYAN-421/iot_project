"""Reusable API-to-database synchronization for hosted startup."""
from database import DEFAULT_DB_PATH, init_db, save_forecasts
from data_parser import parse_temperature_forecast


def sync_forecasts(db_path: str = DEFAULT_DB_PATH) -> dict:
    # Import lazily: viewing an existing database requires no API credentials.
    from cwa_api import fetch_weather_data

    forecasts = parse_temperature_forecast(fetch_weather_data())
    if forecasts.empty:
        raise ValueError("CWA returned no temperature forecasts")
    init_db(db_path)
    return save_forecasts(forecasts, db_path)
