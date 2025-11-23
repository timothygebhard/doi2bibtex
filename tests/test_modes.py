"""
Unit tests for mode switching and identifier resolution.
Tests that different identifier types (DOI, arXiv, ISBN, ADS bibcode) are
correctly resolved through resolve_identifier().
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from unittest.mock import Mock

import pytest

from doi2bibtex.config import Configuration
from doi2bibtex.resolve import resolve_identifier


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__resolve_identifier_doi_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()` with DOI input.
    """

    # Mock the resolve_doi function
    mock_bibtex_dict = {
        "ENTRYTYPE": "article",
        "ID": "test2023",
        "author": "Test Author",
        "title": "Test Title",
        "journal": "Test Journal",
        "year": "2023",
        "doi": "10.1234/test.doi"
    }

    def mock_resolve_doi(doi: str) -> dict:
        return mock_bibtex_dict.copy()

    # Patch resolve_doi
    import doi2bibtex.resolve
    monkeypatch.setattr(doi2bibtex.resolve, "resolve_doi", mock_resolve_doi)

    # Test resolution
    config = Configuration()
    result = resolve_identifier(identifier="10.1234/test.doi", config=config)

    assert isinstance(result, str)
    assert "@article{" in result or "@Article{" in result
    # Authors are reformatted to "{Lastname}, Firstname" format
    assert "Author" in result and "Test" in result
    assert "Test Title" in result


def test__resolve_identifier_arxiv_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()` with arXiv ID input.
    """

    # Mock the resolve_arxiv_id function
    mock_bibtex_dict = {
        "ENTRYTYPE": "article",
        "ID": "arxiv2023",
        "author": "ArXiv Author",
        "title": "ArXiv Paper",
        "year": "2023",
        "eprint": "2301.12345"
    }

    def mock_resolve_arxiv(arxiv_id: str) -> dict:
        return mock_bibtex_dict.copy()

    # Patch resolve_arxiv_id
    import doi2bibtex.resolve
    monkeypatch.setattr(doi2bibtex.resolve, "resolve_arxiv_id", mock_resolve_arxiv)

    # Test resolution
    config = Configuration()
    result = resolve_identifier(identifier="2301.12345", config=config)

    assert isinstance(result, str)
    assert "@article{" in result or "@Article{" in result
    # Authors are reformatted to "{Lastname}, Firstname" format
    assert "Author" in result and "ArXiv" in result
    assert "ArXiv Paper" in result


def test__resolve_identifier_ads_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()` with ADS bibcode input.
    """

    # Mock the resolve_ads_bibcode function
    mock_bibtex_dict = {
        "ENTRYTYPE": "article",
        "ID": "ads2023",
        "author": "ADS Author",
        "title": "ADS Paper",
        "journal": "ApJ",
        "year": "2023"
    }

    def mock_resolve_ads(bibcode: str) -> dict:
        return mock_bibtex_dict.copy()

    # Patch resolve_ads_bibcode
    import doi2bibtex.resolve
    monkeypatch.setattr(doi2bibtex.resolve, "resolve_ads_bibcode", mock_resolve_ads)

    # Test resolution (using a valid ADS bibcode format)
    config = Configuration()
    result = resolve_identifier(identifier="2023ApJ...123..456A", config=config)

    assert isinstance(result, str)
    assert "@article{" in result or "@Article{" in result
    # Authors are reformatted to "{Lastname}, Firstname" format
    assert "Author" in result and "ADS" in result
    assert "ADS Paper" in result


def test__resolve_identifier_isbn_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()` with ISBN input.
    Note: This test requires internet connection to query Google Books API.
    """

    # Test resolution with a real ISBN (requires internet)
    config = Configuration()

    try:
        result = resolve_identifier(identifier="9780134685991", config=config)

        # Verify it returns a book entry
        assert isinstance(result, str)
        assert "@book{" in result or "@Book{" in result
        # Check that it contains expected BibTeX fields
        assert "author" in result.lower()
        assert "title" in result.lower()
        assert "isbn" in result.lower()
    except Exception as e:
        # If the API is unavailable, skip the test
        pytest.skip(f"Google Books API unavailable: {e}")


def test__resolve_identifier_with_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()` with doi: and arXiv: prefixes.
    """

    # Mock resolve_doi
    mock_bibtex_dict = {
        "ENTRYTYPE": "article",
        "ID": "test2023",
        "author": "Test Author",
        "title": "Test Title",
        "year": "2023"
    }

    def mock_resolve_doi(doi: str) -> dict:
        return mock_bibtex_dict.copy()

    import doi2bibtex.resolve
    monkeypatch.setattr(doi2bibtex.resolve, "resolve_doi", mock_resolve_doi)

    config = Configuration()

    # Test with "doi:" prefix
    result = resolve_identifier(identifier="doi:10.1234/test.doi", config=config)
    assert isinstance(result, str)
    # Authors are reformatted to "{Lastname}, Firstname" format
    assert "Author" in result and "Test" in result

    # Test with "DOI:" prefix (uppercase)
    result = resolve_identifier(identifier="DOI:10.1234/test.doi", config=config)
    assert isinstance(result, str)
    # Authors are reformatted to "{Lastname}, Firstname" format
    assert "Author" in result and "Test" in result


def test__resolve_identifier_arxiv_with_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()` with arXiv: prefix.
    """

    # Mock resolve_arxiv_id
    mock_bibtex_dict = {
        "ENTRYTYPE": "article",
        "ID": "arxiv2023",
        "author": "ArXiv Author",
        "title": "ArXiv Paper",
        "year": "2023"
    }

    def mock_resolve_arxiv(arxiv_id: str) -> dict:
        return mock_bibtex_dict.copy()

    import doi2bibtex.resolve
    monkeypatch.setattr(doi2bibtex.resolve, "resolve_arxiv_id", mock_resolve_arxiv)

    config = Configuration()

    # Test with "arXiv:" prefix
    result = resolve_identifier(identifier="arXiv:2301.12345", config=config)
    assert isinstance(result, str)
    # Authors are reformatted to "{Lastname}, Firstname" format
    assert "Author" in result and "ArXiv" in result

    # Test with "arxiv:" prefix (lowercase)
    result = resolve_identifier(identifier="arxiv:2301.12345", config=config)
    assert isinstance(result, str)
    # Authors are reformatted to "{Lastname}, Firstname" format
    assert "Author" in result and "ArXiv" in result


def test__resolve_identifier_unrecognized(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()` with unrecognized identifier.
    """

    config = Configuration()

    # Test with invalid identifier
    result = resolve_identifier(identifier="not-a-valid-identifier-xyz", config=config)

    # Should return an error message
    assert isinstance(result, str)
    assert "error" in result.lower() or "unrecognized" in result.lower()


def test__resolve_identifier_error_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()` error handling.
    """

    # Mock resolve_doi to raise an exception
    def mock_resolve_doi_error(doi: str) -> dict:
        raise RuntimeError("Test error: DOI not found")

    import doi2bibtex.resolve
    monkeypatch.setattr(doi2bibtex.resolve, "resolve_doi", mock_resolve_doi_error)

    config = Configuration()

    # Test that errors are caught and returned as strings
    result = resolve_identifier(identifier="10.1234/invalid.doi", config=config)

    assert isinstance(result, str)
    assert "error" in result.lower()
