from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, Text, DateTime
from sqlalchemy.sql import func
from .database import Base
import json

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    brand = Column(String, index=True)
    category = Column(String, index=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    rating = Column(Float, default=0)
    reviews = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)
    discount = Column(Integer, default=0)
    colors = Column(JSON)
    storage = Column(JSON)
    main_image = Column(String)
    images = Column(JSON)
    description = Column(Text)
    specs = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def set_colors(self, colors_list):
        """Store colors as JSON"""
        self.colors = colors_list
    
    def get_colors(self):
        """Return colors as list"""
        if self.colors is None:
            return []
        if isinstance(self.colors, str):
            return json.loads(self.colors)
        return self.colors
    
    def set_storage(self, storage_list):
        """Store storage as JSON"""
        self.storage = storage_list
    
    def get_storage(self):
        """Return storage as list"""
        if self.storage is None:
            return []
        if isinstance(self.storage, str):
            return json.loads(self.storage)
        return self.storage
    
    def set_images(self, images_list):
        """Store images as JSON"""
        self.images = images_list
    
    def get_images(self):
        """Return images as list"""
        if self.images is None:
            return []
        if isinstance(self.images, str):
            return json.loads(self.images)
        return self.images
    
    def set_specs(self, specs_dict):
        """Store specs as JSON"""
        self.specs = specs_dict
    
    def get_specs(self):
        """Return specs as dict"""
        if self.specs is None:
            return {}
        if isinstance(self.specs, str):
            return json.loads(self.specs)
        return self.specs
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'price': self.price,
            'original_price': self.original_price,
            'rating': self.rating,
            'reviews': self.reviews,
            'in_stock': self.in_stock,
            'featured': self.featured,
            'discount': self.discount,
            'colors': self.get_colors(),
            'storage': self.get_storage(),
            'main_image': self.main_image,
            'images': self.get_images(),
            'description': self.description,
            'specs': self.get_specs(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }