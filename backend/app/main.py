
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes
from routes import convo_routes
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000"],  # Replace with your frontend's URL
    # allow_credentials=True,  # Allow cookies to be sent with requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(convo_routes.router, prefix="/conversations")

@app.get("/")
def root():
    return {"message": "API is up"}