import math
import time
from typing import Any, Dict, List, Literal, Optional

from langchain_core.tools import ToolException
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from scrapeless import Scrapeless
from scrapeless.types import (
    CrawlParams,
    CrawlStatusResponse,
    ScrapeParams,
    ScrapingTaskRequest,
    UniversalScrapingRequest,
)

from langchain_scrapeless.utils import create_scrapeless_client

# Base API URL for Scrapeless
SCRAPELESS_API_URL = "https://api.scrapeless.com"


class ScrapelessAPIWrapper(BaseModel):
    """Base wrapper for Scrapeless API."""

    model_config = ConfigDict(arbitrary_types_allowed=True, hide_input_in_errors=True)

    scrapeless_api_key: SecretStr | None = Field(default=None, exclude=True, repr=False)
    scrapeless_client: Scrapeless = Field(exclude=True, repr=False)

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        """Validate that API key exists in environment.

        Args:
            values (Dict): The values to validate.

        Returns:
            Dict: Updated values with API key.
        """
        scrapeless_api_key = get_from_dict_or_env(
            values, "scrapeless_api_key", "SCRAPELESS_API_KEY"
        )

        if not scrapeless_api_key:
            raise ValueError("Scrapeless API key must be provided.")

        secret = (
            scrapeless_api_key
            if isinstance(scrapeless_api_key, SecretStr)
            else SecretStr(scrapeless_api_key)
        )
        values["scrapeless_api_key"] = secret
        values["scrapeless_client"] = create_scrapeless_client(
            Scrapeless, secret.get_secret_value()
        )

        return values


class ScrapelessUniversalScrapingAPIWrapper(ScrapelessAPIWrapper):
    """Wrapper for Scrapeless Universal Scraping API.

    This wrapper can be used with the Scrapeless Universal Scraping scenarios.
    """

    def get_page_content(
        self,
        url: str,
        headless: Optional[bool] = True,
        js_render: Optional[bool] = True,
        js_wait_until: Optional[
            Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]
        ] = "domcontentloaded",
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
        ] = "html",
        response_image_full_page: Optional[bool] = False,
        selector: Optional[str] = None,
        proxy_country: Optional[str] = "ANY",
    ) -> Dict:
        """Get the content of a page.

        Args:
            url (str): The URL of the page to scrape.
            headless (bool): Whether to use a headless browser.
            js_render (bool): Whether to use JavaScript rendering.
            js_wait_until (Optional[Literal[
                "load", "domcontentloaded", "networkidle0", "networkidle2"
            ]]): The wait until condition for JavaScript rendering.
            outputs (Optional[Literal[
                "phone_numbers", "headings", "images", "audios", "videos", "links",
                "menus", "hashtags", "emails", "metadata", "tables", "favicon"
            ]]): The outputs to return.
            response_type (Optional[Literal[
                "html", "plaintext", "markdown", "png", "jpeg"
            ]]): The response type.
            response_image_full_page (Optional[bool]):
                Whether to return the full page image.
            selector (Optional[str]): The selector to use for the page.
            proxy_country (Optional[str]): The proxy country to use for the request.
        """

        data = UniversalScrapingRequest(
            actor="unlocker.webunlocker",
            input={
                "url": url,
                "headless": headless,
                "js_render": js_render,
                "js_wait_until": js_wait_until,
                "outputs": outputs,
                "selector": selector,
                "response_type": response_type,
            },
            proxy={
                "country": proxy_country,
            },
        )

        # only when the response_type is png or jpeg add the response_image_full_page
        if response_type in ["png", "jpeg"]:
            data.input["response_image_full_page"] = response_image_full_page

        response = self.scrapeless_client.universal.scrape(data)
        return response


class ScrapelessDeepSerpAPIWrapper(ScrapelessAPIWrapper):
    """Wrapper for Scrapeless DeepSerp API.

    This wrapper can be used with the Scrapeless DeepSerp scenarios.
    """

    def scrape_results(self, data: ScrapingTaskRequest) -> Dict:
        response = self.scrapeless_client.scraping.scrape(data)
        return response

    def get_google_search_results(
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
    ) -> Dict:
        """Get the content of a page.

        Args:
             q (str): The query to search for.
             hl (Optional[str]): The language to use for the search.
             gl (Optional[str]): The country to use for the search.
             google_domain (Optional[str]): The domain to use for the search.
             start (Optional[int]): The start index for the search.
             num (Optional[int]): The number of results to return.
             ludocid (Optional[str]): The ludocid to use for the search.
             kgmid (Optional[str]): The kgmid to use for the search.
             ibp (Optional[str]): The ibp to use for the search.
             cr (Optional[str]): The cr to use for the search.
             lr (Optional[str]): The lr to use for the search.
             tbs (Optional[str]): The tbs to use for the search.
             safe (Optional[Literal[
                 "active", "off"
             ]]): The safe to use for the search.
             nfpr (Optional[Literal[
                 "1", "0"
             ]]): The nfpr to use for the search.
             filter (Optional[Literal[
                 "1", "0"
             ]]): The filter to use for the search.
             tbm (Optional[Literal[
                 "isch", "lcl", "nws", "shop", "vid", "pts", "jobs"
             ]]): The tbm to use for the search.
        """

        data = ScrapingTaskRequest(
            actor="scraper.google.search",
            input={
                "q": q,
                "hl": hl,
                "gl": gl,
                "google_domain": google_domain,
                "start": start,
                "num": num,
                "ludocid": ludocid,
                "kgmid": kgmid,
                "ibp": ibp,
                "cr": cr,
                "lr": lr,
                "tbs": tbs,
                "safe": safe,
                "nfpr": nfpr,
                "filter": filter,
                "tbm": tbm,
            },
        )

        response = self.scrape_results(data)
        return response

    def get_google_trends_results(
        self,
        q: str,
        data_type: Optional[
            Literal[
                "autocomplete",
                "interest_over_time",
                "compared_breakdown_by_region",
                "interest_by_subregion",
                "related_queries",
                "related_topics",
            ]
        ] = "interest_over_time",
        date: Optional[str] = "today 1-m",
        hl: Optional[str] = "en",
        tz: Optional[str] = "420",
        geo: Optional[str] = None,
        cat: Optional[str] = None,
    ) -> Dict:
        """Get the content of a page.

        Args:
            q (str): The query to search for.
            data_type (Optional[Literal[
                "autocomplete", "interest_over_time",
                "compared_breakdown_by_region", "interest_by_subregion",
                "related_queries", "related_topics"
            ]]): The data type to use for the search.
            date (Optional[str]): The date to use for the search.
            hl (Optional[str]): The language to use for the search.
            tz (Optional[str]): The time zone to use for the search.
            geo (Optional[str]): The geo to use for the search.
            cat (Optional[str]): The category to use for the search.
        """

        data = ScrapingTaskRequest(
            actor="scraper.google.trends",
            input={
                "q": q,
                "data_type": data_type,
                "date": date,
                "hl": hl,
                "tz": tz,
                "geo": geo,
                "cat": cat,
            },
        )

        response = self.scrape_results(data)
        return response


class ScrapelessCrawlerScrapeAPIWrapper(ScrapelessAPIWrapper):
    """Wrapper for Scrapeless Crawler Scrape API.

    This wrapper can be used with the Scrapeless Crawler Scrape scenarios.
    """

    def scrape_results(
        self,
        urls: List[str],
        formats: Optional[List[str]] = ["markdown"],
        only_main_content: Optional[bool] = True,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        wait_for: Optional[int] = 0,
        timeout: Optional[int] = 30000,
        poll_timeout: float = 180,
    ) -> Dict:
        """Scrape the results from the URLs.

        Args:
             urls (List[str]): The URLs to scrape.
             format (Optional[Literal[
                 "markdown", "rawHtml", "screenshot@fullPage",
                 "json", "links", "screenshot", "html"
             ]]): The format of the output.
             only_main_content (Optional[bool]):
                 Whether to only return the main content of the page.
             include_tags (Optional[List[str]]):
                 The tags to include in the output.
             exclude_tags (Optional[List[str]]):
                 The tags to exclude in the output.
             headers (Optional[Dict[str, str]]):
                 The headers to send with the request.
             wait_for (Optional[int]):
                 The number of milliseconds to wait for the page to load.
             timeout (Optional[int]):
                 The timeout in milliseconds for the request.
        """

        if not math.isfinite(poll_timeout) or poll_timeout <= 0:
            raise ValueError("poll_timeout must be a positive finite number of seconds.")
        data = ScrapeParams(
            waitFor=wait_for,
            timeout=timeout,
            onlyMainContent=only_main_content,
            includeTags=include_tags,
            excludeTags=exclude_tags,
            headers=headers,
            formats=formats,
            browserOptions={
                "proxy_country": "ANY",
                "session_name": "Crawl",
                "session_recording": True,
                "session_ttl": 900,
            },
        )

        service = self.scrapeless_client.scraping_crawl.scrape
        task = service.async_batch_scrape_urls(urls, data)
        task_id = task.get("id")
        if not task_id:
            raise ToolException("Batch scrape did not return a task ID.")

        deadline = time.monotonic() + poll_timeout
        while time.monotonic() < deadline:
            try:
                result = service.check_batch_scrape_status(task_id)
            except Exception as error:
                raise ToolException(
                    f"Could not retrieve batch scrape task {task_id}. "
                    "Check this task before submitting another scrape."
                ) from error
            status = result.get("status")
            if status in {"completed", "failed", "cancelled", "canceled"}:
                return result
            if status not in {"scraping", "pending", "queued", "active", "running", "waiting"}:
                raise ToolException(
                    f"Unexpected batch scrape status {status!r}. Task ID: {task_id}"
                )
            remaining = deadline - time.monotonic()
            time.sleep(max(0, min(2, remaining)))
        raise ToolException(
            f"Batch scrape polling timed out. Task ID: {task_id}. "
            "Retrieve this task through the SDK before submitting another scrape."
        )


class ScrapelessCrawlerCrawlAPIWrapper(ScrapelessAPIWrapper):
    """Wrapper for Scrapeless Crawler Crawl API.

    This wrapper can be used with the Scrapeless Crawler Crawl scenarios.
    """

    def crawl_results(
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
        formats: Optional[List[str]] = ["markdown"],
        only_main_content: Optional[bool] = True,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        wait_for: Optional[int] = 0,
        timeout: Optional[int] = 30000,
    ) -> CrawlStatusResponse:
        browser_options = {
            "proxy_country": "ANY",
            "session_name": "Crawl",
            "session_recording": True,
            "session_ttl": 900,
        }

        params = CrawlParams(
            limit=limit,
            delay=delay,
            maxDepth=max_depth,
            maxDiscoveryDepth=max_discovery_depth,
            ignoreSitemap=ignore_sitemap,
            ignoreQueryParameters=ignore_query_params,
            deduplicateSimilarURLs=deduplicate_similar_urls,
            regexOnFullURL=regex_on_full_url,
            allowBackwardLinks=allow_backward_links,
            allowExternalLinks=allow_external_links,
            includePaths=include_paths,
            excludePaths=exclude_paths,
            scrapeOptions=ScrapeParams(
                waitFor=wait_for,
                timeout=timeout,
                onlyMainContent=only_main_content,
                includeTags=include_tags,
                excludeTags=exclude_tags,
                headers=headers,
                formats=formats,
                browserOptions=browser_options,
            ),
            browserOptions=browser_options,
        )
        response = self.scrapeless_client.scraping_crawl.crawl.crawl_url(url, params)
        return response
