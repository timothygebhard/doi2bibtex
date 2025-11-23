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
        help="Identifier to resolve (DOI or arXiv ID). Optional positional argument. If not provided, enters interactive console mode.",
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
        "--title",
        metavar="TITLE",
        type=str,
        help="Search for papers by title and select interactively.",
    )
    parser.add_argument(
        "--first",
        action="store_true",
        help="When used with --title, automatically select the first result.",
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


def search_by_title(title: str, config: Configuration, auto_select_first: bool = False) -> None:
    """
    Search for papers by title and display results.
    If auto_select_first is True, automatically select the first result.
    Otherwise, display results in interactive mode.
    """
    from doi2bibtex.resolve import resolve_title
    from doi2bibtex.interactive.selection import app as select_from_results

    console = Console()

    # Search for papers
    console.print(f"\n[cyan]Searching for: {title}[/cyan]\n")

    try:
        with console.status("Searching..."):
            results, warnings = resolve_title(title, config)

        if not results:
            console.print("[yellow]No results found. Try a different search term.[/yellow]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Search error: {str(e)}[/red]")
        sys.exit(1)

    # Select a result
    if auto_select_first:
        # Automatically select the first result
        selected_doi = results[0].get("doi")
        if not selected_doi:
            console.print("[red]Error: First result has no DOI.[/red]")
            sys.exit(1)
        console.print(f"[green]Auto-selected first result:[/green] {results[0].get('title', 'N/A')}\n")
    else:
        # Interactive selection
        selected_doi = select_from_results(results, title, console, config, warnings)

    if not selected_doi:
        console.print("[yellow]No selection made.[/yellow]")
        sys.exit(0)

    # Get the BibTeX entry for the selected DOI
    console.print(f"\n[cyan]Fetching BibTeX for DOI: {selected_doi}[/cyan]\n")

    with console.status("Fetching BibTeX..."):
        bibtex = resolve_identifier(identifier=selected_doi, config=config)

    console.print(f'[green]BibTeX entry:[/green]\n')

    # Apply syntax highlighting
    syntax = Syntax(
        code=bibtex,
        lexer="bibtex",
        theme=config.pygments_theme,
        word_wrap=True,
    )

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

    # If --title is provided, search by title
    if args.title:
        search_by_title(title=args.title, config=config, auto_select_first=args.first)
        sys.exit(0)

    # If no identifier is provided, enter interactive mode
    if args.identifier is None:
        from doi2bibtex.interactive.interactive import app as interactive_mode # lazy loading
        interactive_mode(config=config)
        sys.exit(0)

    # Either print the result as plain text, or make it fancy
    if args.plain:
        plain(identifier=args.identifier, config=config)
    else:
        fancy(identifier=args.identifier, config=config)
