#!/usr/bin/env python3
"""
Test script for the new AI-friendly search tool
Run this to verify the reconstructed search tool works correctly
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from tools.search_tool import search_tool
from tools.search_helper import analyze_vehicle_search, format_analysis_for_ai

def test_search_functionality():
    """Test basic search functionality"""
    print("🔍 Testing AI-Friendly Search Tool")
    print("=" * 50)
    
    # Test queries for different search types
    test_queries = [
        {
            "query": "Honda Fit 2015",
            "search_type": "general",
            "description": "General search for Honda Fit 2015"
        },
        {
            "query": "Toyota Prius",
            "search_type": "vehicle_specs",
            "description": "Specifications search for Toyota Prius"
        },
        {
            "query": "Nissan Leaf electric car",
            "search_type": "vehicle_reviews",
            "description": "Reviews search for Nissan Leaf"
        },
        {
            "query": "BMW 3 Series reliability",
            "search_type": "problems",
            "description": "Problems search for BMW 3 Series"
        }
    ]
    
    # Check if API key is available
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("⚠️  SERPER_API_KEY not found in environment variables")
        print("   The search tool will return error responses, but we can test the structure")
        print()
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print(f"Type: {test_case['search_type']}")
        print("-" * 30)
        
        try:
            # Use the search tool
            result = search_tool._run(
                query=test_case["query"],
                search_type=test_case["search_type"],
                limit=3
            )
            
            # Parse and display the result
            try:
                parsed_result = json.loads(result)
                print(f"Status: {parsed_result.get('status', 'unknown')}")
                print(f"Query: {parsed_result.get('query', 'N/A')}")
                print(f"Search Type: {parsed_result.get('search_type', 'N/A')}")
                print(f"Total Results: {parsed_result.get('total_results', 0)}")
                
                if parsed_result.get('status') == 'success':
                    print("✅ Search successful!")
                    results = parsed_result.get('results', [])
                    
                    if results:
                        print("\nTop Results:")
                        for j, res in enumerate(results[:2], 1):
                            print(f"  {j}. {res.get('title', 'No title')}")
                            print(f"     URL: {res.get('url', 'No URL')}")
                            print(f"     Type: {res.get('content_type', 'other')}")
                            print(f"     Score: {res.get('relevance_score', 0)}")
                        
                        # Test the analysis helper
                        print("\n🔬 Testing Search Analysis...")
                        analysis = analyze_vehicle_search(result)
                        
                        if 'error' not in analysis:
                            formatted_analysis = format_analysis_for_ai(analysis)
                            print("Analysis Result:")
                            print(formatted_analysis[:500] + "..." if len(formatted_analysis) > 500 else formatted_analysis)
                        else:
                            print(f"Analysis Error: {analysis['error']}")
                    
                elif parsed_result.get('status') == 'error':
                    print(f"❌ Search failed: {parsed_result.get('error_message', 'Unknown error')}")
                    
                    # Test error response analysis
                    analysis = analyze_vehicle_search(result)
                    print(f"Analysis of error: {analysis}")
                
                # Check suggested queries
                suggested = parsed_result.get('suggested_queries', [])
                if suggested:
                    print(f"\nSuggested follow-up queries:")
                    for suggestion in suggested:
                        print(f"  • {suggestion}")
                        
            except json.JSONDecodeError:
                print("❌ Invalid JSON response:")
                print(result[:200] + "..." if len(result) > 200 else result)
                
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
        
        print("\n" + "=" * 50 + "\n")

def test_search_types():
    """Test different search type enhancements"""
    print("🎯 Testing Search Type Enhancements")
    print("=" * 50)
    
    from tools.search_tool import AIFriendlySearchTool
    
    search_instance = AIFriendlySearchTool()
    
    test_cases = [
        ("Honda Civic", "general"),
        ("Honda Civic", "vehicle_specs"),
        ("Honda Civic", "vehicle_reviews"),
        ("Honda Civic", "market_data"),
        ("Honda Civic", "problems"),
        ("Honda Civic vs Toyota Corolla", "comparison")
    ]
    
    for query, search_type in test_cases:
        enhanced = search_instance._enhance_query(query, search_type)
        print(f"Original: '{query}' ({search_type})")
        print(f"Enhanced: '{enhanced}'")
        print()

def test_offline_analysis():
    """Test the analysis functionality with mock data"""
    print("🧪 Testing Offline Analysis with Mock Data")
    print("=" * 50)
    
    # Create mock search results
    mock_search_results = {
        "query": "Honda Fit 2015",
        "search_type": "general",
        "total_results": 3,
        "status": "success",
        "results": [
            {
                "title": "2015 Honda Fit Review: Excellent Fuel Economy and Reliability",
                "url": "https://edmunds.com/honda/fit/2015/review",
                "snippet": "The 2015 Honda Fit offers excellent fuel economy with 36 mpg combined. Reliable and practical small car with good interior space. Some complaints about road noise.",
                "relevance_score": 2.1,
                "content_type": "review"
            },
            {
                "title": "Honda Fit 2015 Specifications - Engine and Performance",
                "url": "https://honda.com/fit/2015/specs",
                "snippet": "2015 Honda Fit powered by 1.5L 4-cylinder engine producing 130 hp. CVT automatic transmission standard. Length: 160 inches, excellent safety ratings.",
                "relevance_score": 1.9,
                "content_type": "specs"
            },
            {
                "title": "Common Problems with 2015 Honda Fit - Owner Forums",
                "url": "https://reddit.com/r/honda/fit-problems",
                "snippet": "Some 2015 Honda Fit owners report issues with CVT transmission and paint problems. Overall reliability is good with proper maintenance.",
                "relevance_score": 1.7,
                "content_type": "forum"
            }
        ],
        "suggested_queries": [
            "Honda Fit 2015 specifications",
            "Honda Fit 2015 reviews",
            "Honda Fit 2015 problems issues"
        ]
    }
    
    # Convert to JSON string
    mock_json = json.dumps(mock_search_results, indent=2)
    
    print("Mock Search Results:")
    print(mock_json[:300] + "..." if len(mock_json) > 300 else mock_json)
    print()
    
    # Test analysis
    analysis = analyze_vehicle_search(mock_json)
    print("Analysis Result:")
    print(json.dumps(analysis, indent=2, default=str))
    print()
    
    # Test formatted output
    formatted = format_analysis_for_ai(analysis)
    print("Formatted for AI:")
    print(formatted)

if __name__ == "__main__":
    print("🚀 AI-Friendly Search Tool Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Search type enhancements
        test_search_types()
        
        # Test 2: Offline analysis with mock data
        test_offline_analysis()
        
        # Test 3: Live search functionality (if API key available)
        test_search_functionality()
        
        print("✅ All tests completed!")
        
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
