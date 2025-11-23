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
   <img src="./assets/demo.gif" width="600" alt="A GIF showing how to use doi2bibtex in the command line">
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



### 🔑 Setting up an API key

You can use an API key either by setting an environment variable and exporting it (`export MY_TOKEN="xxx" d2b`), or by creating a dedicated file in the config directory `~/.doi2bibtex`.

#### ADS

> Environment variable name `ADS_TOKEN` or filename `ads_token`

> [!NOTE]  
> If you do not want to use ADS, you can disable this feature (which is enabled by default) by setting `resolve_adsurl: false` in your `~/.doi2bibtex/config.yaml` file.

If you want to use the `ads` backend to resolve the `adsurl` field, you need to create an ADS account (if you do not alreay have one) and set up an [API token](https://ui.adsabs.harvard.edu/help/api/) to be able to query ADS. You can actually do this in two different ways:

#### Semantic Scholar

> Environment variable name `SEMANTIC_SCHOLAR_API_KEY` or filename `semanticscholar_api_key`


### 💻 Using the command line interface

Once installed, using the package is as simple as running the `d2b` command in your terminal:

```bash
d2b <doi-or-arxiv_id>
```

You can also add the `--plain` flag to output only the BibTeX entry without any fancy formatting. This can be useful if you, for example, want to pipe the output of the `d2b` command to another program.

### 🔍 Search by title

You can search for papers by title using the `--title` flag:

```bash
d2b --title "Attention is all you need"
```

This will search for papers matching the title and display an interactive selection menu where you can browse results and choose the one you want. Add `--first` to automatically select the first result:

```bash
d2b --title "Deep Learning" --first
```

### 🎨 Interactive mode

Launch **doi2bibtex** without any arguments to enter interactive mode:

```bash
d2b
```

This opens an interactive console where you can search by title or DOI, explore potential matches, and retrieve BibTeX citations.
This feature is particularly useful when working with open PDFs where the title is easier to copy than the DOI, since DOIs often are superimposed on papers making them difficult to select, whereas titles are typically plain text. Additionally, since copied titles often span multiple lines due to formatting, it would normally break when pasted into a standard terminal command.

Each search result displays:
- Paper title
- Authors
- Publication year
- Journal/venue
- Abstract

The console also supports pasting images directly, using OCR ([RapidOCR](https://github.com/RapidAI/RapidOCR)) to extract the title automatically.

**Note:** The image is processed only to be converted as plain text. It does not automatically locate the title within a full page. Ensure your image is cropped to focus on the title area.
While automatic title detection is technically feasible ([GROBID](https://github.com/kermitt2/grobid), [VILA](https://github.com/NVlabs/VILA), [CERMINE](https://github.com/CeON/CERMINE), [Moondream2](https://huggingface.co/vikhyatk/moondream2), [Qwen3-VL 2B](https://github.com/QwenLM/Qwen3-VL)), it would require significant computational resources without providing proportional benefits for this project's use case.

### 🌐 Multi-source search

**doi2bibtex** uses multiple academic search APIs to find papers by title. By default, it queries three sources in parallel and merges the results:

1. **OpenAlex** (default)
2. **CrossRef**
3. **Semantic Scholar**

Use the config file to select desired endpoint (default: `search_sources: ["openalex", "crossref"]`)

#### Search modes

The search system can operate in two modes:

- **Parallel mode** (default `merge_search_results: true` in the config): Queries all enabled sources simultaneously, then interleaves results (1st from each source, then 2nd from each, etc.) and removes duplicates by DOI
- **Sequential mode**: Tries sources in order until results are found


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
search_sources: ["openalex", "crossref", "semanticscholar"] # Sources to query when searching articles by title
merge_search_results: true # If true, combines results from all sources; if false, uses sources sequentially until a match is found
openalex_email: "" # OpenAlex email if needed
```



## 🦄 Features

Besides the eponymous ability of resolving DOIs (and other identifiers) to BibTeX entries, this package offers a lot more features:

### Search & Discovery
- **Interactive mode** with title search, DOI lookup, and history navigation
- **OCR support** for extracting research title/DOI text from images 
- **Search by title**
- **Post-processing customization**

### BibTeX post-processing
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
