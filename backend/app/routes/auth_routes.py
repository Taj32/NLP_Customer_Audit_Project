# backend/app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException
from app.models import User
from app.database import SessionLocal
from app.auth import hash_password, verify_password, create_token
from pydantic import BaseModel, EmailStr

router = APIRouter()

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
