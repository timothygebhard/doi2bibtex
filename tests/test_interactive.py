"""
Unit tests for interactive.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from typing import Any
from unittest.mock import Mock, MagicMock

import pytest

from doi2bibtex.interactive import (
    format_authors,
    get_clipboard_image,
    ocr_image,
)
from doi2bibtex.resolve import resolve_title
from doi2bibtex.config import Configuration


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__resolve_title(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_title()`.
    """

    # Mock the requests.get function
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "items": [
                {
                    "DOI": "10.1234/test.doi",
                    "title": ["Test Paper Title"],
                    "author": [
                        {"given": "John", "family": "Doe"},
                        {"given": "Jane", "family": "Smith"}
                    ],
                    "published": {"date-parts": [[2023]]},
                    "container-title": ["Test Journal"],
                    "abstract": "This is a test abstract.",
                    "publisher": "Test Publisher",
                    "type": "journal-article"
                }
            ]
        }
    }

    import requests
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_response)

    # Create a config object
    config = Configuration()
    config.search_sources = ["crossref"]  # Only use crossref for this test
    config.merge_search_results = False

    # Test the function
    results, warnings = resolve_title("quantum computing", config, limit=1)

    assert len(results) == 1
    assert results[0]["doi"] == "10.1234/test.doi"
    assert results[0]["title"] == "Test Paper Title"
    assert results[0]["year"] == "2023"
    assert results[0]["journal"] == "Test Journal"
    assert results[0]["abstract"] == "This is a test abstract."
    assert len(results[0]["authors"]) == 2
    assert isinstance(warnings, list)


def test__resolve_title__error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_title()` with network error.
    Note: In sequential mode, errors are collected as warnings but don't stop execution.
    In this test, all sources will fail, resulting in empty results with warnings.
    """

    # Mock requests.get to raise an exception
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("Network error")

    import requests
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_response)

    # Create a config object
    config = Configuration()
    config.search_sources = ["crossref"]
    config.merge_search_results = False

    # Test that the function returns empty results with warnings
    results, warnings = resolve_title("test query", config)
    assert results == []
    assert len(warnings) > 0  # Should have collected error as warning


def test__resolve_title__no_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_title()` with no results.
    """

    # Mock the requests.get function with empty results
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "items": []
        }
    }

    import requests
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_response)

    # Create a config object
    config = Configuration()
    config.search_sources = ["crossref"]
    config.merge_search_results = False

    # Test the function
    results, warnings = resolve_title("nonexistent paper xyz123", config)
    assert results == []
    assert isinstance(warnings, list)


def test__format_authors() -> None:
    """
    Test `format_authors()`.
    """

    # Test with normal author list
    authors = [
        {"given": "John", "family": "Doe"},
        {"given": "Jane", "family": "Smith"},
        {"given": "Bob", "family": "Johnson"}
    ]

    result = format_authors(authors, max_authors=2)
    assert result == "John Doe, Jane Smith, et al."

    result = format_authors(authors, max_authors=3)
    assert result == "John Doe, Jane Smith, Bob Johnson"

    result = format_authors(authors, max_authors=5)
    assert result == "John Doe, Jane Smith, Bob Johnson"

    # Test with author without given name
    authors_no_given = [
        {"family": "Doe"},
        {"given": "Jane", "family": "Smith"}
    ]
    result = format_authors(authors_no_given, max_authors=3)
    assert result == "Doe, Jane Smith"

    # Test with empty list
    result = format_authors([])
    assert result == "Unknown authors"


def test__get_clipboard_image(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `get_clipboard_image()` with PIL available and image in clipboard.
    """

    # Create a mock image with save method
    mock_image = MagicMock()
    mock_image.save = MagicMock()

    # Mock the PIL.ImageGrab module
    try:
        import PIL.ImageGrab
        # If PIL is available, mock its grabclipboard function
        monkeypatch.setattr(PIL.ImageGrab, "grabclipboard", lambda: mock_image)

        result = get_clipboard_image()
        assert result is not None
        assert hasattr(result, 'save')
    except ImportError:
        # If PIL is not installed, skip this test
        pytest.skip("PIL not installed")


def test__get_clipboard_image__no_image(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `get_clipboard_image()` when clipboard has no image.
    """

    # Mock PIL.ImageGrab with no image
    def mock_grabclipboard():
        return None

    mock_imagegrab = MagicMock()
    mock_imagegrab.grabclipboard = mock_grabclipboard

    import sys
    sys.modules['PIL.ImageGrab'] = mock_imagegrab

    try:
        result = get_clipboard_image()
        assert result is None
    finally:
        # Cleanup
        if 'PIL.ImageGrab' in sys.modules:
            del sys.modules['PIL.ImageGrab']


def test__get_clipboard_image__no_pil(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `get_clipboard_image()` when PIL is not available.
    """

    # Test when PIL import fails - get_clipboard_image should return None
    # The function catches the exception and returns None
    import sys

    # Remove PIL from modules if it exists
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('PIL')]
    for module in modules_to_remove:
        del sys.modules[module]

    # The function should handle ImportError gracefully
    result = get_clipboard_image()
    # When PIL is not available, the function returns None
    assert result is None
