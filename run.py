#!/usr/bin/env python
"""
Script to locally execute doi2bibtex
Usage: python run.py <doi-ou-arxiv-id> [--plain]
"""

from doi2bibtex.cli import main

if __name__ == "__main__":
    main()
