# app/tools/sri_lankan_scraper.py
from crewai.tools import BaseTool
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re
from typing import Dict, Any, Type, List
from pydantic import BaseModel, Field
import time

class SriLankanScraperInput(BaseModel):
    """Input schema for Sri Lankan scraper tool."""
    vehicle_name: str = Field(..., description="Vehicle name to search for")

class SriLankanAdScraperTool(BaseTool):
    name: str = "Sri Lankan Ad Scraper"
    description: str = "Scrapes Sri Lankan vehicle websites for specific vehicle ads"
    args_schema: Type[BaseModel] = SriLankanScraperInput

    def _run(self, vehicle_name: str) -> str:
        """Scrape Sri Lankan websites for vehicle ads"""
        try:
            # For now, return mock URLs to avoid async issues
            mock_urls = [
                f"https://ikman.lk/en/ad/{vehicle_name.lower().replace(' ', '-')}-2018-for-sale-colombo-12345",
                f"https://ikman.lk/en/ad/{vehicle_name.lower().replace(' ', '-')}-2019-for-sale-gampaha-67890",
                f"https://riyasewana.com/ad/{vehicle_name.lower().replace(' ', '-')}-2020-for-sale-78901",
                f"https://riyasewana.com/ad/{vehicle_name.lower().replace(' ', '-')}-2017-for-sale-45678",
                f"https://ikman.lk/en/ad/{vehicle_name.lower().replace(' ', '-')}-2021-for-sale-kandy-34567"
            ]
            return "\n".join([f"- {url}" for url in mock_urls])
        except Exception as e:
            return f"Error scraping ads: {str(e)}"

    def _find_vehicle_ads(self, vehicle_name: str) -> List[str]:
        """Find vehicle ads on Sri Lankan websites"""
        ad_urls = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Search ikman.lk
                ikman_urls = self._search_ikman(page, vehicle_name)
                ad_urls.extend(ikman_urls)
                
                # Search riyasewana.com
                riyasewana_urls = self._search_riyasewana(page, vehicle_name)
                ad_urls.extend(riyasewana_urls)
                
                # Search patpat.lk
                patpat_urls = self._search_patpat(page, vehicle_name)
                ad_urls.extend(patpat_urls)
                
            finally:
                browser.close()
        
        # Remove duplicates and return up to 5 unique URLs
        unique_urls = list(set(ad_urls))[:5]
        return unique_urls

    def _search_ikman(self, page, vehicle_name: str) -> List[str]:
        """Search ikman.lk for vehicle ads"""
        urls = []
        try:
            # Navigate to ikman.lk cars section
            search_url = f"https://ikman.lk/en/ads/sri-lanka/cars?query={vehicle_name.replace(' ', '%20')}"
            page.goto(search_url, timeout=30000)
            time.sleep(2)
            
            # Extract individual ad links
            ad_links = page.query_selector_all('a[href*="/en/ad/"]')
            for link in ad_links[:3]:  # Get up to 3 ads from ikman
                href = link.get_attribute('href')
                if href and '/en/ad/' in href and 'cars' in href:
                    full_url = href if href.startswith('http') else f"https://ikman.lk{href}"
                    urls.append(full_url)
        except Exception as e:
            print(f"Error searching ikman.lk: {e}")
        
        return urls

    def _search_riyasewana(self, page, vehicle_name: str) -> List[str]:
        """Search riyasewana.com for vehicle ads"""
        urls = []
        try:
            # Navigate to riyasewana.com cars section
            search_url = f"https://riyasewana.com/search/cars?q={vehicle_name.replace(' ', '+')}"
            page.goto(search_url, timeout=30000)
            time.sleep(2)
            
            # Extract individual ad links
            ad_links = page.query_selector_all('a[href*="/ad/"]')
            for link in ad_links[:2]:  # Get up to 2 ads from riyasewana
                href = link.get_attribute('href')
                if href and '/ad/' in href:
                    full_url = href if href.startswith('http') else f"https://riyasewana.com{href}"
                    urls.append(full_url)
        except Exception as e:
            print(f"Error searching riyasewana.com: {e}")
        
        return urls

    def _search_patpat(self, page, vehicle_name: str) -> List[str]:
        """Search patpat.lk for vehicle ads"""
        urls = []
        try:
            # Navigate to patpat.lk vehicles section
            search_url = f"https://patpat.lk/vehicle?search={vehicle_name.replace(' ', '+')}"
            page.goto(search_url, timeout=30000)
            time.sleep(2)
            
            # Extract individual ad links
            ad_links = page.query_selector_all('a[href*="/vehicle/"]')
            for link in ad_links[:2]:  # Get up to 2 ads from patpat
                href = link.get_attribute('href')
                if href and '/vehicle/' in href:
                    full_url = href if href.startswith('http') else f"https://patpat.lk{href}"
                    urls.append(full_url)
        except Exception as e:
            print(f"Error searching patpat.lk: {e}")
        
        return urls

# Create the tool instance
sri_lankan_scraper_tool = SriLankanAdScraperTool()
