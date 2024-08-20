"""
Methods that deal with querying the NASA/ADS database system.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import json
import os

import requests


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

def get_ads_token(raise_on_error: bool = False) -> Optional[str]:
    """
    Get the ADS API token from an environment variable or a file.
    If `raise_on_error` is True, raise an error if no token is found.
    This is False by default so that we can also use this function to
    decide which unit tests to run.
    """

    # Try to get the ADS token from an environment variable
    if (token := os.environ.get("ADS_TOKEN")) is not None:
        return token

    # Try to get the ADS token from a file
    file_path = Path.home() / ".doi2bibtex" / "ads_token"
    if file_path.exists():
        with open(file_path, "r") as f:
            return f.read().strip()

    # If we get here, we didn't find a token
    if raise_on_error:
        raise RuntimeError(
            "No ADS token found! Please set the ADS_TOKEN environment "
            "variable, or create a file at ~/.doi2bibtex/ads_token "
            "containing your ADS token."
        )

    return None


def get_ads_bibcode_for_identifier(identifier: str) -> str:
    """
    Query ADS for the given `identifier` and return the bibcode of the
    matching result (or an empty string, if no results are found).
    """

    # Get the ADS token (and raise an error if we don't have one)
    token = get_ads_token(raise_on_error=True)

    # Query the ADS API manually
    q = urlencode({"identifier": identifier})
    q = q.replace("identifier=", "identifier:")
    fl = "bibcode,identifier"
    r = requests.get(
        url=f"https://api.adsabs.harvard.edu/v1/search/query?q={q}&fl={fl}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    # Check if we got a 200 response
    if r.status_code != 200:
        return ""

    # Parse the response using JSON
    response = json.loads(r.text)["response"]

    # Find the result that matches the identifier
    for result in response["docs"]:
        if any(identifier.lower() in _.lower() for _ in result["identifier"]):
            return str(result["bibcode"])

    # If we get here, we didn't find a match
    return ""
