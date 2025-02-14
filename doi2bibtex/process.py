"""
Look up a BibTeX entry based on a DOI or arXiv ID.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import re

from bibtexparser.customization import splitname

from doi2bibtex.ads import get_ads_bibcode_for_identifier
from doi2bibtex.config import Configuration
from doi2bibtex.constants import JOURNAL_ABBREVIATIONS
from doi2bibtex.dblp import crossmatch_with_dblp
from doi2bibtex.identify import is_arxiv_id
from doi2bibtex.utils import (
    doi_to_url,
    latex_to_unicode,
    remove_accented_characters,
)


# -----------------------------------------------------------------------------
# DEFINITIONS
# -----------------------------------------------------------------------------

def preprocess_identifier(identifier: str) -> str:
    """
    Pre-process the given `identifier`: Remove any leading or trailing
    whitespace, and remove the "doi:" or "arXiv:" prefix.
    """

    # Remove leading and trailing whitespace
    identifier = identifier.strip()

    # Remove the "doi:" prefix
    if identifier.startswith("doi:") or identifier.startswith("DOI:"):
        identifier = identifier[4:]

    # Remove the "arXiv:" prefix
    if identifier.startswith("arXiv:") or identifier.startswith("arxiv:"):
        identifier = identifier[6:]

    return identifier


def postprocess_bibtex(
    bibtex_dict: dict,
    identifier: str,
    config: Configuration,
) -> dict:
    """
    Post-process a BibTeX entry and apply a series of fixes and tweaks.
    """

    # Fix broken ampersand in A&A journal name
    bibtex_dict = fix_broken_ampersand(bibtex_dict)

    # Fix broken page numbers (e.g., "160â€“175" instead of "160--175")
    bibtex_dict = fix_broken_pagenumbers(bibtex_dict)

    # Convert escaped LaTeX character to proper Unicode
    if config.convert_latex_chars:
        bibtex_dict = convert_latex_chars(bibtex_dict)

    # Fix entry type and journal name for arXiv preprints
    if config.fix_arxiv_entrytype:
        bibtex_dict = fix_arxiv_entrytype(bibtex_dict, identifier)

    # Replace journal name with standard abbreviations
    if config.abbreviate_journal_names:
        bibtex_dict = abbreviate_journal_name(bibtex_dict)

    # Generate a citekey
    if config.generate_citekey:
        bibtex_dict = generate_citekey(bibtex_dict)

    # Truncate the author list
    bibtex_dict = truncate_author_list(bibtex_dict, config)

    # Convert author names to a standard format
    if config.format_author_names:
        bibtex_dict = format_author_names(bibtex_dict)

    # Convert the month to a number
    if config.convert_month_to_number:
        bibtex_dict = convert_month_to_number(bibtex_dict)

    # Resolve and add the ADS bibcode
    # This is not unit tested, because it requires an ADS API token
    if config.resolve_adsurl:  # pragma: no cover
        bibtex_dict = resolve_adsurl(bibtex_dict, identifier)

    # Remove fields based on the entry type
    if config.remove_fields:
        bibtex_dict = remove_fields(bibtex_dict, config)

    # Remove the URL if it contains the same information as the DOI
    if config.remove_url_if_doi:
        bibtex_dict = remove_url_if_doi(bibtex_dict)

    # Try to crossmatch the entry with dblp to get venue information
    if config.crossmatch_with_dblp:  # pragma: no cover
        bibtex_dict = crossmatch_with_dblp(bibtex_dict, identifier)

    return bibtex_dict


def abbreviate_journal_name(bibtex_dict: dict) -> dict:
    """
    Replace the journal name with a standard abbreviation.
    """

    if (
        "journal" in bibtex_dict
        and bibtex_dict["journal"] in JOURNAL_ABBREVIATIONS
    ):
        bibtex_dict["journal"] = JOURNAL_ABBREVIATIONS[bibtex_dict["journal"]]

    return bibtex_dict


def convert_latex_chars(bibtex_dict: dict) -> dict:
    """
    Convert escaped LaTeX characters in the `author` and `title` fields
    to proper Unicode. (`journal` needs special treatment.)
    """

    if "author" in bibtex_dict:
        bibtex_dict["author"] = latex_to_unicode(bibtex_dict["author"])
    if "title" in bibtex_dict:
        bibtex_dict["title"] = latex_to_unicode(bibtex_dict["title"])

    return bibtex_dict


def convert_month_to_number(bibtex_dict: dict) -> dict:
    """
    Convert the month names to their corresponding number.
    Example: "jan" -> "1".
    """

    # If there is no month field, return the original dictionary
    if "month" not in bibtex_dict:
        return bibtex_dict

    # Otherwise, convert the month to a number
    month = bibtex_dict["month"].lower()

    # Map the month to a number
    if month in ("jan", "january"):
        number = "1"
    elif month in ("feb", "february"):
        number = "2"
    elif month in ("mar", "march"):
        number = "3"
    elif month in ("apr", "april"):
        number = "4"
    elif month in ("may", "may"):
        number = "5"
    elif month in ("jun", "june"):
        number = "6"
    elif month in ("jul", "july"):
        number = "7"
    elif month in ("aug", "august"):
        number = "8"
    elif month in ("sep", "september"):
        number = "9"
    elif month in ("oct", "october"):
        number = "10"
    elif month in ("nov", "november"):
        number = "11"
    elif month in ("dec", "december"):
        number = "12"
    else:
        number = month

    # Update the dictionary
    bibtex_dict["month"] = number

    return bibtex_dict


def fix_arxiv_entrytype(bibtex_dict: dict, identifier: str) -> dict:
    """
    Fix the entry type for arXiv preprints.
    """

    if is_arxiv_id(identifier):
        bibtex_dict["ENTRYTYPE"] = "article"

    return bibtex_dict


def fix_broken_ampersand(bibtex_dict: dict) -> dict:
    """
    Fix broken ampersand in A&A journal name that we get from CrossRef.
    """

    if "journal" in bibtex_dict:
        bibtex_dict["journal"] = bibtex_dict["journal"].replace(
            r"{\&}amp$\mathsemicolon$", r"\&"
        )
        bibtex_dict["journal"] = bibtex_dict["journal"].replace(
            r"&amp;", r"\&"
        )

    return bibtex_dict


def fix_broken_pagenumbers(bibtex_dict: dict) -> dict:
    """
    Fix broken pagenumbers (UTF-8 issue: "â€“" is an en-dash).
    """

    if "pages" in bibtex_dict:
        bibtex_dict["pages"] = bibtex_dict["pages"].replace(
            "â€“", "--"
        )

    return bibtex_dict


def format_author_names(bibtex_dict: dict) -> dict:
    """
    Clean up the `author` field of a BibTeX entry by splitting it into
    individual authors, converting each author to the  "{Lastname},
    Firstname" format, and joining the everything back together.
    """

    # If there is no author field, return the original dictionary
    if "author" not in bibtex_dict:
        return bibtex_dict

    # Otherwise, split the author string into a list of individual authors
    authors_list = bibtex_dict["author"].split(" and ")

    # Clean up each author's name
    for i, author in enumerate(authors_list):
        author = splitname(author)
        firstname = " ".join(author["first"]).strip()
        von = " ".join(author["von"]).strip()
        von += " " if von else ""
        lastname = " ".join(author["last"]).strip()
        authors_list[i] = f"{{{von}{lastname}}}, {firstname}"

    # Join the authors back together and
    authors_string = " and ".join(authors_list)
    authors_string = authors_string.replace("and {others}, ", "and others")

    # Update the dictionary
    bibtex_dict["author"] = authors_string

    return bibtex_dict


def generate_citekey(bibtex_dict: dict, delim: str = "_") -> dict:
    """
    Generate a citekey for a given BibTeX entry. The citekey has the
    following format: "SimplifiedLastName_Year". For example, if some
    person named "De La Müller-Márquez" published a paper in 2023, the
    citekey would be "DeLaMuellerMarquez_2023".
    """

    # Get the first author's name and split it into parts
    first_author = splitname(bibtex_dict["author"].split(" and ")[0])

    # Drop any accents, dashes, or spaces from the name
    lastname = remove_accented_characters("".join(first_author["last"]))
    lastname = lastname.replace("-", "")
    lastname = lastname.replace(" ", "")

    # Add a "Von" if the author has one
    if von := first_author["von"]:
        lastname = "".join([_.title() for _ in von]) + lastname

    # Add the first word of the title
    articles = {"a", "the", "an"}
    words = bibtex_dict["title"].split(" ")
    first_non_article = next(
        (word for word in words if word.lower() not in articles), None
    )
    if first_non_article is None:
        title = "unknown"
    else:
        title = re.sub(r"[^a-zA-Z0-9]", "", first_non_article)

    # Combine the name, year and title to get the citekey
    citekey = f"{lastname}{delim}{bibtex_dict['year']}{delim}{title}"

    # Update the citekey of the BibTeX entry
    bibtex_dict["ID"] = citekey

    return bibtex_dict


def remove_fields(bibtex_dict: dict, config: Configuration) -> dict:
    """
    Remove fields from a BibTeX entry based on the `entrytype`.
    Background: Removing the publisher from an `article` might make
    more sense than removing it from `book`.
    """

    # Remove fields that are not entry type specific
    for field in config.remove_fields.get('all', []):
        if field in bibtex_dict:
            del bibtex_dict[field]

    # Remove entry type specific fields
    for field in config.remove_fields.get(bibtex_dict["ENTRYTYPE"], []):
        if field in bibtex_dict:
            del bibtex_dict[field]

    return bibtex_dict


def remove_url_if_doi(bibtex_dict: dict) -> dict:
    """
    Remove the `url` field if it is redundant with the the `doi` field.
    """

    if (
        ("url" in bibtex_dict)
        and ("doi" in bibtex_dict)
        and (bibtex_dict["url"] == doi_to_url(bibtex_dict["doi"]))
    ):
        del bibtex_dict["url"]

    return bibtex_dict


def resolve_adsurl(bibtex_dict: dict, identifier: str) -> dict:
    """
    Resolve the `adsurl` field for a given BibTeX entry.
    """

    # If the entry already has an `adsurl` field, return the original dict
    if "adsurl" in bibtex_dict:
        return bibtex_dict

    # Resolve the ADS bibcode
    bibcode = get_ads_bibcode_for_identifier(identifier)

    # If we found a bibcode, construct the ADS URL and add it to the dict
    if bibcode:
        bibtex_dict["adsurl"] = f"https://adsabs.harvard.edu/abs/{bibcode}"

    return bibtex_dict


def truncate_author_list(bibtex_entry: dict, config: Configuration) -> dict:
    """
    Truncate an `author_list` (i.e., the `author` field of a BibTeX
    entry) to the first `limit` authors, and add an "et al." at the end.
    """

    # If there is no author field, return the original dictionary
    if "author" not in bibtex_entry:
        return bibtex_entry

    # Split the author list into individual authors
    authors_list = bibtex_entry['author'].split(" and ")

    # If there are too many authors, truncate the list and add an "et al."
    et_al = ""
    if len(authors_list) > config.limit_authors:
        authors_list = authors_list[:config.limit_authors]
        et_al = " and others"

    # Join the authors back together
    authors_string = " and ".join(authors_list) + et_al

    # Update the author field of the BibTeX entry
    bibtex_entry["author"] = authors_string

    return bibtex_entry
