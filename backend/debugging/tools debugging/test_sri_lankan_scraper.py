#!/usr/bin/env python3

import asyncio
import requests
from bs4 import BeautifulSoup
import json
import sys
import traceback
from app.tools.sri_lankan_scraper import SriLankanAdScraperTool

async def test_individual_sites(vehicle_name):
    """Test each site individually to identify issues"""
    scraper = SriLankanAdScraperTool()
    
    print(f"Testing scraper for vehicle: {vehicle_name}")
    print("=" * 50)
    
    # Test ikman.lk
    print("\n1. Testing ikman.lk...")
    try:
        ikman_urls = await scraper._search_ikman(vehicle_name)
        print(f"   ✅ ikman.lk found {len(ikman_urls)} URLs:")
        for url in ikman_urls:
            print(f"      - {url}")
    except Exception as e:
        print(f"   ❌ ikman.lk failed: {str(e)}")
        print(f"      Error details: {traceback.format_exc()}")
    
    # Test riyasewana.com
    print("\n2. Testing riyasewana.com...")
    try:
        riyasewana_urls = await scraper._search_riyasewana(vehicle_name)
        print(f"   ✅ riyasewana.com found {len(riyasewana_urls)} URLs:")
        for url in riyasewana_urls:
            print(f"      - {url}")
    except Exception as e:
        print(f"   ❌ riyasewana.com failed: {str(e)}")
        print(f"      Error details: {traceback.format_exc()}")
    
    # Test patpat.lk
    print("\n3. Testing patpat.lk...")
    try:
        patpat_urls = await scraper._search_patpat(vehicle_name)
        print(f"   ✅ patpat.lk found {len(patpat_urls)} URLs:")
        for url in patpat_urls:
            print(f"      - {url}")
    except Exception as e:
        print(f"   ❌ patpat.lk failed: {str(e)}")
        print(f"      Error details: {traceback.format_exc()}")

async def test_site_connectivity():
    """Test basic connectivity to Sri Lankan car websites"""
    print("\nTesting site connectivity...")
    print("=" * 30)
    
    sites = [
        ("ikman.lk", "https://ikman.lk/en/ads/sri-lanka/cars"),
        ("riyasewana.com", "https://riyasewana.com/search/cars"),
        ("patpat.lk", "https://patpat.lk/vehicle")
    ]
    
    for site_name, url in sites:
        try:
            print(f"\nTesting {site_name}...")
            response = requests.get(url, timeout=10)
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Size: {len(response.content)} bytes")
            
            # Check if it's blocked or has anti-bot measures
            if "blocked" in response.text.lower() or "robot" in response.text.lower():
                print(f"   ⚠️  Possible anti-bot detection")
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")
            
            if response.status_code == 200:
                print(f"   ✅ {site_name} is accessible")
            else:
                print(f"   ❌ {site_name} returned status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ❌ {site_name} - Connection timeout")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {site_name} - Connection error")
        except Exception as e:
            print(f"   ❌ {site_name} - Error: {str(e)}")

async def test_search_url_formats(vehicle_name):
    """Test if the search URL formats are correct"""
    print(f"\nTesting search URL formats for '{vehicle_name}'...")
    print("=" * 40)
    
    urls = [
        f"https://ikman.lk/en/ads/sri-lanka/cars?query={vehicle_name.replace(' ', '%20')}",
        f"https://riyasewana.com/search/cars?q={vehicle_name.replace(' ', '+')}",
        f"https://patpat.lk/vehicle?search={vehicle_name.replace(' ', '+')}"
    ]
    
    for i, url in enumerate(urls, 1):
        print(f"\n{i}. Testing URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for search results or ad links
                if "ikman.lk" in url:
                    ad_links = soup.find_all('a', href=lambda x: x and '/en/ad/' in x)
                    print(f"   Found {len(ad_links)} potential ad links")
                elif "riyasewana.com" in url:
                    ad_links = soup.find_all('a', href=lambda x: x and '/ad/' in x)
                    print(f"   Found {len(ad_links)} potential ad links")
                elif "patpat.lk" in url:
                    ad_links = soup.find_all('a', href=lambda x: x and '/vehicle/' in x)
                    print(f"   Found {len(ad_links)} potential vehicle links")
                
                # Check for "no results" messages
                page_text = soup.get_text().lower()
                if any(phrase in page_text for phrase in ['no results', 'no ads found', 'not found']):
                    print(f"   ⚠️  No search results found")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def test_full_scraper_tool(vehicle_name):
    """Test the full scraper tool"""
    print(f"\nTesting full scraper tool for '{vehicle_name}'...")
    print("=" * 45)
    
    try:
        scraper = SriLankanAdScraperTool()
        result = await scraper._arun(vehicle_name)
        
        print("Scraper result:")
        print(result)
        
        # Parse the result
        result_data = json.loads(result)
        if result_data.get("status") == "success":
            urls = result_data.get("urls", [])
            print(f"\n✅ Scraper succeeded! Found {len(urls)} URLs")
            for url in urls:
                print(f"   - {url}")
        else:
            print(f"\n❌ Scraper failed: {result_data.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Scraper tool failed: {str(e)}")
        print(f"Error details: {traceback.format_exc()}")

async def main():
    """Main test function"""
    vehicle_name = "Toyota Aqua"
    
    print("Sri Lankan Ad Scraper Diagnostic Test")
    print("=====================================")
    
    # Test 1: Basic connectivity
    await test_site_connectivity()
    
    # Test 2: Search URL formats
    await test_search_url_formats(vehicle_name)
    
    # Test 3: Individual site scrapers
    await test_individual_sites(vehicle_name)
    
    # Test 4: Full scraper tool
    await test_full_scraper_tool(vehicle_name)
    
    print("\n" + "=" * 50)
    print("Diagnostic test completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        print(traceback.format_exc())
