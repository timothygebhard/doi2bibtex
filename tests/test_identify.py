"""
Unit tests for identify.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from doi2bibtex.identify import is_ads_bibcode, is_arxiv_id, is_doi


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__is_doi() -> None:
    """
    Test `is_doi()`.
    """

    assert is_doi('10.1051/0004-6361/202142529')
    assert is_doi('10.1002/best.202010001')
    assert is_doi('10.1021/ac0341261')

    assert not is_doi('2010.05591')


def test__is_arxiv_id() -> None:
    """
    Test `is_arxiv_id()`.
    """

    assert is_arxiv_id('2010.05591')
    assert is_arxiv_id('math.GT/0309136')

    assert not is_arxiv_id('10.1051/0004-6361/202142529')


def test__is_ads_bibcode() -> None:
    """
    Test `is_ads_bibcode()`.
    """

    assert is_ads_bibcode('1992ApJ...400L...1W')
    assert is_ads_bibcode('2023TAOS...34....1C')
    assert is_ads_bibcode('2022A&A...666A...9G')

    assert not is_ads_bibcode('9876ABCDF.518L..131')
    assert not is_ads_bibcode('2010.05591')
    assert not is_ads_bibcode('10.1051/0004-6361/202142529')
