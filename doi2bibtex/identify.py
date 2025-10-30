"""
Methods for identifying the type of identifier (DOI or arXiv ID).
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import re

from isbnlib import is_isbn10, is_isbn13


# -----------------------------------------------------------------------------
# DEFINTIONS
# -----------------------------------------------------------------------------

def is_ads_bibcode(identifier: str) -> bool:
    """
    Check if the given `identifier` is an ADS bibcode.
    """

    # Define a pattern for ADS bibcodes (basic format: "YYYYJJJJJVVVVMPPPPA")
    # For details, see: https://ui.adsabs.harvard.edu/help/actions/bibcode
    pattern = (
        r"^"
        r"(?P<YYYY>\d{4})"
        r"(?P<JJJJJ>[\w\.\&]{5})"
        r"(?P<VVVV>[\w\.]{4})"
        r"(?P<M>\S)"
        r"(?P<PPPP>[\d\.]{4})"
        r"(?P<A>[A-Z])"
        r"$"
    )

    return re.match(pattern, identifier) is not None


def is_arxiv_id(identifier: str) -> bool:
    """
    Check if the given `identifier` is an arXiv ID.
    """

    # Define a list of arXiv ID patterns
    # See: https://info.arxiv.org/help/arxiv_identifier.html
    patterns = [
        r"^\d{4}.\d{4,5}(v\d+)?$",
        r"^[a-z\-]+(\.[A-Z]{2})?\/\d{7}(v\d+)?$",
    ]

    return any(re.match(pattern, identifier) for pattern in patterns)


def preprocess_arxiv_identifier(identifier: str) -> str:
    """
    Extract the arXiv ID from various formats.

    Supports:
    - https://arxiv.org/abs/XXXX.XXXXX
    - arxiv.org/abs/XXXX.XXXXX
    - https://doi.org/10.48550/arXiv.XXXX.XXXXX
    - doi.org/10.48550/arXiv.XXXX.XXXXX
    - 10.48550/arXiv.XXXX.XXXXX
    - arXiv.XXXX.XXXXX or arXiv:XXXX.XXXXX
    - XXXX.XXXXX (plain ID)

    Works with old format (pre-2007): arch-ive/YYMMNNN
    Works with new format (post-2007): YYMM.NNNNN

    With or without 'www' and case-insensitive for 'arXiv'.

    Returns the extracted arXiv ID or the original identifier if no pattern matches.
    """

    # Remove non-printable ASCII characters and whitespace (keep only characters from ! to ~)
    identifier = re.sub(r'[^\x21-\x7E]', '', identifier)

    # Pattern for https://arxiv.org/abs/... or arxiv.org/abs/...
    arxiv_url_match = re.search(
        r"(?:https?://)?(?:www\.)?arxiv\.org/abs/(.+)",
        identifier,
        re.IGNORECASE
    )
    if arxiv_url_match:
        return arxiv_url_match.group(1).strip()

    # Pattern for DOI URLs: https://doi.org/10.48550/arXiv.XXXX.XXXXX
    doi_url_match = re.search(
        r"(?:https?://)?(?:www\.)?doi\.org/10\.48550/arxiv[\.:](.+)",
        identifier,
        re.IGNORECASE
    )
    if doi_url_match:
        return doi_url_match.group(1).strip()

    # Pattern for DOI without domain: 10.48550/arXiv.XXXX.XXXXX
    doi_prefix_match = re.search(
        r"^10\.48550/arxiv[\.:](.+)",
        identifier,
        re.IGNORECASE
    )
    if doi_prefix_match:
        return doi_prefix_match.group(1).strip()

    # Pattern for arXiv prefix: arXiv.XXXX.XXXXX or arXiv:XXXX.XXXXX
    arxiv_prefix_match = re.search(
        r"^arxiv[\.:](.+)",
        identifier,
        re.IGNORECASE
    )
    if arxiv_prefix_match:
        return arxiv_prefix_match.group(1).strip()

    # Return the identifier as-is if no pattern matched
    return identifier


def is_doi(identifier: str) -> bool:
    """
    Check if the given `identifier` is a DOI.
    """

    # Define a list of DOI patterns
    # See: https://www.crossref.org/blog/dois-and-matching-regular-expressions
    patterns = [
        r"^10.\d{4,9}/[-.;()/:\w]+$",
        r"^10.1002/[^\s]+$",
        r"^10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\d$",
        r"^10.1021/\w\w\d+$",
        r"^10.1207/[\w\d]+\&\d+_\d+$",
    ]

    return any(re.match(pattern, identifier) for pattern in patterns)


def is_isbn(identifier: str) -> bool:
    """
    Check if the given `identifier` is an ISBN.

    This is just a super thin wrapper around `isbnlib.is_isbn10()` and
    `isbnlib.is_isbn13()`.
    """

    return bool(is_isbn10(identifier)) or bool(is_isbn13(identifier))
