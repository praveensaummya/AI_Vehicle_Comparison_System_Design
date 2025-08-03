# app/tools/beautifulsoup_scraper.py
import requests
from bs4 import BeautifulSoup
import re
import asyncio
from typing import Dict, Any, List

async def extract_ad_details_async(url: str) -> Dict[str, Any]:
    """
    Asynchronously extracts ad details from a given URL using requests and BeautifulSoup.
    """
    try:
        response = await asyncio.to_thread(requests.get, url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title_element = soup.find('h1')
        title = title_element.text.strip() if title_element else "Not Found"

        # Extract price
        price_element = soup.find(attrs={"data-testid": "price"})
        price = price_element.text.strip() if price_element else "Not Found"

        # Extract location
        sublocation_element = soup.find(attrs={"data-testid": "subtitle-sublocation-link"})
        sublocation = sublocation_element.text.strip() if sublocation_element else None
        
        parentlocation_element = soup.find(attrs={"data-testid": "subtitle-parentlocation-link"})
        parentlocation = parentlocation_element.text.strip() if parentlocation_element else None
        
        location = ", ".join(filter(None, [sublocation, parentlocation])) or "Not Found"

        # Extract mileage and year from page content
        body_content = soup.get_text()
        
        mileage = "Not Found"
        mileage_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*km', body_content, re.IGNORECASE)
        if mileage_match:
            mileage = mileage_match.group()

        year = "Not Found"
        year_match = re.search(r'\b(19|20)\d{2}\b', body_content)
        if year_match:
            year = year_match.group()

        return {
            "ad_title": title,
            "price_lkr": price,
            "location": location,
            "mileage_km": mileage,
            "year": year,
            "url": url
        }
    except requests.RequestException as e:
        return {
            "ad_title": f"Error: {e}",
            "price_lkr": "Error",
            "location": "Error",
            "mileage_km": "Error",
            "year": "Error",
            "url": url
        }

async def batch_extract_ad_details_async(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Asynchronously extracts ad details from a list of URLs.
    """
    tasks = [extract_ad_details_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
