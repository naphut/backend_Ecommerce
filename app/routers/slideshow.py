from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import SlideShow
from pydantic import BaseModel
import os
import uuid
from ..config import settings

router = APIRouter(prefix="/api/slideshow", tags=["slideshow"])

# Pydantic models
class SlideShowBase(BaseModel):
    title: str
    description: str = None
    image_url: str
    button_text: str = None
    button_link: str = None
    is_active: bool = True
    order: int = 0

class SlideShowCreate(SlideShowBase):
    pass

class SlideShowUpdate(BaseModel):
    title: str = None
    description: str = None
    image_url: str = None
    button_text: str = None
    button_link: str = None
    is_active: bool = None
    order: int = None

class SlideShowResponse(SlideShowBase):
    id: int
    created_at: str
    updated_at: str | None = None

    class Config:
        from_attributes = True

# Helper function to handle image upload
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Create slideshow uploads directory if it doesn't exist
    slideshow_dir = os.path.join(settings.UPLOAD_DIR, "slideshow")
    os.makedirs(slideshow_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(slideshow_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Return the URL path
    return f"/uploads/slideshow/{unique_filename}"

# CRUD endpoints
@router.get("/", response_model=List[SlideShowResponse])
def get_slideshows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all active slideshows for frontend"""
    slideshows = db.query(SlideShow).filter(
        SlideShow.is_active == True
    ).order_by(SlideShow.order).offset(skip).limit(limit).all()
    return slideshows

@router.get("/admin/all", response_model=List[SlideShowResponse])
def get_all_slideshows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all slideshows for admin (including inactive)"""
    slideshows = db.query(SlideShow).order_by(SlideShow.order).offset(skip).limit(limit).all()
    return slideshows

@router.get("/{slideshow_id}", response_model=SlideShowResponse)
def get_slideshow(slideshow_id: int, db: Session = Depends(get_db)):
    """Get specific slideshow by ID"""
    slideshow = db.query(SlideShow).filter(SlideShow.id == slideshow_id).first()
    if not slideshow:
        raise HTTPException(status_code=404, detail="Slideshow not found")
    return slideshow

@router.post("/", response_model=SlideShowResponse)
async def create_slideshow(slideshow: SlideShowCreate, db: Session = Depends(get_db)):
    """Create new slideshow"""
    db_slideshow = SlideShow(**slideshow.dict())
    db.add(db_slideshow)
    db.commit()
    db.refresh(db_slideshow)
    return db_slideshow

@router.post("/upload", response_model=dict)
async def upload_slideshow_image(file: UploadFile = File(...)):
    """Upload image for slideshow"""
    image_url = await upload_image(file)
    return {"image_url": image_url}

@router.put("/{slideshow_id}", response_model=SlideShowResponse)
def update_slideshow(slideshow_id: int, slideshow: SlideShowUpdate, db: Session = Depends(get_db)):
    """Update slideshow"""
    db_slideshow = db.query(SlideShow).filter(SlideShow.id == slideshow_id).first()
    if not db_slideshow:
        raise HTTPException(status_code=404, detail="Slideshow not found")
    
    update_data = slideshow.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_slideshow, field, value)
    
    db.commit()
    db.refresh(db_slideshow)
    return db_slideshow

@router.delete("/{slideshow_id}")
def delete_slideshow(slideshow_id: int, db: Session = Depends(get_db)):
    """Delete slideshow"""
    db_slideshow = db.query(SlideShow).filter(SlideShow.id == slideshow_id).first()
    if not db_slideshow:
        raise HTTPException(status_code=404, detail="Slideshow not found")
    
    db.delete(db_slideshow)
    db.commit()
    return {"message": "Slideshow deleted successfully"}

@router.post("/{slideshow_id}/toggle")
def toggle_slideshow(slideshow_id: int, db: Session = Depends(get_db)):
    """Toggle slideshow active status"""
    db_slideshow = db.query(SlideShow).filter(SlideShow.id == slideshow_id).first()
    if not db_slideshow:
        raise HTTPException(status_code=404, detail="Slideshow not found")
    
    db_slideshow.is_active = not db_slideshow.is_active
    db.commit()
    db.refresh(db_slideshow)
    return {"message": f"Slideshow {'activated' if db_slideshow.is_active else 'deactivated'}"}
