#!/usr/bin/env python3
"""
Database initialization script
"""
from app.core.db import engine
from app.models.ad import Ad
from app.models.comparison import VehicleComparison

def init_database():
    """Initialize database with all tables"""
    print("Creating database tables...")
    
    # Import all models to register them with Base
    from app.models import ad, comparison
    
    # Create all tables
    from app.core.db import Base
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")
    print("Tables created:")
    print("- ads (for storing vehicle advertisement data)")
    print("- vehicle_comparisons (for storing comparison reports)")

if __name__ == "__main__":
    init_database()
