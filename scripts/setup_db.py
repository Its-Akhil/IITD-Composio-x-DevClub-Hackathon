#!/usr/bin/env python3
"""
Initialize database schema
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, engine
from sqlalchemy import inspect

def setup_database():
    """Setup database tables"""
    print("Initializing database...")
    
    try:
        init_db()
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\\n✓ Database initialized with {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        
        print("\\n✅ Database setup complete!")
        
    except Exception as e:
        print(f"\\n❌ Database setup failed: {e}")

if __name__ == "__main__":
    setup_database()
