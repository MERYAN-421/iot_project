"""
database.py
-----------
SQLite database operations for Taiwan Weather Forecast.
Handles table initialization, storing parsed weather forecasts via UPSERT,
and dedicated read/query functions to support Phase 3 (Streamlit).

Database: weather.db
Table: TemperatureForecasts
Schema:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - regionName: TEXT NOT NULL
  - startTime: TEXT NOT NULL
  - minT: INTEGER
  - maxT: INTEGER
  - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  - UNIQUE(regionName, startTime)  <- composite unique constraint

Unique Index:
  - idx_forecast_unique ON TemperatureForecasts (regionName, startTime)

Data Model Semantics:
  - id remains the auto-increment primary key.
  - Exactly one latest forecast per (regionName, startTime) composite unique constraint.
  - Old forecast periods accumulate as historical records across time.
  - Revisions of the same period by CWA update minT/maxT in-place (no revision versioning).
"""

import os
import sqlite3
from pathlib import Path
from contextlib import closing
import pandas as pd

DEFAULT_DB_PATH = os.environ.get("WEATHER_DB_PATH", str(Path(__file__).with_name("weather.db")))


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initializes the SQLite database and creates the TemperatureForecasts
    table and unique index if they do not exist.
    Verifies that no duplicate keys exist before creating the unique index.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS TemperatureForecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        regionName TEXT NOT NULL,
        startTime TEXT NOT NULL,
        minT INTEGER,
        maxT INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (regionName, startTime)
    );
    """
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)

        # Requirement: verify no duplicate keys exist before creating the unique index
        cursor.execute("""
            SELECT regionName, startTime, COUNT(*)
            FROM TemperatureForecasts
            GROUP BY regionName, startTime
            HAVING COUNT(*) > 1;
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(
                f"[WARNING] Found {len(duplicates)} duplicate (regionName, startTime) groups. "
                "Cleaning up older duplicates to enable unique index..."
            )
            cursor.execute("""
                DELETE FROM TemperatureForecasts
                WHERE id NOT IN (
                    SELECT MAX(id)
                    FROM TemperatureForecasts
                    GROUP BY regionName, startTime
                );
            """)
            conn.commit()

        # Create unique index for backward compatibility with existing databases
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_forecast_unique
            ON TemperatureForecasts (regionName, startTime);
        """)
        conn.commit()


def save_forecasts(df: pd.DataFrame, db_path: str = DEFAULT_DB_PATH) -> dict:
    """
    Saves parsed weather forecast DataFrame into SQLite TemperatureForecasts table
    using UPSERT (INSERT ... ON CONFLICT DO UPDATE).

    Distinguishes:
      - inserted: (regionName, startTime) is new to the database
      - changed: existing row where minT or maxT differs from stored value
      - unchanged: existing row where minT and maxT match stored value
      - total: total rows in database after sync

    Returns:
      dict: {"inserted": int, "changed": int, "unchanged": int, "total": int}
    """
    upsert_sql = """
    INSERT INTO TemperatureForecasts (regionName, startTime, minT, maxT)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(regionName, startTime)
    DO UPDATE SET
        minT = excluded.minT,
        maxT = excluded.maxT;
    """
    records = [
        (
            row["regionName"],
            row["startTime"],
            int(row["minT"]) if pd.notna(row["minT"]) else None,
            int(row["maxT"]) if pd.notna(row["maxT"]) else None,
        )
        for _, row in df.iterrows()
    ]

    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()

        # Fetch existing records to categorize inserted / changed / unchanged
        cursor.execute("SELECT regionName, startTime, minT, maxT FROM TemperatureForecasts;")
        stored = {
            (row[0], row[1]): (row[2], row[3])
            for row in cursor.fetchall()
        }

        inserted_count = 0
        changed_count = 0
        unchanged_count = 0

        for rec in records:
            key = (rec[0], rec[1])
            min_t = rec[2]
            max_t = rec[3]

            if key not in stored:
                inserted_count += 1
                stored[key] = (min_t, max_t)
            else:
                stored_min, stored_max = stored[key]
                if stored_min != min_t or stored_max != max_t:
                    changed_count += 1
                    stored[key] = (min_t, max_t)
                else:
                    unchanged_count += 1

        cursor.executemany(upsert_sql, records)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM TemperatureForecasts;")
        total_count = cursor.fetchone()[0]

    return {
        "inserted": inserted_count,
        "changed": changed_count,
        "unchanged": unchanged_count,
        "total": total_count,
    }


def get_forecasts(db_path: str = DEFAULT_DB_PATH, limit: int = 10) -> pd.DataFrame:
    """
    Queries saved forecast records ordered by id DESC (newest first).
    Returns a Pandas DataFrame.
    """
    query_sql = """
    SELECT id, regionName, startTime, minT, maxT, created_at
    FROM TemperatureForecasts
    ORDER BY id DESC
    LIMIT ?;
    """
    with closing(sqlite3.connect(db_path)) as conn:
        df = pd.read_sql_query(query_sql, conn, params=(limit,))
    return df


def get_total_count(db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Returns the total number of records in the TemperatureForecasts table.
    """
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM TemperatureForecasts;")
        count = cursor.fetchone()[0]
    return count


def get_forecasts_by_region(region_name: str, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Fetches all forecast periods for a specific county/city, ordered by startTime ASC.
    Supports Streamlit region trend charts and timeline tables.
    """
    query_sql = """
    SELECT id, regionName, startTime, minT, maxT, created_at
    FROM TemperatureForecasts
    WHERE regionName = ?
    ORDER BY startTime ASC;
    """
    with closing(sqlite3.connect(db_path)) as conn:
        df = pd.read_sql_query(query_sql, conn, params=(region_name,))
    return df


def get_latest_forecasts(periods: int = 3, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Fetches all regions belonging to the latest N distinct forecast periods.
    Orders the final result by startTime ASC, regionName ASC.
    Supports Streamlit overview tables and map visualizer.
    """
    query_sql = """
    WITH latest_periods AS (
        SELECT DISTINCT startTime
        FROM TemperatureForecasts
        ORDER BY startTime DESC
        LIMIT ?
    )
    SELECT f.id, f.regionName, f.startTime, f.minT, f.maxT, f.created_at
    FROM TemperatureForecasts f
    JOIN latest_periods lp ON f.startTime = lp.startTime
    ORDER BY f.startTime ASC, f.regionName ASC;
    """
    with closing(sqlite3.connect(db_path)) as conn:
        df = pd.read_sql_query(query_sql, conn, params=(periods,))
    return df


def get_all_regions(db_path: str = DEFAULT_DB_PATH) -> list[str]:
    """
    Returns a sorted list of distinct region names stored in the database.
    Supports Streamlit dropdown / selectbox widgets.
    """
    query_sql = """
    SELECT DISTINCT regionName
    FROM TemperatureForecasts
    ORDER BY regionName ASC;
    """
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute(query_sql)
        regions = [row[0] for row in cursor.fetchall()]
    return regions


def get_forecasts_by_time(start_time: str, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Fetches all regional forecasts for a specific forecast startTime.
    Orders results by regionName ASC.
    Supports Streamlit cross-sectional time-slice filter and map slider.
    """
    query_sql = """
    SELECT id, regionName, startTime, minT, maxT, created_at
    FROM TemperatureForecasts
    WHERE startTime = ?
    ORDER BY regionName ASC;
    """
    with closing(sqlite3.connect(db_path)) as conn:
        df = pd.read_sql_query(query_sql, conn, params=(start_time,))
    return df


def get_available_forecast_times(db_path: str = DEFAULT_DB_PATH) -> list[str]:
    """Return distinct forecast start times, newest first."""
    with closing(sqlite3.connect(db_path)) as conn:
        return [row[0] for row in conn.execute(
            "SELECT DISTINCT startTime FROM TemperatureForecasts ORDER BY startTime DESC"
        )]

