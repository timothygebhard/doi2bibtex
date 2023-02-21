"""
Unit tests for ads.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import doi2bibtex.ads


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

@pytest.fixture
def mock_open(mocker: Any) -> None:
    """
    Mock the built-in `open()` function to always return a file-like
    object with the contents "hazzuh".
    """

    mocker.patch("builtins.open", mocker.mock_open(read_data="hazzuh"))


def test__get_ads_token(
    monkeypatch: pytest.MonkeyPatch,
    mock_open: Any,
) -> None:
    """
    Test `get_ads_token()`.
    """

    # Case 1: No ADS token found
    # In this case, we need to both monkeypatch ADS_TOKEN environment variable
    # to an empty value, and the `Path.exists` method to always return False,
    # because the `get_ads_token` function checks if there exists a file at
    # `~/.doi2bibtex/ads_token`, and we don't want to modify any actual file
    # that may exist there.
    monkeypatch.delenv("ADS_TOKEN", raising=False)
    monkeypatch.setattr(Path, "exists", lambda _: False)
    assert doi2bibtex.ads.get_ads_token() is None
    with pytest.raises(RuntimeError) as runtime_error:
        doi2bibtex.ads.get_ads_token(raise_on_error=True)
    assert "No ADS token found" in str(runtime_error)

    # Case 2: ADS token found in environment variable
    monkeypatch.setenv("ADS_TOKEN", "huzzah")
    assert doi2bibtex.ads.get_ads_token() == "huzzah"

    # Case 3: Both environment variable and file exist
    assert doi2bibtex.ads.get_ads_token() == "huzzah"

    # Case 4: ADS token found in file
    monkeypatch.delenv("ADS_TOKEN", raising=False)
    monkeypatch.setattr(Path, "exists", lambda _: True)
    assert doi2bibtex.ads.get_ads_token() == "hazzuh"


# Do not run this test on CI where no ADS token is available
@pytest.mark.skipif(
    condition=doi2bibtex.ads.get_ads_token() is None,
    reason="No ADS token found.",
)
def test__get_ads_bibcode_for_identifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test `get_ads_bibcode_for_identifier()`.
    """

    # Case 1:
    bibcode = doi2bibtex.ads.get_ads_bibcode_for_identifier(
        "10.1051/0004-6361/202142529"
    )
    assert bibcode == "2022A&A...666A...9G"

    # Case 2:
    bibcode = doi2bibtex.ads.get_ads_bibcode_for_identifier("2010.05591")
    assert bibcode == "2020arXiv201005591G"

    # Case 3:
    bibcode = doi2bibtex.ads.get_ads_bibcode_for_identifier(
        "ThisIsNotAValidIdentifier"
    )
    assert bibcode == ""

    # Case 4:
    bibcode = doi2bibtex.ads.get_ads_bibcode_for_identifier(
        "10.1103/PhysRevLett.116.061102"
    )
    assert bibcode == "2016PhRvL.116f1102A"

    # Case 5: Simulate failed request
    with monkeypatch.context() as m:
        m.setattr(
            "requests.get",
            lambda *_, **__: SimpleNamespace(status_code=418),
        )
        bibcode = doi2bibtex.ads.get_ads_bibcode_for_identifier(
            "10.1103/PhysRevLett.116.061102"
        )
        assert bibcode == ""
