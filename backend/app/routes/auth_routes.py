# backend/app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, Header
from models import User
from database import SessionLocal
from auth import hash_password, verify_password, create_token
from pydantic import BaseModel, EmailStr
from jose import jwt
import os
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()  # Load environment variables from .env

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")  # Use fallback for safety
ALGORITHM = "HS256"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    business_name: str

@router.post("/register")
def register_user(data: RegisterRequest):
    db = SessionLocal()
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, detail="Email already exists")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        business_name=data.business_name
    )
    db.add(user)
    db.commit()
    return {"msg": "User created"}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login_user(data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(400, detail="Invalid credentials")
    token = create_token({"sub": str(user.id)})
    return {"access_token": token}

# Helper function to decode the JWT token and get the user ID
def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# New route to get user account information
@router.get("/account")
def get_account_info(authorization: str = Header(...)):
    try:
        # Extract the token from the "Bearer <token>" format
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    db = SessionLocal()
    user_id = get_user_id_from_token(token)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "business_name": user.business_name,
        "created_at": user.created_at
    }

