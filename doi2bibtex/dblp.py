"""
Handle interactions with dlbp.org.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import requests
import json

from bibtexparser.customization import splitname


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

def crossmatch_with_dblp(
    bibtex_dict: dict,
    identifier: str,
) -> dict:
    """
    Cross-match the given BibTeX entry with the dblp database to check
    if there is a matching conference paper. If so, add the venue and
    year of the conference paper to the BibTeX entry.
    Note: This function usually only makes sense for arXiv preprints.
    """

    # If we do not have a title and author, we cannot cross-match with dblp
    if "title" not in bibtex_dict or "author" not in bibtex_dict:
        return bibtex_dict

    # Extract the title and first author from the BibTeX entry
    # We are not adding the year because the year of the arXiv preprint does
    # not necessarily match the year of the conference paper.
    title = bibtex_dict["title"]
    author = splitname(bibtex_dict["author"].split(" and ")[0])

    # Construct query and make request to the dblp API
    # Unfortunately, the dblp API does not allow to search for a specific
    # arXiv identifier, so we have to search for the title and first author
    query = "+".join(author["last"]) + "+" + title.replace(" ", "+")
    url = f"https://dblp.org/search/publ/api?q={query}&format=json&h=1000"

    # Check if the request was successful
    r = requests.get(url)
    if not r.status_code == 200:
        raise RuntimeError(
            f"Could not get data from dblp. Status code: {r.status_code}."
        )

    # Parse the response as JSON and extract the papers; if there are no
    # papers, we return the original BibTeX entry
    data = dict(json.loads(r.text))
    if "hit" not in data["result"]["hits"]:
        return bibtex_dict
    papers = data["result"]["hits"]["hit"]

    # Find the paper in the list of papers
    # For this, we use two criteria: (1) the paper needs to be a conference
    # paper and (2) the title or the identifier needs to match the one from
    # the BibTeX entry. The `[:-1]` is used to remove the trailing dot from
    # the title that seems present in all dlbp entries.
    for paper in papers:
        info = dict(paper["info"])
        if (
            "type" in info and info["type"] == "Conference and Workshop Papers"
        ) and (
            ("title" in info and title == info["title"][:-1])
            or ("ee" in info and identifier in info["ee"])
            or ("volume" in info and identifier in info["volume"])
        ):
            break

    # If we got here, this means we did not break out of the loop, i.e., we
    # did not find the paper in the list of papers
    else:
        info = {}

    # Add the venue information from dblp to the BibTeX entry by augmenting
    # the `addendum` field
    if info and "venue" in info and "year" in info:
        bibtex_dict["addendum"] = (
            bibtex_dict.get("addendum", "")
            + " "
            + f"Published at {info['venue']}~{info['year']}."
        ).strip()

    return bibtex_dict
