# app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.vehicle_schemas import VehicleAnalysisRequest, VehicleAnalysisResponse, AdDetails
from app.gemini_crew import GeminiVehicleAnalysisCrew
from app.core.config import settings
from app.utils.ad_stats import filter_and_stats
import structlog
import coloredlogs
import logging

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure coloredlogs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
coloredlogs.install(level='INFO', logger=logging.getLogger())

# Create logger instance
logger = structlog.get_logger()
logger.info("Starting AI Vehicle Comparison System API")

# Simplified crew selection function
async def _select_optimal_crew(vehicle1: str, vehicle2: str):
    """
    Select the Gemini crew for vehicle analysis
    Uses the free Gemini API with generous quotas
    """
    
    # Check if Gemini API key is configured
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        logger.error("Gemini API key not configured", 
                    vehicle1=vehicle1, vehicle2=vehicle2)
        raise ValueError("GEMINI_API_KEY is not properly configured. Please add your Gemini API key to the .env file.")
    
    try:
        logger.info("Selecting Gemini crew (free tier with generous quotas)", 
                   vehicle1=vehicle1, vehicle2=vehicle2, 
                   provider="google-gemini", model=settings.GEMINI_MODEL)
        return GeminiVehicleAnalysisCrew(vehicle1, vehicle2)
    except Exception as e:
        logger.error("Gemini crew initialization failed", 
                    error=str(e), error_type=type(e).__name__,
                    vehicle1=vehicle1, vehicle2=vehicle2)
        raise

app = FastAPI(
    title="AI Vehicle Analyst API",
    description="An API to compare vehicles and find local ads using a crew of AI agents.",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost:3001",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/api/v1/analyze-vehicles", response_model=VehicleAnalysisResponse)
async def analyze_vehicles(request: VehicleAnalysisRequest):
    """
    Analyzes two vehicle models by:
    1. Comparing their specifications, pros, cons, and reliability.
    2. Finding current advertisements for them on popular Sri Lankan websites.
    """
    logger.info("Received vehicle analysis request", 
                vehicle1=request.vehicle1, 
                vehicle2=request.vehicle2,
                endpoint="/api/v1/analyze-vehicles")
    
    if not request.vehicle1 or not request.vehicle2:
        logger.warning("Validation failed: Missing vehicle input", 
                      vehicle1=request.vehicle1, 
                      vehicle2=request.vehicle2)
        raise HTTPException(status_code=400, detail="Both vehicle1 and vehicle2 must be provided.")
        
    try:
        # Intelligent crew selection based on provider configuration
        crew = await _select_optimal_crew(request.vehicle1, request.vehicle2)
        
        logger.info("Starting crew execution")
        result = crew.run() # This now returns a structured dictionary
        logger.info("Crew execution completed successfully")
        
        # Validate the dictionary with our Pydantic response model
        validated_result = VehicleAnalysisResponse(**result)
        logger.info("Analysis completed successfully", 
                   vehicle1=request.vehicle1, 
                   vehicle2=request.vehicle2,
                   ads_found_v1=len(validated_result.vehicle1_ads),
                   ads_found_v2=len(validated_result.vehicle2_ads))
        return validated_result

    except Exception as e:
        error_msg = str(e)
        
        logger.error("Analysis failed with exception", 
                    vehicle1=request.vehicle1, 
                    vehicle2=request.vehicle2,
                    error=error_msg,
                    error_type=type(e).__name__)
        # Provide a more generic error to the client for security
        raise HTTPException(status_code=500, detail=f"An internal server error occurred.")

@app.post("/api/v1/vehicle-ads-stats")
async def vehicle_ads_stats(
    ads: list[AdDetails],
    min_price: int = Query(None),
    max_price: int = Query(None),
    year: int = Query(None),
    location: str = Query(None)
):
    """
    Filter ads and return price statistics.
    """
    logger.info("Received vehicle ads stats request",
               ads_count=len(ads),
               min_price=min_price,
               max_price=max_price,
               year=year,
               location=location,
               endpoint="/api/v1/vehicle-ads-stats")
    
    try:
        # Convert AdDetails to dicts if needed
        ads_dicts = [ad.dict() if hasattr(ad, 'dict') else ad for ad in ads]
        result = filter_and_stats(ads_dicts, min_price, max_price, year, location)
        
        logger.info("Vehicle ads stats computed successfully",
                   filtered_ads_count=result.get('stats', {}).get('count', 0),
                   avg_price=result.get('stats', {}).get('avg_price'))
        return result
        
    except Exception as e:
        logger.error("Failed to process vehicle ads stats",
                    error=str(e),
                    error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to process ads statistics")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Vehicle Analyst API"}

@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint that includes API connectivity status
    """
    health_status = {
        "status": "healthy",
        "timestamp": "2025-08-01T14:55:32Z",
        "version": "1.0.0",
        "services": {
            "api": "operational",
            "openai_configured": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here"),
            "serper_configured": bool(settings.SERPER_API_KEY and settings.SERPER_API_KEY != "your_serper_api_key_here"),
            "mock_mode": settings.USE_MOCK_CREW
        }
    }
    
    logger.info("Health check requested", 
                openai_configured=health_status["services"]["openai_configured"],
                mock_mode=health_status["services"]["mock_mode"])
    
    return health_status

@app.post("/api/v1/test-openai")
async def test_openai_connection():
    """
    Test OpenAI API connectivity (uses minimal quota)
    """
    logger.info("OpenAI connection test requested")
    
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Make a minimal test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'OK'"}
            ],
            max_tokens=5,
            temperature=0
        )
        
        logger.info("OpenAI connection test successful", 
                   model_used="gpt-3.5-turbo",
                   tokens_used=response.usage.total_tokens if response.usage else "unknown")
        
        return {
            "status": "success",
            "message": "OpenAI API connection successful",
            "model": "gpt-3.5-turbo",
            "response": response.choices[0].message.content if response.choices else "No response",
            "tokens_used": response.usage.total_tokens if response.usage else None
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error("OpenAI connection test failed", 
                    error=error_msg,
                    error_type=type(e).__name__)
        
        if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            return {
                "status": "quota_exceeded",
                "message": "OpenAI API quota exceeded - using mock mode",
                "error": "API quota or rate limit exceeded",
                "suggestion": "Add credits to your OpenAI account or use mock mode"
            }
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return {
                "status": "unauthorized",
                "message": "OpenAI API key invalid",
                "error": "Invalid API key",
                "suggestion": "Check your OPENAI_API_KEY configuration"
            }
        else:
            return {
                "status": "error",
                "message": "OpenAI API connection failed",
                "error": error_msg,
                "suggestion": "Check your internet connection and API key"
            }
