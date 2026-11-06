"""Backward-compatible import path for the ChatGPT AI Scraper engine."""

import time  # noqa: F401 - retain the original polling instrumentation import

from .ai_scraper import ChatGPTScraperInput, ScrapelessChatGPTScraperTool

__all__ = ["ChatGPTScraperInput", "ScrapelessChatGPTScraperTool"]
