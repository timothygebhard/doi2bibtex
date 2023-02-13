"""
Utility functions.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pylatexenc.latex2text import LatexNodes2Text
from unidecode import unidecode

import urllib.parse


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

def doi_to_url(doi: str) -> str:
    """
    Convert a DOI to a URL.
    """

    encoded_doi = urllib.parse.quote(doi, safe="")
    return f"https://doi.org/{encoded_doi}"


def latex_to_unicode(text: str) -> str:
    """
    Convert LaTeX-escaped to Unicode. Example: "{\"a}" -> "ä".
    Note: characters in math mode are *not* converted.
    """
    return str(LatexNodes2Text(math_mode='verbatim').latex_to_text(text))


def remove_accented_characters(string: str) -> str:
    """
    Remove accented characters from a string (e.g., to generate an
    ASCII-compatible citekey).
    """

    # Manually replace some characters
    string = string.replace("Ä", "Ae")
    string = string.replace("Ö", "Oe")
    string = string.replace("Ü", "Ue")
    string = string.replace("ä", "ae")
    string = string.replace("ö", "oe")
    string = string.replace("ü", "ue")
    string = string.replace("ß", "ss")

    # Use unidecode to replace the rest (e.g., "é" -> "e")
    string = str(unidecode(string, "utf-8"))

    return string
