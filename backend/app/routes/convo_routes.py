from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Conversation, User
from jose import jwt
from pydantic import BaseModel
from datetime import datetime

# Initialize the router
router = APIRouter()

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"

# Helper function to decode the JWT token and get the user ID
def get_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic model for conversation requests
class ConversationRequest(BaseModel):
    transcript: str
    sentiment_score: str
    emotion_scores: dict
    summary: str

# Routes

## List all conversations for the authenticated user
@router.get("/")
def list_conversations(authorization: str = Header(...)):
    try:
        # Extract the token from the "Bearer <token>" format
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    db = SessionLocal()
    user_id = get_user(token)
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()

    if not conversations:
        return {"message": "No records found"}

    return conversations

## Get a specific conversation by ID
@router.get("/{id}")
def get_conversation(id: int, authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    db = SessionLocal()
    user_id = get_user(token)
    convo = db.query(Conversation).filter(Conversation.id == id).first()
    if not convo or convo.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or not found")
    return convo

## Create a new conversation
@router.post("/")
def create_conversation(data: ConversationRequest, authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    db = SessionLocal()
    user_id = get_user(token)

    convo = Conversation(
        user_id=user_id,
        transcript=data.transcript,
        sentiment_score=data.sentiment_score,
        emotion_scores=data.emotion_scores,
        summary=data.summary,
        created_at=datetime.utcnow()
    )
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo

## Update an existing conversation
@router.put("/{id}")
def update_conversation(id: int, data: ConversationRequest, authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    db = SessionLocal()
    user_id = get_user(token)

    convo = db.query(Conversation).filter(Conversation.id == id).first()
    if not convo or convo.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or not found")

    convo.transcript = data.transcript
    convo.sentiment_score = data.sentiment_score
    convo.emotion_scores = data.emotion_scores
    convo.summary = data.summary
    db.commit()
    return convo

## Delete a conversation
@router.delete("/{id}")
def delete_conversation(id: int, authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    db = SessionLocal()
    user_id = get_user(token)

    convo = db.query(Conversation).filter(Conversation.id == id).first()
    if not convo or convo.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or not found")

    db.delete(convo)
    db.commit()
    return {"message": f"Conversation {id} deleted"}