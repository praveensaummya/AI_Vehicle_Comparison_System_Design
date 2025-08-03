#!/usr/bin/env python3
"""
Enhanced test to find correct selectors for ikman.lk
"""
from playwright.sync_api import sync_playwright
import re

def find_ikman_selectors():
    """Find the correct selectors for ikman.lk vehicle ads"""
    # Test with a real vehicle sale ad (not rental)
    test_urls = [
        "https://ikman.lk/en/ad/honda-vezel-z-premium-b-new-2025-for-sale-colombo-1",
        # Add more URLs if needed
    ]
    
    for url in test_urls:
        print(f"🔍 Testing URL: {url}")
        analyze_ikman_page(url)
        print("\n" + "="*80 + "\n")

def analyze_ikman_page(url):
    """Analyze an ikman.lk page to find the correct selectors"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)
            
            # Get the page HTML to analyze structure
            html_content = page.content()
            
            print("📝 Successfully extracted elements:")
            
            # Title - we know h1 works
            title = page.text_content('h1')
            print(f"  Title (h1): {title}")
            
            # Price - we know [data-testid="price"] works
            price = page.text_content('[data-testid="price"]')
            print(f"  Price ([data-testid=\"price\"]): {price}")
            
            # Look for location in various ways
            print("\n📍 Searching for location:")
            
            # Try to find location from breadcrumbs or other elements
            location_candidates = [
                '.breadcrumbs',
                '.breadcrumb',
                '[data-testid="breadcrumbs"]',
                '.location-breadcrumb',
                '.ad-location-breadcrumb'
            ]
            
            for selector in location_candidates:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.text_content()
                        if text and text.strip():
                            print(f"  ✅ {selector}: {text.strip()}")
                except:
                    pass
            
            # Look for location in the page text using patterns
            body_text = page.text_content('body')
            location_pattern = r'(?:Posted on.*?)([A-Za-z\s]+,\s*[A-Za-z\s]+)'
            location_matches = re.findall(location_pattern, body_text)
            if location_matches:
                print(f"  ✅ Pattern match: {location_matches[0].strip()}")
            
            # Look for specific ikman elements
            print(f"\n🔍 Looking for ikman-specific elements:")
            
            # Check all elements with data-testid attributes
            all_testids = page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('[data-testid]');
                    const testids = [];
                    elements.forEach(el => {
                        const testid = el.getAttribute('data-testid');
                        const text = el.textContent?.trim();
                        if (text && text.length < 200) {
                            testids.push({testid, text});
                        }
                    });
                    return testids;
                }
            """)
            
            print("  Elements with data-testid:")
            for item in all_testids[:20]:  # Show first 20
                print(f"    [{item['testid']}]: {item['text'][:100]}")
            
            # Look for year and mileage patterns in the page
            print(f"\n📅 Looking for year and mileage patterns:")
            
            # Year pattern (4 digits)
            year_pattern = r'\b(19|20)\d{2}\b'
            year_matches = re.findall(year_pattern, body_text)
            if year_matches:
                full_years = [y + m for y, m in year_matches]
                print(f"  Year candidates: {full_years}")
            
            # Mileage patterns
            mileage_patterns = [
                r'\b(\d{1,3}(?:,\d{3})*)\s*km\b',
                r'\b(\d+)\s*(?:k|K)(?:m|M)?\b',
                r'mileage[:\s]*(\d+(?:,\d{3})*)',
                r'(\d+(?:,\d{3})*)\s*(?:kilometers|kilometres)'
            ]
            
            for pattern in mileage_patterns:
                matches = re.findall(pattern, body_text, re.IGNORECASE)
                if matches:
                    print(f"  Mileage pattern '{pattern}': {matches}")
            
            # Check for details section or specs
            print(f"\n📊 Looking for vehicle details/specs sections:")
            
            details_selectors = [
                '.vehicle-details',
                '.ad-details',
                '.specifications',
                '.specs',
                '.details-section',
                '[data-testid="ad-details"]',
                '[data-testid="specifications"]'
            ]
            
            for selector in details_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.text_content()
                        if text and text.strip():
                            print(f"  ✅ {selector}: {text.strip()[:200]}...")
                except:
                    pass
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    find_ikman_selectors()
