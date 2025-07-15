from typing import Type

from langchain_scrapeless.tools import (
    ScrapelessUniversalScrapingTool,
    ScrapelessDeepSerpGoogleSearchTool,
)
from langchain_tests.unit_tests import ToolsUnitTests


def create_tool_test_class(name, tool_cls, example_args):
    class _TestTool(ToolsUnitTests):
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


TestScrapelessTool = create_tool_test_class(
    "TestScrapelessTool",
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

TestGoogleSearchTool = create_tool_test_class(
    "TestGoogleSearchTool",
    ScrapelessDeepSerpGoogleSearchTool,
    {
        "q": "AI news",
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "start": 0,
        "num": 10,
    },
)
