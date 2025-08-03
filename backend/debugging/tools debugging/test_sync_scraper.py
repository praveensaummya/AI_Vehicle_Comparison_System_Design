#!/usr/bin/env python3
# test_sync_scraper.py

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.tools.sync_beautifulsoup_scraper import extract_ad_details_sync, batch_extract_ad_details_sync
from app.tools.sync_ad_details_tool import SyncAdDetailsExtractorTool
import json

def test_sync_scraper():
    """Test the synchronous scraper with sample URLs"""
    print("🧪 Testing Synchronous BeautifulSoup Scraper")
    print("=" * 50)
    
    # Test URLs - using generic test URLs since we don't have real ikman.lk URLs
    test_urls = [
        "https://httpbin.org/html",  # Simple HTML test
        "https://httpbin.org/json",  # JSON response test
    ]
    
    print("📋 Test URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"  {i}. {url}")
    
    print("\n🔄 Testing single URL extraction...")
    try:
        result = extract_ad_details_sync(test_urls[0])
        print("✅ Single extraction successful:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Single extraction failed: {e}")
    
    print("\n🔄 Testing batch URL extraction...")
    try:
        results = batch_extract_ad_details_sync(test_urls)
        print(f"✅ Batch extraction successful - processed {len(results)} URLs:")
        for i, result in enumerate(results, 1):
            print(f"  Result {i}: {result.get('ad_title', 'No title')[:50]}...")
    except Exception as e:
        print(f"❌ Batch extraction failed: {e}")
    
    print("\n🔧 Testing CrewAI Tool...")
    try:
        tool = SyncAdDetailsExtractorTool()
        tool_result = tool._run(test_urls, parallel=True)
        print("✅ CrewAI tool test successful")
        print("📊 Tool result length:", len(tool_result))
    except Exception as e:
        print(f"❌ CrewAI tool test failed: {e}")
    
    print("\n✨ Sync scraper tests completed!")

if __name__ == "__main__":
    test_sync_scraper()
