"""
Unit tests for bibtex.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from deepdiff import DeepDiff

from doi2bibtex.bibtex import bibtex_string_to_dict, dict_to_bibtex_string


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__bibtex_string_to_dict() -> None:
    """
    Test `bibtex_string_to_dict()`.
    """

    bibtex_string = """
    @article{citekey,
        author = {Jane Doe and Richard Roe},
        title = {Some really cool paper},
        journal = {The Made-Up Journal},
        volume = {725},
        number = {2},
        pages = {1197-1206},
        year = {2010},
        month = {10},
    }
    """

    assert not DeepDiff(
        bibtex_string_to_dict(bibtex_string),
        {
            'ENTRYTYPE': 'article',
            'ID': 'citekey',
            'author': 'Jane Doe and Richard Roe',
            'title': 'Some really cool paper',
            'journal': 'The Made-Up Journal',
            'volume': '725',
            'number': '2',
            'pages': '1197-1206',
            'year': '2010',
            'month': '10',
        }
    )


def test__dict_to_bibtex_string() -> None:
    """
    Test `dict_to_bibtex_string()`.
    """

    bibtex_dict = {
        'ENTRYTYPE': 'article',
        'ID': 'citekey',
        'author': 'Jane Doe and Richard Roe',
        'title': 'Some really cool paper',
        'journal': 'The Made-Up Journal',
        'volume': '725',
        'number': '2',
        'pages': '1197-1206',
        'year': '2010',
        'month': '10',
    }
    assert dict_to_bibtex_string(bibtex_dict) == (
        '@article{citekey,\n'
        '  author        = {Jane Doe and Richard Roe},\n'
        '  journal       = {The Made-Up Journal},\n'
        '  month         = {10},\n'
        '  number        = {2},\n'
        '  pages         = {1197-1206},\n'
        '  title         = {Some really cool paper},\n'
        '  volume        = {725},\n'
        '  year          = {2010}\n'
        '}'
    )
