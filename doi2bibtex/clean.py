import os
import re

from tqdm import tqdm

from doi2bibtex.resolve import resolve_identifier


def process_references(tex_dir_path,
                       bib_dir_path,
                       output_dir_path,
                       config):
    """
    This function processes references in .tex files, matches them with DOIs or ADS codes in .bib files,
    resolves DOIs to BibTeX entries using doi2bibtex, and creates cleaned and unresolved .bib files.

    Args:
        tex_dir_path (str): Path to the directory containing .tex files.
        bib_dir_path (str): Path to the directory containing .bib files.
        output_dir_path (str): Path to the output directory for saving cleaned and unresolved entries.

    Returns:
        None: Outputs relevant files to the specified directories.
    """

    # Patterns to process .tex files
    citation_patterns = r"\\cite(?:p|t|alt)?(?:\[[^\]]*\])?(?:\[[^\]]*\])?\{([^}]*)\}"

    # Initialize an empty set to store unique references
    unique_references = set()

    # Step 1: Extract unique keys from .tex files
    for file_name in os.listdir(tex_dir_path):
        if file_name.endswith('.tex'):
            file_path = os.path.join(tex_dir_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                matches = re.findall(citation_patterns, file_content)
                for match in matches:
                    keys = [key.strip() for key in match.split(',')]
                    unique_references.update(keys)

    print(f"Total unique references: {len(unique_references)}")

    # Step 2: Match keys with DOIs or ADS codes in .bib files
    entry_pattern = r"@.*?\{(.*?),"
    doi_pattern = r"doi\s*=\s*\{(.*?)\}"
    ads_pattern = r"annotation\s*=\s*\{.*?ADS Bibcode:\s*([^\s,]+)"
    key_to_doi = {}

    for bib_file_name in os.listdir(bib_dir_path):
        if bib_file_name.endswith('.bib'):
            bib_file_path = os.path.join(bib_dir_path, bib_file_name)
            with open(bib_file_path, 'r', encoding='utf-8') as bib_file:
                bib_content = bib_file.read()
                entries = bib_content.split('@')[1:]  # Skip part before the first '@'
                entries = ['@' + entry for entry in entries]  # Add '@' back to each entry

                for entry in entries:
                    key_match = re.search(entry_pattern, entry)
                    doi_match = re.search(doi_pattern, entry)
                    ads_match = re.search(ads_pattern, entry) if not doi_match else None

                    if key_match:
                        key = key_match.group(1).strip()
                        if doi_match:
                            identifier = doi_match.group(1).strip()
                        elif ads_match:
                            identifier = ads_match.group(1).strip()[:-1]
                        else:
                            identifier = None

                        if key in unique_references and identifier:
                            key_to_doi[key] = identifier

    print(f"Keys matched with DOIs: {len(key_to_doi)}")

    unmatched_keys = [key for key in unique_references if key not in key_to_doi]
    print(f"Keys without matching DOI: {unmatched_keys}")

    # Step 3: Resolve DOIs using doi2bibtex
    resolved_entries = {}
    unresolved_keys = []

    for key, doi in tqdm(key_to_doi.items(), desc="Resolving DOIs"):
        resolved_bibtex = resolve_identifier(identifier=doi, config=config)
        if 'There was an error:' not in resolved_bibtex:
            resolved_bibtex = resolved_bibtex.strip()
            resolved_bibtex = re.sub(r"@\w+\{.*?,", f"@article{{{key},", resolved_bibtex, count=1)
            resolved_entries[key] = resolved_bibtex
        else:
            print(f"Could not resolve DOI for key '{key}' (DOI: {doi})")
            unresolved_keys.append(key)

    unresolved_keys.extend(unmatched_keys)

    # Step 4: Retrieve unresolved original BibTeX entries
    original_entries = {}
    for bib_file_name in os.listdir(bib_dir_path):
        if bib_file_name.endswith('.bib'):
            bib_file_path = os.path.join(bib_dir_path, bib_file_name)
            with open(bib_file_path, 'r', encoding='utf-8') as bib_file:
                bib_content = bib_file.read()
                entries = bib_content.split('@')[1:]  # Skip before the first '@'
                entries = ['@' + entry for entry in entries]

                for entry in entries:
                    key_match = re.search(entry_pattern, entry)
                    if key_match:
                        key = key_match.group(1).strip()
                        if key in unresolved_keys:
                            original_entries[key] = entry.strip()

    # Step 5: Save results to .bib files
    clean_bib_file = os.path.join(output_dir_path, 'references_clean.bib')
    unresolved_bib_file = os.path.join(output_dir_path, 'references_unresolved.bib')
    combined_bib_file = os.path.join(output_dir_path, 'references.bib')

    with open(clean_bib_file, 'w', encoding='utf-8') as clean_file:
        for key, bibtex in resolved_entries.items():
            clean_file.write(bibtex + '\n\n')

    with open(unresolved_bib_file, 'w', encoding='utf-8') as unresolved_file:
        for key, entry in original_entries.items():
            unresolved_file.write(entry + '\n\n')

    with open(combined_bib_file, 'w', encoding='utf-8') as combined_file:
        for key, bibtex in resolved_entries.items():
            combined_file.write(bibtex + '\n\n')
        for key, entry in original_entries.items():
            combined_file.write(entry + '\n\n')

    # Summary
    print(f"Resolved entries saved to: {clean_bib_file}")
    print(f"Unresolved entries saved to: {unresolved_bib_file}")
    print(f"Combined entries saved to: {combined_bib_file}")
    print(f"Unresolved keys: {unresolved_keys}")