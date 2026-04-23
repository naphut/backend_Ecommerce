import os
import time
from sqlalchemy import text
from .database import engine, Base, SessionLocal
from .models import User
from .config import settings
import hashlib

def wait_for_database(max_retries=30, retry_interval=2):
    """Wait for database to be ready"""
    retries = 0
    while retries < max_retries:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print(f"Database connection successful (attempt {retries + 1})")
                
                # Verify it's PostgreSQL in production
                if settings.DATABASE_URL.startswith("postgresql"):
                    try:
                        pg_version = conn.execute(text("SELECT version()")).scalar()
                        print(f"PostgreSQL version: {pg_version[:50]}...")
                    except:
                        pass
                
                return True
        except Exception as e:
            retries += 1
            print(f"Database connection attempt {retries}/{max_retries} failed: {e}")
            if retries < max_retries:
                time.sleep(retry_interval)
    
    print(f"Failed to connect to database after {max_retries} attempts")
    print(f"Database URL was: {settings.DATABASE_URL[:50]}...")
    return False

def initialize_database():
    """Initialize database with proper error handling"""
    try:
        print("Starting database initialization...")
        
        # Wait for database to be ready
        if not wait_for_database():
            print("Database not ready, using fallback SQLite")
            return False
        
        # Create tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create admin user
        print("Creating admin user...")
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.email == "admin@gmail.com").first()
            if not admin_user:
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                admin_user = User(
                    email="admin@gmail.com",
                    username="admin",
                    full_name="System Administrator",
                    hashed_password=password_hash,
                    is_admin=True,
                    is_active=True
                )
                db.add(admin_user)
                db.commit()
                print("Admin user created successfully")
            else:
                print("Admin user already exists")
            
            # Verify database is working
            user_count = db.query(User).count()
            print(f"Database initialized successfully. Total users: {user_count}")
            
        except Exception as e:
            print(f"Error creating admin user: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

def check_database_health():
    """Check if database is healthy"""
    try:
        db = SessionLocal()
        user_count = db.query(User).count()
        db.close()
        return {
            "healthy": True,
            "user_count": user_count,
            "database_type": "PostgreSQL" if settings.DATABASE_URL.startswith("postgresql") else "SQLite"
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "database_type": "PostgreSQL" if settings.DATABASE_URL.startswith("postgresql") else "SQLite"
        }
