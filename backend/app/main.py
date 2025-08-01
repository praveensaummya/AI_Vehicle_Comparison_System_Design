# app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.vehicle_schemas import VehicleAnalysisRequest, VehicleAnalysisResponse, AdDetails
from app.crew import VehicleAnalysisCrew
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
        logger.info("Initializing vehicle analysis crew", 
                   vehicle1=request.vehicle1, 
                   vehicle2=request.vehicle2)
        crew = VehicleAnalysisCrew(request.vehicle1, request.vehicle2)
        
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
        logger.error("Analysis failed with exception", 
                    vehicle1=request.vehicle1, 
                    vehicle2=request.vehicle2,
                    error=str(e),
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