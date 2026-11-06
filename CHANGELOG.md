# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## 0.1.4

- Add the full documented AI Scraper family: ChatGPT, Perplexity, Copilot, Gemini, Google AI Mode, Google AI Overview, Grok, and Amazon Alexa.
- Add a unified AI Scraper tool and a result lookup tool, engine-specific validation, complete JSON output, nonblocking submission, and resumable polling.
- Preserve the existing ChatGPT import path and prompt-only text output.

- Add a technical research example with page-body evidence, source mapping, and cited answers.
- Wait through queued Crawl batch tasks with bounded polling and preserve task IDs on lookup errors.
- Update the Scrapeless Python SDK to 1.3.0 and add a ChatGPT Scraper tool that polls for a completed answer.
- Add a Google Search and ChatGPT Scraper example that saves search results and cites a saved source.
- Fix API key initialization for all five tools and keep credentials and SDK clients out of tool representations and serialized output.
- Support installation with LangChain Core 1.x while retaining compatibility with the tested 0.3.x setup. Require Python 3.10 or later.
- Document installation from source and add a LangChain 1.x agent example.
- Validate Google Search domains and Google Trends region codes by format and pass them through to Scrapeless.
- Run offline tests on GitHub Actions and require them before publishing a release.

- Forward Google Search filtering and search-type options to the SDK.
- Validate release version updates and trigger PyPI publishing on published GitHub Releases.
- Correct tool documentation references.

### [0.1.3](https://github.com/scrapeless-ai/langchain-scrapeless/compare/v0.1.2...v0.1.3)


### Bug Fixes

* fix project authors format ([bc03c69](https://github.com/scrapeless-ai/langchain-scrapeless/commit/bc03c694144f4ba40b82ad718d3c64cd73373f66))

### [0.1.2](https://github.com/scrapeless-ai/langchain-scrapeless/compare/v0.1.1...v0.1.2)

### 0.1.1


### Features

* complete project configuration ([51e39bd](https://github.com/scrapeless-ai/langchain-scrapeless/commit/51e39bde2a1e0f145f0aa66a92d935fecff4427f))
* complete scraping api tool ([60bad51](https://github.com/scrapeless-ai/langchain-scrapeless/commit/60bad5110a45964d964aace83760915c222c7d90))
* complete universal scraping api tool ([5924f18](https://github.com/scrapeless-ai/langchain-scrapeless/commit/5924f18f8c71e134325095d353c8f1751e59502b))
* **crawler:** replace default values ([fcd381f](https://github.com/scrapeless-ai/langchain-scrapeless/commit/fcd381f2e6feb7455d164ea5c78404404ddee183))
* update test cases ([b131de1](https://github.com/scrapeless-ai/langchain-scrapeless/commit/b131de16e3ff4892b780b502f8735921936a1061))
