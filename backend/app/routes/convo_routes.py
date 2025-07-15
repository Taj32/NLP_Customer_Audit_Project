from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Conversation, User
from jose import jwt

router = APIRouter()

def get_user(token: str):
    payload = jwt.decode(token, "yoursecret", algorithms=["HS256"])
    return int(payload.get("sub"))

@router.get("/")
def list_conversations(token: str):
    db = SessionLocal()
    user_id = get_user(token)
    return db.query(Conversation).filter(Conversation.user_id == user_id).all()

@router.get("/{id}")
def get_conversation(id: int, token: str):
    db = SessionLocal()
    user_id = get_user(token)
    convo = db.query(Conversation).filter(Conversation.id == id).first()
    if convo.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return convo
