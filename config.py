"""
config.py
---------
Loads environment variables from .env using python-dotenv.
Provides the CWA API key to other modules.
"""

import os
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv()

CWA_API_KEY = os.getenv("CWA_API_KEY")

if not CWA_API_KEY:
    raise EnvironmentError(
        "CWA_API_KEY not found. "
        "Please create a .env file with: CWA_API_KEY=your_key_here"
    )
