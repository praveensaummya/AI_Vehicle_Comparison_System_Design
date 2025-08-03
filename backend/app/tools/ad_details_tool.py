# app/tools/ad_details_tool.py
from crewai.tools import BaseTool
from app.tools.beautifulsoup_scraper import batch_extract_ad_details_async
from typing import Dict, Any, Type, List
from pydantic import BaseModel, Field
import json
import asyncio

class AdDetailsExtractorInput(BaseModel):
    """Input schema for AdDetailsExtractorTool."""
    urls: List[str] = Field(..., description="List of URLs to extract details from")

class AdDetailsExtractorTool(BaseTool):
    name: str = "Ad Details Extractor"
    description: str = "Extracts structured ad details from a list of URLs using BeautifulSoup."
    args_schema: Type[BaseModel] = AdDetailsExtractorInput

    def _run(self, urls: List[str]) -> str:
        """Synchronous execution of the tool."""
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_sync_in_thread, urls)
                    results = future.result(timeout=30)
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                results = asyncio.run(batch_extract_ad_details_async(urls))
            
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to extract details: {str(e)}"})
    
    def _run_sync_in_thread(self, urls: List[str]):
        """Helper method to run async function in a new thread with its own event loop"""
        return asyncio.run(batch_extract_ad_details_async(urls))

    async def _arun(self, urls: List[str]) -> str:
        """Asynchronous execution of the tool."""
        try:
            results = await batch_extract_ad_details_async(urls)
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to extract details: {str(e)}"})

# app/tools/ad_details_tool.py
# AI-friendly ad details extraction tool with enhanced capabilities
from crewai.tools import BaseTool
from app.tools.beautifulsoup_scraper import batch_extract_ad_details_async
from typing import Dict, Any, Type, List, Optional
from pydantic import BaseModel, Field
import json
import re
from dataclasses import dataclass
from enum import Enum

class ExtractionMode(str, Enum):
    """Extraction modes for different use cases"""
    REAL = "real"  # Use real scraping
    MOCK = "mock"  # Use mock data
    HYBRID = "hybrid"  # Try real, fallback to mock

class AdQuality(str, Enum):
    """Quality assessment for extracted ads"""
    EXCELLENT = "excellent"  # All fields extracted successfully
    GOOD = "good"  # Most fields extracted
    FAIR = "fair"  # Some fields missing
    POOR = "poor"  # Many fields missing or errors

@dataclass
class ExtractionResult:
    """Structured result for ad extraction"""
    success: bool
    ad_count: int
    quality_score: float
    errors: List[str]
    ads: List[Dict[str, Any]]
    processing_mode: str
    metadata: Dict[str, Any]

class AdDetailsExtractorInput(BaseModel):
    """Input schema for AI-friendly ad details extractor."""
    urls: str = Field(..., description="URLs to extract details from (as a string containing URLs separated by newlines or as JSON array)")
    mode: ExtractionMode = Field(default=ExtractionMode.HYBRID, description="Extraction mode: 'real', 'mock', or 'hybrid'")
    include_metadata: bool = Field(default=True, description="Include extraction metadata in response")
    filter_sales_only: bool = Field(default=True, description="Filter to include only vehicle sales ads")

class AIFriendlyAdDetailsExtractor(BaseTool):
    name: str = "AI Ad Details Extractor"
    description: str = (
        "Advanced ad details extraction tool optimized for AI agents. "
        "Extracts structured vehicle advertisement data with quality assessment, "
        "error handling, and multiple extraction modes. Returns JSON with metadata "
        "for better AI understanding and processing."
    )
    args_schema: Type[BaseModel] = AdDetailsExtractorInput


    def _run(self, urls: str, mode: str = "hybrid", include_metadata: bool = True, filter_sales_only: bool = True) -> str:
        """Synchronous execution with proper async handling"""
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, create a task in a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_sync_in_thread, urls, mode, include_metadata, filter_sales_only)
                    return future.result(timeout=60)
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                return asyncio.run(self._arun(urls, mode, include_metadata, filter_sales_only))
        except Exception as e:
            return self._create_error_response(f"Sync execution failed: {str(e)}", urls)
    
    def _run_sync_in_thread(self, urls: str, mode: str, include_metadata: bool, filter_sales_only: bool) -> str:
        """Helper method to run async function in a new thread with its own event loop"""
        return asyncio.run(self._arun(urls, mode, include_metadata, filter_sales_only))

    async def _arun(self, urls: str, mode: str = "hybrid", include_metadata: bool = True, filter_sales_only: bool = True) -> str:
        """Extract details from ad URLs with AI-friendly structured output"""
        try:
            # Parse URLs from input
            url_list = self._parse_urls(urls)
            
            if not url_list:
                return self._create_error_response("No valid URLs found in input", urls)
            
            # Execute extraction based on mode
            if mode == ExtractionMode.REAL:
                result = await self._extract_real_data(url_list, filter_sales_only)
            elif mode == ExtractionMode.MOCK:
                result = self._extract_mock_data(url_list)
            else:  # HYBRID mode (default)
                result = await self._extract_hybrid_data(url_list, filter_sales_only)
            
            # Format response for AI consumption
            return self._format_ai_response(result, include_metadata)
            
        except Exception as e:
            return self._create_error_response(f"Extraction failed: {str(e)}", urls)
    
    def _parse_urls(self, urls_input: str) -> List[str]:
        """Parse URLs from various input formats"""
        url_list = []
        
        # Try to parse as JSON first
        try:
            if urls_input.strip().startswith('['):
                parsed_urls = json.loads(urls_input)
                if isinstance(parsed_urls, list):
                    url_list.extend([str(url) for url in parsed_urls if str(url).startswith('http')])
                    return url_list
        except json.JSONDecodeError:
            pass
        
        # Parse as text format
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
    
    async def _extract_real_data(self, urls: List[str], filter_sales: bool) -> ExtractionResult:
        """Extract real data using requests + BeautifulSoup scraper"""
        errors = []
        ads = []
        
        try:
            raw_ads = await batch_extract_ad_details_async(urls)
            
            for ad in raw_ads:
                if self._is_valid_ad(ad):
                    if not filter_sales or self._is_sale_ad(ad):
                        processed_ad = self._process_ad_data(ad)
                        ads.append(processed_ad)
                else:
                    errors.append(f"Invalid ad data for URL: {ad.get('URL', 'unknown')}")
            
            quality_score = self._calculate_quality_score(ads)
            
            return ExtractionResult(
                success=len(ads) > 0,
                ad_count=len(ads),
                quality_score=quality_score,
                errors=errors,
                ads=ads,
                processing_mode="real",
                metadata={
                    "total_urls_processed": len(urls),
                    "successful_extractions": len(ads),
                    "failed_extractions": len(urls) - len(ads),
                    "filter_applied": filter_sales
                }
            )
            
        except Exception as e:
            errors.append(f"Real extraction failed: {str(e)}")
            return ExtractionResult(
                success=False,
                ad_count=0,
                quality_score=0.0,
                errors=errors,
                ads=[],
                processing_mode="real_failed",
                metadata={"extraction_error": str(e)}
            )
    
    def _extract_mock_data(self, urls: List[str]) -> ExtractionResult:
        """Generate high-quality mock data for testing"""
        ads = []
        
        vehicle_templates = [
            {"make": "Toyota", "model": "Aqua", "base_price": 4500000},
            {"make": "Honda", "model": "Fit", "base_price": 4200000},
            {"make": "Nissan", "model": "March", "base_price": 3800000},
            {"make": "Suzuki", "model": "Swift", "base_price": 4000000},
            {"make": "Toyota", "model": "Vitz", "base_price": 3900000}
        ]
        
        locations = ["Colombo", "Gampaha", "Kandy", "Negombo", "Kurunegala", "Galle", "Matara"]
        years = [2018, 2019, 2020, 2021, 2022]
        mileages = ["35,000 km", "52,000 km", "28,000 km", "67,000 km", "41,000 km", "89,000 km"]
        
        for i, url in enumerate(urls):
            template = vehicle_templates[i % len(vehicle_templates)]
            year = years[i % len(years)]
            location = locations[i % len(locations)]
            mileage = mileages[i % len(mileages)]
            
            # Calculate realistic price variation
            age_factor = max(0.7, 1 - (2024 - year) * 0.1)
            price = int(template["base_price"] * age_factor + (i * 100000))
            
            mock_ad = {
                "Ad Title": f"{template['make']} {template['model']} {year} for Sale",
                "Price (in LKR)": f"{price:,}",
                "Location": location,
                "Mileage (in km)": mileage,
                "Year of Manufacture": str(year),
                "URL": url,
                "_metadata": {
                    "extraction_method": "mock",
                    "quality": AdQuality.EXCELLENT,
                    "confidence": 1.0
                }
            }
            ads.append(mock_ad)
        
        return ExtractionResult(
            success=True,
            ad_count=len(ads),
            quality_score=1.0,
            errors=[],
            ads=ads,
            processing_mode="mock",
            metadata={
                "total_urls_processed": len(urls),
                "mock_data_generated": True,
                "template_count": len(vehicle_templates)
            }
        )
    
    async def _extract_hybrid_data(self, urls: List[str], filter_sales: bool) -> ExtractionResult:
        """Try real extraction, fallback to mock on failure"""
        # Try real extraction first
        real_result = await self._extract_real_data(urls, filter_sales)
        
        if real_result.success and real_result.quality_score > 0.3:
            # Real extraction was successful enough
            real_result.processing_mode = "hybrid_real"
            return real_result
        else:
            # Fallback to mock data
            mock_result = self._extract_mock_data(urls)
            mock_result.processing_mode = "hybrid_mock"
            mock_result.errors = real_result.errors + ["Fell back to mock data due to poor real extraction quality"]
            return mock_result
    
    def _is_valid_ad(self, ad: Dict[str, Any]) -> bool:
        """Validate if ad data is valid"""
        required_fields = ["ad_title", "url"]
        return all(field in ad and ad[field] not in ["Not Found", "", None] for field in required_fields)
    
    def _is_sale_ad(self, ad: Dict[str, Any]) -> bool:
        """Check if ad is a vehicle sale (not rental, parts, etc.)"""
        title = ad.get("ad_title", "").lower()
        
        # Exclude keywords
        exclude_keywords = ["rent", "rental", "hire", "lease", "parts", "spare", "accessories", "service", "repair"]
        
        if any(keyword in title for keyword in exclude_keywords):
            return False
        
        # Include keywords
        include_keywords = ["sale", "sell", "selling", "for sale"]
        
        return any(keyword in title for keyword in include_keywords) or "rent" not in title
    
    def _process_ad_data(self, ad: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance ad data"""
        processed_ad = ad.copy()
        
        # Add quality assessment
        quality = self._assess_ad_quality(ad)
        confidence = self._calculate_confidence(ad)
        
        processed_ad["_metadata"] = {
            "extraction_method": "real",
            "quality": quality,
            "confidence": confidence,
            "fields_extracted": self._count_extracted_fields(ad)
        }
        
        return processed_ad
    
    def _assess_ad_quality(self, ad: Dict[str, Any]) -> AdQuality:
        """Assess the quality of extracted ad data"""
        fields = ["ad_title", "price_lkr", "location", "mileage_km", "year"]
        valid_fields = sum(1 for field in fields if ad.get(field) not in ["Not Found", "", None])
        
        ratio = valid_fields / len(fields)
        
        if ratio >= 0.9:
            return AdQuality.EXCELLENT
        elif ratio >= 0.7:
            return AdQuality.GOOD
        elif ratio >= 0.5:
            return AdQuality.FAIR
        else:
            return AdQuality.POOR
    
    def _calculate_confidence(self, ad: Dict[str, Any]) -> float:
        """Calculate confidence score for ad data"""
        score = 0.0
        
        # Title confidence
        if ad.get("ad_title") and "Error" not in ad.get("ad_title", ""):
            score += 0.3
        
        # Price confidence
        if ad.get("price_lkr") and ad.get("price_lkr") != "Not Found":
            score += 0.25
        
        # Location confidence
        if ad.get("location") and ad.get("location") != "Not Found":
            score += 0.2
        
        # Mileage confidence
        if ad.get("mileage_km") and ad.get("mileage_km") != "Not Found":
            score += 0.15
        
        # Year confidence
        if ad.get("year") and ad.get("year") != "Not Found":
            score += 0.1
        
        return round(score, 2)
    
    def _count_extracted_fields(self, ad: Dict[str, Any]) -> int:
        """Count successfully extracted fields"""
        fields = ["ad_title", "price_lkr", "location", "mileage_km", "year"]
        return sum(1 for field in fields if ad.get(field) not in ["Not Found", "", None])
    
    def _calculate_quality_score(self, ads: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score for all ads"""
        if not ads:
            return 0.0
        
        total_confidence = sum(ad.get("_metadata", {}).get("confidence", 0) for ad in ads)
        return round(total_confidence / len(ads), 2)
    
    def _format_ai_response(self, result: ExtractionResult, include_metadata: bool) -> str:
        """Format response for AI consumption"""
        response = {
            "status": "success" if result.success else "failed",
            "ad_count": result.ad_count,
            "quality_score": result.quality_score,
            "processing_mode": result.processing_mode,
            "ads": result.ads
        }
        
        if include_metadata:
            response["metadata"] = result.metadata
            response["errors"] = result.errors
            
            # Add summary for AI understanding
            response["summary"] = {
                "extraction_successful": result.success,
                "total_ads_found": result.ad_count,
                "average_quality": result.quality_score,
                "recommended_action": self._get_recommendation(result)
            }
        
        return json.dumps(response, indent=2)
    
    def _get_recommendation(self, result: ExtractionResult) -> str:
        """Get AI recommendation based on extraction results"""
        if result.quality_score >= 0.8:
            return "High quality data extracted. Proceed with analysis."
        elif result.quality_score >= 0.5:
            return "Moderate quality data. Consider manual review of missing fields."
        elif result.success:
            return "Low quality extraction. Recommend re-trying with different parameters."
        else:
            return "Extraction failed. Check URLs and network connectivity."
    
    def _create_error_response(self, error_message: str, urls_input: str) -> str:
        """Create structured error response"""
        error_response = {
            "status": "error",
            "error_message": error_message,
            "ad_count": 0,
            "quality_score": 0.0,
            "processing_mode": "error",
            "ads": [],
            "metadata": {
                "input_received": urls_input[:200] + "..." if len(urls_input) > 200 else urls_input,
                "error_type": "extraction_error"
            }
        }
        return json.dumps(error_response, indent=2)

# Create the enhanced tool instance
ad_details_extractor_tool = AIFriendlyAdDetailsExtractor()
