import os
from typing import Any, Dict, List, Literal, Optional, Type

from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field
from scrapeless.client import Scrapeless as ScrapelessClient
from scrapeless.types import CrawlStatusResponse

from langchain_scrapeless.error_messages import ERROR_SCRAPELESS_TOKEN_ENV_VAR_NOT_SET
from langchain_scrapeless.utils import create_scrapeless_client, format_default_value
from langchain_scrapeless.wrappers import (
    ScrapelessCrawlerCrawlAPIWrapper,
)


class ScrapelessCrawlerCrawlInput(BaseModel):
    """Input for Scrapeless Crawler Crawl tool."""

    url: str = Field(description="The base URL to start crawling from")
    limit: Optional[int] = Field(
        description="Maximum number of pages to crawl.", default=10000
    )
    include_paths: Optional[List[str]] = Field(
        description="""
        URL pathname regex patterns that include matching URLs in the crawl. 
        Only the paths that match the specified patterns 
            will be included in the response. 
        For example, if you set 'includePaths': ['blog/.*'] 
            for the base URL firecrawl.dev, 
        only results matching that pattern will be included, 
        such as https://www.scrapeless.com/blog/firecrawl-launch-week-1-recap.
        """,
        default=None,
    )
    exclude_paths: Optional[List[str]] = Field(
        description="""
        URL pathname regex patterns that exclude matching URLs from the crawl. 
        For example, if you set 'excludePaths': ['blog/.*'] 
            for the base URL firecrawl.dev, 
        any results matching that pattern will be excluded, 
        such as https://www.scrapeless.com/blog/firecrawl-launch-week-1-recap.
        """,
        default=None,
    )
    max_depth: Optional[int] = Field(
        description="""
        Maximum depth to crawl relative to the base URL. 
        Basically, the max number of slashes the pathname of a scraped URL may contain.
        """,
        default=10,
    )
    max_discovery_depth: Optional[int] = Field(
        description="""
        Maximum depth to crawl based on discovery order.
        The root site and sitemapped pages has a discovery depth of 0. 
        For example, if you set it to 1, and you set ignoreSitemap, 
        you will only crawl the entered URL and all URLs that are linked on that page.
        """,
        default=None,
    )
    ignore_sitemap: Optional[bool] = Field(
        description="Ignore the website sitemap when crawling", default=False
    )
    ignore_query_params: Optional[bool] = Field(
        description="""
        Do not re-scrape the same path with different (or none) query parameters
        """,
        default=False,
    )
    deduplicate_similar_urls: Optional[bool] = Field(
        description="Controls whether similar URLs should be deduplicated.",
        default=None,
    )
    regex_on_full_url: Optional[bool] = Field(
        description="""
        Controls whether the regular expression should be applied to the full URL.
        """,
        default=None,
    )
    allow_backward_links: Optional[bool] = Field(
        description="""
        By default, the crawl skips sublinks that aren’t 
            part of the URL hierarchy you specify. 
        For example, crawling https://example.com/products/ 
            wouldn’t capture pages under https://example.com/promotions/deal-567. 
        To include such links, enable the allowBackwardLinks parameter.
        """,
        default=False,
    )
    allow_external_links: Optional[bool] = Field(
        description="Allows the crawler to follow links to external websites.",
        default=False,
    )
    delay: Optional[int] = Field(
        description="""
        Delay in seconds between scrapes. 
        This helps respect website rate limits.
        """,
        default=None,
    )

    # Scrape options
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


class ScrapelessCrawlerCrawlTool(BaseTool):
    """Tool that runs Scrapeless Crawler Crawl API.

    To use, you should have the environment variable `SCRAPELESS_API_KEY` set
    with your API key, or pass `scrapeless_api_key`
    as a named parameter to the constructor.

    For details, see  https://docs.apify.com/platform/integrations/langchain

    Example:
      .. code-block:: python

        from langchain_openai import ChatOpenAI
        from langchain_scrapeless import ScrapelessCrawlerCrawlTool
        from langgraph.prebuilt import create_react_agent

        llm = ChatOpenAI()

        tool = ScrapelessCrawlerCrawlTool()

        # Use the tool with an agent
        tools = [tool]
        agent = create_react_agent(llm, tools)

        prompt_text = (
            "Use the scrapeless crawler crawl tool to crawl the website https://example.com\n"
            "and output the markdown content as a string."
        )

        for chunk in agent.stream(
                {"messages": [("human", prompt_text)]},
                stream_mode="values"
        ):
            chunk["messages"][-1].pretty_print()
        )
    """

    name: str = "scrapeless_crawler_crawl"
    description: str = """
     The tool can be used to crawl a website.
     It allows you to get the data you want from web pages with a single call. 
     You can scrape page content and capture its data in various formats.
     It can be used to crawl the content of a single website or a list of websites.
    """

    args_schema: Type[BaseModel] = ScrapelessCrawlerCrawlInput
    handle_tool_error: bool = True

    scrapeless_crawler_api_wrapper: ScrapelessCrawlerCrawlAPIWrapper = Field(
        default_factory=ScrapelessCrawlerCrawlAPIWrapper
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
            kwargs["scrapeless_crawler_api_wrapper"] = ScrapelessCrawlerCrawlAPIWrapper(
                scrapeless_api_key=scrapeless_api_key,
                scrapeless_client=scrapeless_client,
            )

        super().__init__(**kwargs)

    def _run(
        self,
        url: str,
        limit: Optional[int] = 10000,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        max_depth: Optional[int] = 10,
        max_discovery_depth: Optional[int] = None,
        ignore_sitemap: Optional[bool] = False,
        ignore_query_params: Optional[bool] = False,
        deduplicate_similar_urls: Optional[bool] = None,
        regex_on_full_url: Optional[bool] = None,
        allow_backward_links: Optional[bool] = False,
        allow_external_links: Optional[bool] = False,
        delay: Optional[int] = None,
        # Scrape options
        formats: Optional[List[str]] = None,
        only_main_content: Optional[bool] = True,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        wait_for: Optional[int] = 0,
        timeout: Optional[int] = 30000,
    ) -> CrawlStatusResponse:
        """Execute the Scrapeless Crawler Scrape API to scrape a website."""

        try:
            limit_to_use = format_default_value(limit, 10000)
            include_paths_to_use = format_default_value(include_paths, [])
            exclude_paths_to_use = format_default_value(exclude_paths, [])
            max_depth_to_use = format_default_value(max_depth, 10)
            max_discovery_depth_to_use = format_default_value(max_discovery_depth, 5)
            ignore_sitemap_to_use = format_default_value(ignore_sitemap, False)
            ignore_query_params_to_use = format_default_value(
                ignore_query_params, False
            )
            deduplicate_similar_urls_to_use = format_default_value(
                deduplicate_similar_urls, True
            )
            regex_on_full_url_to_use = format_default_value(regex_on_full_url, True)
            allow_backward_links_to_use = format_default_value(
                allow_backward_links, False
            )
            allow_external_links_to_use = format_default_value(
                allow_external_links, False
            )
            delay_to_use = format_default_value(delay, 1)
            formats_to_use = format_default_value(formats, ["markdown"])
            only_main_content_to_use = format_default_value(only_main_content, True)
            include_tags_to_use = format_default_value(include_tags, [])
            exclude_tags_to_use = format_default_value(exclude_tags, [])
            headers_to_use = format_default_value(headers, {})
            wait_for_to_use = format_default_value(wait_for, 0)
            timeout_to_use = format_default_value(timeout, 30000)

            results = self.scrapeless_crawler_api_wrapper.crawl_results(
                url=url,
                limit=limit_to_use,
                include_paths=include_paths_to_use,
                exclude_paths=exclude_paths_to_use,
                max_depth=max_depth_to_use,
                max_discovery_depth=max_discovery_depth_to_use,
                ignore_sitemap=ignore_sitemap_to_use,
                ignore_query_params=ignore_query_params_to_use,
                deduplicate_similar_urls=deduplicate_similar_urls_to_use,
                regex_on_full_url=regex_on_full_url_to_use,
                allow_backward_links=allow_backward_links_to_use,
                allow_external_links=allow_external_links_to_use,
                delay=delay_to_use,
                # Scrape options
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
                f"An error occurred while crawling the url {url}: {str(e)}"
            )
