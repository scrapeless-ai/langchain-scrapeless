import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

spec = importlib.util.spec_from_file_location(
    "research", Path(__file__).parents[2] / "examples" / "research.py"
)
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)

BODY = (
    "# HTTP caching\n\n"
    "Cache-Control max-age defines freshness for a stored response. ETag identifies "
    "a representation and can be sent in If-None-Match during revalidation.\n\n"
    + "An unchanged representation can produce a 304 response. " * 8
)


def search_payload():
    return {"organic_results": [
        {"position": 1, "title": "Caching", "link": "https://example.com/caching#first"},
        {"position": 2, "title": "Duplicate", "link": "https://example.com/caching#second"},
        {"position": 3, "title": "Headers", "link": "https://example.com/headers"},
        {"position": 4, "title": "Other", "link": "https://unrelated.example/page"},
    ]}


def test_search_deduplicates_and_limits_sources_to_domain():
    result = research.search_sources(
        Mock(invoke=Mock(return_value=search_payload())), research.QUESTION, "HTTP caching",
        "example.com",
    )
    assert [source["url"] for source in result["sources"]] == [
        "https://example.com/caching", "https://example.com/headers"
    ]


@pytest.mark.parametrize("escaped", [False, True])
def test_full_workflow_writes_body_evidence_and_cited_answer(tmp_path, monkeypatch, escaped):
    answer = (
        "## Answer\nFreshness and validation work together. [S1] [S2]\n\n"
        "## Comparison\n| Field | Purpose |\n| ETag | Validation [S2] |\n\n"
        "## Example\nUse If-None-Match to revalidate. [S1]\n\n"
        "## Limitations\nThese excerpts cover HTTP caching. [S2]"
    )
    if escaped:
        answer = answer.replace("[S1]", r"\[S1\]").replace("[S2]", r"\[S2\]")
    search_tool = Mock(invoke=Mock(return_value=search_payload()))
    # The service returns pages in a different order from the search results.
    scrape_tool = Mock(invoke=Mock(return_value={"status": "completed", "data": [
        {"markdown": BODY, "metadata": {"sourceURL": "https://example.com/headers", "statusCode": 200}},
        {"markdown": BODY, "metadata": {"sourceURL": "https://example.com/caching", "statusCode": 200}},
    ]}))
    answer_tool = Mock(invoke=Mock(return_value=answer))
    monkeypatch.setattr(research, "ScrapelessDeepSerpGoogleSearchTool", lambda: search_tool)
    monkeypatch.setattr(research, "ScrapelessCrawlerScrapeTool", lambda: scrape_tool)
    monkeypatch.setattr(research, "ScrapelessChatGPTScraperTool", lambda: answer_tool)

    research.main(["run", "--output-dir", str(tmp_path), "--domain", "example.com"])

    pages = json.loads((tmp_path / "pages.json").read_text())
    evidence = json.loads((tmp_path / "evidence.json").read_text())
    for source in evidence["sources"]:
        page = next(page for page in pages["pages"] if page["id"] == source["id"])
        for excerpt in source["excerpts"]:
            assert excerpt["text"] == page["markdown"][excerpt["start"]:excerpt["end"]]
    output = (tmp_path / "answer.md").read_text()
    assert "[S1] Caching - <https://example.com/caching>" in output
    assert "[S2] Headers - <https://example.com/headers>" in output
    assert r"\[S1\]" not in output
    assert not (tmp_path / ".research.lock").exists()
    assert search_tool.invoke.call_count == scrape_tool.invoke.call_count == answer_tool.invoke.call_count == 1
    with pytest.raises(ValueError, match="new output directory"):
        research.main(["run", "--output-dir", str(tmp_path)])
    assert search_tool.invoke.call_count == 1


def test_evidence_rejects_stale_or_insufficient_pages():
    search = {"run_id": "new", "question": research.QUESTION}
    with pytest.raises(ValueError, match="another search"):
        research.build_evidence(search, {"run_id": "old", "pages": []})
    with pytest.raises(ValueError, match="At least two"):
        research.build_evidence(search, {"run_id": "new", "pages": []})


def test_evidence_includes_explanatory_context_instead_of_only_link_headings():
    body = (
        "# [HTTP caching Cache-Control ETag](https://example.com/etag)\n\n"
        + "Unrelated navigation. " * 300 + "\n\n"
        + "The ETag identifies a resource version and is sent with a conditional request "
        "when an existing cached representation needs revalidation.\n\n"
        + "If the representation is unchanged, the server returns 304 Not Modified."
    )
    pages = {"run_id": "r", "pages": [
        {"id": source_id, "url": "https://example.com/" + source_id,
         "title": source_id, "status": "success", "markdown": body}
        for source_id in ("S1", "S2")
    ]}
    evidence = research.build_evidence(
        {"run_id": "r", "question": research.QUESTION, "query": research.QUERY}, pages
    )
    for source in evidence["sources"]:
        assert any("304 Not Modified" in item["text"] for item in source["excerpts"])


def test_answer_rejects_unknown_citations():
    evidence = {"question": research.QUESTION, "sources": [
        {"id": "S1", "title": "Caching", "url": "https://example.com", "excerpts": []}
    ]}
    tool = Mock(invoke=Mock(return_value="Generated claim [S1] [S9]"))
    with pytest.raises(ValueError, match="valid evidence"):
        research.answer_question(tool, evidence)
