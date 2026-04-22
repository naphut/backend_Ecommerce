from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Product schemas
class ProductSpecs(BaseModel):
    display: Optional[str] = None
    processor: Optional[str] = None
    camera: Optional[str] = None
    battery: Optional[str] = None
    water_resistant: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    brand: str
    category: str
    price: float
    original_price: Optional[float] = None
    rating: Optional[float] = 0
    reviews: Optional[int] = 0
    in_stock: bool = True
    featured: bool = False
    discount: Optional[int] = 0
    colors: List[str] = []
    storage: List[str] = []
    description: str = ""
    specs: Optional[Dict[str, Any]] = {}

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    in_stock: Optional[bool] = None
    featured: Optional[bool] = None
    discount: Optional[int] = None
    colors: Optional[List[str]] = None
    storage: Optional[List[str]] = None
    description: Optional[str] = None
    specs: Optional[Dict[str, Any]] = None

class ProductResponse(ProductBase):
    id: int
    main_image: Optional[str] = None
    images: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Upload schemas
class UploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
    file_type: str