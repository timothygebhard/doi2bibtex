"""
Unit tests for isbn.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import pytest

from doi2bibtex.isbn import resolve_isbn_with_google_api


# -----------------------------------------------------------------------------
# TESTS
# -----------------------------------------------------------------------------

def test__resolve_isbn_with_google_api() -> None:
    """
    Test `resolve_isbn_with_google_api()`.
    """

    # Case 1
    with pytest.raises(RuntimeError) as runtime_error:
        resolve_isbn_with_google_api("invalid-isbn")
    assert "no BibTeX entry found" in str(runtime_error)

    # Case 2
    bibtex_dict = resolve_isbn_with_google_api("978-1-4008-3530-0")
    assert bibtex_dict == {
        "ENTRYTYPE": "book",
        "ID": "Seager_2010",
        "author": "Sara Seager",
        "isbn": "978-1-4008-3530-0",
        "publisher": "Princeton University Press",
        "title": "Exoplanet Atmospheres: Physical Processes",
        "year": "2010",
    }

    # Case 3
    bibtex_dict = resolve_isbn_with_google_api("9780691248493")
    assert bibtex_dict == {
        "ENTRYTYPE": "book",
        "ID": "Sinclair_2023",
        "author": (
            "Ian Sinclair and Phil Hockey and Warwick Tarboton and "
            "Niall Perrins and Dominic Rollinson and Peter Ryan"
        ),
        "isbn": "9780691248493",
        "publisher": "Princeton University Press",
        "title": "Birds of Southern Africa: Fifth Edition",
        "year": "2023",
    }
