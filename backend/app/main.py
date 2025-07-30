# app/main.py
from fastapi import FastAPI, HTTPException, Query
from app.schemas.vehicle_schemas import VehicleAnalysisRequest, VehicleAnalysisResponse, AdDetails
from app.crew import VehicleAnalysisCrew
from app.utils.ad_stats import filter_and_stats

app = FastAPI(
    title="AI Vehicle Analyst API",
    description="An API to compare vehicles and find local ads using a crew of AI agents.",
    version="1.0.0"
)

@app.post("/api/v1/analyze-vehicles", response_model=VehicleAnalysisResponse)
async def analyze_vehicles(request: VehicleAnalysisRequest):
    """
    Analyzes two vehicle models by:
    1. Comparing their specifications, pros, cons, and reliability.
    2. Finding current advertisements for them on popular Sri Lankan websites.
    """
    if not request.vehicle1 or not request.vehicle2:
        raise HTTPException(status_code=400, detail="Both vehicle1 and vehicle2 must be provided.")
        
    try:
        crew = VehicleAnalysisCrew(request.vehicle1, request.vehicle2)
        result = crew.run() # This now returns a structured dictionary
        
        # Validate the dictionary with our Pydantic response model
        validated_result = VehicleAnalysisResponse(**result)
        return validated_result

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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
    # Convert AdDetails to dicts if needed
    ads_dicts = [ad.dict() if hasattr(ad, 'dict') else ad for ad in ads]
    result = filter_and_stats(ads_dicts, min_price, max_price, year, location)
    return result

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Vehicle Analyst API"}