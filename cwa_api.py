"""
cwa_api.py
----------
Calls the CWA Open Data API endpoint F-C0032-001.
Returns the raw JSON response as a Python dictionary.

Endpoint: 36-hour general weather forecast for all Taiwan cities/counties.

Note: verify=False is used because the CWA government server has a non-standard
SSL certificate (missing Subject Key Identifier) that Python 3.14 rejects.
This is safe for a known, trusted government API endpoint.
"""

import urllib3
import requests
from config import CWA_API_KEY

# Suppress the InsecureRequestWarning caused by verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CWA_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"


def fetch_weather_data() -> dict:
    """
    Calls the CWA F-C0032-001 API and returns the raw JSON as a dict.
    Raises an exception if the request fails.

    verify=False: bypasses SSL check for CWA's non-standard government certificate.
    """
    params = {
        "Authorization": CWA_API_KEY,
        "format": "JSON",
    }

    print(f"Fetching data from CWA API: {CWA_API_URL}")
    response = requests.get(CWA_API_URL, params=params, timeout=10, verify=False)
    response.raise_for_status()

    data = response.json()
    print("API call successful.")
    return data
