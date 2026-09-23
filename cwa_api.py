"""
cwa_api.py
----------
Calls the CWA Open Data API endpoint F-C0032-001.
Returns the raw JSON response as a Python dictionary.

Endpoint: 36-hour general weather forecast for all Taiwan cities/counties.

SSL Note:
  The CWA server certificate is missing a Subject Key Identifier (SKI) extension,
  which violates RFC 5280. Python 3.12+ (via OpenSSL 3.x) enforces this strictly.

  Approaches tested and their results (Phase 1.5 investigation):
    - verify=True (default)        → FAILED: SSLCertVerificationError (Missing SKI)
    - verify=certifi.where()       → FAILED: same error (not a CA trust issue)
    - truststore (OS cert store)   → FAILED: same error (SKI is enforced at OpenSSL level)
    - verify=False                 → SUCCESS (22 locations returned)

  Conclusion: verify=False is currently the only working option.
  This is a limitation of the remote server's certificate configuration.
  A warning is printed every time this fallback is used.
  When CWA updates their certificate, verify=True should be restored.
"""

import requests
import urllib3
from config import CWA_API_KEY

CWA_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"


def fetch_weather_data() -> dict:
    """
    Calls the CWA F-C0032-001 API and returns the raw JSON as a dict.
    Raises an exception if the request fails.

    Uses verify=False as a temporary fallback due to a server-side SSL
    certificate deficiency (Missing Subject Key Identifier, RFC 5280).
    A visible warning is printed each time the fallback is active.
    """
    params = {
        "Authorization": CWA_API_KEY,
        "format": "JSON",
    }

    print(f"Fetching data from CWA API: {CWA_API_URL}")

    # Attempt 1: Standard SSL verification
    try:
        import certifi
        response = requests.get(
            CWA_API_URL, params=params, timeout=10, verify=certifi.where()
        )
        response.raise_for_status()
        data = response.json()
        print("API call successful (SSL verified).")
        return data

    except requests.exceptions.SSLError:
        # Attempt 2: Fallback — SSL verification disabled
        # Reason: CWA server cert is missing Subject Key Identifier (RFC 5280).
        # Tested: verify=True, certifi, and truststore all fail with the same error.
        # This warning should be removed once CWA fixes their certificate.
        print(
            "\n[WARNING] SSL certificate verification failed.\n"
            "  Cause: CWA server certificate is missing Subject Key Identifier (RFC 5280).\n"
            "  Tested: verify=True, certifi, truststore — all failed with the same error.\n"
            "  Falling back to verify=False (temporary workaround).\n"
            "  Action required: restore verify=True when CWA updates their certificate.\n"
        )
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(
            CWA_API_URL, params=params, timeout=10, verify=False
        )
        response.raise_for_status()
        data = response.json()
        print("API call successful (SSL verification bypassed — see warning above).")
        return data
