"""
Methods that deal with querying the NASA/ADS database system.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pathlib import Path
from typing import Optional

import os

import ads


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

def get_ads_token() -> Optional[str]:
    """
    Get the ADS API token from an environment variable or a file.
    """

    # Try to get the ADS token from an environment variable
    if (token := os.environ.get("ADS_TOKEN")) is not None:
        return token

    # Try to get the ADS token from a file
    file_path = Path.home() / ".doi2bibtex" / "ads_token"
    if file_path.exists():
        with open(file_path, "r") as f:
            return f.read().strip()

    return None


def resolve_ads_bibcode(identifier: str) -> str:
    """
    Query ADS for the given `identifier` and return the bibcode of the
    first result (or an empty string, if no results are found).
    """

    # Get the ADS token (and raise an error if we don't have one)
    if (token := get_ads_token()) is None:
        raise RuntimeError(
            "No ADS token found! Please set the ADS_TOKEN environment "
            "variable, or create a file at ~/.doi2bibtex/ads_token "
            "containing your ADS token."
        )

    # Set the ADS token
    # noinspection PyUnresolvedReferences
    ads.config.token = token

    # Query ADS, return the bibcode of the first result, or an empty string
    # the the query returns no results
    try:
        query = ads.SearchQuery(q=identifier, fl=["bibcode"])
        return str(next(query).bibcode)
    except StopIteration:
        return ""
