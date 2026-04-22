from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
from ..utils.image_handler import image_handler
from .. import auth, schemas

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/image", response_model=schemas.UploadResponse, dependencies=[Depends(auth.get_current_admin_user)])
async def upload_image(file: UploadFile = File(...)):
    """Upload a single image"""
    result = await image_handler.save_upload(file)
    return result

@router.post("/images", response_model=List[schemas.UploadResponse], dependencies=[Depends(auth.get_current_admin_user)])
async def upload_images(files: List[UploadFile] = File(...)):
    """Upload multiple images"""
    results = []
    for file in files:
        if file.filename:
            result = await image_handler.save_upload(file)
            results.append(result)
    return results

@router.delete("/image/{image_path:path}", dependencies=[Depends(auth.get_current_admin_user)])
def delete_image(image_path: str):
    """Delete an image"""
    image_handler.delete_image(image_path)
    return {"message": "Image deleted successfully"}