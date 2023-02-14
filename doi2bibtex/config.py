"""
Handle configuration.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from pathlib import Path
from typing import Dict, List
from warnings import warn

import yaml


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

class Configuration:

    def __init__(self) -> None:

        # Define the default configuration
        self.abbreviate_journal_names: bool = True
        self.citekey_delimiter: str = "_"
        self.convert_latex_chars: bool = True
        self.convert_month_to_number: bool = True
        self.crossmatch_with_dblp: bool = False
        self.fix_arxiv_entrytype: bool = True
        self.format_author_names: bool = True
        self.generate_citekey: bool = True
        self.limit_authors: int = 1000
        self.pygments_theme: str = "dracula"
        self.remove_fields: Dict[str, List[str]] = {
            "all": ["abstract"],
            "article": ["publisher"]
        }
        self.remove_url_if_doi: bool = True
        self.resolve_adsurl: bool = True
        self.update_arxiv_if_doi: bool = True

        # Load the configuration from the config file
        self.load_from_yaml_file()

    def __str__(self) -> str:
        settings = [f"  {k}={repr(v)},\n" for k, v in vars(self).items()]
        return "Configuration(\n" + "".join(sorted(settings)) + ")"

    def load_from_yaml_file(self) -> None:

        # Define the expected path to the configuration file
        file_path = Path.home() / ".doi2bibtex" / "config.yaml"

        # If no configuration file exists, we are done
        if not file_path.exists():
            return

        # Load the configuration from the file
        with open(file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)

        # If the file is empty, we are done
        if config is None:
            return

        # Otherwise, update the configuration, only store known keys
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                warn(f'Warning: Ignoring unknown configuration key "{key}"!')
