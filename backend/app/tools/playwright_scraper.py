# app/tools/playwright_scraper.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re

def interpret_mileage(raw_mileage: str) -> str:
    """
    Intelligently interpret mileage values, converting abbreviated forms to full values.
    
    Examples:
    - "50" or "50 km" -> "50,000 km" (if context suggests it's vehicle mileage)
    - "just 25km" -> "25,000 km"
    - "only 80" -> "80,000 km"
    - "125,000 km" -> "125,000 km" (already proper format)
    """
    if not raw_mileage or raw_mileage.strip().lower() in ['not found', 'error', '']:
        return raw_mileage
    
    # Clean the input
    mileage_text = raw_mileage.strip().lower()
    
    # Look for patterns that suggest abbreviated mileage
    # Pattern 1: "just X" or "only X" where X is a small number
    abbreviated_pattern = r'(?:just|only)\s*(\d{1,3})(?:\s*k?m?)?'
    match = re.search(abbreviated_pattern, mileage_text)
    if match:
        number = int(match.group(1))
        if number < 500:  # Likely abbreviated (e.g., "just 50" means "50,000")
            return f"{number * 1000:,} km"
    
    # Pattern 2: Simple number under 500 followed by km (likely abbreviated)
    simple_pattern = r'^(\d{1,3})\s*k?m?$'
    match = re.search(simple_pattern, mileage_text)
    if match:
        number = int(match.group(1))
        if number < 500:  # Likely abbreviated
            return f"{number * 1000:,} km"
        else:
            return f"{number:,} km"
    
    # Pattern 3: Already properly formatted large numbers
    proper_pattern = r'(\d{1,3}(?:,\d{3})+)\s*km?'
    match = re.search(proper_pattern, mileage_text)
    if match:
        return f"{match.group(1)} km"
    
    # Pattern 4: Large numbers without commas
    large_number_pattern = r'^(\d{4,})\s*k?m?$'
    match = re.search(large_number_pattern, mileage_text)
    if match:
        number = int(match.group(1))
        return f"{number:,} km"
    
    # If no pattern matches, return original (might be valid as-is or truly "Not Found")
    return raw_mileage

def extract_ad_details(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=60000)
            
            # Enhanced selectors for Sri Lankan websites
            title = (
                page.text_content('h1') or 
                page.text_content('.ad-title') or 
                page.text_content('.title') or 
                page.text_content('[data-testid="ad-title"]') or 
                page.text_content('.listing-title') or
                "Not Found"
            )
            
            price = (
                page.text_content('.price') or 
                page.text_content('.ad-price') or 
                page.text_content('[data-testid="price"]') or 
                page.text_content('.listing-price') or 
                page.text_content('.amount') or
                "Not Found"
            )
            
            location = (
                page.text_content('.location') or 
                page.text_content('.ad-location') or 
                page.text_content('[data-testid="location"]') or 
                page.text_content('.city') or 
                page.text_content('.area') or
                "Not Found"
            )
            
            mileage = (
                page.text_content('.mileage') or 
                page.text_content('.ad-mileage') or 
                page.text_content('[data-testid="mileage"]') or 
                page.text_content('.km') or 
                page.text_content('.odometer') or
                "Not Found"
            )
            
            year = (
                page.text_content('.year') or 
                page.text_content('.ad-year') or 
                page.text_content('[data-testid="year"]') or 
                page.text_content('.model-year') or 
                page.text_content('.manufacture-year') or
                "Not Found"
            )
            
        except PlaywrightTimeoutError:
            title = price = location = mileage = year = "Not Found"
        except Exception as e:
            title = price = location = mileage = year = f"Error: {e}"
        finally:
            browser.close()
            
        # Apply intelligent mileage interpretation
        processed_mileage = interpret_mileage(mileage) if mileage else "Not Found"
        
        return {
            "Ad Title": title.strip() if title else "Not Found",
            "Price (in LKR)": price.strip() if price else "Not Found",
            "Location": location.strip() if location else "Not Found",
            "Mileage (in km)": processed_mileage,
            "Year of Manufacture": year.strip() if year else "Not Found",
            "URL": url
        }

def batch_extract_ad_details(urls: list) -> list:
    results = []
    for url in urls:
        results.append(extract_ad_details(url))
    return results