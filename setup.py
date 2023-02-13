"""
Setup script to install `doi2bibtex` as a Python package.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from setuptools import find_packages, setup


# -----------------------------------------------------------------------------
# RUN setup() FUNCTION
# -----------------------------------------------------------------------------

# Run setup()
setup(
    name="doi2bibtex",
    author="Timothy Gebhard",
    url="https://github.com/timothygebhard/doi2bib",
    description=(
        "Resolve DOIs and arXiv identifiers to formatted BibTeX entries"
    ),
    long_description=(
        "See [project homepage](https://github.com/timothygebhard/doi2bib) "
        "for more information."
    ),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    install_requires=[
        "ads",
        "beautifulsoup4",
        "bibtexparser",
        "pylatexenc",
        "pyyaml",
        "requests",
        "rich",
        "unidecode",
    ],
    extras_require={
        "develop": [
            "coverage",
            "deepdiff",
            "flake8",
            "mypy",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "types-beautifulsoup4",
            "types-PyYAML",
            "types-requests",
            "types-setuptools",
        ]
    },
    entry_points={
        "console_scripts": [
            "d2b = doi2bibtex.cli:main",
        ],
    },
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(),
    zip_safe=False,
)
