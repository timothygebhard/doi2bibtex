from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("doi2bibtex")
except PackageNotFoundError:
    __version__ = "unknown version"
