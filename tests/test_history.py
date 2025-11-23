"""
Unit tests for history navigation logic.
Tests the history navigation behavior used in interactive mode.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import pytest


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

class HistoryNavigator:
    """
    Helper class to simulate history navigation logic.
    This mimics the behavior implemented in interactive.py.
    """

    def __init__(self):
        self.input_history = []
        self.history_index = None
        self.current_draft = None
        self.current_text = ""

    def navigate_up(self):
        """Navigate to previous history entry."""
        if not self.input_history:
            return

        # If we're not in history mode, save current text and start from the end
        if self.history_index is None:
            self.current_draft = self.current_text
            self.history_index = len(self.input_history) - 1
        elif self.history_index > 0:
            # Save current modifications to history before moving
            self.input_history[self.history_index] = self.current_text
            self.history_index -= 1

        # Load history entry
        if 0 <= self.history_index < len(self.input_history):
            self.current_text = str(self.input_history[self.history_index])

    def navigate_down(self):
        """Navigate to next history entry."""
        if not self.input_history or self.history_index is None:
            return

        # Save current modifications to history before moving
        self.input_history[self.history_index] = self.current_text

        if self.history_index < len(self.input_history) - 1:
            self.history_index += 1
            self.current_text = str(self.input_history[self.history_index])
        else:
            # Restore draft when going past the end
            self.history_index = None
            self.current_text = self.current_draft if self.current_draft is not None else ""

    def submit_text(self, text: str):
        """Submit text to history."""
        # Add to history (avoid duplicates of the last entry)
        if not self.input_history or self.input_history[-1] != text:
            self.input_history.append(text)
        # Reset history index
        self.history_index = None
        self.current_draft = None


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

def test__history_navigation_basic() -> None:
    """
    Test basic history navigation (up and down).
    """

    nav = HistoryNavigator()

    # Add some history
    nav.submit_text("first search")
    nav.submit_text("second search")

    assert len(nav.input_history) == 2

    # Navigate up - should go to "second search"
    nav.navigate_up()
    assert nav.current_text == "second search"
    assert nav.history_index == 1

    # Navigate up again - should go to "first search"
    nav.navigate_up()
    assert nav.current_text == "first search"
    assert nav.history_index == 0

    # Navigate down - should go to "second search"
    nav.navigate_down()
    assert nav.current_text == "second search"
    assert nav.history_index == 1


def test__history_navigation_with_draft() -> None:
    """
    Test history navigation preserves draft when returning.
    """

    nav = HistoryNavigator()

    # Add history
    nav.submit_text("first search")
    nav.submit_text("second search")

    # Start typing new text (not submitted)
    nav.current_text = "third search"

    # Navigate up - should save draft
    nav.navigate_up()
    assert nav.current_draft == "third search"
    assert nav.current_text == "second search"

    # Navigate down past end - should restore draft
    nav.navigate_down()
    assert nav.current_text == "third search"
    assert nav.history_index is None


def test__history_navigation_modify_and_restore() -> None:
    """
    Test that modifications to history entries are preserved and draft is restored.
    This is the main scenario from the original test_history.py.
    """

    nav = HistoryNavigator()

    # Add initial history
    nav.input_history = ["titre 1", "titre 2"]
    nav.current_text = "titre 3"

    # Navigate up (to "titre 2")
    nav.navigate_up()
    assert nav.current_text == "titre 2"
    assert nav.current_draft == "titre 3"
    assert nav.history_index == 1

    # Navigate up again (to "titre 1")
    nav.navigate_up()
    assert nav.current_text == "titre 1"
    assert nav.history_index == 0
    assert nav.current_draft == "titre 3"  # Draft should still be intact

    # Modify "titre 1" to "titre 1 modifié"
    nav.current_text = "titre 1 modifié"

    # Navigate down (to "titre 2")
    nav.navigate_down()
    assert nav.current_text == "titre 2"
    assert nav.history_index == 1
    assert nav.input_history[0] == "titre 1 modifié"  # Modification saved

    # Navigate down again (back to draft)
    nav.navigate_down()
    assert nav.current_text == "titre 3"  # Draft restored!
    assert nav.history_index is None


def test__history_navigation_empty_history() -> None:
    """
    Test history navigation with empty history.
    """

    nav = HistoryNavigator()

    # Try to navigate with no history
    nav.navigate_up()
    assert nav.current_text == ""
    assert nav.history_index is None

    nav.navigate_down()
    assert nav.current_text == ""
    assert nav.history_index is None


def test__history_navigation_single_entry() -> None:
    """
    Test history navigation with single entry.
    """

    nav = HistoryNavigator()
    nav.submit_text("only search")

    # Navigate up
    nav.navigate_up()
    assert nav.current_text == "only search"
    assert nav.history_index == 0

    # Try to navigate up again (should stay at first entry)
    nav.navigate_up()
    assert nav.current_text == "only search"
    assert nav.history_index == 0


def test__history_navigation_duplicate_prevention() -> None:
    """
    Test that duplicate consecutive entries are prevented.
    """

    nav = HistoryNavigator()

    # Submit same text twice
    nav.submit_text("same search")
    nav.submit_text("same search")

    # Should only have one entry
    assert len(nav.input_history) == 1
    assert nav.input_history[0] == "same search"

    # Submit different text, then same again
    nav.submit_text("different search")
    assert len(nav.input_history) == 2

    nav.submit_text("same search")
    assert len(nav.input_history) == 3  # This is allowed (not consecutive duplicate)


def test__history_navigation_modifications_persist() -> None:
    """
    Test that modifications to history entries persist across navigation.
    """

    nav = HistoryNavigator()
    nav.input_history = ["entry 1", "entry 2", "entry 3"]

    # Navigate to entry 2
    nav.navigate_up()  # to entry 3
    nav.navigate_up()  # to entry 2
    assert nav.current_text == "entry 2"

    # Modify it
    nav.current_text = "entry 2 modified"

    # Navigate away
    nav.navigate_up()  # to entry 1
    assert nav.input_history[1] == "entry 2 modified"

    # Navigate back
    nav.navigate_down()  # back to entry 2
    assert nav.current_text == "entry 2 modified"


def test__history_navigation_edge_case_at_boundaries() -> None:
    """
    Test navigation at history boundaries.
    """

    nav = HistoryNavigator()
    nav.input_history = ["a", "b", "c"]

    # Navigate to first entry
    nav.navigate_up()  # to "c"
    nav.navigate_up()  # to "b"
    nav.navigate_up()  # to "a"
    assert nav.history_index == 0

    # Try to go up past first - should stay at first
    nav.navigate_up()
    assert nav.history_index == 0
    assert nav.current_text == "a"

    # Navigate to last entry
    nav.navigate_down()  # to "b"
    nav.navigate_down()  # to "c"
    assert nav.history_index == 2

    # Navigate down past end - should reset to None
    nav.current_draft = "draft"
    nav.navigate_down()
    assert nav.history_index is None
    assert nav.current_text == "draft"


def test__history_submit_resets_state() -> None:
    """
    Test that submitting text resets history navigation state.
    """

    nav = HistoryNavigator()
    nav.submit_text("first")

    # Start navigating
    nav.current_text = "draft"
    nav.navigate_up()
    assert nav.history_index == 0
    assert nav.current_draft == "draft"

    # Submit new text
    nav.submit_text("second")

    # State should be reset
    assert nav.history_index is None
    assert nav.current_draft is None
    assert len(nav.input_history) == 2
