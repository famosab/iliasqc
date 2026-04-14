"""iliasqc – convert txt files into Ilias-compatible question-pool zip archives."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("iliasqc")
except PackageNotFoundError:  # package is not installed
    __version__ = "unknown"

__all__ = ["__version__"]
