from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth import hash_password, verify_password, create_token
from pydantic import BaseModel, EmailStr

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    business_name: str

@router.post("/register")
def register(req: RegisterRequest):
    db = SessionLocal()
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        business_name=req.business_name
    )
    db.add(user)
    db.commit()
    return {"message": "User registered"}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login(req: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({"sub": str(user.id)})
    return {"access_token": token}
