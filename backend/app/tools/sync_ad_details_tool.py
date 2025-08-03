# app/tools/sync_ad_details_tool.py
from crewai.tools import BaseTool
from app.tools.sync_beautifulsoup_scraper import batch_extract_ad_details_sync, extract_ad_details_sequential
from typing import Dict, Any, Type, List
from pydantic import BaseModel, Field
import json

class SyncAdDetailsExtractorInput(BaseModel):
    """Input schema for SyncAdDetailsExtractorTool."""
    urls: List[str] = Field(..., description="List of URLs to extract details from")
    parallel: bool = Field(default=True, description="Use parallel processing (faster) or sequential (more reliable)")

class SyncAdDetailsExtractorTool(BaseTool):
    name: str = "Sync Ad Details Extractor"
    description: str = "Extracts structured ad details from URLs using synchronous requests and BeautifulSoup. No AsyncIO conflicts."
    args_schema: Type[BaseModel] = SyncAdDetailsExtractorInput

    def _run(self, urls: List[str], parallel: bool = True) -> str:
        """Synchronous execution of the tool - no async needed."""
        try:
            if parallel:
                # Use parallel processing with ThreadPoolExecutor
                results = batch_extract_ad_details_sync(urls, max_workers=3)
            else:
                # Use sequential processing for maximum reliability
                results = extract_ad_details_sequential(urls)
            
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to extract details: {str(e)}"})

    async def _arun(self, urls: List[str], parallel: bool = True) -> str:
        """Asynchronous execution - just calls the sync version."""
        return self._run(urls, parallel)
