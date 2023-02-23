"""
Methods for resolving identifiers to BibTeX entries.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from bs4 import BeautifulSoup

import json

import requests

from doi2bibtex.ads import get_ads_token
from doi2bibtex.bibtex import bibtex_string_to_dict, dict_to_bibtex_string
from doi2bibtex.config import Configuration
from doi2bibtex.identify import is_arxiv_id, is_doi, is_ads_bibcode
from doi2bibtex.process import preprocess_identifier, postprocess_bibtex


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

def resolve_ads_bibcode(ads_bibcode: str) -> dict:
    """
    Resolve an ADS bibcode using the ADS API and return the BibTeX.
    """

    # Get the ADS token (and raise an error if we don't have one)
    token = get_ads_token(raise_on_error=True)

    # Query the ADS API manually
    r = requests.post(
        url="https://api.adsabs.harvard.edu/v1/export/bibtex",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps({"bibcode": [ads_bibcode]}),
    )

    # Check if we got a 200 response; if not, raise an error
    if (error := r.status_code) != 200:
        raise RuntimeError(
            f'Error {error} resolving "{ads_bibcode}": no BibTeX entry found'
        )

    # Parse the response using JSON
    bibtex_string = json.loads(r.text)["export"]

    # Parse the bibstring to a dict
    bibtex_dict = bibtex_string_to_dict(bibtex_string)

    return bibtex_dict


def resolve_arxiv_id(arxiv_id: str) -> dict:
    """
    Resolve an arXiv ID using arxiv2bibtex.org and return the BibTeX
    entry.
    """

    # Send a request to arxiv2bibtex.org
    # We could also use the arXiv API instead, but it's a bit more complicated
    # and would require us to parse the XML response ourselves...
    r = requests.get(f"https://arxiv2bibtex.org/?q={arxiv_id}&format=biblatex")
    if (error := r.status_code) != 200:
        raise RuntimeError(f"Error {error} resolving {arxiv_id}")

    # Find the BibLaTeX entry using BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    textarea = soup.select_one("#biblatex textarea.wikiinfo")
    if textarea is None:
        raise RuntimeError(
            f'Error resolving "{arxiv_id}": no BibTeX entry found'
        )
    bibtex_string = textarea.get_text()

    # Parse the bibstring to a dict
    bibtex_dict = bibtex_string_to_dict(bibtex_string)

    return bibtex_dict


def resolve_doi(doi: str) -> dict:
    """
    Resolve a DOI using the Crossref API and return the BibTeX entry.
    """

    # Send a request to the Crossref API to get the BibTeX entry
    r = requests.get(
        f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
    )
    if (error := r.status_code) != 200:
        raise RuntimeError(
            f'Error {error} resolving DOI "{doi}": no BibTeX entry found'
        )

    # Parse the response into a dict
    bibtex = bibtex_string_to_dict(r.text)

    return bibtex


def resolve_identifier(identifier: str, config: Configuration) -> str:
    """
    Resolve the given `identifier` to a BibTeX entry. This function
    basically just determines the type of the identifier, calls the
    appropriate resolver function, and post-processes the result.
    """

    try:

        # Remove the "doi:" or "arXiv:" prefix, if present
        identifier = preprocess_identifier(identifier)

        # Resolve the identifier to a BibTeX entry (as a dict)
        if is_doi(identifier):
            bibtex_dict = resolve_doi(identifier)
        elif is_arxiv_id(identifier):
            bibtex_dict = resolve_arxiv_id(identifier)
        elif is_ads_bibcode(identifier):
            bibtex_dict = resolve_ads_bibcode(identifier)
        else:
            raise RuntimeError(f"Unrecognized identifier: {identifier}")

        # If we resolved an arXiv ID and we got a BibTeX entry with a DOI,
        # we can update the identifier to the DOI and resolve that one to
        # get a better BibTeX entry (published paper instead of preprint)
        if (
            config.update_arxiv_if_doi and
            is_arxiv_id(identifier) and
            "doi" in bibtex_dict
        ):
            identifier = bibtex_dict["doi"]
            bibtex_dict = resolve_doi(identifier)

        # Post-process the BibTeX dict
        bibtex_dict = postprocess_bibtex(bibtex_dict, identifier, config)

        # Convert the BibTeX dict to a string
        return dict_to_bibtex_string(bibtex_dict).strip()

    except Exception as e:
        return "\n" + "  There was an error:\n  " + str(e) + "\n"
