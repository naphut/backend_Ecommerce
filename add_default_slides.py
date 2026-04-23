#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import SlideShow

def add_default_slides():
    """Add default slides to the database"""
    db = SessionLocal()
    
    try:
        # Check if slides already exist
        existing_slides = db.query(SlideShow).count()
        if existing_slides > 0:
            print(f"Slides already exist ({existing_slides} found). Skipping default slides creation.")
            return
        
        default_slides = [
            {
                "title": "Latest Smartphones",
                "description": "Discover the newest technology and innovations in mobile phones",
                "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1780&q=80",
                "button_text": "Shop Now",
                "button_link": "/products",
                "is_active": True,
                "order": 1
            },
            {
                "title": "Exclusive Deals",
                "description": "Up to 40% off on selected models - Limited time offer!",
                "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1742&q=80",
                "button_text": "View Deals",
                "button_link": "/products?category=deals",
                "is_active": True,
                "order": 2
            },
            {
                "title": "Premium Accessories",
                "description": "Complete your phone experience with our premium accessories",
                "image_url": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1740&q=80",
                "button_text": "Explore",
                "button_link": "/products?category=accessories",
                "is_active": True,
                "order": 3
            }
        ]
        
        for slide_data in default_slides:
            slide = SlideShow(**slide_data)
            db.add(slide)
        
        db.commit()
        print(f"Successfully added {len(default_slides)} default slides to the database")
        
    except Exception as e:
        print(f"Error adding default slides: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_default_slides()
