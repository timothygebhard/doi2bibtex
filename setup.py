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
    name='doi2bibtex',
    version='0.1.0',
    author='Timothy Gebhard',
    url='https://github.com/timothygebhard/doi2bib',
    description='doi2bibtex: Get BibTeX entries from a DOI or arXiv ID',
    install_requires=[
        'ads',
        'beautifulsoup4',
        'bibtexparser',
        'pylatexenc',
        'pyyaml',
        'requests',
        'rich',
        'unidecode',
    ],
    extras_require={
        'develop': [
            'coverage',
            'deepdiff',
            'flake8',
            'mypy',
            'pytest',
            'pytest-cov',
            'pytest-mock',
            'types-beautifulsoup4',
            'types-PyYAML',
            'types-requests',
            'types-setuptools',
        ]
    },
    entry_points={
        'console_scripts': [
            'd2b = doi2bibtex.cli:main',
        ],
    },
    packages=find_packages(),
    zip_safe=False,
)
