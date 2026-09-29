"""
main.py
-------
Entry point for Phase 2 of the Taiwan Weather Forecast project.

Flow:
  1. Load API key from .env (via config.py)
  2. Call CWA F-C0032-001 API (via cwa_api.py)
  3. Parse JSON and extract MinT / MaxT (via data_parser.py)
  4. Initialize SQLite database and table (via database.py)
  5. Store parsed DataFrame into SQLite (append mode)
  6. Query and display sample rows from SQLite for verification

Note:
  Append behavior is active for this milestone; rerunning main.py
  will insert another 66 rows into weather.db each time.
"""

import sys
import io

# Fix Chinese character encoding for Windows terminal (PowerShell / CMD)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from cwa_api import fetch_weather_data
from data_parser import parse_temperature_forecast
from database import init_db, save_forecasts, get_forecasts, get_total_count


def main():
    print("=== Taiwan Weather Forecast - Phase 2 (SQLite Integration) ===\n")

    # Step 1: Fetch raw JSON from CWA API
    raw_data = fetch_weather_data()

    # Step 2: Parse and extract temperature forecasts
    df = parse_temperature_forecast(raw_data)
    print(f"\nParsed records: {len(df)}")
    print(f"Regions found: {df['regionName'].nunique()}")

    # Step 3: Initialize SQLite database & table
    print("\n--- SQLite Database Operations ---")
    init_db()
    print("Database and table 'TemperatureForecasts' initialized.")

    # Step 4: Save DataFrame to SQLite
    inserted_count = save_forecasts(df)
    total_count = get_total_count()
    print(f"Successfully inserted: {inserted_count} rows.")
    print(f"Total rows currently in database: {total_count}")
    print("[Note: Append mode is active; rerunning main.py will add another 66 rows.]")

    # Step 5: Query sample rows back from SQLite (ordered by id DESC)
    print("\n--- Sample Queried Rows (ORDER BY id DESC, limit 5) ---")
    sample_df = get_forecasts(limit=5)
    print(sample_df.to_string(index=False))


if __name__ == "__main__":
    main()

