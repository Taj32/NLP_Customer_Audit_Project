# backend/app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, Header
from models import User
from database import SessionLocal
from auth import hash_password, verify_password, create_token
from pydantic import BaseModel, EmailStr
from jose import jwt
import os
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText

router = APIRouter()
load_dotenv()  # Load environment variables from .env

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")  # Use fallback for safety
ALGORITHM = "HS256" 

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    business_name: str

# Generate verification token
def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt="email-verification")

# Verify token
def verify_token(token):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt="email-verification", max_age=3600)  # Token valid for 1 hour
        return email
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

# Send verification email
def send_verification_email(email, token):
    verification_url = f"http://localhost:3000/verify/{token}"
    message = MIMEText(f"Please verify your email by clicking the link: {verification_url}")
    message["Subject"] = "Email Verification"
    message["From"] = EMAIL_SENDER
    message["To"] = email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)  # Authenticate
            server.sendmail(EMAIL_SENDER, email, message.as_string())
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate with the email server.")
    except Exception as e:
        print(f"SMTP Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email.")

@router.post("/register")
def register_user(data: RegisterRequest):
    db = SessionLocal()
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, detail="Email already exists")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        business_name=data.business_name,
        verified=False
    )
    db.add(user)
    db.commit()

    # Generate and send verification email
    token = generate_verification_token(data.email)
    send_verification_email(data.email, token)

    return {"msg": "User created. Please verify your email."}

@router.get("/verify/{token}")
def verify_email(token: str):
    email = verify_token(token)
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.verified = True
    db.commit()
    return {"msg": "Email verified successfully"}

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

