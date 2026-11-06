import pytest
from pydantic import ValidationError

from langchain_scrapeless import (
    ScrapelessDeepSerpGoogleSearchTool,
    ScrapelessDeepSerpGoogleTrendsTool,
)


@pytest.mark.parametrize(
    ("tool_class", "method", "field", "value", "invalid"),
    [
        (
            ScrapelessDeepSerpGoogleSearchTool,
            "get_google_search_results",
            "google_domain",
            "google.co.uk",
            "https://example.com",
        ),
        (
            ScrapelessDeepSerpGoogleTrendsTool,
            "get_google_trends_results",
            "geo",
            "GB",
            "GBR",
        ),
    ],
)
def test_localization_is_validated_and_forwarded(
    monkeypatch, tool_class, method, field, value, invalid
):
    tool = tool_class(scrapeless_api_key="offline-test-key")
    wrapper = tool.scrapeless_deepserp_api_wrapper
    received = []

    def get_results(self, **params):
        received.append(params[field])
        return {"results": []}

    monkeypatch.setattr(type(wrapper), method, get_results)
    tool.invoke({"q": "Scrapeless", field: value})
    assert received == [value]
    with pytest.raises(ValidationError):
        tool.invoke({"q": "Scrapeless", field: invalid})
    assert received == [value]


def test_search_options_reach_sdk_request(monkeypatch):
    tool = ScrapelessDeepSerpGoogleSearchTool(scrapeless_api_key="offline-test-key")
    service = tool.scrapeless_deepserp_api_wrapper.scrapeless_client.scraping
    received = []

    def scrape(request):
        received.append(request.input)
        return {"organic_results": []}

    monkeypatch.setattr(service, "scrape", scrape)
    tool.invoke({"q": "HTTP caching", "nfpr": "1", "filter": "0", "tbm": "nws"})
    assert len(received) == 1
    assert {key: received[0][key] for key in ("nfpr", "filter", "tbm")} == {
        "nfpr": "1", "filter": "0", "tbm": "nws"
    }
