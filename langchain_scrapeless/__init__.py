from importlib import metadata

from langchain_scrapeless.tools.clawer import (
    ScrapelessCrawlerCrawlTool,
    ScrapelessCrawlerScrapeTool,
)
from langchain_scrapeless.tools.scrapeless_universal_scraping import (
    ScrapelessUniversalScrapingTool,
)
from langchain_scrapeless.tools.scraping_api import (
    ScrapelessDeepSerpGoogleSearchTool,
    ScrapelessDeepSerpGoogleTrendsTool,
)
from langchain_scrapeless.wrappers import (
    ScrapelessAPIWrapper,
    ScrapelessCrawlerCrawlAPIWrapper,
    ScrapelessCrawlerScrapeAPIWrapper,
    ScrapelessDeepSerpAPIWrapper,
    ScrapelessUniversalScrapingAPIWrapper,
)

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "ScrapelessDeepSerpGoogleSearchTool",
    "ScrapelessDeepSerpGoogleTrendsTool",
    "ScrapelessUniversalScrapingTool",
    "ScrapelessAPIWrapper",
    "ScrapelessUniversalScrapingAPIWrapper",
    "ScrapelessCrawlerScrapeAPIWrapper",
    "ScrapelessCrawlerCrawlAPIWrapper",
    "ScrapelessDeepSerpAPIWrapper",
    "ScrapelessCrawlerScrapeTool",
    "ScrapelessCrawlerCrawlTool",
    "__version__",
]
