"""
database.py
-----------
SQLite database operations for Taiwan Weather Forecast.
Handles table initialization, storing parsed weather forecasts, and querying data.

Database: weather.db
Table: TemperatureForecasts
Schema:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - regionName: TEXT NOT NULL
  - startTime: TEXT NOT NULL
  - minT: INTEGER
  - maxT: INTEGER
  - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Milestone 1 behavior:
  - Appends records to the database.
  - Note: Rerunning save_forecasts (or main.py) will insert another 66 rows each time.
    Deduplication and upsert logic will be introduced in future milestones.
"""

import sqlite3
import pandas as pd

DEFAULT_DB_PATH = "weather.db"


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initializes the SQLite database and creates the TemperatureForecasts
    table if it does not exist.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS TemperatureForecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        regionName TEXT NOT NULL,
        startTime TEXT NOT NULL,
        minT INTEGER,
        maxT INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()


def save_forecasts(df: pd.DataFrame, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Saves parsed weather forecast DataFrame into SQLite TemperatureForecasts table.
    
    Append behavior:
      Inserts all rows from the DataFrame. Note that rerunning this function
      will insert another set of records (e.g. 66 rows) each time.

    Returns:
      Number of rows inserted.
    """
    insert_sql = """
    INSERT INTO TemperatureForecasts (regionName, startTime, minT, maxT)
    VALUES (?, ?, ?, ?);
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

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(insert_sql, records)
        conn.commit()

    return len(records)


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
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query_sql, conn, params=(limit,))
    return df


def get_total_count(db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Returns the total number of records in the TemperatureForecasts table.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM TemperatureForecasts;")
        count = cursor.fetchone()[0]
    return count
