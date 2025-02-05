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
from doi2bibtex.clean import process_references


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
    parser.add_argument(
        "--clean-references",
        action="store_true",
        help="Process references in .tex and .bib files and clean them.",
    )
    parser.add_argument(
        "--tex-dir",
        metavar="TEX_DIR",
        help="Path to the directory containing .tex files (used with --clean-references).",
    )
    parser.add_argument(
        "--bib-dir",
        metavar="BIB_DIR",
        help="Path to the directory containing .bib files (used with --clean-references).",
    )
    parser.add_argument(
        "--output-dir",
        metavar="OUTPUT_DIR",
        help="Path to the directory for saving cleaned and unresolved .bib files (used with --clean-references).",
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


def clean_references(tex_dir: str,
                     bib_dir: str,
                     output_dir: str,
                     config) -> None:
    """
    Wrapper function to call the clean references functionality.

    Args:
        tex_dir (str): Path to the directory containing .tex files.
        bib_dir (str): Path to the directory containing .bib files.
        output_dir (str): Path to the directory for saving results.
    """
    if not tex_dir or not bib_dir or not output_dir:
        raise ValueError("tex_dir, bib_dir, and output_dir must be provided"
                         " for --clean-references.")

    process_references(tex_dir_path=tex_dir,
                       bib_dir_path=bib_dir,
                       output_dir_path=output_dir,
                       config=config)


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

    # Handle clean references functionality
    if args.clean_references:
        try:
            clean_references(
                tex_dir=args.tex_dir,
                bib_dir=args.bib_dir,
                output_dir=args.output_dir,
                config=config,
            )
            sys.exit(0)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Either print the result as plain text, or make it fancy
    if args.plain:
        plain(identifier=args.identifier, config=config)
    else:
        fancy(identifier=args.identifier, config=config)
