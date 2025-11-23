from typing import List, Dict, Optional, Any

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import UIControl, UIContent
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.mouse_events import MouseEventType
from rich.panel import Panel

from doi2bibtex.interactive.utils import parse_jats_text, format_authors


class ResultsControl(UIControl):
    """Custom UIControl for displaying and scrolling through results"""

    def __init__(self, results: List[Dict[str, Any]], original_query: str, warnings: List[str] = None):
        self.results = results
        self.original_query = original_query
        self.warnings = warnings or []
        self.current_index = 0
        self.scroll_offset = 0
        self.lines_per_result = 6  # title + identifier + authors + year/journal + type/publisher + empty line

    def create_content(self, width: int, height: int) -> UIContent:
        """Generate the content to display"""
        # Calculate reserved lines for header, warnings, footer
        header_lines = 2  # "Search results for:" + empty line
        warning_lines = len(self.warnings) + 1 if self.warnings else 0  # warnings + empty line
        footer_lines = 3  # empty line + footer + potential scroll indicator
        reserved_lines = header_lines + warning_lines + footer_lines

        # Calculate how many results fit on screen
        visible_results = max(1, (height - reserved_lines) // self.lines_per_result)

        # Adjust scroll offset to keep current selection visible
        if self.current_index < self.scroll_offset:
            self.scroll_offset = self.current_index
        elif self.current_index >= self.scroll_offset + visible_results:
            self.scroll_offset = self.current_index - visible_results + 1

        # Ensure scroll_offset is valid
        self.scroll_offset = max(0, min(self.scroll_offset, len(self.results) - visible_results))

        # Build the display lines - each line is a list of (style, text) tuples
        lines = []

        # Header
        lines.append([("class:header", f"Search results for: {self.original_query}")])
        lines.append([("", "")])

        # Display warnings if any
        if self.warnings:
            for warning in self.warnings:
                lines.append([("fg:yellow", f"  ⚠ {warning}")])
            lines.append([("", "")])

        # Show scroll indicator at top
        if self.scroll_offset > 0:
            lines.append([("class:info", f"  ↑ {self.scroll_offset} more above ↑")])
            lines.append([("", "")])

        # Display visible results
        end_index = min(len(self.results), self.scroll_offset + visible_results)
        for i in range(self.scroll_offset, end_index):
            result = self.results[i]
            is_selected = (i == self.current_index)
            prefix = "► " if is_selected else "  "
            style = "class:selected" if is_selected else ""
            source_style = "class:selected italic" if is_selected else "italic"
            title_style = "class:selected fg:#fff176" if is_selected else "fg:cyan"

            title = result.get("title", "")
            identifier = result.get("doi", "")
            year = result.get("year", "") or "✗"
            journal = result.get("journal", "") or "✗"
            authors = format_authors(result.get("authors", []), max_authors=3)
            pub_type = result.get("type", "") or "✗"
            publisher = result.get("publisher", "") or "✗"
            source = result.get("source")

            # Truncate long fields
            if publisher != "✗" and len(publisher) > 40:
                publisher = publisher[:37] + "..."
            if journal != "✗" and len(journal) > 40:
                journal = journal[:37] + "..."

            lines.append([(title_style, f"{prefix}[{i+1}] {title}")])
            lines.append([
                (f"{style} bold", f"    Identifier: {identifier} "),
                (source_style, f"(from {source})")
            ])
            lines.append([(style, f"    Authors: {authors}")])
            lines.append([(style, f"    Year: {year}, Journal: {journal}")])
            lines.append([(style, f"    Type: {pub_type}, Publisher: {publisher}")])
            lines.append([("", "")])

        # Show scroll indicator at bottom
        if end_index < len(self.results):
            remaining = len(self.results) - end_index
            lines.append([("class:info", f"  ↓ {remaining} more below ↓")])
            lines.append([("", "")])

        # Footer
        lines.append([("", "")])
        lines.append([("fg:cyan", "Navigation: [↑↓] Navigate  [SPACE] View abstract  [ENTER] Select  [ESC] Cancel")])

        return UIContent(
            get_line=lambda i: lines[i] if i < len(lines) else [("", "")],
            line_count=len(lines),
            show_cursor=False,
        )

    def mouse_handler(self, mouse_event):
        """Handle mouse events (optional)"""
        if mouse_event.event_type == MouseEventType.MOUSE_UP:
            return None
        return None

    def move_cursor_down(self):
        """Move selection down"""
        if self.current_index < len(self.results) - 1:
            self.current_index += 1

    def move_cursor_up(self):
        """Move selection up"""
        if self.current_index > 0:
            self.current_index -= 1

    def get_selected_result(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected result"""
        if 0 <= self.current_index < len(self.results):
            return self.results[self.current_index]
        return None


def show_abstract_popup(result: Dict[str, Any], console: Any) -> None:
    """Display the paper information and abstract for a result"""
    # Extract all paper info
    title = result["title"]
    identifier = result["doi"]
    year = result.get("year", "") or "✗"
    journal = result.get("journal", "") or "✗"
    pub_type = result.get("type", "") or "✗"
    publisher = result.get("publisher", "") or "✗"
    source = result.get("source")
    authors = format_authors(result.get("authors", []), max_authors=10)  # Show more authors in detail view
    raw_abstract = result.get("abstract", "")

    console.print("\n")

    # First panel: Paper Information
    info_content = f"""[bold]Title:[/bold] {title}
[bold]Identifier:[/bold] {identifier}
[bold]Source:[/bold] {source}
[bold]Authors:[/bold] {authors}
[bold]Year:[/bold] {year}
[bold]Journal:[/bold] {journal}
[bold]Type:[/bold] {pub_type}
[bold]Publisher:[/bold] {publisher}"""

    console.print(Panel(
        info_content,
        title="[cyan bold]Paper Information[/cyan bold]",
        border_style="cyan"
    ))

    console.print("")  # Spacing between panels

    # Second panel: Abstract
    if raw_abstract:
        abstract = parse_jats_text(raw_abstract)
        console.print(Panel(
            abstract,
            title=f"[cyan bold]Abstract[/cyan bold]",
            border_style="cyan"
        ))
    else:
        console.print(Panel(
            "[red]No abstract available[/red]",
            title=f"[cyan bold]Abstract[/cyan bold]",
            border_style="cyan"
        ))

    console.print("\n[dim]Press any key to return...[/dim]")


def app(
    results: List[Dict[str, Any]],
    original_query: str,
    Console: Any,
    config: Dict,
    warnings: List[str] = None,
) -> Optional[str]:
    """
    Display results and let user navigate and select.
    Returns the selected DOI or None if user cancelled.
    """

    console = Console
    control = ResultsControl(results, original_query, warnings or [])
    show_abstract_mode = [False]  # Use list for mutability in nested function

    # Key bindings
    kb = KeyBindings()

    @kb.add('up')
    def _(event):
        """Move selection up"""
        if not show_abstract_mode[0]:
            control.move_cursor_up()

    @kb.add('down')
    def _(event):
        """Move selection down"""
        if not show_abstract_mode[0]:
            control.move_cursor_down()

    @kb.add('space')
    def _(event):
        """Toggle abstract view"""
        if not show_abstract_mode[0]:
            result = control.get_selected_result()
            if result:
                show_abstract_mode[0] = True
                event.app.exit(result="__SHOW_ABSTRACT__")

    @kb.add('enter')
    def _(event):
        """Select current result"""
        if not show_abstract_mode[0]:
            result = control.get_selected_result()
            if result:
                event.app.exit(result=result.get("doi"))

    @kb.add('escape')
    @kb.add('c-c')
    def _(event):
        """Cancel"""
        event.app.exit(result=None)

    # Create the application
    application = Application(
        layout=Layout(
            HSplit([
                Window(
                    content=control,
                    wrap_lines=False
                )
            ])
        ),
        key_bindings=kb,
        full_screen=True,
        mouse_support=False,
        style_transformation=None,
        erase_when_done=True,
    )

    # Main loop - handle abstract viewing
    while True:
        try:
            result = application.run()

            if result == "__SHOW_ABSTRACT__":
                # Show abstract
                selected = control.get_selected_result()
                if selected:
                    show_abstract_popup(selected, console)
                    # Wait for key press
                    import sys, tty, termios
                    old_settings = termios.tcgetattr(sys.stdin)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

                    show_abstract_mode[0] = False
                    # Continue the loop to show menu again
                    continue
            else:
                # Return the selected DOI or None
                return result

        except (KeyboardInterrupt, EOFError):
            return None
