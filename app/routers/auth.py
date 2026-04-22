from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated
from pydantic import BaseModel, EmailStr
from .. import schemas, auth, models
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

# Add a Pydantic model for JSON login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=schemas.Token)
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login endpoint that accepts both form data and JSON
    """
    # Check content type
    content_type = request.headers.get("content-type", "")
    
    if "application/json" in content_type:
        # Handle JSON request
        body = await request.json()
        email = body.get("email") or body.get("username")
        password = body.get("password")
    else:
        # Handle form data
        form = await request.form()
        email = form.get("email") or form.get("username")
        password = form.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email and password are required"
        )
    
    # Authenticate user
    user = auth.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Keep the OAuth2 form endpoint for compatibility
@router.post("/token", response_model=schemas.Token)
async def login_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user = Depends(auth.get_current_active_user)):
    return current_user

# Create default admin user
@router.post("/create-admin", response_model=schemas.UserResponse)
def create_admin(db: Session = Depends(get_db)):
    # Check if admin exists
    admin = db.query(models.User).filter(models.User.email == "admin@gmail.com").first()
    if admin:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    # Create admin user
    hashed_password = auth.get_password_hash("11112222")
    admin = models.User(
        email="admin@gmail.com",
        username="admin",
        full_name="System Administrator",
        hashed_password=hashed_password,
        is_admin=True,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin