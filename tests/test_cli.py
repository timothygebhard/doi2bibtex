"""
Unit tests for cli.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pathlib import Path

import pytest

from doi2bibtex.cli import parse_cli_args, plain, fancy
from doi2bibtex.config import Configuration


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__parse_cli_args(capsys: pytest.CaptureFixture) -> None:
    """
    Test `parse_cli_args()`.
    """

    # Case 1
    args = parse_cli_args(["some-id"])
    assert not args.plain
    assert len(args.identifier) == 1
    assert args.identifier[0] == "some-id"

    # Case 2
    args = parse_cli_args(["some-other-id", "--plain"])
    assert args.plain
    assert len(args.identifier) == 1
    assert args.identifier[0] == "some-other-id"

    # Case 3
    try:
        parse_cli_args(["--help"])
    except SystemExit:
        pass
    assert "[-h] [--plain] <doi-or-arxiv-id>" in capsys.readouterr().out


def test__plain(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """
    Test `plain()`.
    """

    # Load modified default configuration (disable `resolve_adsurl`)
    with monkeypatch.context() as m:
        m.setattr(Path, "exists", lambda _: False)
        config = Configuration()
        config.resolve_adsurl = False

    # Case 1
    plain(identifier="1312.6114", config=config)
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == "@article{Kingma_2013,\n"
        "  author    = {{Kingma}, Diederik P and {Welling}, Max},\n"
        "  eprint    = {1312.6114},\n"
        "  journal   = {arXiv preprints},\n"
        "  title     = {Auto-Encoding Variational Bayes},\n"
        "  year      = {2013}\n"
        "}\n"
    )


def test__fancy(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """
    Test `fancy()`.
    """

    # Load modified default configuration (disable `resolve_adsurl`)
    with monkeypatch.context() as m:
        m.setattr(Path, "exists", lambda _: False)
        config = Configuration()
        config.resolve_adsurl = False

    # Case 1
    fancy(identifier="1312.6114", config=config)
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == "\nd2b: Resolve DOIs and arXiv IDs to BibTeX\n\nBibTeX entry for"
        ' identifier "1312.6114":\n\n@article{Kingma_2013,                  '
        "                                         \n  author    = {{Kingma},"
        " Diederik P and {Welling}, Max},                        \n  eprint "
        "   = {1312.6114},                                                  "
        "    \n  journal   = {arXiv preprints},                             "
        "                   \n  title     = {Auto-Encoding Variational"
        " Bayes},                                \n  year      = {2013}     "
        "                                                       \n}         "
        "                                                                   "
        "   \n\n\n"
    )
