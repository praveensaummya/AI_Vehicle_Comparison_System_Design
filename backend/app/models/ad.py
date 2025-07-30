# app/models/ad.py
from sqlalchemy import Column, Integer, String
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