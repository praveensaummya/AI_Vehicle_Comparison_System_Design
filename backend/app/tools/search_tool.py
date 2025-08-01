# app/tools/search_tool.py
# Simple search tool implementation (replacing SerperDevTool temporarily)
from crewai.tools import BaseTool
import requests
import os
from typing import Dict, Any, Type
from pydantic import BaseModel, Field

class SearchToolInput(BaseModel):
    """Input schema for SearchTool."""
    query: str = Field(..., description="Search query for web search")

class SearchTool(BaseTool):
    name: str = "Web Search"
    description: str = "Search the web for information about vehicles, specifications, reviews, and market data"
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str) -> str:
        """Search the web using Serper API"""
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Search functionality temporarily unavailable - API key not configured"
        
        try:
            url = "https://google.serper.dev/search"
            payload = {"q": query}
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json()
                if "organic" in results:
                    formatted_results = []
                    for result in results["organic"][:5]:  # Limit to top 5 results
                        formatted_results.append(f"Title: {result.get('title', 'N/A')}\nLink: {result.get('link', 'N/A')}\nSnippet: {result.get('snippet', 'N/A')}\n")
                    return "\n".join(formatted_results)
                else:
                    return "No search results found"
            else:
                return f"Search API error: {response.status_code}"
        except Exception as e:
            return f"Search error: {str(e)}"

# Create the search tool instance
search_tool = SearchTool()
