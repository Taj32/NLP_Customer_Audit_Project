# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes
from routes import convo_routes
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

# Load allowed origins from environment variables
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS, 
        "https://nlp-customer-audit-project.vercel.app",  # Production Vercel domain
        "https://nlp-customer-audit-project-db3b3wk03-taj32s-projects.vercel.app"  # Temporary Vercel deployment domain
        ],
    allow_credentials=True,  # Allow cookies to be sent with requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(convo_routes.router, prefix="/conversations")

@app.get("/")
def root():
    return {"message": "API is up"}