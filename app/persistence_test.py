import time
from datetime import datetime
from .database import SessionLocal
from .models import User
from .config import settings
import hashlib

def test_data_persistence():
    """Test if data persists between sessions"""
    print("=== Testing Data Persistence ===")
    
    try:
        db = SessionLocal()
        
        # Create a test record with timestamp
        timestamp = datetime.utcnow().isoformat()
        test_email = f"test_{int(time.time())}@example.com"
        
        test_user = User(
            email=test_email,
            username=f"test_user_{int(time.time())}",
            full_name=f"Test User {timestamp}",
            hashed_password=hashlib.sha256(f"test_{timestamp}".encode()).hexdigest(),
            is_admin=False,
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        test_id = test_user.id
        print(f"✓ Created test user with ID: {test_id}")
        
        # Verify it exists
        saved_user = db.query(User).filter(User.id == test_id).first()
        if saved_user:
            print(f"✓ Verified test user exists: {saved_user.email}")
        else:
            print("✗ Test user not found after creation!")
            return False
        
        db.close()
        
        # Wait a moment and test again with new session
        time.sleep(1)
        db2 = SessionLocal()
        retrieved_user = db2.query(User).filter(User.id == test_id).first()
        
        if retrieved_user:
            print(f"✓ Data persists across sessions: {retrieved_user.email}")
            # Clean up
            db2.delete(retrieved_user)
            db2.commit()
            db2.close()
            return True
        else:
            print("✗ Data does NOT persist across sessions!")
            db2.close()
            return False
            
    except Exception as e:
        print(f"✗ Persistence test failed: {e}")
        return False

def get_database_info():
    """Get detailed database information"""
    try:
        db = SessionLocal()
        
        # Count users
        user_count = db.query(User).count()
        
        # Get database type
        db_type = "PostgreSQL" if settings.DATABASE_URL.startswith("postgresql") else "SQLite"
        
        # Get recent users
        recent_users = db.query(User).order_by(User.id.desc()).limit(3).all()
        
        db.close()
        
        return {
            "database_type": db_type,
            "database_url": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
            "user_count": user_count,
            "recent_users": [{"id": u.id, "email": u.email, "username": u.username} for u in recent_users],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "database_type": "Unknown",
            "timestamp": datetime.utcnow().isoformat()
        }
