from app.database import SessionLocal
from app.models import User
from app.auth import verify_password, get_password_hash
import sys

def debug_auth():
    db = SessionLocal()
    
    print("="*50)
    print("AUTHENTICATION DEBUG")
    print("="*50)
    
    # Check all users
    users = db.query(User).all()
    print(f"\nTotal users in database: {len(users)}")
    
    for user in users:
        print(f"\n--- User: {user.email} ---")
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Full Name: {user.full_name}")
        print(f"Is Admin: {user.is_admin}")
        print(f"Is Active: {user.is_active}")
        print(f"Password Hash: {user.hashed_password[:50]}...")
        
        # Test password verification
        test_password = "11112222"
        is_valid = verify_password(test_password, user.hashed_password)
        print(f"Password '11112222' valid: {is_valid}")
    
    # Try to find admin specifically
    print("\n" + "="*50)
    print("ADMIN USER SEARCH")
    print("="*50)
    
    admin = db.query(User).filter(User.email == "admin@gmail.com").first()
    if admin:
        print(f"✓ Admin user found: {admin.email}")
        print(f"Testing password '11112222': {verify_password('11112222', admin.hashed_password)}")
    else:
        print("✗ Admin user NOT found!")
        
        # Create admin if not exists
        print("\nCreating admin user...")
        hashed = get_password_hash("11112222")
        new_admin = User(
            email="admin@gmail.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=hashed,
            is_admin=True,
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        print("✓ Admin user created successfully")
        
        # Verify new admin
        admin = db.query(User).filter(User.email == "admin@gmail.com").first()
        print(f"Testing new admin password: {verify_password('11112222', admin.hashed_password)}")
    
    db.close()

if __name__ == "__main__":
    debug_auth()