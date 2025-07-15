from typing import Type

from langchain_scrapeless.tools import ScrapelessUniversalScrapingTool
from langchain_tests.unit_tests import ToolsUnitTests


class TestParrotMultiplyToolUnit(ToolsUnitTests):
    @property
    def tool_constructor(self) -> Type[ScrapelessUniversalScrapingTool]:
        return ScrapelessUniversalScrapingTool

    @property
    def tool_constructor_params(self) -> dict:
        # if your tool constructor instead required initialization arguments like
        # `def __init__(self, some_arg: int):`, you would return those here
        # as a dictionary, e.g.: `return {'some_arg': 42}`
        return {}

    @property
    def tool_invoke_params_example(self) -> dict:
        """
        Returns a dictionary representing the "args" of an example tool call.

        This should NOT be a ToolCall dict - i.e. it should not
        have {"name", "id", "args"} keys.
        """
        return {
            "url": "https://example.com",
            "headless": True,
            "js_render": True,
            "js_wait_until": "domcontentloaded",
            "outputs": None,
            "response_type": "html",
            "response_image_full_page": False,
            "selector": None,
            "proxy_country": "ANY",
        }
