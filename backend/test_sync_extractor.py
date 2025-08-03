#!/usr/bin/env python3
"""
Test script for the synchronous real data ad extractor
"""

import sys
import json
from pathlib import Path

# Add the app directory to Python path
backend_dir = Path(__file__).parent
app_dir = backend_dir / "app"
sys.path.insert(0, str(backend_dir))

def test_sync_extractor():
    """Test the synchronous ad extractor tool with real data"""
    print("🧪 Testing Synchronous Real Data Ad Extractor...")
    
    try:
        from app.tools.sync_ad_extractor import sync_ad_extractor_tool
        
        # Test URLs - using actual ikman.lk URLs
        test_urls = """
        https://ikman.lk/en/ad/suzuki-alto-lxi-850-2018-for-sale-gampaha
        https://ikman.lk/en/ad/suzuki-alto-g-grade-2018-for-sale-colombo
        https://ikman.lk/en/ad/suzuki-alto-2018-for-sale-gampaha-14
        """
        
        print("📋 Test Input URLs:")
        for url in test_urls.strip().split('\n'):
            if url.strip():
                print(f"  • {url.strip()}")
        
        print("\n🔄 Running synchronous real data extractor...")
        result = sync_ad_extractor_tool._run(
            urls=test_urls,
            vehicle_name="Suzuki Alto",
            timeout=15  # Shorter timeout for testing
        )
        
        print("✅ Extraction completed!")
        
        # Parse and display results
        result_data = json.loads(result)
        
        print(f"\n📊 Results Summary:")
        print(f"  Status: {result_data.get('status')}")
        print(f"  Ad Count: {result_data.get('ad_count')}")
        print(f"  Quality Score: {result_data.get('quality_score')}")
        print(f"  Processing Mode: {result_data.get('processing_mode')}")
        
        summary = result_data.get('summary', {})
        print(f"  Data Source: {summary.get('data_source')}")
        print(f"  Extraction Method: {summary.get('extraction_method')}")
        print(f"  Extraction Successful: {summary.get('extraction_successful')}")
        
        print(f"\n🚗 Extracted Ads:")
        ads = result_data.get('ads', [])
        
        for i, ad in enumerate(ads, 1):
            print(f"\n  Ad #{i}:")
            print(f"    Title: {ad.get('Ad Title')}")
            print(f"    Price: {ad.get('Price (in LKR)')}")
            print(f"    Location: {ad.get('Location')}")
            print(f"    Year: {ad.get('Year of Manufacture')}")
            print(f"    Mileage: {ad.get('Mileage (in km)')}")
            
            if 'Condition' in ad:
                print(f"    Condition: {ad.get('Condition')}")
            if 'Transmission' in ad:
                print(f"    Transmission: {ad.get('Transmission')}")
            if 'Fuel Type' in ad:
                print(f"    Fuel Type: {ad.get('Fuel Type')}")
            
            print(f"    URL: {ad.get('URL')}")
            
            # Show metadata
            metadata = ad.get('_metadata', {})
            print(f"    Quality: {metadata.get('quality')}")
            print(f"    Confidence: {metadata.get('confidence')}")
            print(f"    Fields Extracted: {metadata.get('fields_extracted')}")
            
            if 'error_type' in metadata:
                print(f"    Error Type: {metadata.get('error_type')}")
            if '_extraction_error' in ad:
                print(f"    Extraction Error: {ad.get('_extraction_error')}")
        
        # Analyze results
        successful_ads = [ad for ad in ads if not ad.get('Ad Title', '').startswith('Error') and not ad.get('Ad Title', '').startswith('Timeout')]
        error_ads = [ad for ad in ads if ad.get('Ad Title', '').startswith('Error') or ad.get('Ad Title', '').startswith('Timeout')]
        
        print(f"\n📈 Analysis:")
        print(f"  Total URLs Processed: {len(ads)}")
        print(f"  Successful Extractions: {len(successful_ads)}")
        print(f"  Failed/Error Extractions: {len(error_ads)}")
        print(f"  Success Rate: {(len(successful_ads)/len(ads)*100):.1f}%" if ads else "0%")
        
        if successful_ads:
            print("\n✅ Real data extraction is working!")
            return True
        else:
            print("\n⚠️ No successful extractions. This might be due to:")
            print("  - Network connectivity issues")
            print("  - Website structure changes")
            print("  - Rate limiting or blocking")
            print("  - Timeout issues")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_url_parsing():
    """Test URL parsing functionality"""
    print("\n🧪 Testing URL Parsing...")
    
    try:
        from app.tools.sync_ad_extractor import SynchronousAdExtractor
        
        extractor = SynchronousAdExtractor()
        
        # Test different URL formats
        test_cases = [
            "https://ikman.lk/en/ad/test-1\nhttps://riyasewana.com/ad/test-2",
            "- https://ikman.lk/en/ad/test-3\n* https://riyasewana.com/ad/test-4",
            "• https://ikman.lk/en/ad/test-5\nhttps://example.com/test-6"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n  Test Case #{i}:")
            print(f"    Input: {repr(test_case)}")
            
            urls = extractor._parse_urls(test_case)
            print(f"    Parsed URLs: {urls}")
            print(f"    Count: {len(urls)}")
        
        print("\n✅ URL parsing test completed!")
        return True
        
    except Exception as e:
        print(f"❌ URL parsing test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Synchronous Real Data Ad Extractor Tests\n")
    
    test_results = []
    
    # Run tests
    test_results.append(("URL Parsing", test_url_parsing()))
    test_results.append(("Sync Real Data Extractor", test_sync_extractor()))
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 Test Results Summary:")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! The synchronous real data extractor is ready!")
        print("\n📝 Next Steps:")
        print("  1. The extractor will now fetch real data from websites")
        print("  2. CrewAI agents will use synchronous HTTP requests")
        print("  3. No more async/await complexity issues")
        print("  4. Better compatibility with CrewAI's synchronous nature")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("  - Check network connectivity")
        print("  - Verify website accessibility")
        print("  - Consider adjusting timeout values")
        print("  - Check if websites have changed their structure")
    
    return passed == len(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
