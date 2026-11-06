"""Offline contract tests; these fixtures are not live engine responses."""

from unittest.mock import Mock

import pytest
from langchain_core.tools import ToolException
from langchain_tests.unit_tests import ToolsUnitTests
from pydantic import ValidationError

from langchain_scrapeless import (
    ScrapelessAIScraperResultTool,
    ScrapelessAIScraperTool,
    ScrapelessAlexaScraperTool,
    ScrapelessChatGPTScraperTool,
    ScrapelessCopilotScraperTool,
    ScrapelessGeminiScraperTool,
    ScrapelessGoogleAIModeScraperTool,
    ScrapelessGoogleAIOverviewScraperTool,
    ScrapelessGrokScraperTool,
    ScrapelessPerplexityScraperTool,
)
from langchain_scrapeless.tools import ai_scraper

CASES = [
    (
        ScrapelessChatGPTScraperTool,
        "chatgpt",
        {
            "prompt": "Explain caching",
            "country": "JP",
            "web_search": True,
            "shopping": True,
            "should_fetch_share_link": True,
            "should_fetch_html": True,
        },
        "result_text",
    ),
    (
        ScrapelessPerplexityScraperTool,
        "perplexity",
        {
            "prompt": "Explain caching",
            "country": "GB",
            "web_search": False,
            "should_fetch_share_link": False,
            "should_fetch_html": True,
        },
        "result_text",
    ),
    (
        ScrapelessCopilotScraperTool,
        "copilot",
        {
            "prompt": "Explain caching",
            "country": "US",
            "mode": "study",
            "should_fetch_share_link": True,
            "should_fetch_html": True,
        },
        "result_text",
    ),
    (
        ScrapelessGeminiScraperTool,
        "gemini",
        {"prompt": "Explain caching", "country": "US", "shopping": True},
        "result_text",
    ),
    (
        ScrapelessGoogleAIModeScraperTool,
        "aimode",
        {
            "prompt": "Explain caching",
            "country": "US",
            "shopping": False,
            "location": "New York,New York,United States",
            "should_fetch_share_link": True,
        },
        "result_md",
    ),
    (
        ScrapelessGoogleAIOverviewScraperTool,
        "overview",
        {
            "prompt": "Explain caching",
            "country": "US",
            "shopping": False,
            "uule": "encoded-location",
            "should_fetch_share_link": True,
        },
        "content",
    ),
    (
        ScrapelessGrokScraperTool,
        "grok",
        {"prompt": "Explain caching", "country": "US", "should_fetch_share_link": True},
        "full_response",
    ),
    (
        ScrapelessAlexaScraperTool,
        "alexa",
        {"prompt": "Explain caching", "country": "US"},
        "md_text",
    ),
]


def make_tool(cls=ScrapelessAIScraperTool):
    tool = cls(scrapeless_api_key="offline-family-test-key")
    return tool, tool.scrapeless_api_wrapper.scrapeless_client.ai_scraper


@pytest.mark.parametrize("cls,engine,actor_input,text_field", CASES)
def test_sdk_serialization_and_full_result_preserved(
    monkeypatch, cls, engine, actor_input, text_field
):
    tool, service = make_tool(cls)
    payload = {
        text_field: "Answer",
        "citations": [{"url": "https://example.com"}],
        "products": [{"nested": {"offers": [1]}}],
        "future_field": {"retained": True},
    }
    # Mock the SDK's HTTP boundary, not the integration's result conversion.
    request = Mock(return_value={"status": "success", "task_result": payload})
    monkeypatch.setattr(service, "request", request)
    result = tool.invoke(
        {
            **actor_input,
            "output_format": "json",
            "webhook_url": "https://example.com/hook",
            "poll_timeout": 20,
        }
    )
    assert result["task_result"] == payload
    args, kwargs = request.call_args
    assert args == (
        "/api/v2/scraper/request",
        "POST",
        {
            "actor": f"scraper.{engine}",
            "input": actor_input,
            "webhook": {"url": "https://example.com/hook"},
        },
    )
    assert kwargs["additional_headers"] == {"x-api-token": "offline-family-test-key"}
    assert request.call_count == 1


@pytest.mark.parametrize("cls,engine,actor_input,text_field", CASES)
def test_engine_specific_text_mode(monkeypatch, cls, engine, actor_input, text_field):
    tool, service = make_tool(cls)
    monkeypatch.setattr(
        service,
        "create_task",
        Mock(
            return_value={"status": "success", "task_result": {text_field: " Answer "}}
        ),
    )
    assert tool.invoke({**actor_input, "output_format": "text"}) == "Answer"


@pytest.mark.parametrize("cls,engine,actor_input,text_field", CASES)
def test_generic_entry_point_covers_every_engine(
    monkeypatch, cls, engine, actor_input, text_field
):
    tool, service = make_tool()
    create = Mock(
        return_value={"status": "success", "task_result": {text_field: "Answer"}}
    )
    monkeypatch.setattr(service, "create_task", create)
    result = tool.invoke({"engine": engine, "input": actor_input})
    assert result["task_result"][text_field] == "Answer"
    assert create.call_args.args[0].actor == f"scraper.{engine}"


@pytest.mark.parametrize(
    "engine,bad",
    [
        ("copilot", {"prompt": "x"}),
        ("copilot", {"prompt": "x", "mode": "invalid"}),
        ("alexa", {"prompt": "x", "shopping": True}),
        ("gemini", {"prompt": "x", "web_search": True}),
        ("grok", {"prompt": "x", "should_fetch_html": True}),
        (
            "aimode",
            {"prompt": "x", "country": "US", "url": "https://google.com/search"},
        ),
        ("aimode", {"prompt": "x"}),
        ("aimode", {"url": "file:///tmp/example"}),
        ("overview", {"prompt": "x", "location": "NY", "uule": "encoded"}),
        ("chatgpt", {"prompt": " "}),
        ("chatgpt", {"prompt": "x", "country": "USA"}),
        ("chatgpt", {"prompt": "x", "poll_timeout": float("inf")}),
        ("chatgpt", {"prompt": "x", "poll_interval": 0}),
        ("chatgpt", {"prompt": "x", "webhook_url": "http://example.com"}),
    ],
)
def test_invalid_input_never_submits(monkeypatch, engine, bad):
    tool, service = make_tool()
    create = Mock()
    monkeypatch.setattr(service, "create_task", create)
    with pytest.raises(ValidationError):
        tool.invoke({"engine": engine, "input": bad})
    create.assert_not_called()


def test_url_only_mode_does_not_inject_actor_defaults(monkeypatch):
    tool, service = make_tool(ScrapelessGoogleAIModeScraperTool)
    create = Mock(
        return_value={"status": "success", "task_result": {"result_text": "x"}}
    )
    monkeypatch.setattr(service, "create_task", create)
    tool.invoke({"url": "https://www.google.com/search?udm=50&q=caching"})
    assert create.call_args.args[0].input == {
        "url": "https://www.google.com/search?udm=50&q=caching"
    }


def test_polling_preserves_id_and_fields(monkeypatch):
    tool, service = make_tool(ScrapelessGrokScraperTool)
    create = Mock(return_value={"status": "pending", "task_id": "task-1"})
    get = Mock(
        side_effect=[
            {"status": "running"},
            {
                "status": "success",
                "task_result": {
                    "full_response": "x",
                    "x_search_results": [1],
                    "footnotes": {"a": 1},
                },
            },
        ]
    )
    monkeypatch.setattr(service, "create_task", create)
    monkeypatch.setattr(service, "get_task_result", get)
    monkeypatch.setattr(ai_scraper.time, "sleep", lambda _: None)
    result = tool.invoke({"prompt": "x"})
    assert result["task_id"] == "task-1"
    assert result["task_result"]["x_search_results"] == [1]
    assert create.call_count == 1
    assert get.call_count == 2


def test_nonblocking_submission_and_resume(monkeypatch):
    tool, service = make_tool(ScrapelessAlexaScraperTool)
    get = Mock()
    monkeypatch.setattr(
        service,
        "create_task",
        Mock(return_value={"status": "pending", "task_id": "resume-1"}),
    )
    monkeypatch.setattr(service, "get_task_result", get)
    assert tool.invoke({"prompt": "x", "wait": False}) == {
        "status": "pending",
        "task_id": "resume-1",
    }
    get.assert_not_called()
    reader, service = make_tool(ScrapelessAIScraperResultTool)
    create = Mock()
    monkeypatch.setattr(service, "create_task", create)
    monkeypatch.setattr(
        service,
        "get_task_result",
        Mock(
            return_value={
                "status": "success",
                "task_result": {"md_text": "Answer", "references": []},
            }
        ),
    )
    result = reader.invoke({"task_id": "resume-1", "engine": "alexa"})
    assert result["task_id"] == "resume-1"
    assert result["task_result"]["md_text"] == "Answer"
    create.assert_not_called()


@pytest.mark.parametrize(
    "task",
    [
        None,
        {},
        {"status": "unexpected"},
        {"status": "pending"},
        {"status": "success"},
        {"status": "failed", "message": "sensitive upstream content"},
    ],
)
def test_invalid_or_failed_tasks_are_not_retried(monkeypatch, task):
    tool, service = make_tool(ScrapelessGeminiScraperTool)
    create = Mock(return_value=task)
    monkeypatch.setattr(service, "create_task", create)
    with pytest.raises(ToolException) as caught:
        tool.invoke({"prompt": "x"})
    assert "sensitive upstream content" not in str(caught.value)
    assert create.call_count == 1


def test_timeout_keeps_task_id_without_resubmitting(monkeypatch):
    tool, service = make_tool(ScrapelessGeminiScraperTool)
    create = Mock(return_value={"status": "running", "task_id": "keep-1"})
    get = Mock()
    clock = iter([0, 0, 2])
    monkeypatch.setattr(service, "create_task", create)
    monkeypatch.setattr(service, "get_task_result", get)
    monkeypatch.setattr(ai_scraper.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(ai_scraper.time, "sleep", lambda _: None)
    with pytest.raises(ToolException, match="keep-1"):
        tool.invoke({"prompt": "x", "poll_timeout": 1})
    assert create.call_count == 1
    get.assert_not_called()


def test_overview_without_answer_is_valid_structured_success(monkeypatch):
    tool, service = make_tool(ScrapelessGoogleAIOverviewScraperTool)
    payload = {
        "status": "success",
        "task_result": {
            "content": "",
            "rawtext": "",
            "web_source": [{"url": "https://example.com"}],
        },
    }
    monkeypatch.setattr(service, "create_task", Mock(return_value=payload))
    assert tool.invoke({"prompt": "x"}) == payload
    assert tool.invoke({"prompt": "x", "output_format": "text"}) == ""


@pytest.mark.asyncio
async def test_async_invoke_uses_same_sdk_and_result_contract(monkeypatch):
    tool, service = make_tool(ScrapelessPerplexityScraperTool)
    payload = {
        "status": "success",
        "task_result": {"result_text": "Answer", "web_results": []},
    }
    monkeypatch.setattr(service, "create_task", Mock(return_value=payload))
    assert await tool.ainvoke({"prompt": "x"}) == payload


@pytest.mark.parametrize("cls,engine,actor_input,text_field", CASES)
def test_all_engine_keys_are_private_and_explicit_key_wins(
    monkeypatch, cls, engine, actor_input, text_field
):
    monkeypatch.setenv("SCRAPELESS_API_KEY", "environment-key")
    tool, _ = make_tool(cls)
    assert (
        tool.scrapeless_api_wrapper.scrapeless_api_key.get_secret_value()
        == "offline-family-test-key"
    )
    assert "offline-family-test-key" not in repr(tool)
    assert "offline-family-test-key" not in tool.model_dump_json(
        exclude={"args_schema"}
    )


# Exercise LangChain's standard tool contract for the newly exposed classes.
for _cls, _engine, _input, _text_field in CASES[1:]:

    def _standard(cls, example):
        class Standard(ToolsUnitTests):
            @property
            def tool_constructor(self):
                return cls

            @property
            def tool_constructor_params(self):
                return {"scrapeless_api_key": "offline-test-key"}

            @property
            def tool_invoke_params_example(self):
                return example

        return Standard

    globals()[f"Test{_cls.__name__}"] = _standard(_cls, _input)


@pytest.mark.parametrize("code", [401, 403, 410, 429, 500])
def test_retrieval_errors_do_not_create_tasks(monkeypatch, code):
    from scrapeless import ScrapelessError

    tool, service = make_tool(ScrapelessAIScraperResultTool)
    create = Mock()
    monkeypatch.setattr(service, "create_task", create)
    monkeypatch.setattr(
        service,
        "get_task_result",
        Mock(side_effect=ScrapelessError(f"HTTP {code} sensitive detail")),
    )
    with pytest.raises(ToolException) as caught:
        tool.invoke({"task_id": "existing-1"})
    assert "sensitive detail" not in str(caught.value)
    create.assert_not_called()


def test_polling_request_failure_retains_resume_id(monkeypatch):
    from scrapeless import ScrapelessError

    tool, service = make_tool(ScrapelessGeminiScraperTool)
    create = Mock(return_value={"status": "pending", "task_id": "keep-id"})
    monkeypatch.setattr(service, "create_task", create)
    monkeypatch.setattr(
        service, "get_task_result", Mock(side_effect=ScrapelessError("upstream detail"))
    )
    monkeypatch.setattr(ai_scraper.time, "sleep", lambda _: None)
    with pytest.raises(ToolException, match="keep-id"):
        tool.invoke({"prompt": "x"})
    assert create.call_count == 1


@pytest.mark.parametrize(
    "engine,example",
    [
        ("aimode", {"url": "https://www.google.com/search?q=test&udm=50"}),
        ("copilot", {"prompt": "x", "mode": "reasoning"}),
    ],
)
def test_langchain_tool_call_preserves_structured_result(monkeypatch, engine, example):
    from langchain_core.messages import ToolMessage

    tool, service = make_tool()
    payload = {
        "status": "success",
        "task_result": {"result_text": "Answer", "citations": []},
    }
    monkeypatch.setattr(service, "create_task", Mock(return_value=payload))
    result = tool.invoke(
        {
            "name": tool.name,
            "type": "tool_call",
            "id": "call-1",
            "args": {"engine": engine, "input": example},
        }
    )
    assert isinstance(result, ToolMessage)
    import json

    assert json.loads(result.content) == payload


TestUnifiedAIScraperTool = _standard(
    ScrapelessAIScraperTool, {"engine": "gemini", "input": {"prompt": "x"}}
)
TestAIScraperResultTool = _standard(
    ScrapelessAIScraperResultTool, {"task_id": "existing-task", "wait": False}
)


@pytest.mark.parametrize("cls,engine,actor_input,text_field", CASES)
def test_sdk_http_boundary_for_every_engine(
    monkeypatch, cls, engine, actor_input, text_field
):
    from scrapeless.services import base

    tool, _ = make_tool(cls)
    payload = {"status": "success", "task_result": {text_field: "Answer"}}
    response = Mock(
        ok=True,
        status_code=201,
        headers={"Content-Type": "application/json"},
        json=Mock(return_value=payload),
    )
    request = Mock(return_value=response)
    monkeypatch.setattr(base.requests, "request", request)
    assert tool.invoke({**actor_input, "output_format": "json"}) == payload
    args, kwargs = request.call_args
    assert args == ("POST", "https://api.scrapeless.com/api/v2/scraper/request")
    assert kwargs["json"] == {"actor": f"scraper.{engine}", "input": actor_input}
    assert kwargs["headers"]["x-api-token"] == "offline-family-test-key"
