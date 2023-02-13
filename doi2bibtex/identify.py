"""
Methods for identifying the type of identifier (DOI or arXiv ID).
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import re


# -----------------------------------------------------------------------------
# DEFINTIONS
# -----------------------------------------------------------------------------

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
