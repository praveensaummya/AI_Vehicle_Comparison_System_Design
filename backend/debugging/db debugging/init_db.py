#!/usr/bin/env python3
"""
Database initialization script
"""

def init_database():
    """Initialize database with all tables"""
    print("Creating database tables...")
    
    # Import database engine and Base first
    from app.core.db import engine, Base
    
    # Import all models to register them with Base - order matters!
    from app.models.ad import Ad
    from app.models.comparison import VehicleComparison
    
    print(f"Registered models: {Base.metadata.tables.keys()}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")
    print("Tables created:")
    print("- ads (for storing vehicle advertisement data)")
    print("- vehicle_comparisons (for storing comparison reports)")

if __name__ == "__main__":
    init_database()
