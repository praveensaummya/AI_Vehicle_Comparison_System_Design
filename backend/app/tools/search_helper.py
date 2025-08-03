# app/tools/search_helper.py
# Helper utilities for AI agents to better process search results
from typing import Dict, List, Any, Optional
import json
import re
from dataclasses import dataclass

@dataclass
class VehicleInfo:
    """Structured vehicle information extracted from search results"""
    make: str = ""
    model: str = ""
    year: Optional[int] = None
    engine: str = ""
    transmission: str = ""
    fuel_type: str = ""
    price_range: str = ""
    pros: List[str] = None
    cons: List[str] = None
    specs: Dict[str, str] = None
    common_problems: List[str] = None
    
    def __post_init__(self):
        if self.pros is None:
            self.pros = []
        if self.cons is None:
            self.cons = []
        if self.specs is None:
            self.specs = {}
        if self.common_problems is None:
            self.common_problems = []

class SearchResultAnalyzer:
    """Analyzes search results to extract meaningful vehicle information"""
    
    def __init__(self):
        self.vehicle_makes = [
            "toyota", "honda", "nissan", "suzuki", "mazda", "mitsubishi", "hyundai",
            "kia", "ford", "chevrolet", "bmw", "mercedes", "audi", "volkswagen",
            "subaru", "lexus", "infiniti", "acura", "jeep", "land rover", "volvo"
        ]
        
        self.spec_keywords = {
            "engine": ["engine", "motor", "cc", "displacement", "cylinder", "liter", "hp", "bhp"],
            "transmission": ["transmission", "gearbox", "manual", "automatic", "cvt", "speed"],
            "fuel": ["fuel", "petrol", "gasoline", "diesel", "hybrid", "electric", "mpg", "kmpl"],
            "safety": ["safety", "airbags", "abs", "esp", "traction", "stability"],
            "dimensions": ["length", "width", "height", "wheelbase", "ground clearance"]
        }
    
    def analyze_search_results(self, search_results_json: str) -> Dict[str, Any]:
        """
        Analyze search results JSON and extract structured vehicle information
        
        Args:
            search_results_json: JSON string from search tool
            
        Returns:
            Dict with analyzed information categorized by type
        """
        try:
            search_data = json.loads(search_results_json)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format in search results"}
        
        if search_data.get("status") != "success":
            return {"error": search_data.get("error_message", "Search failed")}
        
        results = search_data.get("results", [])
        
        analysis = {
            "vehicle_info": self._extract_vehicle_info(results),
            "reviews_summary": self._summarize_reviews(results),
            "specs_found": self._extract_specifications(results),
            "problems_mentioned": self._extract_problems(results),
            "price_info": self._extract_price_info(results),
            "best_sources": self._rank_sources(results),
            "search_quality": self._assess_search_quality(search_data)
        }
        
        return analysis
    
    def _extract_vehicle_info(self, results: List[Dict]) -> VehicleInfo:
        """Extract basic vehicle information from search results"""
        vehicle_info = VehicleInfo()
        
        # Combine all text for analysis
        all_text = ""
        for result in results:
            all_text += f"{result.get('title', '')} {result.get('snippet', '')} "
        
        all_text = all_text.lower()
        
        # Extract make and model
        for make in self.vehicle_makes:
            if make in all_text:
                vehicle_info.make = make.title()
                break
        
        # Extract years mentioned
        years = re.findall(r'\b(19|20)\d{2}\b', all_text)
        if years:
            # Get the most recent year mentioned
            vehicle_info.year = max(int(year) for year in years)
        
        return vehicle_info
    
    def _summarize_reviews(self, results: List[Dict]) -> Dict[str, List[str]]:
        """Extract and summarize review information"""
        review_results = [r for r in results if r.get('content_type') == 'review']
        
        pros = []
        cons = []
        
        for result in review_results:
            snippet = result.get('snippet', '').lower()
            
            # Look for positive indicators
            if any(word in snippet for word in ['excellent', 'great', 'good', 'reliable', 'efficient']):
                pros.append(self._extract_sentence_with_keywords(
                    snippet, ['excellent', 'great', 'good', 'reliable', 'efficient']
                ))
            
            # Look for negative indicators
            if any(word in snippet for word in ['poor', 'bad', 'problem', 'issue', 'fault']):
                cons.append(self._extract_sentence_with_keywords(
                    snippet, ['poor', 'bad', 'problem', 'issue', 'fault']
                ))
        
        return {
            "pros": list(set(filter(None, pros))),
            "cons": list(set(filter(None, cons))),
            "review_count": len(review_results)
        }
    
    def _extract_specifications(self, results: List[Dict]) -> Dict[str, List[str]]:
        """Extract technical specifications from results"""
        spec_results = [r for r in results if r.get('content_type') in ['specs', 'other']]
        
        extracted_specs = {}
        
        for category, keywords in self.spec_keywords.items():
            extracted_specs[category] = []
            
            for result in spec_results:
                text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
                
                for keyword in keywords:
                    if keyword in text:
                        spec_info = self._extract_spec_detail(text, keyword)
                        if spec_info:
                            extracted_specs[category].append(spec_info)
        
        # Remove duplicates and empty lists
        return {k: list(set(v)) for k, v in extracted_specs.items() if v}
    
    def _extract_problems(self, results: List[Dict]) -> List[str]:
        """Extract common problems mentioned in search results"""
        problems = []
        problem_keywords = ['problem', 'issue', 'fault', 'recall', 'complaint', 'defect']
        
        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
            
            for keyword in problem_keywords:
                if keyword in text:
                    problem_detail = self._extract_sentence_with_keywords(text, [keyword])
                    if problem_detail:
                        problems.append(problem_detail)
        
        return list(set(problems))
    
    def _extract_price_info(self, results: List[Dict]) -> Dict[str, str]:
        """Extract price and market value information"""
        price_info = {}
        
        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
            
            # Look for price patterns
            price_patterns = [
                r'\$[\d,]+',  # $25,000
                r'rs\.?\s*[\d,]+',  # Rs. 2,500,000
                r'lkr\s*[\d,]+',  # LKR 2500000
                r'price.*?[\d,]+',  # price range 20-30
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    price_info['price_mentioned'] = matches[0]
                    break
        
        return price_info
    
    def _rank_sources(self, results: List[Dict]) -> List[Dict]:
        """Rank sources by reliability and relevance"""
        ranked = sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return [{
            'title': r.get('title', ''),
            'url': r.get('url', ''),
            'content_type': r.get('content_type', ''),
            'relevance_score': r.get('relevance_score', 0)
        } for r in ranked[:3]]
    
    def _assess_search_quality(self, search_data: Dict) -> Dict[str, Any]:
        """Assess the quality and completeness of search results"""
        results = search_data.get('results', [])
        
        quality_metrics = {
            'total_results': len(results),
            'content_type_distribution': {},
            'relevance_scores': [r.get('relevance_score', 0) for r in results],
            'has_authoritative_sources': False,
            'coverage_score': 0
        }
        
        # Content type distribution
        for result in results:
            content_type = result.get('content_type', 'other')
            quality_metrics['content_type_distribution'][content_type] = \
                quality_metrics['content_type_distribution'].get(content_type, 0) + 1
        
        # Check for authoritative sources
        authoritative_domains = ['edmunds.com', 'kbb.com', 'motortrend.com', 'caranddriver.com']
        for result in results:
            url = result.get('url', '').lower()
            if any(domain in url for domain in authoritative_domains):
                quality_metrics['has_authoritative_sources'] = True
                break
        
        # Calculate coverage score (how well different content types are represented)
        content_types = set(quality_metrics['content_type_distribution'].keys())
        desired_types = {'review', 'specs', 'forum', 'news'}
        coverage = len(content_types.intersection(desired_types)) / len(desired_types)
        quality_metrics['coverage_score'] = round(coverage, 2)
        
        return quality_metrics
    
    def _extract_sentence_with_keywords(self, text: str, keywords: List[str]) -> Optional[str]:
        """Extract sentence containing specific keywords"""
        sentences = text.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                return sentence.strip()
        
        return None
    
    def _extract_spec_detail(self, text: str, keyword: str) -> Optional[str]:
        """Extract specific specification detail around a keyword"""
        # Find the keyword and extract surrounding context
        pattern = rf'.{{0,30}}{keyword}.{{0,30}}'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group().strip()
        
        return None

# Helper functions for AI agents
def analyze_vehicle_search(search_results_json: str) -> Dict[str, Any]:
    """
    Main function for AI agents to analyze vehicle search results
    
    Usage:
        from app.tools.search_helper import analyze_vehicle_search
        
        # After getting search results from search_tool
        analysis = analyze_vehicle_search(search_results_json)
        
        # Access structured information
        vehicle_info = analysis['vehicle_info']
        reviews = analysis['reviews_summary']
        specs = analysis['specs_found']
    """
    analyzer = SearchResultAnalyzer()
    return analyzer.analyze_search_results(search_results_json)

def format_analysis_for_ai(analysis: Dict[str, Any]) -> str:
    """
    Format analysis results in a way that's easy for AI to understand and use
    """
    if 'error' in analysis:
        return f"SEARCH ANALYSIS ERROR: {analysis['error']}"
    
    formatted = "=== VEHICLE SEARCH ANALYSIS ===\n\n"
    
    # Vehicle info
    vehicle_info = analysis.get('vehicle_info', {})
    if hasattr(vehicle_info, 'make') and vehicle_info.make:
        formatted += f"VEHICLE: {vehicle_info.make}"
        if hasattr(vehicle_info, 'model') and vehicle_info.model:
            formatted += f" {vehicle_info.model}"
        if hasattr(vehicle_info, 'year') and vehicle_info.year:
            formatted += f" ({vehicle_info.year})"
        formatted += "\n\n"
    
    # Reviews summary
    reviews = analysis.get('reviews_summary', {})
    if reviews.get('pros'):
        formatted += "POSITIVE ASPECTS:\n"
        for pro in reviews['pros'][:3]:  # Top 3
            formatted += f"  • {pro}\n"
        formatted += "\n"
    
    if reviews.get('cons'):
        formatted += "CONCERNS:\n"
        for con in reviews['cons'][:3]:  # Top 3
            formatted += f"  • {con}\n"
        formatted += "\n"
    
    # Specifications
    specs = analysis.get('specs_found', {})
    if specs:
        formatted += "SPECIFICATIONS FOUND:\n"
        for category, spec_list in specs.items():
            if spec_list:
                formatted += f"  {category.upper()}: {', '.join(spec_list[:2])}\n"
        formatted += "\n"
    
    # Problems
    problems = analysis.get('problems_mentioned', [])
    if problems:
        formatted += "COMMON ISSUES MENTIONED:\n"
        for problem in problems[:3]:  # Top 3
            formatted += f"  • {problem}\n"
        formatted += "\n"
    
    # Best sources
    best_sources = analysis.get('best_sources', [])
    if best_sources:
        formatted += "TOP SOURCES:\n"
        for source in best_sources:
            formatted += f"  • {source['title']} (Score: {source['relevance_score']})\n"
            formatted += f"    {source['url']}\n"
        formatted += "\n"
    
    # Search quality
    quality = analysis.get('search_quality', {})
    formatted += f"SEARCH QUALITY: {quality.get('coverage_score', 0)*100:.0f}% coverage"
    if quality.get('has_authoritative_sources'):
        formatted += " (includes authoritative sources)"
    formatted += "\n"
    
    return formatted
