#!/usr/bin/env python3
"""
Test script to debug web scraping selectors
"""
from app.tools.playwright_scraper import extract_ad_details
from playwright.sync_api import sync_playwright

def test_real_url():
    """Test scraping with a real URL from the database"""
    # Using one of the URLs from the database
    test_url = "https://ikman.lk/en/ad/toyota-aqua-for-rent-for-sale-colombo-637"
    
    print(f"🔍 Testing scraper with URL: {test_url}")
    
    # Test the current scraper
    print("\n📊 Current scraper results:")
    result = extract_ad_details(test_url)
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # Now let's inspect the actual page structure
    print("\n🔎 Inspecting actual page structure...")
    inspect_page_structure(test_url)

def inspect_page_structure(url):
    """Inspect the actual HTML structure of the page"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to see the browser
        page = browser.new_page()
        
        try:
            print(f"Loading page: {url}")
            page.goto(url, timeout=30000)
            
            # Wait for content to load
            page.wait_for_timeout(3000)
            
            # Try to find title elements
            print("\n📝 Looking for title elements:")
            title_selectors = [
                'h1', '.ad-title', '.title', '[data-testid="ad-title"]', 
                '.listing-title', '.gtm-ad-title', '.ad-post-title'
            ]
            
            for selector in title_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.text_content()
                        if text and text.strip():
                            print(f"  ✅ {selector}: {text.strip()[:100]}")
                        else:
                            print(f"  ❌ {selector}: Found but empty")
                    else:
                        print(f"  ❌ {selector}: Not found")
                except Exception as e:
                    print(f"  ❌ {selector}: Error - {e}")
            
            # Try to find price elements
            print("\n💰 Looking for price elements:")
            price_selectors = [
                '.price', '.ad-price', '[data-testid="price"]', 
                '.listing-price', '.amount', '.gtm-ad-price', '.price-text'
            ]
            
            for selector in price_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.text_content()
                        if text and text.strip():
                            print(f"  ✅ {selector}: {text.strip()}")
                        else:
                            print(f"  ❌ {selector}: Found but empty")
                    else:
                        print(f"  ❌ {selector}: Not found")
                except Exception as e:
                    print(f"  ❌ {selector}: Error - {e}")
            
            # Try to find location elements
            print("\n📍 Looking for location elements:")
            location_selectors = [
                '.location', '.ad-location', '[data-testid="location"]', 
                '.city', '.area', '.gtm-ad-location', '.location-text'
            ]
            
            for selector in location_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.text_content()
                        if text and text.strip():
                            print(f"  ✅ {selector}: {text.strip()}")
                        else:
                            print(f"  ❌ {selector}: Found but empty")
                    else:
                        print(f"  ❌ {selector}: Not found")
                except Exception as e:
                    print(f"  ❌ {selector}: Error - {e}")
            
            # Get page title for reference
            page_title = page.title()
            print(f"\n📄 Page title: {page_title}")
            
            # Get some general info about the page
            print("\n🔍 General page inspection:")
            all_text = page.text_content('body')[:500]
            print(f"  Body text preview: {all_text}...")
            
            # Check if this is actually a valid ikman.lk ad page
            if "ikman.lk" in url:
                print("\n🔗 Ikman.lk specific checks:")
                # Check for ikman-specific elements
                ikman_selectors = [
                    '.ad-detail-title', '.ui-title-price', '.price-section',
                    '.location-section', '.description-section'
                ]
                
                for selector in ikman_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            text = element.text_content()
                            print(f"  ✅ {selector}: {text.strip()[:100] if text else 'Found but empty'}")
                        else:
                            print(f"  ❌ {selector}: Not found")
                    except Exception as e:
                        print(f"  ❌ {selector}: Error - {e}")
        
        except Exception as e:
            print(f"❌ Error loading page: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_real_url()
