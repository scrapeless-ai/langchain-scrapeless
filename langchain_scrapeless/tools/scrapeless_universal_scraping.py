import os
from typing import Type, Optional, Literal, Any, Dict
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field

from langchain_scrapeless.error_messages import ERROR_SCRAPELESS_TOKEN_ENV_VAR_NOT_SET
from langchain_scrapeless.utils import create_scrapeless_client
from langchain_scrapeless.wrappers import ScrapelessUniversalScrapingAPIWrapper
from scrapeless.client import Scrapeless as ScrapelessClient


class ScrapelessUniversalScrapingInput(BaseModel):
    """Input for Scrapeless Universal Scraping tool."""

    url: str = Field(description="The url of the website to scrape.")

    headless: Optional[bool] = Field(
        default=True,
        description="Whether to use a headless browser.",
    )

    js_render: Optional[bool] = Field(
        default=True, description="Whether to use JavaScript rendering."
    )

    js_wait_until: Optional[
        Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]
    ] = Field(
        default="domcontentloaded",
        description=""" 
          The wait until condition for JavaScript rendering.

          Options include:
          - "load": Wait until the page is fully loaded.
          - "domcontentloaded": Wait until the DOM is fully loaded.
          - "networkidle0": Wait until the network is idle.
          - "networkidle2": Wait until the network is idle for 2 seconds.
        """,
    )

    outputs: Optional[
        Literal[
            "phone_numbers",
            "headings",
            "images",
            "audios",
            "videos",
            "links",
            "menus",
            "hashtags",
            "emails",
            "metadata",
            "tables",
            "favicon",
        ]
    ] = Field(
        default=None,
        description="""
          The outputs to return.
    
          Options include:
          - "phone_numbers": Return phone numbers.
          - "headings": Return headings.
          - "images": Return images.
          - "audios": Return audios.
          - "videos": Return videos.
          - "links": Return links.
          - "menus": Return menus.
          - "hashtags": Return hashtags.
          - "emails": Return emails.
          - "metadata": Return metadata.
          - "tables": Return tables.
          - "favicon": Return favicon.
        """,
    )

    response_type: Optional[Literal["html", "plaintext", "markdown", "png", "jpeg"]] = (
        Field(
            description="""
      The response type.

      Options include:
      - "html": Return the HTML of the page.
      - "plaintext": Return the plain text of the page.
      - "markdown": Return the markdown of the page.
      - "png": Return the PNG image of the page.
      - "jpeg": Return the JPEG image of the page.
      """,
            default="html",
        )
    )

    response_image_full_page: Optional[bool] = Field(
        default=False,
        description="""
      Whether to return the full page image.
      """,
    )

    selector: Optional[str] = Field(
        default=None,
        description="""
      The selector to use for the page.
      """,
    )

    proxy_country: Optional[str] = Field(
        default="ANY",
        description="""
        Two-letter country code for geo-specific access.
        
        Set this when you need to view the website as if accessing from a specific country.
        Example values: "us", "gb", "de", "jp", etc.
        
        Leave as None to use default country routing.
      """,
    )


class ScrapelessUniversalScrapingTool(BaseTool):
    """Tool that runs Scrapeless Universal Scraping API.

    To use, you should have the environment variable `SCRAPELESS_API_KEY` set
    with your API key, or pass `scrapeless_api_key`
    as a named parameter to the constructor.

    For details, see  https://docs.apify.com/platform/integrations/langchain

    Example:
      .. code-block:: python

        from langchain_openai import ChatOpenAI
        from langchain_scrapeless import ScrapelessUniversalScrapingTool
        from langgraph.prebuilt import create_react_agent

        llm = ChatOpenAI()

        tool = ScrapelessUniversalScrapingTool()

        # Use the tool with an agent
        tools = [tool]
        agent = create_react_agent(llm, tools)

        for chunk in agent.stream(
                {"messages": [("human", "Use the scrapeless scraping tool to fetch https://www.scrapeless.com/en and extract the h1 tag.")]},
                stream_mode="values"
        ):
            chunk["messages"][-1].pretty_print()
        )

    """

    name: str = "scrapeless_universal_scraping"
    description: str = (
        "Extract structured data from websites using the Scrapeless Universal Scraping API."
        "Universal Scraping API helps you bypass website blocks in real-time using advanced technology."
        "It includes features like recognizing browser fingerprints, solving CAPTCHAs, rotating IPs,"
        " and intelligently retrying requests. This ensures you can access any public website without interruptions."
        "It supports various scraping methods, excels in rendering JavaScript, and implements anti-scraping techniques,"
        "giving you the tools to navigate the web effectively."
    )

    args_schema: Type[BaseModel] = ScrapelessUniversalScrapingInput
    handle_tool_error: bool = True

    headless: bool = True
    js_render: bool = True
    js_wait_until: Optional[
        Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]
    ] = "domcontentloaded"
    outputs: Optional[
        Literal[
            "phone_numbers",
            "headings",
            "images",
            "audios",
            "videos",
            "links",
            "menus",
            "hashtags",
            "emails",
            "metadata",
            "tables",
            "favicon",
        ]
    ] = None
    response_type: Optional[Literal["html", "plaintext", "markdown", "png", "jpeg"]] = (
        "html"
    )
    response_image_full_page: Optional[bool] = False
    selector: Optional[str] = None
    proxy_country: Optional[str] = "ANY"

    scrapeless_universal_scraping_api_wrapper: ScrapelessUniversalScrapingAPIWrapper = (
        Field(default_factory=ScrapelessUniversalScrapingAPIWrapper)
    )

    def __int__(self, scrapeless_api_key: str | None = None, **kwargs: Any) -> None:
        """Initialize the ScrapelessUniversalScrapingTool.

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
            kwargs["scrapeless_universal_scraping_api_wrapper"] = (
                ScrapelessUniversalScrapingAPIWrapper(
                    scrapeless_api_key=scrapeless_api_key,
                    scrapeless_client=scrapeless_client,
                )
            )

        super().__init__(**kwargs)

    def _run(
            self,
            url: str,
            headless: Optional[bool] = None,
            js_render: Optional[bool] = None,
            js_wait_until: Optional[
                Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]
            ] = None,
            outputs: Optional[
                Literal[
                    "phone_numbers",
                    "headings",
                    "images",
                    "audios",
                    "videos",
                    "links",
                    "menus",
                    "hashtags",
                    "emails",
                    "metadata",
                    "tables",
                    "favicon",
                ]
            ] = None,
            response_type: Optional[
                Literal["html", "plaintext", "markdown", "png", "jpeg"]
            ] = None,
            response_image_full_page: Optional[bool] = None,
            selector: Optional[str] = None,
            proxy_country: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute the Scrapeless Universal Scraping API to scrape a website."""

        try:
            headless_to_use = headless if headless is not None else self.headless
            js_render_to_use = js_render if js_render is not None else self.js_render
            js_wait_until_to_use = (
                js_wait_until if js_wait_until is not None else self.js_wait_until
            )
            outputs_to_use = outputs if outputs is not None else self.outputs
            response_type_to_use = (
                response_type if response_type is not None else self.response_type
            )
            response_image_full_page_to_use = (
                response_image_full_page
                if response_image_full_page is not None
                else self.response_image_full_page
            )
            selector_to_use = selector if selector is not None else self.selector
            proxy_country_to_use = (
                proxy_country if proxy_country is not None else self.proxy_country
            )

            results = self.scrapeless_universal_scraping_api_wrapper.get_page_content(
                url=url,
                headless=headless_to_use,
                js_render=js_render_to_use,
                js_wait_until=js_wait_until_to_use,
                outputs=outputs_to_use,
                response_type=response_type_to_use,
                response_image_full_page=response_image_full_page_to_use,
                selector=selector_to_use,
                proxy_country=proxy_country_to_use,
            )
            return results

        except Exception as e:
            if isinstance(e, ToolException):
                raise e
            raise ValueError(
                f"An error occurred while scraping the URL {url}: {str(e)}"
            )
