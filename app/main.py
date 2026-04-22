from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import auth, products, upload
from .config import settings
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce Admin API", version="1.0.0")

# Configure CORS with more permissive settings for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default port
        "https://frontend-user-first.vercel.app",
        "https://frontend-admin-first-6bpu.vercel.app",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://backend-ecommerce-vhi7.onrender.com",  # Render backend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"],  # Exposes all headers
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "products"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "products", "main"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "products", "additional"), exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(upload.router)

@app.get("/")
def root():
    return {"message": "E-commerce Admin API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/debug")
def debug_info():
    try:
        from .database import engine, Base
        from .models import User
        from sqlalchemy.orm import sessionmaker
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@gmail.com").first()
        admin_exists = admin_user is not None
        
        db.close()
        
        return {
            "database_connected": True,
            "admin_user_exists": admin_exists,
            "tables_created": True
        }
    except Exception as e:
        return {
            "database_connected": False,
            "error": str(e)
        }