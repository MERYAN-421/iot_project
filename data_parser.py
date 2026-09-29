"""CWA parsers; join forecasts by time and preserve missing observation values."""
import math
import pandas as pd


def number(value, minimum=None, maximum=None):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value) or value in (-99, -999, -9999, -98):
        return None
    if minimum is not None and value < minimum:
        return None
    if maximum is not None and value > maximum:
        return None
    return value


def parse_temperature_forecast(data: dict) -> pd.DataFrame:
    rows = []
    for location in data.get("records", {}).get("location", []):
        periods = {}
        mapping = {"MinT": "minT", "MaxT": "maxT", "Wx": "weather", "PoP": "pop", "CI": "comfort"}
        for element in location.get("weatherElement", []):
            field = mapping.get(element.get("elementName"))
            if not field:
                continue
            for period in element.get("time", []):
                start = period.get("startTime")
                if not start:
                    continue
                row = periods.setdefault(start, {"regionName": location["locationName"], "startTime": start})
                row["endTime"] = period.get("endTime")
                value = period.get("parameter", {}).get("parameterName")
                row[field] = number(value) if field in ("minT", "maxT", "pop") else value
        rows.extend(periods.values())
    return pd.DataFrame(rows, columns=["regionName", "startTime", "minT", "maxT", "endTime", "weather", "pop", "comfort"])


def parse_observations(data: dict) -> pd.DataFrame:
    from database import STATION_COLUMNS
    rows = []
    for station in data.get("records", {}).get("Station", []):
        geo = station.get("GeoInfo", {})
        coords = next((c for c in geo.get("Coordinates", []) if c.get("CoordinateName") == "WGS84"), {})
        lat = number(coords.get("StationLatitude"), -90, 90)
        lon = number(coords.get("StationLongitude"), -180, 180)
        if lat is None or lon is None or not station.get("StationId"):
            continue
        weather = station.get("WeatherElement", {})
        rain = weather.get("Now", {}).get("Precipitation")
        rows.append(dict(
            stationId=station["StationId"], stationName=station.get("StationName", station["StationId"]),
            regionName=geo.get("CountyName", "").replace("台", "臺"), townName=geo.get("TownName", ""),
            latitude=lat, longitude=lon, observedAt=station.get("ObsTime", {}).get("DateTime"),
            temperature=number(weather.get("AirTemperature"), -80, 65),
            humidity=number(weather.get("RelativeHumidity"), 0, 100),
            windSpeed=number(weather.get("WindSpeed"), 0),
            precipitation=number(rain, 0), rainTrace=int(rain == "T"),
            weather=weather.get("Weather") if weather.get("Weather") not in ("-99", "X") else None,
        ))
    return pd.DataFrame(rows, columns=STATION_COLUMNS).drop_duplicates("stationId", keep="last")
