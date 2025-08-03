# app/models/comparison.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class VehicleComparison(Base):
    __tablename__ = "vehicle_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    analysis_session_id = Column(String, unique=True, index=True)  # Unique session identifier
    vehicle1 = Column(String, index=True)
    vehicle2 = Column(String, index=True)
    comparison_report = Column(Text)
    metadata_info = Column(Text)  # JSON string for additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to ads - temporarily disabled to avoid circular import issues
    # ads = relationship("Ad", back_populates="comparison")
