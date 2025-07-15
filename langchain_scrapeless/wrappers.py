from typing import Dict, Any, Optional, Literal

from langchain_core.utils import get_from_dict_or_env
from pydantic import SecretStr, ConfigDict, model_validator, BaseModel
from scrapeless import Scrapeless
from scrapeless.types import UniversalScrapingRequest

from langchain_scrapeless.utils import create_scrapeless_client

# Base API URL for Scrapeless
SCRAPELESS_API_URL = "https://api.scrapeless.com"


class ScrapelessAPIWrapper(BaseModel):
    """Base wrapper for Scrapeless API."""

    # allow arbitrary types in the model config for the apify client fields
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    scrapeless_api_key: str | None = None
    scrapeless_client: Scrapeless



    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        """ Validate that API key exists in environment.

         Args:
             values (Dict): The values to validate.

         Returns:
             Dict: Updated values with API key.
         """
        scrapeless_api_key = get_from_dict_or_env(values, "scrapeless_api_key", "SCRAPELESS_API_KEY")

        if not scrapeless_api_key:
            raise ValueError("Scrapeless API key must be provided.")

        values["scrapeless_api_key"] = scrapeless_api_key
        values["scrapeless_client"] = create_scrapeless_client(Scrapeless, scrapeless_api_key)

        return values


class ScrapelessUniversalScrapingAPIWrapper(ScrapelessAPIWrapper):
    """Wrapper for Scrapeless Universal Scraping API.

    This wrapper can be used with the Scrapeless Universal Scraping scenarios.
    """

    def get_page_content(
            self,
            url: str,
            headless: bool = True,
            js_render: bool = True,
            js_wait_until: Optional[Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]] = "domcontentloaded",
            outputs: Optional[Literal[
                "phone_numbers", "headings", "images", "audios", "videos", "links", "menus", "hashtags", "emails", "metadata", "tables", "favicon"]] = None,
            response_type: Optional[Literal["html", "plaintext", "markdown", "png", "jpeg"]] = "html",
            response_image_full_page: Optional[bool] = False,
            selector: Optional[str] = None,
            proxy_country: Optional[str] = "ANY",
    ) -> Dict:
        """Get the content of a page.
        
        Args:
            url (str): The URL of the page to scrape.
            headless (bool): Whether to use a headless browser.
            js_render (bool): Whether to use JavaScript rendering.
            js_wait_until (Optional[Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]]): The wait until condition for JavaScript rendering.
            outputs (Optional[Literal["phone_numbers", "headings", "images", "audios", "videos", "links", "menus", "hashtags", "emails", "metadata", "tables", "favicon"]]): The outputs to return.
            response_type (Optional[Literal["html", "plaintext", "markdown", "png", "jpeg"]]): The response type.
            response_image_full_page (Optional[bool]): Whether to return the full page image.
            selector (Optional[str]): The selector to use for the page.
            proxy_country (Optional[str]): The proxy country to use for the request.
        """

        data = UniversalScrapingRequest(
            actor='unlocker.webunlocker',
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
            }
        )

        # only when the response_type is png or jpeg add the response_image_full_page
        if response_type in ["png", "jpeg"]:
            data.input["response_image_full_page"] = response_image_full_page

        response = self.scrapeless_client.universal.scrape(data)
        return response
