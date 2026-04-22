from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import logging
from .. import models, schemas, auth
from ..database import get_db
from ..utils.image_handler import image_handler

router = APIRouter(prefix="/products", tags=["products"])
logger = logging.getLogger(__name__)

# Public endpoints
@router.get("/", response_model=List[schemas.ProductResponse])
def read_products(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional filters"""
    query = db.query(models.Product)
    
    if category:
        query = query.filter(models.Product.category == category)
    if featured is not None:
        query = query.filter(models.Product.featured == featured)
    
    products = query.offset(skip).limit(limit).all()
    
    # Convert to list of dicts for proper JSON serialization
    result = []
    for product in products:
        result.append(product.to_dict())
    
    return result

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product.to_dict()

# Admin endpoints
@router.post("/", response_model=schemas.ProductResponse)
async def create_product(
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    original_price: Optional[float] = Form(None),
    rating: Optional[float] = Form(0),
    reviews: Optional[int] = Form(0),
    in_stock: bool = Form(True),
    featured: bool = Form(False),
    discount: Optional[int] = Form(0),
    colors: str = Form("[]"),
    storage: str = Form("[]"),
    description: str = Form(""),
    specs: str = Form("{}"),
    main_image: UploadFile = File(...),
    additional_images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Create a new product (admin only)"""
    try:
        logger.info(f"Creating product: {name}")
        
        # Parse JSON strings
        try:
            colors_list = json.loads(colors)
            storage_list = json.loads(storage)
            specs_dict = json.loads(specs)
            
            # Ensure we have proper types
            if not isinstance(colors_list, list):
                colors_list = []
            if not isinstance(storage_list, list):
                storage_list = []
            if not isinstance(specs_dict, dict):
                specs_dict = {}
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        # Save main image
        main_image_data = await image_handler.save_upload(main_image, "main")
        
        # Save additional images
        additional_images_data = []
        for img in additional_images:
            if img.filename:
                img_data = await image_handler.save_upload(img, "additional")
                additional_images_data.append(img_data["file_path"])
        
        # Create product
        db_product = models.Product(
            name=name,
            brand=brand,
            category=category,
            price=price,
            original_price=original_price,
            rating=rating,
            reviews=reviews,
            in_stock=in_stock,
            featured=featured,
            discount=discount,
            main_image=main_image_data["file_path"],
            description=description
        )
        
        # Set JSON fields - store as Python objects, not strings
        db_product.colors = colors_list
        db_product.storage = storage_list
        db_product.specs = specs_dict
        db_product.images = additional_images_data
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"Product created successfully with ID: {db_product.id}")
        return db_product.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    original_price: Optional[float] = Form(None),
    rating: Optional[float] = Form(None),
    reviews: Optional[int] = Form(None),
    in_stock: Optional[bool] = Form(None),
    featured: Optional[bool] = Form(None),
    discount: Optional[int] = Form(None),
    colors: Optional[str] = Form(None),
    storage: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    specs: Optional[str] = Form(None),
    main_image: Optional[UploadFile] = File(None),
    additional_images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Update a product (admin only)"""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Update basic fields if provided
        if name is not None:
            db_product.name = name
        if brand is not None:
            db_product.brand = brand
        if category is not None:
            db_product.category = category
        if price is not None:
            db_product.price = price
        if original_price is not None:
            db_product.original_price = original_price
        if rating is not None:
            db_product.rating = rating
        if reviews is not None:
            db_product.reviews = reviews
        if in_stock is not None:
            db_product.in_stock = in_stock
        if featured is not None:
            db_product.featured = featured
        if discount is not None:
            db_product.discount = discount
        if description is not None:
            db_product.description = description
        
        # Update JSON fields if provided
        if colors is not None:
            try:
                colors_list = json.loads(colors)
                db_product.colors = colors_list if isinstance(colors_list, list) else []
            except json.JSONDecodeError:
                pass
        
        if storage is not None:
            try:
                storage_list = json.loads(storage)
                db_product.storage = storage_list if isinstance(storage_list, list) else []
            except json.JSONDecodeError:
                pass
        
        if specs is not None:
            try:
                specs_dict = json.loads(specs)
                db_product.specs = specs_dict if isinstance(specs_dict, dict) else {}
            except json.JSONDecodeError:
                pass
        
        # Update main image if provided
        if main_image and main_image.filename:
            # Delete old main image
            if db_product.main_image:
                image_handler.delete_image(db_product.main_image)
            # Save new image
            main_image_data = await image_handler.save_upload(main_image, "main")
            db_product.main_image = main_image_data["file_path"]
        
        # Add additional images if provided
        if additional_images and any(img.filename for img in additional_images):
            current_images = db_product.get_images()
            for img in additional_images:
                if img.filename:
                    img_data = await image_handler.save_upload(img, "additional")
                    current_images.append(img_data["file_path"])
            db_product.images = current_images
        
        db.commit()
        db.refresh(db_product)
        return db_product.to_dict()
        
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{product_id}")
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Delete a product (admin only)"""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Delete images
        if db_product.main_image:
            image_handler.delete_image(db_product.main_image)
        
        for image_path in db_product.get_images():
            image_handler.delete_image(image_path)
        
        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{product_id}/images/{image_index}")
def delete_product_image(
    product_id: int, 
    image_index: int, 
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Delete a specific image from a product (admin only)"""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    images = db_product.get_images()
    if image_index < 0 or image_index >= len(images):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Delete image file
        image_handler.delete_image(images[image_index])
        
        # Remove from list
        images.pop(image_index)
        db_product.images = images
        
        db.commit()
        return {"message": "Image deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))