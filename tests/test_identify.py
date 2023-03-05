"""
Unit tests for identify.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from doi2bibtex.identify import (
    is_ads_bibcode,
    is_arxiv_id,
    is_doi,
    is_isbn,
)


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


def test__is_isbn() -> None:
    """
    Test `is_isbn()`.
    """

    # Test ISBN-10
    assert is_isbn('0826497527')
    assert is_isbn('isbn 0-8264-9752-7')
    assert is_isbn('954430603X')
    assert not is_isbn('0826497520')

    # Test ISBN-13
    assert is_isbn('9780826497529')
    assert is_isbn('9791090636071')
    assert is_isbn('978-3442151479')
    assert is_isbn('978-3-16-148410-0')
    assert is_isbn('978-3-16-148410-0')
    assert not is_isbn('9780826497520')
    assert not is_isbn('9700000000000')
    assert not is_isbn('9000000000000')
    assert not is_isbn('9710000000000')
