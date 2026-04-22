from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash
import os

def init_db():
    """Initialize database and create admin user"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@gmail.com").first()
        if not admin:
            print("Creating admin user...")
            # Create admin user
            admin = User(
                email="admin@gmail.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("11112222"),
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Admin user created successfully")
        else:
            print("Admin user already exists")
            # Update password just in case
            admin.hashed_password = get_password_hash("11112222")
            db.commit()
            print("Admin password updated")
        
        # List all users
        users = db.query(User).all()
        print(f"\nTotal users in database: {len(users)}")
        for user in users:
            print(f"- {user.email} (Admin: {user.is_admin})")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialization complete")