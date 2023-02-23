"""
Unit tests for resolve.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pathlib import Path
from types import SimpleNamespace

from deepdiff import DeepDiff

import pytest

from doi2bibtex.ads import get_ads_token
from doi2bibtex.config import Configuration
from doi2bibtex.resolve import (
    resolve_ads_bibcode,
    resolve_arxiv_id,
    resolve_doi,
    resolve_identifier,
)


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------


# Do not run this test on CI where no ADS token is available
@pytest.mark.skipif(
    condition=get_ads_token() is None,
    reason="No ADS token found.",
)
def test__resolve_ads_bibcode() -> None:
    # Case 1: Identifier does not exist
    with pytest.raises(RuntimeError) as runtime_error:
        resolve_ads_bibcode("ThisIsNotAValidBibcode")
    assert "no BibTeX entry found" in str(runtime_error)

    # Case 2: Successful request
    bibtex_dict = resolve_ads_bibcode("2022A&A...666A...9G")
    assert bibtex_dict["ID"] == "2022A&A...666A...9G"
    assert bibtex_dict["ENTRYTYPE"] == "article"
    assert bibtex_dict["doi"] == "10.1051/0004-6361/202142529"


def test__resolve_arxiv_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_arxiv_id()`.
    """

    # Case 1: Simulate failed request
    with monkeypatch.context() as m:
        m.setattr("requests.get", lambda _: SimpleNamespace(status_code=404))
        with pytest.raises(RuntimeError) as runtime_error:
            resolve_arxiv_id("1312.6114")
        assert "Error 404 resolving" in str(runtime_error)

    # Case 2: Identifier does not exist
    with pytest.raises(RuntimeError) as runtime_error:
        resolve_arxiv_id("this-identifier-does-not-exist")
    assert "no BibTeX entry found" in str(runtime_error)

    # Case 3: Successful request
    assert not DeepDiff(
        resolve_arxiv_id("1312.6114"),
        {
            "eprinttype": "arXiv",
            "eprint": "1312.6114",
            "year": "2013",
            "title": "Auto-Encoding Variational Bayes",
            "author": "Diederik P Kingma and Max Welling",
            "ENTRYTYPE": "online",
            "ID": "1312.6114",
        },
    )


def test__resolve_doi(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_doi()`.
    """

    # Case 1: Simulate failed request
    with monkeypatch.context() as m:
        m.setattr("requests.get", lambda _: SimpleNamespace(status_code=404))
        with pytest.raises(RuntimeError) as runtime_error:
            resolve_doi("10.1088/1742-6596/898/7/072029")
        assert "Error 404 resolving" in str(runtime_error)

    # Case 2: Identifier does not exist
    with pytest.raises(RuntimeError) as runtime_error:
        resolve_doi("this-identifier-does-not-exist")
    assert "no BibTeX entry found" in str(runtime_error)

    # Case 3: Successful request
    assert not DeepDiff(
        resolve_doi("10.1088/1742-6596/898/7/072029"),
        {
            "journal": "Journal of Physics: Conference Series",
            "title": "Software Quality Control at Belle {II}",
            "author": (
                "M Ritter and T Kuhr and T Hauth and T Gebard and "
                "M Kristof and C Pulvermacher and"
            ),
            "pages": "072029",
            "volume": "898",
            "publisher": "{IOP} Publishing",
            "month": "oct",
            "year": "2017",
            "url": "https://doi.org/10.1088%2F1742-6596%2F898%2F7%2F072029",
            "doi": "10.1088/1742-6596/898/7/072029",
            "ENTRYTYPE": "article",
            "ID": "Ritter_2017",
        },
    )


def test__resolve_identifier(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `resolve_identifier()`.
    """

    # Set up a modified default config object (prevent loading from file)
    with monkeypatch.context() as m:
        m.setattr(Path, "exists", lambda _: False)
        config = Configuration()
        config.resolve_adsurl = False
        config.limit_authors = 2

    # Case 1: Successfully resolve an arXiv identifier
    assert (
        resolve_identifier("1312.6114", config) ==
        "@article{Kingma_2013,\n"
        "  author    = {{Kingma}, Diederik P and {Welling}, Max},\n"
        "  eprint    = {1312.6114},\n"
        "  journal   = {arXiv preprints},\n"
        "  title     = {Auto-Encoding Variational Bayes},\n"
        "  year      = {2013}\n"
        "}"
    )

    # Case 2: Successfully resolve a DOI
    assert (
        resolve_identifier("10.1088/1742-6596/898/7/072029", config) ==
        "@article{Ritter_2017,\n"
        "  author    = {{Ritter}, M and {Kuhr}, T and others},\n"
        "  doi       = {10.1088/1742-6596/898/7/072029},\n"
        "  journal   = {Journal of Physics: Conference Series},\n"
        "  month     = {10},\n"
        "  pages     = {072029},\n"
        "  title     = {Software Quality Control at Belle II},\n"
        "  volume    = {898},\n"
        "  year      = {2017}\n"
        "}"
    )

    # Case 3: Resolve arXiv identifier which has a DOI
    assert (
        resolve_identifier("2204.03439", config)
        == resolve_identifier("10.1051/0004-6361/202142529", config)
    )

    # Case 4: Resolve ADS bibcode (only if ADS token is available)
    if get_ads_token(raise_on_error=False) is not None:
        assert (
            resolve_identifier("2010ApJ...721L..67R", config) ==
            "@article{Robinson_2010,\n"
            "  adsnote       = {Provided by the SAO/NASA Astrophysics "
            "Data System},\n"
            "  adsurl        = {https://ui.adsabs.harvard.edu/abs/"
            "2010ApJ...721L..67R},\n"
            "  archiveprefix = {arXiv},\n"
            "  author        = {{Robinson}, Tyler D. and {Meadows}, "
            "Victoria S. and others},\n"
            "  doi           = {10.1088/2041-8205/721/1/L67},\n"
            "  eprint        = {1008.3864},\n"
            r"  journal       = {\apjl}," "\n"
            "  keywords      = {astrobiology, Earth, planets and satellites: "
            "composition, radiative transfer, scattering, techniques: "
            "photometric, Astrophysics - Earth and Planetary Astrophysics},\n"
            "  month         = {9},\n"
            "  number        = {1},\n"
            "  pages         = {L67-L71},\n"
            "  primaryclass  = {astro-ph.EP},\n"
            "  title         = {Detecting Oceans on Extrasolar Planets Using "
            "the Glint Effect},\n"
            "  volume        = {721},\n"
            "  year          = {2010}\n"
            "}"
        )

    # Case 5: Failure due to invalid identifier
    result = resolve_identifier("this-is-not-a-valid-identifier", config)
    assert "Unrecognized identifier" in result
