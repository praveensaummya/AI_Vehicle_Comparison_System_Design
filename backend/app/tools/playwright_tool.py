# app/tools/playwright_tool.py
from crewai_tools import BaseTool
from app.tools.playwright_scraper import batch_extract_ad_details

class PlaywrightBatchExtractTool(BaseTool):
    name = "PlaywrightBatchExtract"
    description = "Extracts ad details from a list of URLs using Playwright."

    def _run(self, urls: list):
        return batch_extract_ad_details(urls)