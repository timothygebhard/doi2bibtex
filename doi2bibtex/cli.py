"""
Provide a command line interface for doi2bibtex.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from argparse import ArgumentParser, Namespace
from typing import Any

import sys

from rich.console import Console, Text
from rich.syntax import Syntax

from doi2bibtex import __version__
from doi2bibtex.config import Configuration
from doi2bibtex.resolve import resolve_identifier


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

def parse_cli_args(args: Any = None) -> Namespace:
    """
    Parse the command line arguments.
    """

    parser = ArgumentParser()
    parser.add_argument(
        "identifier",
        metavar="IDENTIFIER",
        nargs='?',
        help="Identifier to resolve (DOI or arXiv ID).",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Print result plain text. Useful for piping to other programs.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the version number and exit.",
    )
    parsed_args = parser.parse_args(args)
    return parsed_args


def plain(identifier: str, config: Configuration) -> None:
    """
    Print the result plain text.
    """

    # Get the BibTeX entry from the identifier
    bibtex = resolve_identifier(identifier=identifier, config=config)

    # Print the result
    sys.stdout.write(bibtex + "\n")


def fancy(identifier: str, config: Configuration) -> None:
    """
    Print the result as a fancy rich console output.
    """

    # Set up a rich Console for some fancy output
    console = Console()
    text = Text("\nd2b: Resolve DOIs and arXiv IDs to BibTeX\n", style="bold")
    console.print(text)

    # Get the BibTeX entry from the identifier
    with console.status(f'Resolving identifier "{identifier}" ...'):
        bibtex = resolve_identifier(identifier=identifier, config=config)

    console.print(f'BibTeX entry for identifier "{identifier}":\n')

    # Apply syntax highlighting
    syntax = Syntax(
        code=bibtex,
        lexer="bibtex",
        theme=config.pygments_theme,
        word_wrap=True,
    )

    # Print the result
    console.print(syntax)
    console.print("\n")


def main() -> None:  # pragma: no cover
    """
    Get identifier from the command line and resolve it.
    """

    # Get command line arguments and load the configuration
    args = parse_cli_args(sys.argv[1:])
    config = Configuration()

    # Print the version number and exit if requested
    if args.version:
        print(__version__)
        sys.exit(0)

    # Either print the result as plain text, or make it fancy
    if args.plain:
        plain(identifier=args.identifier[0], config=config)
    else:
        fancy(identifier=args.identifier[0], config=config)
