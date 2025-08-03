# app/tools/sync_beautifulsoup_scraper.py
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List
import time
import concurrent.futures

def extract_ad_details_sync(url: str) -> Dict[str, Any]:
    """
    Synchronously extracts ad details from a given URL using requests and BeautifulSoup.
    """
    try:
        response = requests.get(url, timeout=10)
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

def batch_extract_ad_details_sync(urls: List[str], max_workers: int = 5) -> List[Dict[str, Any]]:
    """
    Extract ad details from multiple URLs using ThreadPoolExecutor for parallel processing.
    """
    if not urls:
        return []
    
    results = []
    
    # Use ThreadPoolExecutor for parallel requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_url = {executor.submit(extract_ad_details_sync, url): url for url in urls}
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_url, timeout=60):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                url = future_to_url[future]
                error_result = {
                    "ad_title": f"Error: {e}",
                    "price_lkr": "Error",
                    "location": "Error",
                    "mileage_km": "Error",
                    "year": "Error",
                    "url": url
                }
                results.append(error_result)
    
    return results

def extract_ad_details_sequential(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Extract ad details sequentially for maximum reliability (slower but more stable).
    """
    results = []
    for url in urls:
        try:
            result = extract_ad_details_sync(url)
            results.append(result)
            # Small delay to be respectful to the server
            time.sleep(0.5)
        except Exception as e:
            error_result = {
                "ad_title": f"Error: {e}",
                "price_lkr": "Error",
                "location": "Error",
                "mileage_km": "Error",
                "year": "Error",
                "url": url
            }
            results.append(error_result)
    
    return results
