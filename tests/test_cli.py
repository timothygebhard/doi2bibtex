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
    assert args.identifier == "some-id"

    # Case 2
    args = parse_cli_args(["some-other-id", "--plain"])
    assert args.plain
    assert args.identifier == "some-other-id"

    # Case 3 - Test --title option
    args = parse_cli_args(["--title", "Some paper title"])
    assert args.title == "Some paper title"
    assert not args.first

    # Case 4 - Test --title with --first
    args = parse_cli_args(["--title", "Another title", "--first"])
    assert args.title == "Another title"
    assert args.first

    # Case 5 - Test help message
    try:
        parse_cli_args(["--help"])
    except SystemExit:
        pass
    help_output = capsys.readouterr().out
    assert "IDENTIFIER" in help_output
    assert "--title" in help_output
    assert "--first" in help_output


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
        "  author        = {{Kingma}, Diederik P and {Welling}, Max},\n"
        "  eprint        = {1312.6114},\n"
        "  journal       = {arXiv preprints},\n"
        "  title         = {Auto-Encoding Variational Bayes},\n"
        "  year          = {2013}\n"
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
        list(map(lambda x: str(x).rstrip(' '), outerr.out.split("\n")))
        == [
            '',
            'd2b: Resolve DOIs and arXiv IDs to BibTeX',
            '',
            'BibTeX entry for identifier "1312.6114":',
            '',
            '@article{Kingma_2013,',
            '  author        = {{Kingma}, Diederik P and {Welling}, Max},',
            '  eprint        = {1312.6114},',
            '  journal       = {arXiv preprints},',
            '  title         = {Auto-Encoding Variational Bayes},',
            '  year          = {2013}',
            '}',
            '',
            '',
            '',
        ]
    )
