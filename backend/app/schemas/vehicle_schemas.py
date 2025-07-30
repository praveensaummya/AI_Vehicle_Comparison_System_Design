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

class VehicleAnalysisResponse(BaseModel):
    """Response model for vehicle analysis."""
    comparison_report: str
    vehicle1_ads: List[AdDetails]
    vehicle2_ads: List[AdDetails] 