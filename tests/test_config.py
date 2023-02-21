"""
Unit tests for config.py.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from copy import deepcopy
from pathlib import Path
from typing import Any

from deepdiff import DeepDiff

import pytest

from doi2bibtex.config import Configuration


# -----------------------------------------------------------------------------
# UNIT TESTS
# -----------------------------------------------------------------------------

@pytest.fixture(params=[True, False])
def mock_open(request: Any, mocker: Any) -> None:
    """
    Mock the built-in `open()` function to return a file-like object,
    either empty or with a fake YAML configuration file.
    """

    # String of a fake YAML configuration file
    if request.param:
        yaml_file = ""
    else:
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

    # Copy the default configuration object (we will use this later)
    default_config = deepcopy(config)

    # Check what the `mock_open` fixture does (i.e., if it returns an empty
    # file or a fake YAML file)
    with open('') as f:
        is_empty = f.read() == ''

    # Case 2a: If the file is empty, we do not get a warning
    if is_empty:
        with monkeypatch.context() as m:
            m.setattr(Path, 'exists', lambda _: True)
            config = Configuration()
        assert not DeepDiff(config, default_config)

    # Case 2b: If the file is not empty, we do get a warning
    else:
        with monkeypatch.context() as m:
            m.setattr(Path, 'exists', lambda _: True)
            with pytest.warns(UserWarning) as user_warning:
                config = Configuration()
        assert "Ignoring unknown " in str(user_warning[0].message)
        assert config.limit_authors == 3
        assert 'ignored_property' not in vars(config)
