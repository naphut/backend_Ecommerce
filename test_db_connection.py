#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import engine, SessionLocal
from app.models import User
from sqlalchemy import text

def test_database_connection():
    """Test database connection and type"""
    print("=== Database Connection Test ===")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    
    # Test basic connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    # Check database type
    if settings.DATABASE_URL.startswith("postgresql"):
        print("✓ Using PostgreSQL (persistent)")
    elif settings.DATABASE_URL.startswith("sqlite"):
        print("✗ Using SQLite (ephemeral - this is the problem!)")
        return False
    else:
        print(f"? Unknown database type: {settings.DATABASE_URL}")
    
    # Test data persistence
    try:
        db = SessionLocal()
        user_count = db.query(User).count()
        print(f"✓ Current user count: {user_count}")
        
        # Test adding a test user
        test_user = User(
            email="test@example.com",
            username="test_user",
            full_name="Test User",
            hashed_password="test_hash",
            is_admin=False,
            is_active=True
        )
        db.add(test_user)
        db.commit()
        
        # Verify it was added
        new_count = db.query(User).count()
        print(f"✓ After adding test user: {new_count}")
        
        # Clean up
        db.delete(test_user)
        db.commit()
        final_count = db.query(User).count()
        print(f"✓ After cleanup: {final_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Data persistence test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    if success:
        print("\n✓ Database test PASSED")
        sys.exit(0)
    else:
        print("\n✗ Database test FAILED")
        sys.exit(1)
