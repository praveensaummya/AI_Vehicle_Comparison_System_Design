#!/usr/bin/env python3
"""
OpenAI API Connection Test Script
Run this to verify your OpenAI API key and connectivity independently of CrewAI
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test OpenAI API connectivity with minimal token usage"""
    
    # Check if API key is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY is set to placeholder value")
        return False
    
    print(f"✅ API Key configured: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        from openai import OpenAI
        
        print("📡 Testing OpenAI API connection...")
        
        client = OpenAI(api_key=api_key)
        
        # Make a minimal test request (uses ~5-10 tokens)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello'"}
            ],
            max_tokens=5,
            temperature=0
        )
        
        result = response.choices[0].message.content if response.choices else "No response"
        tokens_used = response.usage.total_tokens if response.usage else "Unknown"
        
        print(f"✅ Connection successful!")
        print(f"📊 Model: gpt-3.5-turbo")
        print(f"📝 Response: {result}")
        print(f"🎯 Tokens used: {tokens_used}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        
        if "quota" in error_msg.lower():
            print("💡 Issue: API quota exceeded")
            print("🔧 Solution: Add credits to your OpenAI account")
            print("🔗 URL: https://platform.openai.com/account/billing")
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            print("💡 Issue: Invalid API key")
            print("🔧 Solution: Check your OPENAI_API_KEY in .env file")
        elif "rate limit" in error_msg.lower():
            print("💡 Issue: Rate limit exceeded")
            print("🔧 Solution: Wait a moment and try again")
        else:
            print("💡 Issue: Network or configuration problem")
            print("🔧 Solution: Check internet connection and API key")
        
        return False

def main():
    """Main test function"""
    print("🚀 OpenAI API Connection Test")
    print("=" * 40)
    
    success = test_openai_connection()
    
    print("=" * 40)
    if success:
        print("🎉 All tests passed! Your OpenAI API is working correctly.")
        print("✨ CrewAI should be able to connect successfully.")
    else:
        print("⚠️  Connection test failed.")
        print("🔄 The system will automatically use mock responses instead.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
