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
