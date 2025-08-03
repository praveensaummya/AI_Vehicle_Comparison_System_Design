# app/tools/sync_ad_extractor.py
# Synchronous real data ad extractor optimized for CrewAI
from crewai.tools import BaseTool
from typing import Dict, Any, Type, List
from pydantic import BaseModel, Field
import json
import re
import requests
from bs4 import BeautifulSoup
import time
import random

class SyncAdExtractorInput(BaseModel):
    """Input schema for synchronous ad extractor."""
    urls: str = Field(..., description="URLs to extract details from (as a string containing URLs separated by newlines)")
    vehicle_name: str = Field(default="Vehicle", description="Name of the vehicle being searched for")
    timeout: int = Field(default=30, description="Request timeout in seconds")

class SynchronousAdExtractor(BaseTool):
    name: str = "Synchronous Ad Extractor"
    description: str = (
        "Synchronous real data extraction tool optimized for CrewAI. "
        "Extracts vehicle advertisement details using HTTP requests and BeautifulSoup parsing. "
        "Returns structured JSON with actual ad data from Sri Lankan websites."
    )
    args_schema: Type[BaseModel] = SyncAdExtractorInput

    def _run(self, urls: str, vehicle_name: str = "Vehicle", timeout: int = 30) -> str:
        """Extract real ad details synchronously"""
        try:
            # Parse URLs from input
            url_list = self._parse_urls(urls)
            
            if not url_list:
                return self._create_error_response("No valid URLs found in input", urls)
            
            # Extract real data synchronously
            ads = self._extract_real_ads(url_list, timeout)
            
            response = {
                "status": "success",
                "ad_count": len(ads),
                "quality_score": self._calculate_quality_score(ads),
                "processing_mode": "sync_real",
                "vehicle_searched": vehicle_name,
                "ads": ads,
                "summary": {
                    "extraction_successful": len(ads) > 0,
                    "total_ads_found": len(ads),
                    "data_source": "Real website scraping",
                    "extraction_method": "HTTP + BeautifulSoup"
                }
            }
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            return self._create_error_response(f"Extraction failed: {str(e)}", urls)
    
    def _parse_urls(self, urls_input: str) -> List[str]:
        """Parse URLs from various input formats"""
        url_list = []
        
        for line in urls_input.strip().split('\n'):
            line = line.strip()
            
            # Remove common prefixes
            if line.startswith('- '):
                line = line[2:]
            elif line.startswith('* '):
                line = line[2:]
            elif line.startswith('• '):
                line = line[2:]
            
            # Extract URLs from text
            url_matches = re.findall(r'https?://[^\s]+', line)
            url_list.extend(url_matches)
            
            # If the line itself is a URL
            if line.startswith('http'):
                url_list.append(line)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in url_list:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def _extract_real_ads(self, urls: List[str], timeout: int) -> List[Dict[str, Any]]:
        """Extract real ad details using HTTP requests and BeautifulSoup"""
        ads = []
        
        # Setup session with proper headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        for i, url in enumerate(urls):
            try:
                # Add random delay to avoid rate limiting
                if i > 0:
                    time.sleep(random.uniform(1, 3))
                
                # Make request
                response = session.get(url, timeout=timeout)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract ad details based on site structure
                ad_data = self._extract_ad_from_soup(soup, url)
                ads.append(ad_data)
                
            except requests.exceptions.Timeout:
                ads.append(self._create_timeout_ad(url))
            except requests.exceptions.RequestException as e:
                ads.append(self._create_error_ad(url, f"Request error: {str(e)}"))
            except Exception as e:
                ads.append(self._create_error_ad(url, f"Parse error: {str(e)}"))
        
        return ads
    
    def _extract_ad_from_soup(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract ad details from BeautifulSoup object"""
        
        # Initialize with defaults
        ad_data = {
            "Ad Title": "Not Found",
            "Price (in LKR)": "Not Found",
            "Location": "Not Found",
            "Mileage (in km)": "Not Found",
            "Year of Manufacture": "Not Found",
            "URL": url,
            "Condition": "Not Found",
            "Transmission": "Not Found",
            "Fuel Type": "Not Found"
        }
        
        try:
            # Extract title - try multiple selectors
            title_selectors = ['h1', '.ad-title', '[data-testid="ad-title"]', '.title', 'title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    ad_data["Ad Title"] = title_elem.get_text(strip=True)
                    break
            
            # Extract price - try multiple selectors
            price_selectors = ['[data-testid="price"]', '.price', '.ad-price', '.price-value']
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem and price_elem.get_text(strip=True):
                    price_text = price_elem.get_text(strip=True)
                    # Clean price text
                    price_clean = re.sub(r'[^\d,]', '', price_text)
                    if price_clean:
                        ad_data["Price (in LKR)"] = price_clean
                        break
            
            # Extract location - try multiple approaches
            location_selectors = [
                '[data-testid="subtitle-sublocation-link"]',
                '[data-testid="subtitle-parentlocation-link"]',
                '.location', '.ad-location', '.area'
            ]
            
            locations = []
            for selector in location_selectors:
                location_elems = soup.select(selector)
                for elem in location_elems:
                    loc_text = elem.get_text(strip=True)
                    if loc_text and loc_text not in locations:
                        locations.append(loc_text)
            
            if locations:
                ad_data["Location"] = ", ".join(locations)
            
            # Extract all text content for mileage and year parsing
            all_text = soup.get_text()
            
            # Extract mileage using regex
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})+)\s*(?:km|kilometers?)',
                r'(\d+)\s*(?:km|kilometers?)',
                r'mileage[:\s]*(\d+(?:,\d{3})*)',
                r'(\d+(?:,\d{3})*)\s*k?m'
            ]
            
            for pattern in mileage_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    mileage_value = match.group(1)
                    ad_data["Mileage (in km)"] = self._format_mileage(mileage_value)
                    break
            
            # Extract year
            year_pattern = r'\b(20\d{2})\b'
            years = re.findall(r'\b(20\d{2})\b', all_text)
            if years:
                ad_data["Year of Manufacture"] = years[0]
            
            # Extract additional details if available
            if 'automatic' in all_text.lower():
                ad_data["Transmission"] = "Automatic"
            elif 'manual' in all_text.lower():
                ad_data["Transmission"] = "Manual"
            
            if any(fuel in all_text.lower() for fuel in ['hybrid', 'petrol', 'diesel']):
                for fuel in ['hybrid', 'petrol', 'diesel']:
                    if fuel in all_text.lower():
                        ad_data["Fuel Type"] = fuel.title()
                        break
            
            # Add metadata
            ad_data["_metadata"] = {
                "extraction_method": "sync_real",
                "quality": self._assess_single_ad_quality(ad_data),
                "confidence": self._calculate_single_ad_confidence(ad_data),
                "fields_extracted": self._count_extracted_fields(ad_data)
            }
            
        except Exception as e:
            ad_data["_extraction_error"] = str(e)
        
        return ad_data
    
    def _format_mileage(self, mileage_str: str) -> str:
        """Format mileage string properly"""
        try:
            # Remove commas and convert to int
            clean_mileage = int(mileage_str.replace(',', ''))
            
            # If it's a small number, it might be in thousands
            if clean_mileage < 500:
                clean_mileage *= 1000
            
            # Format with commas
            return f"{clean_mileage:,} km"
        except:
            return mileage_str
    
    def _create_timeout_ad(self, url: str) -> Dict[str, Any]:
        """Create ad data for timeout cases"""
        return {
            "Ad Title": "Timeout Error",
            "Price (in LKR)": "Timeout",
            "Location": "Timeout",
            "Mileage (in km)": "Timeout",
            "Year of Manufacture": "Timeout",
            "URL": url,
            "_metadata": {
                "extraction_method": "sync_real",
                "quality": "poor",
                "confidence": 0.0,
                "error_type": "timeout"
            }
        }
    
    def _create_error_ad(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Create ad data for error cases"""
        return {
            "Ad Title": f"Error: {error_msg}",
            "Price (in LKR)": "Error",
            "Location": "Error",
            "Mileage (in km)": "Error",
            "Year of Manufacture": "Error",
            "URL": url,
            "_metadata": {
                "extraction_method": "sync_real",
                "quality": "poor",
                "confidence": 0.0,
                "error_type": "extraction_error",
                "error_message": error_msg
            }
        }
    
    def _assess_single_ad_quality(self, ad: Dict[str, Any]) -> str:
        """Assess quality of a single ad"""
        important_fields = ["Ad Title", "Price (in LKR)", "Location", "Year of Manufacture"]
        found_fields = sum(1 for field in important_fields if ad.get(field, "Not Found") not in ["Not Found", "Error", "Timeout"])
        
        ratio = found_fields / len(important_fields)
        if ratio >= 0.9:
            return "excellent"
        elif ratio >= 0.7:
            return "good"
        elif ratio >= 0.5:
            return "fair"
        else:
            return "poor"
    
    def _calculate_single_ad_confidence(self, ad: Dict[str, Any]) -> float:
        """Calculate confidence score for a single ad"""
        score = 0.0
        
        if ad.get("Ad Title", "Not Found") not in ["Not Found", "Error", "Timeout"]:
            score += 0.3
        if ad.get("Price (in LKR)", "Not Found") not in ["Not Found", "Error", "Timeout"]:
            score += 0.25
        if ad.get("Location", "Not Found") not in ["Not Found", "Error", "Timeout"]:
            score += 0.2
        if ad.get("Year of Manufacture", "Not Found") not in ["Not Found", "Error", "Timeout"]:
            score += 0.15
        if ad.get("Mileage (in km)", "Not Found") not in ["Not Found", "Error", "Timeout"]:
            score += 0.1
        
        return round(score, 2)
    
    def _count_extracted_fields(self, ad: Dict[str, Any]) -> int:
        """Count successfully extracted fields"""
        important_fields = ["Ad Title", "Price (in LKR)", "Location", "Mileage (in km)", "Year of Manufacture"]
        return sum(1 for field in important_fields if ad.get(field, "Not Found") not in ["Not Found", "Error", "Timeout"])
    
    def _calculate_quality_score(self, ads: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score"""
        if not ads:
            return 0.0
        
        total_confidence = sum(ad.get("_metadata", {}).get("confidence", 0) for ad in ads)
        return round(total_confidence / len(ads), 2)
    
    def _create_error_response(self, error_message: str, urls_input: str) -> str:
        """Create structured error response"""
        error_response = {
            "status": "error",
            "error_message": error_message,
            "ad_count": 0,
            "quality_score": 0.0,
            "processing_mode": "sync_real_error",
            "ads": [],
            "summary": {
                "extraction_successful": False,
                "error_details": error_message,
                "data_source": "HTTP + BeautifulSoup",
                "extraction_method": "synchronous"
            }
        }
        return json.dumps(error_response, indent=2)

# Create the synchronous tool instance
sync_ad_extractor_tool = SynchronousAdExtractor()
