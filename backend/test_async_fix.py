#!/usr/bin/env python3
"""
Test script to verify the async compatibility fix for Playwright tools
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def test_async_extraction():
    """Test the async-compatible extraction"""
    print("🔧 Testing Async-Compatible Extraction")
    print("=" * 50)
    
    try:
        from tools.ad_details_tool import ad_details_extractor_tool
        
        test_urls = """
        - https://ikman.lk/en/ad/toyota-aqua-2020-for-sale-colombo
        - https://ikman.lk/en/ad/honda-fit-2019-for-sale-gampaha
        """
        
        print("Testing extraction in async context...")
        result = ad_details_extractor_tool._run(
            urls=test_urls,
            mode="hybrid",
            include_metadata=True
        )
        
        try:
            data = json.loads(result)
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Processing mode: {data.get('processing_mode')}")
            print(f"✅ Ad count: {data.get('ad_count')}")
            print(f"✅ Quality score: {data.get('quality_score')}")
            
            if data.get('errors'):
                print("Errors encountered:")
                for error in data['errors']:
                    print(f"  - {error}")
            
            if data.get('ads'):
                print("Sample ad extracted:")
                sample_ad = data['ads'][0]
                print(f"  Title: {sample_ad.get('Ad Title')}")
                print(f"  Price: {sample_ad.get('Price (in LKR)')}")
                print(f"  Location: {sample_ad.get('Location')}")
                
            return True
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON response")
            print(f"Response preview: {result[:200]}...")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sync_extraction():
    """Test extraction in sync context"""
    print("\n🔧 Testing Sync Context Extraction")
    print("=" * 50)
    
    try:
        from tools.ad_details_tool import ad_details_extractor_tool
        
        test_urls = """
        - https://ikman.lk/en/ad/suzuki-alto-2020-for-sale-colombo
        """
        
        print("Testing extraction in sync context...")
        result = ad_details_extractor_tool._run(
            urls=test_urls,
            mode="mock",  # Use mock mode for quick test
            include_metadata=True
        )
        
        try:
            data = json.loads(result)
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Processing mode: {data.get('processing_mode')}")
            print(f"✅ Ad count: {data.get('ad_count')}")
            print(f"✅ Quality score: {data.get('quality_score')}")
            
            return True
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON response")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Async Compatibility Fix Test")
    print("=" * 60)
    
    # Test 1: Sync context
    sync_result = test_sync_extraction()
    
    # Test 2: Async context
    async_result = await test_async_extraction()
    
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Sync Context Test: {'PASS' if sync_result else 'FAIL'}")
    print(f"✅ Async Context Test: {'PASS' if async_result else 'FAIL'}")
    
    if sync_result and async_result:
        print("🎉 ALL TESTS PASSED!")
        print("The async compatibility fix is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
