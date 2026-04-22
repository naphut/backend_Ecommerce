import os
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
import uuid
from datetime import datetime
from ..config import settings

class ImageHandler:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.products_dir = self.upload_dir / "products"
        self.temp_dir = self.upload_dir / "temp"
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        self.products_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_image(self, file: UploadFile):
        """Validate image file type and size"""
        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Check file size (we'll check after reading)
        return ext
    
    async def save_upload(self, file: UploadFile, subdir: str = "") -> dict:
        """Save uploaded file and return file info"""
        # Validate file
        ext = self.validate_image(file)
        
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}{ext}"
        
        # Create subdirectory path
        save_dir = self.products_dir
        if subdir:
            save_dir = save_dir / subdir
            save_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = save_dir / filename
        
        # Save file
        content = await file.read()
        
        # Check file size
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Optimize image
        self.optimize_image(file_path)
        
        # Return relative path for database
        relative_path = f"uploads/products/{subdir}/{filename}" if subdir else f"uploads/products/{filename}"
        
        return {
            "filename": filename,
            "file_path": relative_path,
            "file_size": len(content),
            "file_type": file.content_type
        }
    
    def optimize_image(self, image_path: Path, max_size=(1200, 1200), quality=85):
        """Optimize image by resizing and compressing"""
        try:
            img = Image.open(image_path)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert RGBA to RGB if saving as JPEG
            if image_path.suffix.lower() in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            img.save(image_path, optimize=True, quality=quality)
        except Exception as e:
            print(f"Error optimizing image: {e}")
    
    def delete_image(self, image_path: str):
        """Delete image file"""
        full_path = Path(settings.UPLOAD_DIR) / image_path.replace("uploads/", "")
        if full_path.exists():
            full_path.unlink()
    
    def get_image_url(self, image_path: str) -> str:
        """Convert file path to URL"""
        return f"/{image_path}"

image_handler = ImageHandler()