"""
Unit tests for processing.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pathlib import Path

from deepdiff import DeepDiff

import pytest

from doi2bibtex.ads import get_ads_token
from doi2bibtex.config import Configuration
from doi2bibtex.process import (
    preprocess_identifier,
    postprocess_bibtex,
    abbreviate_journal_name,
    convert_latex_chars,
    convert_month_to_number,
    fix_arxiv_entrytype,
    fix_broken_ampersand,
    format_author_names,
    generate_citekey,
    remove_fields,
    remove_url_if_doi,
    resolve_adsurl,
    truncate_author_list,
)


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__preprocess_identifier() -> None:
    """
    Test `preprocess_identifier()`.
    """

    assert preprocess_identifier(" identifier  ") == "identifier"
    assert preprocess_identifier("doi:identifier") == "identifier"
    assert preprocess_identifier("DOI:identifier") == "identifier"
    assert preprocess_identifier("arXiv:identifier") == "identifier"
    assert preprocess_identifier("arxiv:identifier") == "identifier"


def test__postprocess_bibtex(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `postprocess_bibtex()`.
    """

    # Set up a modified default config object (prevent loading from file)
    with monkeypatch.context() as m:
        m.setattr(Path, "exists", lambda _: False)
        config = Configuration()
        config.limit_authors = 2
        config.resolve_adsurl = False

    # Case 1: DOI
    bibtex_dict = {
        "journal": "Physical Review D",
        "title": (
            "Convolutional neural networks: A magic bullet for "
            "gravitational-wave detection?"
        ),
        "author": (
            r"Timothy D. Gebhard and Niki Kilbertus and Ian Harry and "
            r"Bernhard Sch{\"o}lkopf"
        ),
        "number": "6",
        "volume": "100",
        "publisher": "American Physical Society ({APS})",
        "month": "sep",
        "year": "2019",
        "url": "https://doi.org/10.1103%2Fphysrevd.100.063015",
        "doi": "10.1103/physrevd.100.063015",
        "ENTRYTYPE": "article",
        "ID": "Gebhard_2019",
    }

    assert not DeepDiff(
        postprocess_bibtex(
            bibtex_dict=bibtex_dict,
            identifier="10.1103/physrevd.100.063015",
            config=config,
        ),
        {
            "journal": r"\prd",
            "title": (
                "Convolutional neural networks: A magic bullet for "
                "gravitational-wave detection?"
            ),
            "author": "{Gebhard}, Timothy D. and {Kilbertus}, Niki and others",
            "number": "6",
            "volume": "100",
            "month": "9",
            "year": "2019",
            "doi": "10.1103/physrevd.100.063015",
            "ENTRYTYPE": "article",
            "ID": "Gebhard_2019",
        },
    )


def test__abbreviate_journal_name() -> None:
    """
    Test `abbreviate_journal_name()`.
    """

    assert not DeepDiff(
        abbreviate_journal_name({"journal": r"Astronomy \& Astrophysics"}),
        {"journal": r"\aap"},
    )
    assert not DeepDiff(
        abbreviate_journal_name({"journal": "The Astrophysical Journal"}),
        {"journal": r"\apj"},
    )
    assert not DeepDiff(
        abbreviate_journal_name({"journal": "The Unknown Journal"}),
        {"journal": r"The Unknown Journal"},
    )


def test__convert_latex_chars() -> None:
    """
    Test `convert_latex_chars()`.
    """

    bibtex_dict_1 = {
        "author": r"Thomas M{\"u}ller and H\'el\`ene Martin",
        "title": r"Lyman-$\alpha$ forests in the {\it Gaia} era",
    }
    bibtex_dict_2 = {
        "author": r"Thomas Müller and Hélène Martin",
        "title": r"Lyman-$\alpha$ forests in the Gaia era",
    }

    assert not DeepDiff(convert_latex_chars(bibtex_dict_1), bibtex_dict_2)


def test__convert_month_to_number() -> None:
    """
    Test `convert_month_to_number()`.
    """

    # Case 1
    assert not DeepDiff(
        convert_month_to_number({"key": "value"}),
        {"key": "value"},
    )

    # Case 2
    for i, month in enumerate(
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        start=1,
    ):
        assert not DeepDiff(
            convert_month_to_number({"month": month}),
            {"month": str(i)},
        )

    # Case 3
    for i, month in enumerate(
        [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ],
        start=1,
    ):
        assert not DeepDiff(
            convert_month_to_number({"month": month}),
            {"month": str(i)},
        )

    # Case 4
    assert not DeepDiff(
        convert_month_to_number({"month": "1"}),
        {"month": "1"},
    )


def test__fix_arxiv_entrytype() -> None:
    """
    Test `fix_arxiv_entrytype()`.
    """

    assert not DeepDiff(
        fix_arxiv_entrytype(
            bibtex_dict={
                "ENTRYTYPE": "online",
                "eprinttype": "arXiv",
            },
            identifier="2008.0555",
        ),
        {"ENTRYTYPE": "article", "journal": "arXiv preprints"},
    )


def test__fix_broken_ampersand() -> None:
    """
    Test `fix_broken_ampersand()`.
    """

    assert not DeepDiff(
        fix_broken_ampersand(
            {"journal": r"Astronomy {\&}amp$\mathsemicolon$ Astrophysics"}
        ),
        {"journal": r"Astronomy \& Astrophysics"},
    )


def test__format_author_names() -> None:
    """
    Test `format_author_names()`.
    """

    # Case 1
    bibtex_dict = {"title": "A document with no author"}
    assert not DeepDiff(format_author_names(bibtex_dict), bibtex_dict)

    # Case 2
    bibtex_dict_1 = {
        "author": "Tim Müller and Martin, Hélène and John von Neumann",
    }
    bibtex_dict_2 = {
        "author": "{Müller}, Tim and {Martin}, Hélène and {von Neumann}, John",
    }
    assert not DeepDiff(format_author_names(bibtex_dict_1), bibtex_dict_2)


def test__generate_citekey() -> None:
    bibtex_dict_1 = {
        "ID": "citekey",
        "ENTRYTYPE": "book",
        "author": "Don Quixote de la Mancha",
        "title": "Stories about windmills",
        "year": "1605",
    }
    bibtex_dict_2 = {
        "ID": "DeLaMancha::1605",
        "ENTRYTYPE": "book",
        "author": "Don Quixote de la Mancha",
        "title": "Stories about windmills",
        "year": "1605",
    }
    assert not DeepDiff(
        generate_citekey(bibtex_dict_1, delim="::"),
        bibtex_dict_2,
    )


def test__remove_fields() -> None:
    """
    Test `remove_fields()`.
    """

    # Set up config object
    config = Configuration()
    config.remove_fields = {"all": ["keywords"], "article": ["publisher"]}

    # Case 1
    bibtex_dict = {
        "ENTRYTYPE": "article",
        "publisher": "Some publisher",
        "keywords": "Some keywords",
    }
    assert not DeepDiff(
        remove_fields(bibtex_dict, config),
        {"ENTRYTYPE": "article"},
    )

    # Case 2
    bibtex_dict = {
        "ENTRYTYPE": "book",
        "publisher": "Some publisher",
        "keywords": "Some keywords",
    }

    assert not DeepDiff(
        remove_fields(bibtex_dict, config),
        {
            "ENTRYTYPE": "book",
            "publisher": "Some publisher",
        },
    )


def test__remove_url_if_doi() -> None:
    """
    Test `remove_url_if_doi()`.
    """

    # Case 1
    bibtex_dict = {
        "doi": "10.1234/5678",
        "url": "https://doi.org/10.1234%2F5678",
    }
    assert not DeepDiff(
        remove_url_if_doi(bibtex_dict),
        {"doi": "10.1234/5678"},
    )

    # Case 2
    bibtex_dict = {"doi": "10.1234/5678", "url": "https://example.com"}
    assert not DeepDiff(
        remove_url_if_doi(bibtex_dict),
        bibtex_dict,
    )


@pytest.mark.skipif(
    condition=get_ads_token() is None,
    reason="No ADS token found.",
)
def test__resolve_adsurl() -> None:
    """
    Test `resolve_adsurl()`.
    """

    # Case 1
    assert not DeepDiff(
        resolve_adsurl({"adsurl": "some-url"}, identifier="some-identifier"),
        {"adsurl": "some-url"},
    )

    # Case 2
    assert not DeepDiff(
        resolve_adsurl({}, identifier="this-identifier-does-not-exist"),
        {},
    )

    # Case 3
    assert not DeepDiff(
        resolve_adsurl({}, identifier="10.1103/PhysRevLett.116.061102"),
        {"adsurl": "https://adsabs.harvard.edu/abs/2019PhRvD..99h4054S"},
    )


def test__truncate_author_list() -> None:
    """
    Test `truncate_author_list()`.
    """

    # Set up config object
    config = Configuration()
    config.limit_authors = 2

    # Case 1
    bibtex_dict = {"title": "A document with no author"}
    assert not DeepDiff(truncate_author_list(bibtex_dict, config), bibtex_dict)

    # Case 2
    bibtex_dict = {"author": "Jane Doe and Jim Roe and Kim Poe"}
    assert not DeepDiff(
        truncate_author_list(bibtex_dict, config),
        {"author": "Jane Doe and Jim Roe and others"},
    )
