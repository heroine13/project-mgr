"""
Database initialization script
Creates all tables in the database
"""
import os
import sys

# Add the backend app to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine
from app.models import *  # noqa: F401, F403 - import all models

def init_database():
    """Create all tables"""
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated {len(tables)} tables:")
    for t in sorted(tables):
        print(f"  - {t}")

if __name__ == "__main__":
    init_database()
