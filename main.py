"""
main.py
-------
Entry point for Phase 2.2 of the Taiwan Weather Forecast project.

Flow:
  1. Load API key from .env (via config.py)
  2. Call CWA F-C0032-001 API (via cwa_api.py)
  3. Parse JSON and extract MinT / MaxT (via data_parser.py)
  4. Initialize SQLite database, table, and unique index (via database.py)
  5. Store parsed DataFrame into SQLite using UPSERT
     - Reports: inserted, changed, unchanged, and total
  6. Demonstrate query functions (for future Streamlit dashboard)

Data Model Semantics:
  - id is the auto-increment primary key.
  - UNIQUE(regionName, startTime) is a composite unique constraint.
  - Historical periods accumulate across time.
  - Revisions of the same period update minT/maxT in-place without versioning.
"""

import sys
import io

# Fix Chinese character encoding for Windows terminal (PowerShell / CMD)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from cwa_api import fetch_weather_data
from data_parser import parse_temperature_forecast
from database import (
    init_db,
    save_forecasts,
    get_forecasts,
    get_forecasts_by_region,
    get_latest_forecasts,
    get_all_regions,
)


def main():
    print("=== Taiwan Weather Forecast - Phase 2.2 (Data Semantics & Queries) ===\n")

    # Step 1: Fetch raw JSON from CWA API
    raw_data = fetch_weather_data()

    # Step 2: Parse and extract temperature forecasts
    df = parse_temperature_forecast(raw_data)
    print(f"\nParsed records from CWA: {len(df)}")
    print(f"Regions found: {df['regionName'].nunique()}")

    # Step 3: Initialize SQLite database & table & unique index
    print("\n--- SQLite Database Operations ---")
    init_db()
    print("Database, table 'TemperatureForecasts', and unique index verified.")

    # Step 4: Save DataFrame to SQLite via UPSERT (4-part sync metrics)
    sync_result = save_forecasts(df)
    print("\nSync Metrics:")
    print(f"  - New rows inserted:        {sync_result['inserted']}")
    print(f"  - Existing rows changed:    {sync_result['changed']}")
    print(f"  - Existing rows unchanged:  {sync_result['unchanged']}")
    print(f"  - Total rows after sync:    {sync_result['total']}")

    # Step 5: Verify Query Functions (Phase 3 Foundation)
    print("\n--- Query Verification: get_all_regions() ---")
    regions = get_all_regions()
    print(f"Total available regions ({len(regions)}): {regions[:6]} ...")

    print("\n--- Query Verification: get_forecasts_by_region('臺北市') ---")
    taipei_df = get_forecasts_by_region("臺北市")
    print(taipei_df.to_string(index=False))

    print("\n--- Query Verification: get_latest_forecasts(periods=1) (First 5 regions) ---")
    latest_df = get_latest_forecasts(periods=1)
    print(latest_df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()



