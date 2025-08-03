#!/usr/bin/env python3
"""
Test script for the simplified ad extractor tool
"""

import sys
import json
from pathlib import Path

# Add the app directory to Python path
backend_dir = Path(__file__).parent
app_dir = backend_dir / "app"
sys.path.insert(0, str(backend_dir))

def test_simple_extractor():
    """Test the simplified ad extractor tool"""
    print("🧪 Testing Simplified Ad Extractor Tool...")
    
    try:
        from app.tools.simple_ad_extractor import simple_ad_extractor_tool
        
        # Test URLs
        test_urls = """
        https://ikman.lk/en/ad/toyota-prius-4th-2016-for-sale-colombo-1
        https://ikman.lk/en/ad/toyota-prius-2010-for-sale-colombo-1310
        https://ikman.lk/en/ad/suzuki-alto-2019-for-sale-gampaha
        https://riyasewana.com/ad/honda-fit-2020-for-sale
        https://ikman.lk/en/ad/nissan-march-2018-for-sale-kandy
        """
        
        print("📋 Test Input URLs:")
        for url in test_urls.strip().split('\n'):
            if url.strip():
                print(f"  • {url.strip()}")
        
        print("\n🔄 Running extractor...")
        result = simple_ad_extractor_tool._run(
            urls=test_urls,
            vehicle_name="Toyota Prius",
            use_mock=True
        )
        
        print("✅ Extraction completed!")
        
        # Parse and display results
        result_data = json.loads(result)
        
        print(f"\n📊 Results Summary:")
        print(f"  Status: {result_data.get('status')}")
        print(f"  Ad Count: {result_data.get('ad_count')}")
        print(f"  Quality Score: {result_data.get('quality_score')}")
        print(f"  Processing Mode: {result_data.get('processing_mode')}")
        print(f"  Vehicle Searched: {result_data.get('vehicle_searched')}")
        
        print(f"\n🚗 Generated Ads:")
        for i, ad in enumerate(result_data.get('ads', []), 1):
            print(f"\n  Ad #{i}:")
            print(f"    Title: {ad.get('Ad Title')}")
            print(f"    Price: LKR {ad.get('Price (in LKR)')}")
            print(f"    Location: {ad.get('Location')}")
            print(f"    Year: {ad.get('Year of Manufacture')}")
            print(f"    Mileage: {ad.get('Mileage (in km)')}")
            print(f"    Condition: {ad.get('Condition')}")
            print(f"    Fuel Type: {ad.get('Fuel Type')}")
            print(f"    URL: {ad.get('URL')}")
        
        print(f"\n📈 Summary:")
        summary = result_data.get('summary', {})
        print(f"  Extraction Successful: {summary.get('extraction_successful')}")
        print(f"  Data Source: {summary.get('data_source')}")
        print(f"  Recommendation: {summary.get('recommendation')}")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_url_parsing():
    """Test URL parsing functionality"""
    print("\n🧪 Testing URL Parsing...")
    
    try:
        from app.tools.simple_ad_extractor import SimpleAdDetailsExtractor
        
        extractor = SimpleAdDetailsExtractor()
        
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
    print("🚀 Starting Simplified Ad Extractor Tests\n")
    
    test_results = []
    
    # Run tests
    test_results.append(("Simple Extractor", test_simple_extractor()))
    test_results.append(("URL Parsing", test_url_parsing()))
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 Test Results Summary:")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! The simplified extractor is ready for use.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == len(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
