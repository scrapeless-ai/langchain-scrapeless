<div align="center">
  <img width="180" src="https://app.scrapeless.com/assets/logo.svg" alt="Scrapeless logo">

LangChain Scrapeless: an all-in-one, highly scalable web scraping toolkit for enterprises and developers that also integrates with LangChain’s AI tools. Maintained by [Scrapeless](https://app.scrapeless.com/passport/login?utm_source=github&utm_medium=langchain-scrapeless&utm_campaign=langchain-scrapeless).

[Scrapeless](https://app.scrapeless.com/passport/login?utm_source=github&utm_medium=langchain-scrapeless&utm_campaign=langchain-scrapeless) | [Documentation](https://docs.scrapeless.com) | [LangChain](https://langchain.com)

</div>

---

**langchain-scrapeless** is designed for seamless integration with LangChain, enabling you to:

- Run custom scraping tasks using your own crawlers or scraping logic.
- Automate data extraction and processing workflows in Python.
- Manage and interact with datasets produced by your scraping jobs.
- Access scraping and data handling capabilities as LangChain tools, making them easy to compose with LLM-powered chains and agents.

## 📦 Installation

```bash
pip install langchain-scrapeless
```

## ✅ Prerequisites

You should configure the credentials for the Scrapeless API in your environment variables.

- `SCRAPELESS_API_KEY`: Your Scrapeless API key.

If you don't have an API key, you can register at [here](https://app.scrapeless.com/passport/register?utm_source=github&utm_medium=langchain-scrapeless&utm_campaign=langchain-scrapeless) and learn how to get your API key in [Scrapeless documentation](https://docs.scrapeless.com/en/sdk/node-sdk/#quick-start).

## 🛠️ Available Tools

### 🔍 DeepSerp

#### 🌐 ScrapelessDeepSerpGoogleSearchTool

Perform Google search queries and get the results.

```python
from langchain_scrapeless import ScrapelessDeepSerpGoogleSearchTool

tool = ScrapelessDeepSerpGoogleSearchTool()

# Basic usage
# result = tool.invoke("I want to know Scrapeless")
# print(result)

# Advanced usage
result = tool.invoke({
    "q": "Scrapeless",
    "hl": "en",
    "google_domain": "google.com"
})
print(result)

# With LangChain
from langchain_openai import ChatOpenAI
from langchain_scrapeless import ScrapelessDeepSerpGoogleSearchTool
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI()

tool = ScrapelessDeepSerpGoogleSearchTool()

# Use the tool with an agent
tools = [tool]
agent = create_react_agent(llm, tools)

for chunk in agent.stream(
        {"messages": [("human", "I want to what is Scrapeless")]},
        stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
```

You can visit [here](https://apidocs.scrapeless.com/doc-800321) to learn more customizations options.

#### 🌐 ScrapelessDeepSerpGoogleTrendsTool

Perform Google trends queries and get the results.

```python
from langchain_scrapeless import ScrapelessDeepSerpGoogleTrendsTool

tool = ScrapelessDeepSerpGoogleTrendsTool()

# Basic usage
# result = tool.invoke("Funny 2048,negamon monster trainer")
# print(result)

# Advanced usage
result = tool.invoke({
    "q": "Scrapeless",
    "data_type": "related_topics",
    "hl": "en"
})
print(result)

# With LangChain
from langchain_openai import ChatOpenAI
from langchain_scrapeless import ScrapelessDeepSerpGoogleTrendsTool
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI()

tool = ScrapelessDeepSerpGoogleTrendsTool()

# Use the tool with an agent
tools = [tool]
agent = create_react_agent(llm, tools)

for chunk in agent.stream(
        {"messages": [("human", "I want to know the iphone keyword trends")]},
        stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

```

You can visit [here](https://apidocs.scrapeless.com/doc-796980) to learn more customizations options.

### 🔓 ScrapelessUniversalScrapingTool

Access any website at scale and say goodbye to blocks.

```python
from langchain_scrapeless import ScrapelessUniversalScrapingTool

tool = ScrapelessUniversalScrapingTool()

# Basic usage
# result = tool.invoke("https://example.com")
# print(result)

# Advanced usage
result = tool.invoke({
    "url": "https://exmaple.com",
    "response_type": "markdown"
})
print(result)

# With LangChain
from langchain_openai import ChatOpenAI
from langchain_scrapeless import ScrapelessUniversalScrapingTool
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI()

tool = ScrapelessUniversalScrapingTool()

# Use the tool with an agent
tools = [tool]
agent = create_react_agent(llm, tools)

for chunk in agent.stream(
        {"messages": [("human", "Use the scrapeless scraping tool to fetch https://www.scrapeless.com/en and extract the h1 tag.")]},
        stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
```

You can visit [here](https://apidocs.scrapeless.com/api-12948840) to learn more customizations options.

### 🕷️ Crawler

#### 🌐 ScrapelessCrawlerCrawlTool

Crawl a website and its linked pages to extract comprehensive data

```python
from langchain_scrapeless import ScrapelessCrawlerCrawlTool

tool = ScrapelessCrawlerCrawlTool()

# Basic
# result = tool.invoke("https://example.com")
# print(result)

# Advanced usage
result = tool.invoke({
    "url": "https://exmaple.com",
    "limit": 4
})
print(result)

# With LangChain
from langchain_openai import ChatOpenAI
from langchain_scrapeless import ScrapelessCrawlerCrawlTool
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI()

tool = ScrapelessCrawlerCrawlTool()

# Use the tool with an agent
tools = [tool]
agent = create_react_agent(llm, tools)

for chunk in agent.stream(
        {"messages": [("human", "Use the scrapeless crawler crawl tool to crawl the website https://example.com and output the markdown content as a string.")]},
        stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
```

You can visit [here](https://apidocs.scrapeless.com/api-17509010) to learn more customizations options.

#### 🌐 ScrapelessCrawlerScrapeTool

Extract data from a single or multiple webpages.

```python
from langchain_scrapeless import ScrapelessCrawlerScrapeTool

tool = ScrapelessCrawlerScrapeTool()

result = tool.invoke({
    "urls": ["https://exmaple.com", "https://www.scrapeless.com/en"],
    "formats": ["markdown"]
})
print(result)

# With LangChain
from langchain_openai import ChatOpenAI
from langchain_scrapeless import ScrapelessCrawlerScrapeTool
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI()

tool = ScrapelessCrawlerScrapeTool()

# Use the tool with an agent
tools = [tool]
agent = create_react_agent(llm, tools)

for chunk in agent.stream(
        {"messages": [("human", "Use the scrapeless crawler scrape tool to get the website content of https://example.com and output the html content as a string.")]},
        stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
```
