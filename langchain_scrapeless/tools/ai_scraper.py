"""SDK-backed tools for the eight documented Scrapeless AI Scraper engines."""

import time
from typing import Any, ClassVar, Literal

from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from scrapeless import ScrapelessError
from scrapeless.types import AIScraperTaskRequest

from langchain_scrapeless.wrappers import ScrapelessAPIWrapper

Engine = Literal[
    "chatgpt", "perplexity", "copilot", "gemini", "aimode", "overview", "grok", "alexa"
]


class TaskOptions(BaseModel):
    """Local lifecycle options, never forwarded as actor input."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    wait: bool = Field(default=True, description="Wait for task completion.")
    poll_timeout: float = Field(default=180, gt=0, allow_inf_nan=False)
    poll_interval: float = Field(default=5, gt=0, allow_inf_nan=False)
    output_format: Literal["text", "json"] = Field(
        default="json",
        description="Text answer or complete task response, including all fields.",
    )
    webhook_url: str | None = Field(
        default=None, description="Optional HTTPS result callback."
    )

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook(cls, value: str | None) -> str | None:
        if value is not None:
            from urllib.parse import urlsplit

            url = urlsplit(value)
            if (
                url.scheme != "https"
                or not url.hostname
                or url.username
                or url.password
            ):
                raise ValueError(
                    "webhook_url must be an HTTPS URL without credentials."
                )
        return value


class PromptInput(TaskOptions):
    prompt: str = Field(
        min_length=1, description="Prompt sent to the selected AI engine."
    )
    country: str = Field(default="US", pattern=r"^[A-Z]{2}$")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Enter a non-empty prompt.")
        return value


class ShareInput(PromptInput):
    should_fetch_share_link: bool | None = None


class SearchInput(ShareInput):
    web_search: bool | None = None
    should_fetch_html: bool | None = None


class ChatGPTScraperInput(SearchInput):
    # Preserve the existing tutorial's prompt-only behavior.
    web_search: bool | None = False
    shopping: bool | None = False
    output_format: Literal["text", "json"] = "text"


class PerplexityScraperInput(SearchInput):
    pass


class CopilotScraperInput(ShareInput):
    mode: Literal["search", "smart", "chat", "reasoning", "study"]
    should_fetch_html: bool | None = None


class GeminiScraperInput(PromptInput):
    shopping: bool | None = None


class GoogleAIOverviewScraperInput(ShareInput):
    shopping: bool | None = None
    location: str | None = Field(default=None, min_length=1)
    uule: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_location(self):
        if self.location is not None and self.uule is not None:
            raise ValueError("location and uule are mutually exclusive.")
        return self


class GoogleAIModeScraperInput(GoogleAIOverviewScraperInput):
    prompt: str | None = Field(default=None, min_length=1)
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    url: str | None = None

    @model_validator(mode="after")
    def validate_url_mode(self):
        if self.url is not None:
            from urllib.parse import urlsplit

            parsed = urlsplit(self.url)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                raise ValueError("url must be an absolute HTTP(S) URL.")
            actor_fields = {
                "prompt",
                "country",
                "shopping",
                "location",
                "uule",
                "should_fetch_share_link",
            }
            if any(getattr(self, name) is not None for name in actor_fields):
                raise ValueError(
                    "url is mutually exclusive with all other actor inputs."
                )
        elif self.prompt is None or self.country is None:
            raise ValueError("Provide prompt and country, or url alone.")
        return self


class GrokScraperInput(ShareInput):
    pass


class AlexaScraperInput(PromptInput):
    pass


ENGINE_SCHEMAS: dict[str, type[TaskOptions]] = {
    "chatgpt": ChatGPTScraperInput,
    "perplexity": PerplexityScraperInput,
    "copilot": CopilotScraperInput,
    "gemini": GeminiScraperInput,
    "aimode": GoogleAIModeScraperInput,
    "overview": GoogleAIOverviewScraperInput,
    "grok": GrokScraperInput,
    "alexa": AlexaScraperInput,
}
TEXT_FIELDS = {
    "grok": ("full_response",),
    "alexa": ("md_text", "raw_text"),
    "overview": ("content", "rawtext"),
    "aimode": ("result_md", "result_text"),
}
LOCAL_FIELDS = set(TaskOptions.model_fields)


def _poll(
    service: Any,
    task: Any,
    timeout: float,
    interval: float,
    wait: bool,
    task_id: str | None = None,
) -> dict:
    deadline = time.monotonic() + timeout
    while True:
        if not isinstance(task, dict):
            raise ToolException("AI Scraper returned an invalid task response.")
        task_id = task.get("task_id") or task_id
        status = task.get("status")
        if status not in {"pending", "running", "success", "failed"}:
            raise ToolException(
                f"AI Scraper returned an unknown task status. Task ID: {task_id}"
            )
        if status == "failed":
            # Upstream messages can contain request data or credentials.
            raise ToolException(f"AI Scraper task did not succeed. Task ID: {task_id}")
        result = dict(task)
        if task_id:
            result["task_id"] = task_id
        if status == "success":
            if not isinstance(task.get("task_result"), dict):
                raise ToolException(
                    f"AI Scraper returned no result object. Task ID: {task_id}"
                )
            return result
        if not isinstance(task_id, str) or not task_id.strip():
            raise ToolException("AI Scraper did not return a task ID.")
        if not wait:
            return result
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ToolException(f"AI Scraper is still processing. Task ID: {task_id}")
        time.sleep(min(interval, remaining))
        if time.monotonic() >= deadline:
            raise ToolException(f"AI Scraper is still processing. Task ID: {task_id}")
        try:
            task = service.get_task_result(task_id)
        except ScrapelessError:
            raise ToolException(
                "AI Scraper could not retrieve the task. "
                f"Task ID: {task_id}; no task was resubmitted."
            ) from None


def _format_result(task: dict, engine: str, output_format: str) -> Any:
    if output_format == "json" or task["status"] != "success":
        return task
    result = task["task_result"]
    for field in TEXT_FIELDS.get(engine, ("result_text",)):
        answer = result.get(field)
        if isinstance(answer, str) and answer.strip():
            return answer.strip()
    # Overview may succeed without triggering an overview answer.
    if engine == "overview":
        return ""
    raise ToolException(
        f"AI Scraper returned an empty answer. Task ID: {task.get('task_id')}"
    )


def _execute(service: Any, engine: str, values: dict) -> Any:
    options = ENGINE_SCHEMAS[engine].model_validate(values)
    actor_input = options.model_dump(exclude=LOCAL_FIELDS, exclude_none=True)
    request = AIScraperTaskRequest(
        actor=f"scraper.{engine}",
        input=actor_input,
        webhook={"url": options.webhook_url} if options.webhook_url else None,
    )
    task = service.create_task(request)  # Never retry task creation automatically.
    result = _poll(
        service, task, options.poll_timeout, options.poll_interval, options.wait
    )
    return _format_result(result, engine, options.output_format)


class _SDKTool(BaseTool):
    scrapeless_api_wrapper: ScrapelessAPIWrapper = Field(
        default_factory=ScrapelessAPIWrapper
    )

    def __init__(self, scrapeless_api_key: str | None = None, **kwargs: Any) -> None:
        if scrapeless_api_key and "scrapeless_api_wrapper" not in kwargs:
            kwargs["scrapeless_api_wrapper"] = ScrapelessAPIWrapper(
                scrapeless_api_key=scrapeless_api_key
            )
        super().__init__(**kwargs)


class _EngineTool(_SDKTool):
    engine: ClassVar[str]

    def _run(self, **kwargs: Any) -> Any:
        try:
            return _execute(
                self.scrapeless_api_wrapper.scrapeless_client.ai_scraper,
                self.engine,
                kwargs,
            )
        except ScrapelessError:
            raise ToolException(
                "AI Scraper could not complete the API request; "
                "no task was resubmitted."
            ) from None


class ScrapelessChatGPTScraperTool(_EngineTool):
    """ChatGPT AI Scraper; defaults to text for tutorial compatibility."""

    name: str = "scrapeless_chatgpt_scraper"
    description: str = (
        "Collect a ChatGPT answer. Use "
        "output_format=json for all structured result fields."
    )
    args_schema: type[BaseModel] = ChatGPTScraperInput
    engine: ClassVar[str] = "chatgpt"


class ScrapelessPerplexityScraperTool(_EngineTool):
    name: str = "scrapeless_perplexity_scraper"
    description: str = (
        "Collect Perplexity answers and full source and media data through AI Scraper."
    )
    args_schema: type[BaseModel] = PerplexityScraperInput
    engine: ClassVar[str] = "perplexity"


class ScrapelessCopilotScraperTool(_EngineTool):
    name: str = "scrapeless_copilot_scraper"
    description: str = (
        "Collect Microsoft Copilot answers and citations in the selected mode."
    )
    args_schema: type[BaseModel] = CopilotScraperInput
    engine: ClassVar[str] = "copilot"


class ScrapelessGeminiScraperTool(_EngineTool):
    name: str = "scrapeless_gemini_scraper"
    description: str = (
        "Collect Gemini answers, citations and optional shopping results."
    )
    args_schema: type[BaseModel] = GeminiScraperInput
    engine: ClassVar[str] = "gemini"


class ScrapelessGoogleAIModeScraperTool(_EngineTool):
    name: str = "scrapeless_google_ai_mode_scraper"
    description: str = (
        "Collect Google AI Mode results using prompt and country, or a complete URL."
    )
    args_schema: type[BaseModel] = GoogleAIModeScraperInput
    engine: ClassVar[str] = "aimode"


class ScrapelessGoogleAIOverviewScraperTool(_EngineTool):
    name: str = "scrapeless_google_ai_overview_scraper"
    description: str = (
        "Collect Google AI Overview results. A "
        "successful task may have no overview content."
    )
    args_schema: type[BaseModel] = GoogleAIOverviewScraperInput
    engine: ClassVar[str] = "overview"


class ScrapelessGrokScraperTool(_EngineTool):
    name: str = "scrapeless_grok_scraper"
    description: str = (
        "Collect Grok answers, web and X search data, "
        "footnotes and conversation metadata."
    )
    args_schema: type[BaseModel] = GrokScraperInput
    engine: ClassVar[str] = "grok"


class ScrapelessAlexaScraperTool(_EngineTool):
    name: str = "scrapeless_alexa_scraper"
    description: str = (
        "Collect Amazon Alexa answers, references, sources and response directives."
    )
    args_schema: type[BaseModel] = AlexaScraperInput
    engine: ClassVar[str] = "alexa"


class AIScraperInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    engine: Engine
    input: dict[str, Any] = Field(
        description="Engine-specific fields plus local lifecycle options."
    )

    @model_validator(mode="after")
    def validate_engine_input(self):
        ENGINE_SCHEMAS[self.engine].model_validate(self.input)
        return self


class ScrapelessAIScraperTool(_SDKTool):
    """Unified entry point for all documented AI Scraper engines."""

    name: str = "scrapeless_ai_scraper"
    description: str = (
        "Run one of eight AI Scraper engines with validated engine-specific input."
    )
    args_schema: type[BaseModel] = AIScraperInput

    def _run(self, engine: Engine, input: dict[str, Any]) -> Any:
        try:
            return _execute(
                self.scrapeless_api_wrapper.scrapeless_client.ai_scraper,
                engine,
                {"output_format": "json", **input},
            )
        except ScrapelessError:
            raise ToolException(
                "AI Scraper could not complete the API request; "
                "no task was resubmitted."
            ) from None


class AIScraperResultInput(TaskOptions):
    task_id: str = Field(min_length=1)
    engine: Engine = "chatgpt"
    webhook_url: None = Field(default=None, exclude=True)

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("task_id must not be blank.")
        return value


class ScrapelessAIScraperResultTool(_SDKTool):
    name: str = "scrapeless_ai_scraper_result"
    description: str = (
        "Retrieve an existing AI Scraper task, "
        "optionally waiting; never creates a new task."
    )
    args_schema: type[BaseModel] = AIScraperResultInput

    def _run(self, **kwargs: Any) -> Any:
        options = AIScraperResultInput.model_validate(kwargs)
        service = self.scrapeless_api_wrapper.scrapeless_client.ai_scraper
        try:
            task = service.get_task_result(options.task_id)
            result = _poll(
                service,
                task,
                options.poll_timeout,
                options.poll_interval,
                options.wait,
                options.task_id,
            )
            return _format_result(result, options.engine, options.output_format)
        except ScrapelessError:
            raise ToolException(
                "AI Scraper could not retrieve the task; no task was created."
            ) from None
