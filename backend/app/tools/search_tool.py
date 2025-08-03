# app/tools/search_tool.py
# AI-friendly web search tool with structured output and vehicle-specific capabilities
from crewai.tools import BaseTool
import requests
import os
import json
from typing import Dict, Any, Type, List, Optional
from pydantic import BaseModel, Field
import re

class SearchToolInput(BaseModel):
    """Input schema for AI-friendly SearchTool."""
    query: str = Field(..., description="Search query for web search")
    search_type: str = Field(
        default="general",
        description="Type of search: 'general', 'vehicle_specs', 'vehicle_reviews', 'market_data', 'problems', 'comparison'"
    )
    limit: int = Field(default=5, description="Number of results to return (1-10)")

class SearchResult(BaseModel):
    """Structured search result."""
    title: str
    url: str
    snippet: str
    relevance_score: float
    content_type: str  # 'review', 'specs', 'forum', 'news', 'dealer', 'other'

class SearchResponse(BaseModel):
    """Structured search response."""
    query: str
    search_type: str
    total_results: int
    results: List[SearchResult]
    suggested_queries: List[str]
    status: str
    error_message: Optional[str] = None

class AIFriendlySearchTool(BaseTool):
    name: str = "AI Web Search"
    description: str = (
        "Advanced web search tool optimized for AI agents. Provides structured, "
        "categorized results with relevance scoring. Specializes in vehicle information, "
        "specifications, reviews, market data, and comparisons. Returns JSON-formatted "
        "data that's easy for AI to parse and understand."
    )
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str, search_type: str = "general", limit: int = 5) -> str:
        """Search the web with AI-friendly structured output"""
        api_key = os.getenv("SERPER_API_KEY")
        
        if not api_key:
            return self._create_error_response(
                query, search_type, 
                "SERPER_API_KEY not configured. Please set the environment variable."
            )
        
        # Enhance query based on search type
        enhanced_query = self._enhance_query(query, search_type)
        
        try:
            # Make API request
            response_data = self._make_search_request(enhanced_query, api_key, limit)
            
            if not response_data:
                return self._create_error_response(
                    query, search_type, "No response from search API"
                )
            
            # Process and structure results
            structured_response = self._process_search_results(
                response_data, query, search_type, limit
            )
            
            return json.dumps(structured_response.dict(), indent=2)
            
        except Exception as e:
            return self._create_error_response(
                query, search_type, f"Search execution error: {str(e)}"
            )
    
    def _enhance_query(self, query: str, search_type: str) -> str:
        """Enhance search query based on search type"""
        query_enhancements = {
            "vehicle_specs": f"{query} specifications technical details engine transmission",
            "vehicle_reviews": f"{query} review test drive expert opinion pros cons",
            "market_data": f"{query} price market value depreciation cost ownership",
            "problems": f"{query} problems issues common faults reliability complaints",
            "comparison": f"{query} vs comparison differences which better choose"
        }
        
        return query_enhancements.get(search_type, query)
    
    def _make_search_request(self, query: str, api_key: str, limit: int) -> Optional[Dict]:
        """Make search API request"""
        url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "num": min(limit, 10)  # API limit
        }
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
    
    def _process_search_results(self, data: Dict, original_query: str, search_type: str, limit: int) -> SearchResponse:
        """Process raw search results into structured format"""
        results = []
        
        # Process organic results
        organic_results = data.get("organic", [])
        
        for i, result in enumerate(organic_results[:limit]):
            search_result = SearchResult(
                title=result.get("title", "No title"),
                url=result.get("link", ""),
                snippet=result.get("snippet", "No description available"),
                relevance_score=self._calculate_relevance_score(result, original_query, i),
                content_type=self._classify_content_type(result)
            )
            results.append(search_result)
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return SearchResponse(
            query=original_query,
            search_type=search_type,
            total_results=len(results),
            results=results,
            suggested_queries=self._generate_suggested_queries(original_query, search_type),
            status="success"
        )
    
    def _calculate_relevance_score(self, result: Dict, query: str, position: int) -> float:
        """Calculate relevance score for a search result"""
        score = 1.0
        
        # Position-based scoring (earlier results get higher scores)
        position_score = max(0.1, 1.0 - (position * 0.1))
        score *= position_score
        
        # Title relevance
        title = result.get("title", "").lower()
        query_words = query.lower().split()
        title_matches = sum(1 for word in query_words if word in title)
        if query_words:
            title_relevance = title_matches / len(query_words)
            score *= (1 + title_relevance)
        
        # Snippet relevance
        snippet = result.get("snippet", "").lower()
        snippet_matches = sum(1 for word in query_words if word in snippet)
        if query_words:
            snippet_relevance = snippet_matches / len(query_words)
            score *= (1 + snippet_relevance * 0.5)
        
        # Domain authority boost for known automotive sites
        url = result.get("link", "").lower()
        automotive_domains = [
            "edmunds.com", "kbb.com", "cargurus.com", "autotrader.com", 
            "cars.com", "carfax.com", "motortrend.com", "caranddriver.com",
            "autoblog.com", "topgear.com", "whatcar.com"
        ]
        
        if any(domain in url for domain in automotive_domains):
            score *= 1.3
        
        return round(score, 2)
    
    def _classify_content_type(self, result: Dict) -> str:
        """Classify the type of content based on URL and title"""
        url = result.get("link", "").lower()
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        
        # Check for specific content types
        if any(word in title + snippet for word in ["review", "test drive", "road test"]):
            return "review"
        elif any(word in title + snippet for word in ["specifications", "specs", "technical", "engine"]):
            return "specs"
        elif any(word in url for word in ["forum", "reddit", "discussion"]):
            return "forum"
        elif any(word in title + snippet for word in ["news", "announced", "launched"]):
            return "news"
        elif any(word in url for word in ["dealer", "showroom", "sales"]):
            return "dealer"
        else:
            return "other"
    
    def _generate_suggested_queries(self, query: str, search_type: str) -> List[str]:
        """Generate suggested follow-up queries"""
        suggestions = []
        
        if search_type == "general":
            suggestions = [
                f"{query} specifications",
                f"{query} reviews",
                f"{query} problems issues",
                f"{query} price market value"
            ]
        elif search_type == "vehicle_specs":
            suggestions = [
                f"{query} engine specifications",
                f"{query} fuel economy mpg",
                f"{query} dimensions weight",
                f"{query} safety features"
            ]
        elif search_type == "vehicle_reviews":
            suggestions = [
                f"{query} expert review",
                f"{query} owner reviews",
                f"{query} pros and cons",
                f"{query} test drive experience"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _create_error_response(self, query: str, search_type: str, error_message: str) -> str:
        """Create structured error response"""
        error_response = SearchResponse(
            query=query,
            search_type=search_type,
            total_results=0,
            results=[],
            suggested_queries=[],
            status="error",
            error_message=error_message
        )
        return json.dumps(error_response.dict(), indent=2)

# Create the search tool instance
search_tool = AIFriendlySearchTool()
