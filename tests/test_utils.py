"""
Unit tests for bibtex.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from doi2bibtex.utils import (
    doi_to_url,
    latex_to_unicode,
    remove_accented_characters,
)


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__doi_to_url() -> None:
    """
    Test `doi_to_url()`.
    """

    assert (
        doi_to_url("10.1051/0004-6361/202142529")
        == "https://doi.org/10.1051%2F0004-6361%2F202142529"
    )


def test__latex_to_unicode() -> None:
    """
    Test `latex_to_unicode()`.
    """

    assert latex_to_unicode(r"$\alpha$") == r"$\alpha$"
    assert latex_to_unicode(r"M{\"o}bius") == r"Möbius"
    assert latex_to_unicode(r"\`{o}\^{o}\'{o}") == r"òôó"
    assert latex_to_unicode(r"Erd\H{o}s") == r"Erdős"
    assert latex_to_unicode(r"Sa\~{o} Paulo") == r"Saõ Paulo"
    assert latex_to_unicode(r"Troms\o{}") == r"Tromsø"
    assert latex_to_unicode(r"\t{oo}") == r"oo"
    assert latex_to_unicode(r"\c{c}") == r"ç"


def test__remove_accented_characters() -> None:
    """
    Test `remove_accented_characters()`.
    """

    assert remove_accented_characters("ÄÖÜäöüß") == "AeOeUeaeoeuess"
    assert remove_accented_characters("àáèéïîõøūú") == "aaeeiioouu"
