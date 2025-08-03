#!/usr/bin/env python3
"""
Direct Gemini API Test Script
Test Google AI Studio API connectivity independently of CrewAI
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_direct():
    """Test Gemini API connectivity directly"""
    
    # Check if API key is configured
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return False
    
    if api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY is set to placeholder value")
        return False
    
    print(f"✅ API Key configured: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        
        print("📡 Testing direct Gemini API connection...")
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Create model instance
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Make a minimal test request
        response = model.generate_content("Say 'Hello from Gemini!'")
        
        result = response.text if hasattr(response, 'text') else str(response)
        
        print(f"✅ Connection successful!")
        print(f"📊 Model: gemini-1.5-flash")
        print(f"📝 Response: {result}")
        print(f"🔗 API: Google AI Studio (direct)")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        
        if "API_KEY" in error_msg.upper() or "unauthorized" in error_msg.lower():
            print("💡 Issue: Invalid API key")
            print("🔧 Solution: Check your GEMINI_API_KEY in .env file")
            print("🔗 Get key: https://makersuite.google.com/app/apikey")
        elif "quota" in error_msg.lower():
            print("💡 Issue: API quota exceeded (unlikely for Gemini)")
            print("🔧 Solution: Wait and try again")
        else:
            print("💡 Issue: Network or configuration problem")
            print("🔧 Solution: Check internet connection and API key")
        
        return False

def test_langchain_gemini():
    """Test Gemini via LangChain (what CrewAI uses)"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not configured")
        return False
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        print("📡 Testing Gemini via LangChain...")
        
        # Create LangChain Gemini instance
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Test with a simple message
        from langchain_core.messages import HumanMessage
        
        messages = [HumanMessage(content="Say 'Hello from LangChain Gemini!'")]
        response = llm.invoke(messages)
        
        result = response.content if hasattr(response, 'content') else str(response)
        
        print(f"✅ LangChain Gemini connection successful!")
        print(f"📊 Model: gemini-1.5-flash")
        print(f"📝 Response: {result}")
        print(f"🔗 Integration: LangChain + Google AI Studio")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ LangChain Gemini connection failed: {error_msg}")
        
        if "'ChatGoogleGenerativeAI' object has no attribute 'supports_stop_words'" in error_msg:
            print("💡 Issue: CrewAI compatibility issue")
            print("🔧 Solution: This is the same issue we're trying to solve")
        else:
            print("💡 Issue: LangChain integration problem")
            print("🔧 Solution: Check LangChain Google GenAI package")
        
        return False

def main():
    """Main test function"""
    print("🚀 Gemini API Connection Tests")
    print("=" * 50)
    
    # Test 1: Direct API
    print("\n🧪 Test 1: Direct Gemini API")
    print("-" * 30)
    direct_success = test_gemini_direct()
    
    # Test 2: LangChain integration
    print("\n🧪 Test 2: LangChain Gemini Integration")
    print("-" * 30)
    langchain_success = test_langchain_gemini()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"   Direct API: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"   LangChain:  {'✅ PASS' if langchain_success else '❌ FAIL'}")
    
    if direct_success and not langchain_success:
        print("\n💡 Recommendation: Use mock crew until CrewAI compatibility is fixed")
        print("🔄 The system will automatically fallback to mock responses")
    elif direct_success and langchain_success:
        print("\n🎉 All tests passed! Gemini should work with CrewAI")
    else:
        print("\n⚠️  API configuration issues detected")
        print("🔧 Please check your GEMINI_API_KEY configuration")
    
    return 0 if (direct_success or langchain_success) else 1

if __name__ == "__main__":
    sys.exit(main())
