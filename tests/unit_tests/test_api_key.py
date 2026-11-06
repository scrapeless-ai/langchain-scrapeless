import pytest
from pydantic import SecretStr, ValidationError

from langchain_scrapeless import (
    ScrapelessChatGPTScraperTool,
    ScrapelessCrawlerCrawlTool,
    ScrapelessCrawlerScrapeTool,
    ScrapelessDeepSerpGoogleSearchTool,
    ScrapelessDeepSerpGoogleTrendsTool,
    ScrapelessUniversalScrapingTool,
)


@pytest.fixture(
    params=[
        (ScrapelessChatGPTScraperTool, "scrapeless_api_wrapper"),
        (ScrapelessCrawlerCrawlTool, "scrapeless_crawler_api_wrapper"),
        (ScrapelessCrawlerScrapeTool, "scrapeless_crawler_api_wrapper"),
        (ScrapelessDeepSerpGoogleSearchTool, "scrapeless_deepserp_api_wrapper"),
        (ScrapelessDeepSerpGoogleTrendsTool, "scrapeless_deepserp_api_wrapper"),
        (ScrapelessUniversalScrapingTool, "scrapeless_universal_scraping_api_wrapper"),
    ],
    ids=["chatgpt", "crawl", "scrape", "google-search", "google-trends", "web-unlocker"],
)
def tool_and_wrapper(request):
    return request.param


def test_explicit_key_without_environment(tool_and_wrapper, monkeypatch):
    tool_class, wrapper_name = tool_and_wrapper
    monkeypatch.delenv("SCRAPELESS_API_KEY", raising=False)

    tool = tool_class(scrapeless_api_key="explicit-test-key")

    assert getattr(tool, wrapper_name).scrapeless_api_key == SecretStr("explicit-test-key")


def test_key_and_client_are_hidden(tool_and_wrapper, monkeypatch):
    tool_class, wrapper_name = tool_and_wrapper
    key = "sensitive-test-key"
    monkeypatch.setenv("SCRAPELESS_API_KEY", key)

    for tool in (tool_class(), tool_class(scrapeless_api_key=key)):
        wrapper = getattr(tool, wrapper_name)
        assert key not in repr(tool)
        assert key not in repr(wrapper.scrapeless_api_key)
        assert key not in tool.model_dump_json(exclude={"args_schema"})
        assert "scrapeless_api_key" not in tool.model_dump()[wrapper_name]
        assert "scrapeless_client" not in wrapper.model_dump()


def test_environment_fallback_and_explicit_precedence(tool_and_wrapper, monkeypatch):
    tool_class, wrapper_name = tool_and_wrapper
    monkeypatch.setenv("SCRAPELESS_API_KEY", "environment-test-key")

    env_tool = tool_class()
    explicit_tool = tool_class(scrapeless_api_key="explicit-test-key")

    assert getattr(env_tool, wrapper_name).scrapeless_api_key == SecretStr(
        "environment-test-key"
    )
    assert getattr(explicit_tool, wrapper_name).scrapeless_api_key == SecretStr(
        "explicit-test-key"
    )


def test_missing_key_reports_required_environment_variable(tool_and_wrapper, monkeypatch):
    tool_class, _ = tool_and_wrapper
    monkeypatch.delenv("SCRAPELESS_API_KEY", raising=False)

    with pytest.raises(ValidationError, match="SCRAPELESS_API_KEY"):
        tool_class()


def test_google_search_sends_the_explicit_key(monkeypatch):
    monkeypatch.delenv("SCRAPELESS_API_KEY", raising=False)
    monkeypatch.delenv("SCRAPELESS_BASE_API_URL", raising=False)
    expected = {"organic_results": [{"title": "Scrapeless"}]}

    class Response:
        headers = {"Content-Type": "application/json"}
        ok = True
        status_code = 200

        def json(self):
            return expected

    def request(method, url, *, headers, json, timeout):
        assert method == "POST"
        assert url == "https://api.scrapeless.com/api/v1/scraper/request"
        assert headers["X-API-Key"] == "explicit-test-key"
        assert json["actor"] == "scraper.google.search"
        assert json["input"]["q"] == "Scrapeless"
        return Response()

    monkeypatch.setattr("scrapeless.services.base.requests.request", request)

    tool = ScrapelessDeepSerpGoogleSearchTool(scrapeless_api_key="explicit-test-key")

    assert tool.invoke({"q": "Scrapeless"}) == expected
