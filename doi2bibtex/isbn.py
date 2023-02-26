"""
Resolve ISBN numbers to BibTeX entries.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import json

import requests

from doi2bibtex.process import generate_citekey


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

def resolve_isbn_with_google_api(isbn: str) -> dict:
    """
    Resolve a given `isbn` number using the Google Books API and return
    the BibTeX entry as a dictionary.
    """

    # Query the Google Books API
    r = requests.get(
        url=f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}",
        headers={"Accept": "application/json"},
    )

    # Check if we got a 200 response; if not, raise an error
    if (error := r.status_code) != 200:
        raise RuntimeError(
            f'Error {error} resolving "{isbn}": no BibTeX entry found'
        )

    # Parse the response using JSON
    response = json.loads(r.text)

    # Check if we got any results; if not, raise an error
    if not (items := response.get("items", [])):
        raise RuntimeError(
            f'Error resolving "{isbn}": no BibTeX entry found'
        )

    # Get the first item; define shortcuts
    item = items[0]
    title = item["volumeInfo"].get("title", "")
    subtitle = item["volumeInfo"].get("subtitle", "")

    # Manually construct a BibTeX entry
    bibtex_dict = {
        "ENTRYTYPE": "book",
        "ID": isbn,
        "author": " and ".join(item["volumeInfo"].get("authors", [])),
        "title": title + ((": " + subtitle) if subtitle else ""),
        "publisher": item["volumeInfo"].get("publisher", ""),
        "year": item["volumeInfo"].get("publishedDate", "")[:4],
        "isbn": isbn,
    }

    # Construct the citekey
    bibtex_dict = generate_citekey(bibtex_dict)

    return bibtex_dict
