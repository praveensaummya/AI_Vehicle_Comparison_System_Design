# app/crud/comparison_crud.py
from sqlalchemy.orm import Session
from app.models.comparison import VehicleComparison
from typing import Optional
import json

def create_comparison(db: Session, vehicle1: str, vehicle2: str, comparison_report: str, metadata: dict = None):
    """Create a new vehicle comparison report in the database."""
    metadata_json = json.dumps(metadata) if metadata else None
    
    db_comparison = VehicleComparison(
        vehicle1=vehicle1,
        vehicle2=vehicle2,
        comparison_report=comparison_report,
        metadata_info=metadata_json
    )
    db.add(db_comparison)
    db.commit()
    db.refresh(db_comparison)
    return db_comparison

def get_comparison_by_vehicles(db: Session, vehicle1: str, vehicle2: str) -> Optional[VehicleComparison]:
    """Get the most recent comparison for two specific vehicles."""
    return db.query(VehicleComparison).filter(
        ((VehicleComparison.vehicle1 == vehicle1) & (VehicleComparison.vehicle2 == vehicle2)) |
        ((VehicleComparison.vehicle1 == vehicle2) & (VehicleComparison.vehicle2 == vehicle1))
    ).order_by(VehicleComparison.created_at.desc()).first()

def get_comparisons(db: Session, skip: int = 0, limit: int = 100):
    """Get comparison reports with pagination."""
    return db.query(VehicleComparison).offset(skip).limit(limit).all()

def get_comparison_by_id(db: Session, comparison_id: int) -> Optional[VehicleComparison]:
    """Get a specific comparison by ID."""
    return db.query(VehicleComparison).filter(VehicleComparison.id == comparison_id).first()

def update_comparison(db: Session, comparison_id: int, comparison_report: str, metadata: dict = None) -> Optional[VehicleComparison]:
    """Update an existing comparison report."""
    db_comparison = db.query(VehicleComparison).filter(VehicleComparison.id == comparison_id).first()
    if db_comparison:
        db_comparison.comparison_report = comparison_report
        if metadata:
            db_comparison.metadata_info = json.dumps(metadata)
        db.commit()
        db.refresh(db_comparison)
    return db_comparison

def delete_comparison(db: Session, comparison_id: int) -> bool:
    """Delete a comparison by ID."""
    db_comparison = db.query(VehicleComparison).filter(VehicleComparison.id == comparison_id).first()
    if db_comparison:
        db.delete(db_comparison)
        db.commit()
        return True
    return False

def get_total_comparisons_count(db: Session) -> int:
    """Get total count of comparison reports in the database."""
    return db.query(VehicleComparison).count()
