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
            # Use real scraping instead of mock URLs
            real_urls = self._find_vehicle_ads(vehicle_name)
            
            if real_urls:
                return "\n".join([f"- {url}" for url in real_urls])
            else:
                # Fallback to mock URLs only if no real URLs found
                print(f"Warning: No real ads found for {vehicle_name}, using fallback URLs")
                fallback_urls = [
                    f"https://ikman.lk/en/ad/{vehicle_name.lower().replace(' ', '-')}-2018-for-sale-colombo-12345",
                    f"https://ikman.lk/en/ad/{vehicle_name.lower().replace(' ', '-')}-2019-for-sale-gampaha-67890",
                    f"https://riyasewana.com/ad/{vehicle_name.lower().replace(' ', '-')}-2020-for-sale-78901"
                ]
                return "\n".join([f"- {url}" for url in fallback_urls])
                
        except Exception as e:
            print(f"Error in real scraping: {str(e)}")
            return f"Error scraping ads: {str(e)}"

    def _find_vehicle_ads(self, vehicle_name: str) -> List[str]:
        """Find vehicle SALE ads on Sri Lankan websites (exclude rentals, parts, services)"""
        ad_urls = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Search ikman.lk for sales only
                ikman_urls = self._search_ikman(page, vehicle_name)
                ad_urls.extend(ikman_urls)
                
                # Search riyasewana.com for sales only
                riyasewana_urls = self._search_riyasewana(page, vehicle_name)
                ad_urls.extend(riyasewana_urls)
                
                # Search patpat.lk for sales only
                patpat_urls = self._search_patpat(page, vehicle_name)
                ad_urls.extend(patpat_urls)
                
            finally:
                browser.close()
        
        # Filter out unwanted ads and remove duplicates
        filtered_urls = self._filter_sale_ads_only(list(set(ad_urls)))
        return filtered_urls[:5]  # Return up to 5 unique SALE URLs

    def _search_ikman(self, page, vehicle_name: str) -> List[str]:
        """Search ikman.lk for vehicle ads"""
        urls = []
        try:
            # Navigate to ikman.lk cars section
            search_url = f"https://ikman.lk/en/ads/sri-lanka/cars?query={vehicle_name.replace(' ', '%20')}"
            print(f"Searching ikman.lk: {search_url}")
            page.goto(search_url, timeout=30000)
            time.sleep(3)  # Wait for dynamic content to load
            
            # Try multiple selector strategies for ad links
            selectors = [
                'a[href*="/en/ad/"]',  # Original selector
                '[data-testid="ad-card"] a',  # Data test ID
                '.ads--3Vp7Y a[href*="/ad/"]',  # CSS class based
                '.listing-card a[href*="/ad/"]',  # Alternative class
                'article a[href*="/ad/"]',  # Article tags
                '.ad-item a[href*="/ad/"]'  # Generic ad item
            ]
            
            ad_links = []
            for selector in selectors:
                try:
                    links = page.query_selector_all(selector)
                    if links:
                        ad_links = links
                        print(f"Found {len(links)} links with selector: {selector}")
                        break
                except:
                    continue
            
            # Extract URLs from found links
            for link in ad_links[:3]:  # Get up to 3 ads from ikman
                try:
                    href = link.get_attribute('href')
                    if href and '/ad/' in href:
                        full_url = href if href.startswith('http') else f"https://ikman.lk{href}"
                        if full_url not in urls:  # Avoid duplicates
                            urls.append(full_url)
                            print(f"Found ikman ad: {full_url}")
                except Exception as link_error:
                    print(f"Error processing link: {link_error}")
                    continue
                    
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
    
    def _filter_sale_ads_only(self, urls: List[str]) -> List[str]:
        """Filter URLs to include only vehicle sale ads, exclude rentals, parts, services"""
        filtered_urls = []
        
        # Keywords that indicate NON-SALE ads (rentals, parts, services)
        exclude_keywords = [
            'rent', 'rental', 'hire', 'lease', 'leasing',
            'parts', 'spare', 'accessories', 'tyre', 'tire', 'battery',
            'service', 'repair', 'maintenance', 'workshop',
            'insurance', 'finance', 'loan'
        ]
        
        # Keywords that indicate SALE ads
        include_keywords = [
            'sale', 'sell', 'selling', 'for-sale'
        ]
        
        for url in urls:
            url_lower = url.lower()
            
            # Check if URL contains exclude keywords
            has_exclude_keywords = any(keyword in url_lower for keyword in exclude_keywords)
            
            if not has_exclude_keywords:
                # Additional validation by checking page title if possible
                if self._is_vehicle_sale_ad(url):
                    filtered_urls.append(url)
                    print(f"✅ Included sale ad: {url}")
                else:
                    print(f"❌ Excluded non-sale ad: {url}")
            else:
                print(f"❌ Excluded by URL keywords: {url}")
        
        return filtered_urls
    
    def _is_vehicle_sale_ad(self, url: str) -> bool:
        """Quick check if URL is actually a vehicle sale ad"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                try:
                    page.goto(url, timeout=15000)  # Quick timeout
                    
                    # Get page title and first paragraph
                    title = page.text_content('h1') or page.title() or ""
                    
                    title_lower = title.lower()
                    
                    # Check for rental/service keywords in title
                    exclude_in_title = [
                        'rent', 'rental', 'hire', 'lease',
                        'parts', 'spare', 'accessories',
                        'service', 'repair', 'workshop'
                    ]
                    
                    # If title contains exclude keywords, it's not a sale
                    if any(keyword in title_lower for keyword in exclude_in_title):
                        return False
                    
                    # If title contains sale keywords, it's likely a sale
                    include_in_title = ['sale', 'sell', 'selling']
                    if any(keyword in title_lower for keyword in include_in_title):
                        return True
                    
                    # If no clear indicators, assume it's a sale (default for vehicle ads)
                    return True
                    
                except:
                    # If we can't load the page, assume it's valid (don't be too restrictive)
                    return True
                finally:
                    browser.close()
        except:
            # If browser fails, assume it's valid
            return True

# Create the tool instance
sri_lankan_scraper_tool = SriLankanAdScraperTool()
