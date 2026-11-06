from unittest.mock import Mock

from langchain_scrapeless import ScrapelessCrawlerScrapeTool
from langchain_scrapeless import wrappers


def test_scrape_waits_through_queued_and_running_statuses(monkeypatch):
    tool = ScrapelessCrawlerScrapeTool(scrapeless_api_key="offline-test-key")
    service = tool.scrapeless_crawler_api_wrapper.scrapeless_client.scraping_crawl.scrape
    submit = Mock(return_value={"id": "job-1", "success": True})
    complete = {"status": "completed", "data": [{"markdown": "Actual page content"}]}
    poll = Mock(side_effect=[{"status": "queued"}, {"status": "scraping"}, complete])
    monkeypatch.setattr(service, "async_batch_scrape_urls", submit)
    monkeypatch.setattr(service, "check_batch_scrape_status", poll)
    monkeypatch.setattr(wrappers.time, "sleep", lambda _: None)

    assert tool.invoke({"urls": ["https://example.com"]}) == complete
    assert submit.call_count == 1
    assert poll.call_count == 3


def test_scrape_timeout_retains_task_id(monkeypatch):
    tool = ScrapelessCrawlerScrapeTool(scrapeless_api_key="offline-test-key")
    service = tool.scrapeless_crawler_api_wrapper.scrapeless_client.scraping_crawl.scrape
    monkeypatch.setattr(service, "async_batch_scrape_urls", Mock(return_value={"id": "job-1"}))
    monkeypatch.setattr(service, "check_batch_scrape_status", Mock(return_value={"status": "pending"}))
    monkeypatch.setattr(wrappers.time, "monotonic", Mock(side_effect=[0, 0, 181, 181]))
    monkeypatch.setattr(wrappers.time, "sleep", lambda _: None)

    # BaseTool keeps the existing handle_tool_error=True behavior for callers.
    assert "job-1" in tool.invoke({"urls": ["https://example.com"]})


def test_scrape_preserves_terminal_failure_response(monkeypatch):
    tool = ScrapelessCrawlerScrapeTool(scrapeless_api_key="offline-test-key")
    service = tool.scrapeless_crawler_api_wrapper.scrapeless_client.scraping_crawl.scrape
    failed = {"status": "failed", "error": "Page unavailable", "data": []}
    monkeypatch.setattr(service, "async_batch_scrape_urls", Mock(return_value={"id": "job-1"}))
    monkeypatch.setattr(service, "check_batch_scrape_status", Mock(return_value=failed))

    assert tool.invoke({"urls": ["https://example.com"]}) == failed
