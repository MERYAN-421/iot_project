"""
data_parser.py
--------------
Parses the raw JSON from the CWA F-C0032-001 API.
Extracts regionName, startTime, MinT, and MaxT for each forecast period.
Returns a Pandas DataFrame.

Expected JSON structure:
  data["records"]["location"] -> list of locations
    location["locationName"]  -> region name (e.g. "臺北市")
    location["weatherElement"] -> list of weather elements
      element["elementName"]  -> e.g. "MinT", "MaxT", "Wx"
      element["time"]         -> list of time periods
        time["startTime"]     -> forecast start time
        time["parameter"]["parameterName"] -> the value (e.g. "15")
"""

import pandas as pd


def parse_temperature_forecast(data: dict) -> pd.DataFrame:
    """
    Parses CWA F-C0032-001 JSON and returns a DataFrame with columns:
    [regionName, startTime, minT, maxT]
    """
    records = []

    locations = data.get("records", {}).get("location", [])

    for location in locations:
        region_name = location.get("locationName", "Unknown")

        # Build a dict of elementName -> list of time periods
        elements = {}
        for element in location.get("weatherElement", []):
            element_name = element.get("elementName")
            elements[element_name] = element.get("time", [])

        # MinT and MaxT time periods should align index-by-index
        min_t_periods = elements.get("MinT", [])
        max_t_periods = elements.get("MaxT", [])

        for i, (min_period, max_period) in enumerate(zip(min_t_periods, max_t_periods)):
            start_time = min_period.get("startTime", "")
            min_t = min_period.get("parameter", {}).get("parameterName", None)
            max_t = max_period.get("parameter", {}).get("parameterName", None)

            records.append({
                "regionName": region_name,
                "startTime": start_time,
                "minT": int(min_t) if min_t is not None else None,
                "maxT": int(max_t) if max_t is not None else None,
            })

    df = pd.DataFrame(records, columns=["regionName", "startTime", "minT", "maxT"])
    return df
