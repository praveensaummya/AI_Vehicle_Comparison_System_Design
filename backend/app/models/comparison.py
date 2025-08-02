# app/models/comparison.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.db import Base

class VehicleComparison(Base):
    __tablename__ = "vehicle_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    vehicle1 = Column(String, index=True)
    vehicle2 = Column(String, index=True)
    comparison_report = Column(Text)
    metadata_info = Column(Text)  # JSON string for additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
