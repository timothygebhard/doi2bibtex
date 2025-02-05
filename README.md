<h1 align="center">doi2bibtex</h1>
<p align="center">
<img src="https://img.shields.io/badge/python-3.8+-blue" alt="Python versions: 3.8+">
<a href="https://pypi.org/project/doi2bibtex"><img src="https://badge.fury.io/py/doi2bibtex.svg" alt="PyPI version"></a>
<a href="https://github.com/python/mypy"><img src="https://img.shields.io/badge/mypy-checked-1E5082" alt="Type annotations checked with MyPy"></a>
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
<a href="https://github.com/timothygebhard/doi2bibtex/actions/workflows/tests.yaml"><img src="https://github.com/timothygebhard/doi2bibtex/actions/workflows/tests.yaml/badge.svg?branch=main" alt="Test status"></a>
</p>

**doi2bibtex** is a small Python package that can be used to resolve DOIs (and other identifiers) into a BibTeX entry and format them according to a customizable set of rules (see below for a full list of features). 

<p align="center">
   <img src="https://timothygebhard.de/files/d2b.gif?" width="640" alt="A GIF showing how to use doi2bibtex in the command line">
</p>


Most features of **doi2bibtex** are availabe in other tools. 
For example, you can chain together [doi2bib](https://www.doi2bib.org) with [bibtool](https://github.com/ge-ne/bibtool) or [bibtex-tidy](https://github.com/FlamingTempura/bibtex-tidy) and recover most of the functionality in this package (and some of these tools are actually used under the hood). 
If you use a reference manager like [zotero](https://www.zotero.org/) or [Mendeley](https://www.mendeley.com/), you can also resolve papers based on an identifier and later export entries to a `.bib` file.

The motivation for **doi2bibtex** was rather personal and came from two facts: 1. I have a rather strong opinion on how I want my `.bib` files to look like, and 2. I work on the intersection of astrophysics and machine learning, meaning that I often need the [NASA/ADS](https://adsabs.harvard.edu) bibcodes for the `adsurl` field, but I can’t solely rely on ADS to retrieve BibTeX entries because I also frequently cite papers that are not indexed by ADS. 
At some point, I got tired of the ever-growing mess of shell scripts and bash commands that I used to achieve this, and decided to re-write as a single package that would be easier to maintain and extend.



## 🚀 Quickstart

Follow these instructions to get started with `doi2bibtex`:



### 🤓 Installation

You can simply `pip`-install the package using:

```bash
pip install doi2bibtex
```

Alternatively, you can also clone the repository and install the package locally:

```bash
git clone https://github.com/timothygebhard/doi2bibtex.git
cd doi2bibtex
pip install .
```



### 🔑 Setting up an API key for ADS

> [!NOTE]  
> If you do not want to use ADS, you can disable this feature (which is enabled by default) by setting `resolve_adsurl: false` in your `~/.doi2bibtex/config.yaml` file.

If you want to use the `ads` backend to resolve the `adsurl` field, you need to create an ADS account (if you do not alreay have one) and set up an [API token](https://ui.adsabs.harvard.edu/help/api/) to be able to query ADS. You can actually do this in two different ways:

1. Set the environment variable `ADS_TOKEN` to your API key:
   ```bash
   export ADS_TOKEN="your-token";
   ```
   Ideally, you should add this line to your `.bashrc` or `.zshrc` file.

2. Create a file `~/.doi2bibtex/ads_token` and put your API key in there.


### 💻 Using the command line interface

Once installed, using the package is as simple as running the `d2b` command in your terminal:

```bash
d2b <doi-or-arxiv_id>
```

You can also add the `--plain` flag to output only the BibTeX entry without any fancy formatting. This can be useful if you, for example, want to pipe the output of the `d2b` command to another program.




### ⚙️ Changing the default configuration

A lot of the features of **doi2bibtex** can be configured via a `~/.doi2bibtex/config.yaml` file. Here is an overview of all the supported options (with the default values):

```yaml
abbreviate_journal_names: true  # Convert journal names to LaTeX macros (e.g., "\apj" instead of "The Astrophysical Journal")
citekey_delimiter: '_'          # Delimiter between the author name and the year of publication
convert_latex_chars: true       # Convert LaTeX-encoded characters in author names to Unicode
convert_month_to_number: true   # Convert month names to numbers (e.g., "1" instead of "jan")
crossmatch_with_dblp: false     # [EXPERIMENTAL] Try to crossmatch the paper with DBLP to add venue information to `addendum` (for ML conferences papers)
fix_arxiv_entrytype: true       # Convert arXiv entries to `@article`, set `journal` to "arXiv preprints", and drop the `eprinttype` field
format_author_names: true       # Convert author names to the "{Lastname}, Firstname" format
generate_citekey: true          # Create a citekey based on the first author and year of publication
limit_authors: 1000             # Limit the number of authors in the BibTeX entry
pygments_theme: 'dracula'       # Pygments theme used for syntax highlighting in the terminal
remove_fields:                  # Remove undesired fields (e.g., keywords) from the BibTeX entry
  all: ['abstract']             # Remove the `abstract` from all entries, regardless of entrytype
  article: ['publisher']        # Remove the `publisher` field from @article entries
remove_url_if_doi: true         # Remove the `url` field if it is redundant with the `doi` field
resolve_adsurl: true            # Query ADS to resolve the `adsurl` field, requires API token
update_arxiv_if_doi: true       # Update arXiv entries with DOI information, if available ("related DOI")
```



### ✨ Using the `--clean-references` Feature

The `--clean-references` feature automates the process of cleaning and standardizing the references in `.bib` files for your existing LaTeX projects. It scans `.tex` files for citations, matches them with entries in your `.bib` files, resolves DOIs (if available), and outputs cleaned `.bib` files with consistent formatting.

This feature helps manage large reference libraries by ensuring:
- Missing or inconsistent BibTeX entries in `.bib` files are flagged.
- Resolved DOIs or BibTeX entries are updated and saved cleanly.
- Outputs for resolved and unresolved references are clearly separated.

---

#### **Command Usage**

```bash
d2b --clean-references --tex-dir <path-to-tex-files> --bib-dir <path-to-bib-files> --output-dir <path-to-output>
```

#### **Arguments**

| Argument       | Description                                                                                 |
|----------------|---------------------------------------------------------------------------------------------|
| `--tex-dir`    | Path to the directory containing `.tex` files where references (`\cite`) are located.       |
| `--bib-dir`    | Path to the directory containing `.bib` files to be cleaned and matched.                    |
| `--output-dir` | Path to save the cleaned references and unresolved entries.                                 |

---

#### **What Happens?**

1. **Scans for References**:
   - The tool scans all `.tex` files in `/path/to/my-latex/tex-files` to extract citation keys (e.g., the keys within `\cite{key}`).

2. **Matches Citations**:
   - It looks for matching entries in the `.bib` files stored in `/path/to/my-latex/bib-files`.

3. **Resolves DOIs**:
   - If a DOI (or relevant identifier) is found, it resolves it to its full BibTeX entry.
   - Cleaned BibTeX entries are then saved in a properly formatted `.bib` file.

4. **Handles Unresolved Entries**:
   - Citation keys that cannot be matched or resolved are flagged and saved in a separate `.bib` file.

5. **Generates Output**:
   - **`references_clean.bib`**: Contains all cleaned and resolved BibTeX entries.
   - **`references_unresolved.bib`**: Contains unresolved or unmatched entries for manual review.
   - **`references.bib`**: Combines both resolved and unresolved entries.

---





## 🦄 Features

Besides the eponymous ability of resolving DOIs (and other identifiers) to BibTeX entries, this package offers a lot more features for post-processing the entries. Here are some highlights:

- Automatically resolve the `adsurl` field required by some astrophysics journals (requires an [API token](https://ui.adsabs.harvard.edu/help/api/) for ADS)
- Cross-match entries (in particular: arXiv preprints) with [dblp.org](https://dblp.org/) to retrieve the venue information for conference papers from machine learning (e.g., "ICLR 2021"). Note: This feature is still experimental because querying dblp is somewhat fickle.
- Convert LaTeX-encoded characters in author names to Unicode, for example, `Müller` instead of `M{\"u}ller`
- Author names can automatically be converted to the `{Lastname}, Firstname` format
- You can limit the number of authors in the BibTeX entry
- Create a `citekey` based on the first author and year of publication. The author name is automatically made ASCII-compatible: for example, `Đà Nẵng et al. (2023)` becomes `DaNang_2023`.
- Journal names can automatically be abbreviated according to the common LaTeX macros (e.g., `\apj` instead of `The Astrophysical Journal`)
- Undesired fields (e.g, `keywords`) can be removed from the BibTeX entry (customizable for each `entrytype` — e.g., remove the `publisher` for articles, but keep it for books)
- Easy to extend / modify: Feel free to fork this repository and adjust things to your own needs!



## 🥳 Contributing

Contributions in the form of pull requests are always welcome! Otherwise, you can of course also help the development by creating issues for bugs that you have encountered, or for new features that you would like to see implemented.



## 📃 License

This project is published under a BSD 3-Clause license; see the [LICENSE](LICENSE) file for details.
