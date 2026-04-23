import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Force PostgreSQL in production environments
    database_url = os.getenv("DATABASE_URL")
    
    if database_url and database_url.startswith("postgresql"):
        DATABASE_URL: str = database_url
        print(f"✓ Using PostgreSQL database: {database_url[:30]}...")
    elif database_url:
        DATABASE_URL: str = database_url
        print(f"⚠ Using provided database: {database_url[:30]}...")
    elif os.getenv("RENDER") or os.getenv("VERCEL"):
        # Force PostgreSQL error in cloud environments
        raise ValueError("DATABASE_URL environment variable is required in production!")
    else:
        DATABASE_URL: str = "sqlite:///./database.db"
        print("⚠ Using SQLite database (local development only)")
    
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    
    class Config:
        env_file = ".env"

settings = Settings()