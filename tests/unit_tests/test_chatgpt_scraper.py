from unittest.mock import Mock

import pytest
from langchain_core.tools import ToolException

from langchain_scrapeless import ScrapelessChatGPTScraperTool
from langchain_scrapeless.tools import chatgpt_scraper


def test_chatgpt_scraper_polls_for_result(monkeypatch):
    tool = ScrapelessChatGPTScraperTool(scrapeless_api_key="offline-test-key")
    service = tool.scrapeless_api_wrapper.scrapeless_client.ai_scraper
    create_task = Mock(return_value={"task_id": "task-1", "status": "pending"})
    get_task_result = Mock(side_effect=[
        {"status": "running"},
        {"status": "success", "task_result": {"result_text": "  An answer.  "}},
    ])
    monkeypatch.setattr(service, "create_task", create_task)
    monkeypatch.setattr(service, "get_task_result", get_task_result)
    monkeypatch.setattr(chatgpt_scraper.time, "sleep", lambda _: None)

    assert tool.invoke({"prompt": "Summarize this evidence."}) == "An answer."
    request = create_task.call_args.args[0]
    assert request.actor == "scraper.chatgpt"
    assert request.input == {
        "prompt": "Summarize this evidence.",
        "country": "US",
        "web_search": False,
        "shopping": False,
    }
    assert create_task.call_count == 1
    assert [call.args for call in get_task_result.call_args_list] == [
        ("task-1",),
        ("task-1",),
    ]


@pytest.mark.parametrize(
    ("task", "message"),
    [
        ({"status": "failed"}, "did not succeed"),
        ({"status": "success", "task_result": {"result_text": " "}}, "empty answer"),
    ],
)
def test_chatgpt_scraper_rejects_failed_or_empty_results(monkeypatch, task, message):
    tool = ScrapelessChatGPTScraperTool(scrapeless_api_key="offline-test-key")
    service = tool.scrapeless_api_wrapper.scrapeless_client.ai_scraper
    monkeypatch.setattr(service, "create_task", Mock(return_value=task))

    with pytest.raises(ToolException, match=message):
        tool.invoke({"prompt": "Summarize this evidence."})
