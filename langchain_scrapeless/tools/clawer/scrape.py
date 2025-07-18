import os
from typing import Any, Dict, List, Literal, Optional, Type

from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field
from scrapeless.client import Scrapeless as ScrapelessClient

from langchain_scrapeless.error_messages import ERROR_SCRAPELESS_TOKEN_ENV_VAR_NOT_SET
from langchain_scrapeless.utils import create_scrapeless_client, format_default_value
from langchain_scrapeless.wrappers import (
    ScrapelessCrawlerScrapeAPIWrapper,
)


class ScrapelessCrawlerScrapeInput(BaseModel):
    """Input for Scrapeless Crawler Scrape tool."""

    urls: List[str] = Field(description="The url or urls of the websites to scrape.")
    formats: Optional[
        List[
            Literal[
                "markdown",
                "rawHtml",
                "screenshot@fullPage",
                "json",
                "links",
                "screenshot",
                "html",
            ]
        ]
    ] = Field(description="The format of the output.", default=["markdown"])
    only_main_content: Optional[bool] = Field(
        description="""
        Only return the main content of the page 
        excluding headers, navs, footers, etc.
        """,
        default=True,
    )
    include_tags: Optional[List[str]] = Field(
        description="The tags to include in the output.", default=None
    )
    exclude_tags: Optional[List[str]] = Field(
        description="The tags to exclude in the output.",
        default=None,
    )
    headers: Optional[Dict[str, str]] = Field(
        description="""
        The headers to send with the request. 
        Can be used to send cookies, user-agent, etc.
        """,
        default=None,
    )
    wait_for: Optional[int] = Field(
        description="""
        Specify a delay in milliseconds before fetching the content, 
        allowing the page sufficient time to load.
        """,
        default=0,
    )
    timeout: Optional[int] = Field(
        description="Timeout in milliseconds for the request", default=30000
    )


class ScrapelessCrawlerScrapeTool(BaseTool):
    """Tool that runs Scrapeless Crawler Scrape API.

    To use, you should have the environment variable `SCRAPELESS_API_KEY` set
    with your API key, or pass `scrapeless_api_key`
    as a named parameter to the constructor.

    For details, see  https://docs.apify.com/platform/integrations/langchain

    Example:
      .. code-block:: python

        from langchain_openai import ChatOpenAI
        from langchain_scrapeless import ScrapelessCrawlerScrapeTool
        from langgraph.prebuilt import create_react_agent

        llm = ChatOpenAI()

        tool = ScrapelessCrawlerScrapeTool()

        # Use the tool with an agent
        tools = [tool]
        agent = create_react_agent(llm, tools)

        prompt_text = (
            "Use the scrapeless crawler scrape tool to get the website content of https://example.com\n"
            "and output the html content as a string."
        )

        for chunk in agent.stream(
                {"messages": [("human", prompt_text)]},
                stream_mode="values"
        ):
            chunk["messages"][-1].pretty_print()
        )


    """

    name: str = "scrapeless_crawler_scrape"
    description: str = """
     The tool can be used to scrape the content of a website.
     It allows you to get the data you want from web pages with a single call. 
     You can scrape page content and capture its data in various formats.
     It can be used to scrape the content of a single website or a list of websites.
    """

    args_schema: Type[BaseModel] = ScrapelessCrawlerScrapeInput
    handle_tool_error: bool = True

    scrapeless_crawler_api_wrapper: ScrapelessCrawlerScrapeAPIWrapper = Field(
        default_factory=ScrapelessCrawlerScrapeAPIWrapper
    )

    def __int__(self, scrapeless_api_key: str | None = None, **kwargs: Any) -> None:
        """Initialize the ScrapelessCrawlerScrapeTool.

        Args:
            scrapeless_api_key: The API key for the Scrapeless API.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If the `SCRAPELESS_API_KEY` environment variable is not set.
        """

        scrapeless_api_key = scrapeless_api_key or os.getenv("SCRAPELESS_API_KEY")
        if not scrapeless_api_key:
            msg = ERROR_SCRAPELESS_TOKEN_ENV_VAR_NOT_SET
            raise ValueError(msg)

        scrapeless_client = create_scrapeless_client(
            ScrapelessClient, scrapeless_api_key
        )

        if "scrapeless_api_key" in kwargs:
            kwargs["scrapeless_crawler_api_wrapper"] = (
                ScrapelessCrawlerScrapeAPIWrapper(
                    scrapeless_api_key=scrapeless_api_key,
                    scrapeless_client=scrapeless_client,
                )
            )

        super().__init__(**kwargs)

    def _run(
        self,
        urls: List[str],
        formats: Optional[List[str]] = None,
        only_main_content: Optional[bool] = True,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        wait_for: Optional[int] = 0,
        timeout: Optional[int] = 30000,
    ) -> Dict[str, Any]:
        """Execute the Scrapeless Crawler Scrape API to scrape a website."""

        try:
            formats_to_use = format_default_value(formats, ["markdown"])
            only_main_content_to_use = format_default_value(only_main_content, True)
            include_tags_to_use = format_default_value(include_tags, [])
            exclude_tags_to_use = format_default_value(exclude_tags, [])
            headers_to_use = format_default_value(headers, {})
            wait_for_to_use = format_default_value(wait_for, 0)
            timeout_to_use = format_default_value(timeout, 30000)

            results = self.scrapeless_crawler_api_wrapper.scrape_results(
                urls=urls,
                formats=formats_to_use,
                only_main_content=only_main_content_to_use,
                include_tags=include_tags_to_use,
                exclude_tags=exclude_tags_to_use,
                headers=headers_to_use,
                wait_for=wait_for_to_use,
                timeout=timeout_to_use,
            )
            return results

        except Exception as e:
            if isinstance(e, ToolException):
                raise e
            raise ValueError(
                f"An error occurred while scraping the urls {urls}: {str(e)}"
            )
