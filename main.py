"""
main.py
-------
Entry point for Phase 1 of the Taiwan Weather Forecast project.

Flow:
  1. Load API key from .env (via config.py)
  2. Call CWA F-C0032-001 API (via cwa_api.py)
  3. Parse JSON and extract MinT / MaxT (via data_parser.py)
  4. Print the resulting Pandas DataFrame
"""

import sys
import io

# Fix Chinese character encoding for Windows terminal (PowerShell / CMD)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from cwa_api import fetch_weather_data
from data_parser import parse_temperature_forecast


def main():
    print("=== Taiwan Weather Forecast - Phase 1 ===\n")

    # Step 1: Fetch raw JSON from CWA API
    raw_data = fetch_weather_data()

    # Step 2: Parse and extract temperature forecasts
    df = parse_temperature_forecast(raw_data)

    # Step 3: Display the DataFrame
    print(f"\nTotal records: {len(df)}")
    print(f"Regions found: {df['regionName'].nunique()}\n")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
