from typing import Type

from langchain_scrapeless.tools import (
    ScrapelessUniversalScrapingTool,
    ScrapelessDeepSerpGoogleSearchTool,
    ScrapelessDeepSerpGoogleTrendsTool,
    ScrapelessCrawlerScrapeTool,
    ScrapelessCrawlerCrawlTool,
)
from langchain_tests.integration_tests import ToolsIntegrationTests


def create_tool_test_class(name, tool_cls, example_args):
    class _TestTool(ToolsIntegrationTests):
        @property
        def tool_constructor(self):
            return tool_cls

        @property
        def tool_constructor_params(self):
            return {}

        @property
        def tool_invoke_params_example(self):
            return example_args

    _TestTool.__name__ = name
    return _TestTool


TestScrapelessUniversalScrapingTool = create_tool_test_class(
    "TestScrapelessUniversalScrapingTool",
    ScrapelessUniversalScrapingTool,
    {
        "url": "https://example.com",
        "headless": True,
        "js_render": True,
        "js_wait_until": "domcontentloaded",
        "outputs": None,
        "response_type": "html",
        "response_image_full_page": False,
        "selector": None,
        "proxy_country": "ANY",
    },
)

TestScrapelessDeepSerpGoogleSearchTool = create_tool_test_class(
    "TestScrapelessDeepSerpGoogleSearchTool",
    ScrapelessDeepSerpGoogleSearchTool,
    {
        "q": "AI news",
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "start": 0,
        "num": 10,
        "ludocid": None,
        "kgmid": None,
        "ibp": None,
        "cr": None,
        "lr": None,
        "tbs": None,
        "safe": None,
        "nfpr": None,
        "filter": None,
        "tbm": None,
    },
)

#
TestScrapelessDeepSerpGoogleTrendsTool = create_tool_test_class(
    "TestScrapelessDeepSerpGoogleTrendsTool",
    ScrapelessDeepSerpGoogleTrendsTool,
    {
        "q": "AI news",
        "data_type": "interest_over_time",
        "date": "today 1-m",
        "hl": "en",
        "tz": "420",
        "geo": "US",
        "cat": "0",
    },
)

TestScrapelessCrawlerScrapeTool = create_tool_test_class(
    "TestScrapelessCrawlerScrapeTool",
    ScrapelessCrawlerScrapeTool,
    {
        "urls": ["https://example.com"],
        "formats": ["markdown"],
        "only_main_content": True,
        "include_tags": None,
        "exclude_tags": None,
        "headers": None,
        "wait_for": 0,
        "timeout": 30000,
    },
)

TestScrapelessCrawlerCrawlTool = create_tool_test_class(
    "TestScrapelessCrawlerCrawlTool",
    ScrapelessCrawlerCrawlTool,
    {
        "url": "https://example.com",
        "limit": 10000,
        "include_paths": None,
        "exclude_paths": None,
        "max_depth": 10,
        "max_discovery_depth": None,
        "ignore_sitemap": False,
        "ignore_query_params": False,
        "deduplicate_similar_urls": None,
        "regex_on_full_url": None,
        "allow_backward_links": False,
        "allow_external_links": False,
        "delay": None,
        "formats": ["markdown"],
        "only_main_content": True,
        "include_tags": None,
        "exclude_tags": None,
        "headers": None,
        "wait_for": 0,
        "timeout": 30000,
    },
)
