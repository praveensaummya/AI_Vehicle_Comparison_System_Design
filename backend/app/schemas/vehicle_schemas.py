# app/schemas/vehicle_schemas.py
from pydantic import BaseModel
from typing import List, Optional

class VehicleAnalysisRequest(BaseModel):
    """Request model for vehicle analysis."""
    vehicle1: str
    vehicle2: str

class AdDetails(BaseModel):
    """Model for individual advertisement details."""
    title: str
    price: str
    location: str
    mileage: str
    year: str
    link: str
    analysis_session_id: Optional[str] = None  # Links ad to analysis session
    vehicle_name: Optional[str] = None  # Which vehicle this ad is for

class VehicleAnalysisResponse(BaseModel):
    """Response model for vehicle analysis."""
    analysis_session_id: str  # Unique identifier for this analysis session
    comparison_report: str
    vehicle1_ads: List[AdDetails]
    vehicle2_ads: List[AdDetails]
    vehicle1_name: str  # Name of first vehicle
    vehicle2_name: str  # Name of second vehicle
