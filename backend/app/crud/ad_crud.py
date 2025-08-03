# app/crud/ad_crud.py
from sqlalchemy.orm import Session
from app.models.ad import Ad
from typing import Optional

def create_ad(db: Session, ad_data: dict, analysis_session_id: str = None, vehicle_name: str = None, comparison_id: int = None):
    """Create a new ad in the database."""
    # Add new fields to ad_data if provided
    if analysis_session_id:
        ad_data['analysis_session_id'] = analysis_session_id
    if vehicle_name:
        ad_data['vehicle_name'] = vehicle_name
    if comparison_id:
        ad_data['comparison_id'] = comparison_id
        
    db_ad = Ad(**ad_data)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

def get_ads(db: Session, skip: int = 0, limit: int = 100):
    """Get ads with pagination."""
    return db.query(Ad).offset(skip).limit(limit).all()

def get_existing_ad_by_link(db: Session, link: str) -> Optional[Ad]:
    """Check if an ad with the given link already exists."""
    return db.query(Ad).filter(Ad.link == link).first()

def get_ad_by_id(db: Session, ad_id: int) -> Optional[Ad]:
    """Get a specific ad by ID."""
    return db.query(Ad).filter(Ad.id == ad_id).first()

def get_ads_by_filter(db: Session, min_price=None, max_price=None, year=None, location=None, analysis_session_id=None, vehicle_name=None):
    """Get ads with various filters applied."""
    query = db.query(Ad)
    if year:
        query = query.filter(Ad.year == str(year))
    if location:
        query = query.filter(Ad.location.ilike(f"%{location}%"))
    if analysis_session_id:
        query = query.filter(Ad.analysis_session_id == analysis_session_id)
    if vehicle_name:
        query = query.filter(Ad.vehicle_name.ilike(f"%{vehicle_name}%"))
    # For price, you may want to parse and filter as int, but this is a simple example
    return query.all()

def update_ad(db: Session, ad_id: int, ad_data: dict) -> Optional[Ad]:
    """Update an existing ad."""
    db_ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if db_ad:
        for key, value in ad_data.items():
            setattr(db_ad, key, value)
        db.commit()
        db.refresh(db_ad)
    return db_ad

def delete_ad(db: Session, ad_id: int) -> bool:
    """Delete an ad by ID."""
    db_ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if db_ad:
        db.delete(db_ad)
        db.commit()
        return True
    return False

def get_total_ads_count(db: Session) -> int:
    """Get total count of ads in the database."""
    return db.query(Ad).count()

def get_ads_by_session_id(db: Session, analysis_session_id: str):
    """Get all ads for a specific analysis session."""
    return db.query(Ad).filter(Ad.analysis_session_id == analysis_session_id).all()

def get_ads_by_vehicle_and_session(db: Session, vehicle_name: str, analysis_session_id: str):
    """Get ads for a specific vehicle in a specific analysis session."""
    return db.query(Ad).filter(
        Ad.vehicle_name.ilike(f"%{vehicle_name}%"),
        Ad.analysis_session_id == analysis_session_id
    ).all()
