import os
from typing import Type, Optional, Literal, Any, Dict
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field

from langchain_scrapeless.error_messages import ERROR_SCRAPELESS_TOKEN_ENV_VAR_NOT_SET
from langchain_scrapeless.utils import create_scrapeless_client
from langchain_scrapeless.wrappers import (
    ScrapelessDeepSerpAPIWrapper,
)
from scrapeless.client import Scrapeless as ScrapelessClient


class ScrapelessGoogleSearchInput(BaseModel):
    """Input for Scrapeless DeepSerp Google Search tool."""

    q: str = Field(
        description="Parameter defines the query you want to search. You can use anything that you would use in a regular Google search. e.g. inurl:, site:, intitle:. We also support advanced search query parameters such as as_dt and as_eq."
    )
    hl: Optional[str] = Field(
        default="en",
        description="Parameter defines the language to use for the Google search. It's a two-letter language code. (e.g., en for English, es for Spanish, or fr for French).",
    )
    gl: Optional[str] = Field(
        default="us",
        description="Parameter defines the country to use for the Google search. It's a two-letter country code. (e.g., us for the United States, uk for United Kingdom, or fr for France).",
    )
    google_domain: Optional[
        Literal[
            "google.com",
            "google.ad",
            "google.ae",
            "google.com.af",
            "google.com.ag",
            "google.com.ai",
            "google.al",
            "google.am",
            "google.co.ao",
            "google.com.ar",
            "google.as",
            "google.at",
            "google.com.au",
            "google.az",
            "google.ba",
            "google.com.bd",
            "google.be",
            "google.bf",
            "google.bg",
            "google.com.bh",
            "google.bi",
            "google.bj",
            "google.com.bn",
            "google.com.bo",
            "google.com.br",
            "google.bs",
            "google.bt",
            "google.co.bw",
            "google.by",
            "google.com.bz",
            "google.ca",
            "google.com.kh",
            "google.cd",
            "google.cf",
            "google.cg",
            "google.ch",
            "google.ci",
            "google.co.ck",
            "google.cl",
            "google.cm",
            "google.com.co",
            "google.co.cr",
            "google.com.cu",
            "google.cv",
            "google.com.cy",
            "google.cz",
            "google.de",
            "google.dj",
            "google.dk",
            "google.dm",
            "google.com.do",
            "google.dz",
            "google.com.ec",
            "google.ee",
            "google.com.eg",
            "google.es",
            "google.com.et",
            "google.fi",
            "google.fm",
            "google.com.fj",
            "google.fr",
            "google.ga",
            "google.ge",
            "google.com.gh",
            "google.com.gi",
            "google.gl",
            "google.gm",
            "google.gp",
            "google.gr",
            "google.com.gt",
            "google.gy",
            "google.com.hk",
            "google.hn",
            "google.hr",
            "google.ht",
            "google.hu",
            "google.co.id",
            "google.iq",
            "google.ie",
            "google.co.il",
            "google.co.in",
            "google.is",
            "google.it",
            "google.je",
            "google.com.jm",
            "google.jo",
            "google.co.jp",
            "google.co.ke",
            "google.ki",
            "google.kg",
            "google.co.kr",
            "google.com.kw",
            "google.kz",
            "google.la",
            "google.com.lb",
            "google.li",
            "google.lk",
            "google.co.ls",
            "google.lt",
            "google.lu",
            "google.lv",
            "google.com.ly",
            "google.co.ma",
            "google.md",
            "google.mg",
            "google.mk",
            "google.ml",
            "google.com.mm",
            "google.mn",
            "google.ms",
            "google.com.mt",
            "google.mu",
            "google.mv",
            "google.mw",
            "google.com.mx",
            "google.com.my",
            "google.co.mz",
            "google.com.na",
            "google.ne",
            "google.com.ng",
            "google.com.ni",
            "google.nl",
            "google.no",
            "google.com.np",
            "google.nr",
            "google.nu",
            "google.co.nz",
            "google.com.om",
            "google.com.pk",
            "google.com.pa",
            "google.com.pe",
            "google.com.ph",
            "google.pl",
            "google.com.pg",
            "google.com.pr",
            "google.ps",
            "google.pt",
            "google.com.py",
            "google.com.qa",
            "google.ro",
            "google.rs",
            "google.ru",
            "google.rw",
            "google.com.sa",
            "google.com.sb",
            "google.sc",
            "google.se",
            "google.com.sg",
            "google.sh",
            "google.si",
            "google.sk",
            "google.com.sl",
            "google.sn",
            "google.sm",
            "google.so",
            "google.sr",
            "google.com.sv",
            "google.td",
            "google.tg",
            "google.co.th",
            "google.com.tj",
            "google.tk",
            "google.tl",
            "google.tm",
            "google.to",
            "google.tn",
            "google.com.tr",
            "google.tt",
            "google.com.tw",
            "google.co.tz",
            "google.com.ua",
            "google.co.ug",
            "google.co.uk",
            "google.com.uy",
            "google.co.uz",
            "google.com.vc",
            "google.co.ve",
            "google.vg",
            "google.co.vi",
            "google.com.vn",
            "google.vu",
            "google.ws",
            "google.co.za",
            "google.co.zm",
            "google.co.zw",
        ]
    ] = Field(
        default="google.com",
        description="Parameter defines the Google domain to use. It defaults to google.com.",
    )
    start: Optional[int] = Field(
        default=0,
        description="""
    Parameter defines the result offset. It skips the given number of results. 
    It's used for pagination. (e.g., 0 (default) is the first page of results, 
    10 is the 2nd page of results, 20 is the 3rd page of results, etc.).
    """,
    )
    num: Optional[int] = Field(
        default=10,
        description="""
        Parameter defines the maximum number of results to return. 
        (e.g., 10 (default) returns 10 results, 40 returns 40 results, and 100 returns 100 results).
        """,
    )

    ludocid: Optional[str] = Field(
        default=None,
        description="""
        Parameter defines the id (CID) of the Google My Business listing you want to scrape. 
        Also known as Google Place ID.
        """,
    )

    kgmid: Optional[str] = Field(
        default=None,
        description="""
        Parameter defines the id (KGMID) of the Google Knowledge Graph listing you want to scrape. 
        Also known as Google Knowledge Graph ID. Searches with kgmid parameter will return results 
        for the originally encrypted search parameters. For some searches, kgmid may override 
        all other parameters except start, and num parameters.
        """,
    )

    ibp: Optional[str] = Field(
        default=None,
        description="""
        Parameter is responsible for rendering layouts and expansions for some elements 
        (e.g., gwp;0,7 to expand searches with ludocid for expanded knowledge graph).
        """,
    )

    cr: Optional[str] = Field(
        default=None,
        description="""
        Parameter defines one or multiple countries to limit the search to. 
        It uses country{two-letter upper-case country code} to specify countries and | as a delimiter. 
        (e.g., countryFR|countryDE will only search French and German pages).
        """,
    )

    lr: Optional[str] = Field(
        default=None,
        description="""
        Parameter defines one or multiple languages to limit the search to. 
        It uses lang_{two-letter language code} to specify languages and | as a delimiter. 
        (e.g., lang_fr|lang_de will only search French and German pages).
        """,
    )

    tbs: Optional[str] = Field(
        default=None,
        description="""
        (to be searched) parameter defines advanced search parameters that aren't possible 
        in the regular query field. (e.g., advanced search for patents, dates, news, videos, images, apps, or text contents).
        """,
    )

    safe: Optional[Literal["active", "off"]] = Field(
        default=None,
        description="""
        Parameter defines the level of filtering for adult content. 
        It can be set to active or off, by default Google will blur explicit content.
        """,
    )

    nfpr: Optional[Literal["1", "0"]] = Field(
        default=None,
        description="""
        Parameter defines the exclusion of results from an auto-corrected query 
        when the original query is spelled wrong. It can be set to 1 to exclude these results, 
        or 0 to include them (default). Note that this parameter may not prevent Google 
        from returning results for an auto-corrected query if no other results are available.
        """,
    )

    filter: Optional[Literal["1", "0"]] = Field(
        default=None,
        description="""
        Parameter defines if the filters for 'Similar Results' and 'Omitted Results' are on or off. 
        It can be set to 1 (default) to enable these filters, or 0 to disable these filters.
        """,
    )

    tbm: Optional[Literal["isch", "lcl", "nws", "shop", "vid", "pts", "jobs"]] = Field(
        default=None,
        description="""
        (to be matched) parameter defines the type of search you want to do.

        It can be set to:
        - (no tbm parameter): regular Google Search
        - isch: Google Images API
        - lcl: Google Local API
        - vid: Google Videos API
        - nws: Google News API
        - shop: Google Shopping API
        - pts: Google Patents API
        - jobs: Google Jobs API
        or any other Google service.
        """,
    )


class ScrapelessDeepSerpGoogleSearchTool(BaseTool):
    """Tool that runs Scrapeless DeepSerp Google Search API.

    To use, you should have the environment variable `SCRAPELESS_API_KEY` set
    with your API key, or pass `scrapeless_api_key`
    as a named parameter to the constructor.

    For details, see  https://docs.apify.com/platform/integrations/langchain

    Example:
      .. code-block:: python

        from langchain_openai import ChatOpenAI
        from langchain_scrapeless import ScrapelessDeepSerpGoogleSearchTool
        from langgraph.prebuilt import create_react_agent

        llm = ChatOpenAI()

        tool = ScrapelessDeepSerpGoogleSearchTool()

        # Use the tool with an agent
        tools = [tool]
        agent = create_react_agent(llm, tools)

        for chunk in agent.stream(
                {"messages": [("human", "I want to what is Scrapeless")]},
                stream_mode="values"
        ):
            chunk["messages"][-1].pretty_print()

    """

    name: str = "scrapeless_deepserp_google_search"
    description: str = (
        "Universal Information Search Engine.Retrieves any data information; Explanatory queries (why, how).Comparative analysis requests"
    )

    args_schema: Type[BaseModel] = ScrapelessGoogleSearchInput
    handle_tool_error: bool = True

    scrapeless_deepserp_api_wrapper: ScrapelessDeepSerpAPIWrapper = Field(
        default_factory=ScrapelessDeepSerpAPIWrapper
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
            kwargs["scrapeless_deepserp_api_wrapper"] = ScrapelessDeepSerpAPIWrapper(
                scrapeless_api_key=scrapeless_api_key,
                scrapeless_client=scrapeless_client,
            )

        super().__init__(**kwargs)

    def _run(
        self,
        q: str,
        hl: Optional[str] = "en",
        gl: Optional[str] = "us",
        google_domain: Optional[str] = "google.com",
        start: Optional[int] = 0,
        num: Optional[int] = 10,
        ludocid: Optional[str] = None,
        kgmid: Optional[str] = None,
        ibp: Optional[str] = None,
        cr: Optional[str] = None,
        lr: Optional[str] = None,
        tbs: Optional[str] = None,
        safe: Optional[Literal["active", "off"]] = None,
        nfpr: Optional[Literal["1", "0"]] = None,
        filter: Optional[Literal["1", "0"]] = None,
        tbm: Optional[
            Literal["isch", "lcl", "nws", "shop", "vid", "pts", "jobs"]
        ] = None,
    ) -> Dict[str, Any]:
        """Execute the Scrapeless Universal Scraping API to scrape a website."""

        try:
            results = self.scrapeless_deepserp_api_wrapper.get_google_search_results(
                q=q,
                hl=hl,
                gl=gl,
                google_domain=google_domain,
                start=start,
                num=num,
                ludocid=ludocid,
                kgmid=kgmid,
                ibp=ibp,
                cr=cr,
                lr=lr,
                tbs=tbs,
                safe=safe,
            )
            return results

        except Exception as e:
            if isinstance(e, ToolException):
                raise e
            raise ValueError(
                f"An error occurred while scraping the query {q}: {str(e)}"
            )
