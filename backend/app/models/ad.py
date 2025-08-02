# app/models/ad.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(String)
    location = Column(String)
    mileage = Column(String)
    year = Column(String)
    link = Column(String, unique=True, index=True)
    analysis_session_id = Column(String, index=True)  # Links ads to analysis sessions
    vehicle_name = Column(String, index=True)  # Which vehicle this ad is for
    comparison_id = Column(Integer, ForeignKey("vehicle_comparisons.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to comparison - temporarily disabled to avoid circular import issues
    # comparison = relationship("VehicleComparison", back_populates="ads")
