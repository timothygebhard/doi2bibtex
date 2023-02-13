"""
Unit tests for config.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pathlib import Path
from typing import Any

import pytest

from doi2bibtex.config import Configuration


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

@pytest.fixture
def mock_open(mocker: Any) -> None:
    """
    Mock the built-in `open()` function to always return a file-like
    object with the contents "hazzuh".
    """

    # String of a fake YAML configuration file
    yaml_file = """
    limit_authors: 3
    ignored_property: "some value"
    """

    # Patch the built-in `open()` function to return the fake YAML file
    mocker.patch("builtins.open", mocker.mock_open(read_data=yaml_file))


def test__configuration(
    monkeypatch: pytest.MonkeyPatch,
    mock_open: Any,
) -> None:
    """
    Test `Configuration()`.
    """

    # Case 1: Assume no config file exists; this should return defaults
    with monkeypatch.context() as m:
        m.setattr(Path, 'exists', lambda _: False)
        config = Configuration()
    assert config.limit_authors == 1000
    assert len(str(config).split('\n')) == len(vars(config)) + 2

    # Case 2: Use mock_open to simulate that there is a config file that
    # overwrites the defaults
    with monkeypatch.context() as m:
        m.setattr(Path, 'exists', lambda _: True)
        with pytest.warns(UserWarning) as user_warning:
            config = Configuration()
    assert "Ignoring unknown configuration key" in str(user_warning[0].message)
    assert config.limit_authors == 3
    assert 'ignored_property' not in vars(config)
