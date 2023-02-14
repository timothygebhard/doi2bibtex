"""
Unit tests for dblp.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from types import SimpleNamespace
from warnings import warn

import pytest

from doi2bibtex.dblp import crossmatch_with_dblp


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__crossmatch_with_dblp(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test `crossmatch_with_dblp()`.
    """

    # Case 1: no title / author
    identifier = "1312.6114"
    bibtex_dict = {"key": "value"}
    crossmatched = crossmatch_with_dblp(bibtex_dict, identifier)
    assert crossmatched == bibtex_dict

    # Case 2: Simulate failed request
    with monkeypatch.context() as m:
        m.setattr("requests.get", lambda _: SimpleNamespace(status_code=418))
        with pytest.raises(RuntimeError) as runtime_error:
            identifier = "1312.6114"
            bibtex_dict = {
                "title": "Auto-Encoding Variational Bayes",
                "author": "Kingma, Diederik P and Welling, Max",
            }
            crossmatch_with_dblp(bibtex_dict, identifier)
        assert "Could not get data from dblp." in str(runtime_error)

    # Case 3: No matching papers found
    try:
        identifier = "invalid-identifier"
        bibtex_dict = {
            "title": "Auto-Encoding Bayes",
            "author": "Kingma, Diederik P and Welling, Max",
        }
        crossmatched = crossmatch_with_dblp(bibtex_dict, identifier)
        assert crossmatched == bibtex_dict
    except RuntimeError as e:
        assert "Status code: 500" in str(e)
        warn("Could not test case 3 because dblp returned a status code 500.")

    # Case 4:
    try:
        identifier = "1312.6114"
        bibtex_dict = {
            "title": "Auto-Encoding Variational Bayes",
            "author": "Kingma, Diederik P and Welling, Max",
        }
        crossmatched = crossmatch_with_dblp(bibtex_dict, identifier)
        assert crossmatched["addendum"] == "Published at ICLR~2014."
    except RuntimeError as e:
        assert "Status code: 500" in str(e)
        warn("Could not test case 4 because dblp returned a status code 500.")

    # Case 5:
    try:
        identifier = "1807.01613"
        bibtex_dict = {
            "title": "Conditional Neural Processes",
            "author": "Garnelo, Martha and others",
        }
        crossmatched = crossmatch_with_dblp(bibtex_dict, identifier)
        assert crossmatched["addendum"] == "Published at ICML~2018."
    except RuntimeError as e:
        assert "Status code: 500" in str(e)
        warn("Could not test case 5 because dblp returned a status code 500.")

    # Case 6:
    try:
        identifier = "2110.06562"
        bibtex_dict = {
            "title": "On the Fairness of Causal Algorithmic Recourse",
            "author": "Julius von Kügelgen and others",
        }
        crossmatched = crossmatch_with_dblp(bibtex_dict, identifier)
        assert crossmatched["addendum"] == "Published at AAAI~2022."
    except RuntimeError as e:
        assert "Status code: 500" in str(e)
        warn("Could not test case 6 because dblp returned a status code 500.")

    # Case 7:
    try:
        identifier = "10.1088/1742-6596/898/7/072029"
        bibtex_dict = {
            "title": "Software Quality Control at Belle II",
            "author": "M Ritter and others",
        }
        crossmatched = crossmatch_with_dblp(bibtex_dict, identifier)
        assert "addendum" not in crossmatched
    except RuntimeError as e:
        assert "Status code: 500" in str(e)
        warn("Could not test case 7 because dblp returned a status code 500.")
