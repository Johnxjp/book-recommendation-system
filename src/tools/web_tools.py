"""
Web Tools

This module provides generic web tools

Available tools:
- web_search_tool: Search the web for information
- web_extract_tool: Extract content from specific web pages

# TODO: Do not have this but it could be for summarisation of long page content
LLM Processing:
- Uses OpenRouter API with Gemini 3 Flash Preview for intelligent content extraction
- Extracts key excerpts and creates markdown summaries to reduce token usage

Debug Mode:
- Set WEB_TOOLS_DEBUG=true to enable detailed logging
- Creates web_tools_debug_UUID.json in ./logs directory
- Captures all tool calls, results, and compression metrics

Usage:
    from web_tools import web_search_tool, web_extract_tool, web_crawl_tool

    # Search the web
    results = web_search_tool("Python machine learning libraries", limit=3)

    # Extract content from URLs
    content = web_extract_tool(["https://example.com"], format="markdown")

    # Crawl a website
    crawl_data = web_crawl_tool("example.com", "Find contact information")
"""

import json
import os

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()

fc_client = Firecrawl(
    api_key=os.getenv("FIRECRAWL_API_KEY"),
)


def web_search_tool(query: str, limit: int = 5) -> str:
    """
    Search the web for information relevant to the query.
    Returns a json string of results with title, url, and snippet.
    """
    try:
        result = fc_client.search(
            query=query,
            limit=limit,
            sources=["web", "news"],
        )
        return json.dumps(result.model_dump())
    except Exception as e:
        error_msg = f"Error searching web: {str(e)}"
        return json.dumps({"error": error_msg})


def web_extract_tool(url: str) -> str:
    """Scrape content from specific web pages. Returns a json string with markdown of the content."""
    try:
        result = fc_client.scrape(
            url=url,
            formats=["markdown"],
        )
        return json.dumps(
            {
                "markdown": result.markdown,
            }
        )
    except Exception as e:
        error_msg = f"Error extracting web content: {str(e)}"
        return json.dumps({"error": error_msg})


web_tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "web_search_tool",
            "description": "Search the web for information relevant to the query. Returns a list of results with title, url, and snippet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of search results to return.",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_extract_tool",
            "description": "Scrape content from specific web pages. Returns markdown of the content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to extract content from.",
                    },
                },
                "required": ["url"],
            },
        },
    },
]
