from importlib import metadata

from langchain_scrapeless.tools.scrapeless_universal_scraping import ScrapelessUniversalScrapingTool
from langchain_scrapeless.wrappers import ScrapelessAPIWrapper, ScrapelessUniversalScrapingAPIWrapper

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "ScrapelessUniversalScrapingTool",
    "ScrapelessAPIWrapper",
    "ScrapelessUniversalScrapingAPIWrapper",
    "__version__",
]
