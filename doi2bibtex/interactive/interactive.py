"""
Interactive console mode for searching papers by title.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------


from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.bindings import emacs
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import PromptSession

from doi2bibtex.resolve import resolve_identifier, resolve_title

from doi2bibtex.interactive.utils import (
  get_clipboard_image,
  ocr,
  normalize_text,
  copy_to_clipboard,
)

from doi2bibtex.interactive.selection import app as select_from_results

# Special return values for PromptSession control flow
RESULT_MODE_SWITCH = "__MODE_SWITCH__"
RESULT_OCR_REQUESTED = "__OCR_REQUESTED__"
COPY_EVENT_TRIGGER_CHAR = 'c'

def bibtex_to_clipboard(console, bibtex):
    if copy_to_clipboard(bibtex):
        console.print("\n[green bold]✓ BibTeX copied to clipboard![/green bold]\n")
    else:
        console.print(f"\n[yellow]Could not copy to clipboard[/yellow]\n")

def linux_terminal_buffer(console, bibtex):
    """
    Switch to raw terminal to allow user to select previous displayed text
    as bibtext. And monitor the terminal for continuing.
    prompt_toolkit does not allow to select previous text because it
    captures all the events and would be too much burden to implement
    """
    import sys
    import tty
    import termios

    # Save terminal settings
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        # Set terminal to raw mode to read single character
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(1).lower()

        # Restore terminal settings immediately
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        # If user pressed 'c', copy to clipboard
        if char == COPY_EVENT_TRIGGER_CHAR:
            bibtex_to_clipboard(console, bibtex)
        else:
            console.print()  # Just add newline

    except Exception:
        # Restore settings on error
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        console.print()

def windows_terminal_buffer(console, bibtex):
    import msvcrt
    char = msvcrt.getch().decode('utf-8').lower()

    if char == COPY_EVENT_TRIGGER_CHAR:
        bibtex_to_clipboard(console, bibtex)
    else:
        console.print()

def fallback_terminal_buffer(console, bibtex):
    user_input = input().strip().lower()
    if user_input == 'c':
        bibtex_to_clipboard(console, bibtex)
    else:
        console.print()

def display_bibtex(bibtex: str, console: Console, config) -> None:
    """
    Display BibTeX with syntax highlighting and pause to allow text selection.
    User can optionally copy to clipboard by pressing 'c'.
    """
    console.print(f'[green]BibTeX entry:[/green]\n')

    # Apply syntax highlighting
    syntax = Syntax(
        code=bibtex,
        lexer="bibtex",
        theme=config.pygments_theme,
        word_wrap=True,
    )
    console.print(syntax)

    # Display pause message with copy option
    console.print(Panel.fit(
        "[bold cyan]You can now select and copy the BibTeX text above[/bold cyan]\n\n"
        "[dim]Press 'c' to copy to clipboard, or any other key to continue...[/dim]",
        border_style="cyan"
    ))

    try:
        # Read single character without waiting for ENTER
        # This allows text selection since prompt_toolkit is not active
        try:
            linux_terminal_buffer(console, bibtex)
            return
        except (ImportError, AttributeError):
            pass
        
        try:
            windows_terminal_buffer(console, bibtex)
            return
        except (ImportError, AttributeError):
            pass
        
        fallback_terminal_buffer(console, bibtex)
    
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        console.print()

    

def ocr_image(image_source, console: Console) -> str:
    """
    Perform OCR on an image to extract text using RapidOCR.
    image_source can be a file path (str) or PIL Image object.
    """
    try:
        # Display OCR in progress animation
        with console.status("[cyan]OCR in progress...", spinner="dots"):
            return ocr(image_source)
    except Exception as e:
        return f"Error performing OCR: {e}"

def key_bindings(toolbar_message=None, search_mode=None, txt_buffer=None):
    # Key bindings - defined once, reused for all prompts
    kb = KeyBindings()

    @kb.add('enter')
    def _(event):
        """Validate input on Enter (overrides default multiline behavior)"""
        buffer = event.current_buffer
        # Manually append to history before exiting (since we bypass normal accept flow)
        buffer.append_to_history()
        event.app.exit(result=buffer.text)

    @kb.add('c-v')  # Ctrl+V for image paste only
    def _(event):
        """Paste image from clipboard for OCR"""
        # Try to get image from clipboard
        clipboard_image = get_clipboard_image()

        if clipboard_image:
            # It's an image! Exit with special result to trigger OCR mode
            event.app.exit(result=RESULT_OCR_REQUESTED)
        else:
            # No image in clipboard - show message in toolbar
            toolbar_message[0] = ("warning", "No image")

    # NOTE: We don't bind up/down keys here - let PromptSession use default bindings
    # which handle both multiline navigation and history automatically

    @kb.add('s-tab')  # Shift+Tab to switch search mode
    def _(event):
        """Switch between title and DOI search modes"""
        # Save current text before switching modes
        txt_buffer[0] = event.current_buffer.text

        # Cycle through modes
        if search_mode[0] == "title":
            search_mode[0] = "doi"
        else:
            search_mode[0] = "title"
        # Exit with special result to switch mode
        event.app.exit(result=RESULT_MODE_SWITCH)

    return kb

# Create bottom toolbar showing current mode
def bottom_toolbar(toolbar_message=None, search_mode=None):
    """Generate bottom toolbar with mode indicator"""
    # Build mode indicator
    if search_mode[0] == "title":
        toolbar_parts = [
            ('bg:#0066cc #ffffff bold', ' Title Mode '),
            ('', ' | '),
            ('#888888', 'DOI Mode'),
            ('', '     '),
            ('#888888 italic', '(Shift+Tab to cycle)'),
        ]
    else:
        toolbar_parts = [
            ('#888888', 'Title Mode'),
            ('', ' | '),
            ('bg:#0066cc #ffffff bold', ' DOI Mode '),
            ('', '     '),
            ('#888888 italic', '(Shift+Tab to cycle)'),
        ]

    # Add message if present
    if toolbar_message[0] is not None:
        msg_type, msg_text = toolbar_message[0]
        toolbar_parts.append(('', '     '))  # Spacing
        if msg_type == "error":
            toolbar_parts.append(('bg:#d32f2f #ffffff bold', f' ✗ {msg_text} '))
        elif msg_type == "warning":
            toolbar_parts.append(('bg:#f57c00 #ffffff bold', f' ⚠ {msg_text} '))
        elif msg_type == "success":
            toolbar_parts.append(('bg:#388e3c #ffffff bold', f' ✓ {msg_text} '))
        else:  # info
            toolbar_parts.append(('bg:#1976d2 #ffffff', f' ℹ {msg_text} '))

    return FormattedText(toolbar_parts)


def handle_user_input(session=None, console=None, search_mode=None, txt_buffer=None):
    prompt_text = "Title: " if search_mode[0] == "title" else "DOI: "

    # Use preserved text as default (from mode switch), then clear it
    default_text = txt_buffer[0] if txt_buffer[0] is not None else ""
    txt_buffer[0] = None  # Clear after use

    input_text = session.prompt(message=prompt_text, default=default_text)
    processed_input = None

    # Check for special return values
    if input_text == RESULT_MODE_SWITCH:
        # User pressed Shift+Tab to switch mode
        return
    
    if input_text == RESULT_OCR_REQUESTED:
        # User pressed Ctrl+V with an image in clipboard
        clipboard_image = get_clipboard_image()
        if not clipboard_image:
            # Normal text input
            console.print("[yellow]No input provided.[/yellow]")
            return

        console.print("\n[green]Image detected![/green]")

        # Perform OCR on the clipboard image
        ocr_text = ocr_image(clipboard_image, console)

        if ocr_text.startswith("Error"):
            console.print(f"[red]{ocr_text}[/red]")
            return

        console.print(f"\n[green]Extracted text:[/green]\n{ocr_text}\n")
        console.print("[cyan]Edit the text if needed, then press Enter to search[/cyan]\n")

        # Let user edit the OCR result
        ocr_edited_txt = session.prompt(message="Edit: ", default=ocr_text)

        # Handle special results from OCR editing
        if ocr_edited_txt in [RESULT_MODE_SWITCH, RESULT_OCR_REQUESTED]:
            return

        processed_input = normalize_text(ocr_edited_txt)
    
    
    if processed_input is None:
        processed_input = normalize_text(input_text)
    
    if not processed_input:
        console.print("[yellow]No input provided.[/yellow]")
        return
    
    return processed_input
    
def handle_user_doi(console=None, config=None, identifier=None, toolbar_message=None):
    try:
        with console.status("Resolving DOI..."):
            bibtex = resolve_identifier(identifier=identifier, config=config, raise_on_error=True)

        display_bibtex(bibtex, console, config)
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {str(e)}\n")
        toolbar_message[0] = ("error", f"Error resolving identifier")
        return False

    return True

def resolve_user_input(console=None, search_mode=None, input_text=None, config=None, toolbar_message=None):
    # DOI mode
    if search_mode[0] == "doi":

        console.print(f"\n[cyan]Searching for: {input_text}[/cyan]\n")
        handle_user_doi(
            console=console,
            config=config,
            identifier=input_text,
            toolbar_message=toolbar_message
        )
        return

    # Title mode
    console.print(f"\n[cyan]Searching for: {input_text}[/cyan]\n")
    try:
        with console.status("Searching..."):
            results, warnings = resolve_title(input_text, config)

        if not results:
            console.print(f"\n[yellow]No results found. Try a different search term.[/yellow]\n")
            toolbar_message[0] = ("warning", "No results found")
            return
    except Exception as e:
        console.print(f"\n[red bold]Search error:[/red bold] {str(e)}\n")
        toolbar_message[0] = ("error", "Search error")
        return

    selected_doi = select_from_results(results, input_text, console, config, warnings)
    if selected_doi:
        handle_user_doi(
            console=console,
            config=config,
            identifier=selected_doi,
            toolbar_message=toolbar_message
        )

def app(config) -> None:
    """
    Interactive console mode for searching papers by title.
    """

    console = Console()
    console.print(Panel.fit(
        "[bold cyan]Interactive Mode[/bold cyan]\n\n"
        "Type or paste a paper title or DOI\n"
        "Paste an image (Ctrl+V) for OCR\n\n"
        "Controls:\n"
        "  [bold]Enter[/bold] - Launch search\n"
        "  [bold]Shift+Tab[/bold] - Switch Title/DOI mode\n"
        "  [bold]Arrows[/bold] - Navigate text\n"
        "  [bold]↑/↓[/bold] - Navigate history\n"
        "  [bold]Ctrl+A/E[/bold] - Start/End of line\n"
        "  [bold]Ctrl+W[/bold] - Delete word backward\n"
        "  [bold]Ctrl+V[/bold] - Paste image for OCR\n"
        "  [bold]Ctrl+Shift+V[/bold] - Paste text\n"
        "  [bold]Ctrl+C[/bold] - Exit",
        border_style="cyan"
    ))

    # State variables (as list for mutable effect over function args passing)
    search_mode = ["title"]  # "title" or "doi"
    toolbar_message = [None]  # Message to display in toolbar (persistent across iterations)
    txt_buffer = [None]  # Text to preserve when switching modes or after OCR

    kb = key_bindings(toolbar_message=toolbar_message, search_mode=search_mode, txt_buffer=txt_buffer)
    # Merge custom key bindings with default emacs bindings
    merged_bindings = merge_key_bindings([
        emacs.load_emacs_bindings(),
        kb,
    ])

    get_bottom_toolbar = lambda : bottom_toolbar(toolbar_message=toolbar_message, search_mode=search_mode)

    # Create PromptSession - reused for all inputs
    # PromptSession uses InMemoryHistory by default
    session = PromptSession(
        multiline=True,
        wrap_lines=True,
        editing_mode=EditingMode.EMACS,
        key_bindings=merged_bindings,
        bottom_toolbar=get_bottom_toolbar,
    )

    while True:
        try:
            input_text = handle_user_input(
                session=session,
                console=console,
                search_mode=search_mode,
                txt_buffer=txt_buffer
            )
            if not input_text:
                continue

        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Exiting interactive mode.[/yellow]")
            return

        # Clear toolbar message before processing new input
        toolbar_message[0] = None

        resolve_user_input(
            console=console,
            search_mode=search_mode,
            input_text=input_text,
            config=config,
            toolbar_message=toolbar_message
        )
