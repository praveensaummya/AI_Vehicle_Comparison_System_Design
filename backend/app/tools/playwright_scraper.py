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
            
            # Enhanced selectors for ikman.lk
            title = (
                page.text_content('h1') or 
                "Not Found"
            )
            
            price = (
                page.text_content('[data-testid="price"]') or 
                "Not Found"
            )
            
            # For location, try both sublocation and parent location
            sublocation = page.text_content('[data-testid="subtitle-sublocation-link"]')
            parentlocation = page.text_content('[data-testid="subtitle-parentlocation-link"]')
            
            if sublocation and parentlocation:
                location = f"{sublocation.strip()}, {parentlocation.strip()}"
            elif sublocation:
                location = sublocation.strip()
            elif parentlocation:
                location = parentlocation.strip()
            else:
                location = "Not Found"
            
            # Extract mileage and year from ad metadata or page content
            page_text = page.text_content('body')
            
            # Look for mileage in page content
            mileage_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*km', page_text, re.IGNORECASE)
            if mileage_match:
                mileage = mileage_match.group(0)
            else:
                mileage = "Not Found"
            
            # Look for year in page content (4-digit year)
            year_match = re.search(r'\b(19|20)\d{2}\b', page_text)
            if year_match:
                year = year_match.group(0)
            else:
                year = "Not Found"
            
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