# app/crud/ad_crud.py
from sqlalchemy.orm import Session
from app.models.ad import Ad

def create_ad(db: Session, ad_data: dict):
    db_ad = Ad(**ad_data)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

def get_ads(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ad).offset(skip).limit(limit).all()

def get_ads_by_filter(db: Session, min_price=None, max_price=None, year=None, location=None):
    query = db.query(Ad)
    if year:
        query = query.filter(Ad.year == str(year))
    if location:
        query = query.filter(Ad.location.ilike(f"%{location}%"))
    # For price, you may want to parse and filter as int, but this is a simple example
    return query.all()