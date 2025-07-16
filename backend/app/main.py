# backend/app/main.py
from fastapi import FastAPI
from app.routes import auth_routes

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth")

@app.get("/")
def root():
    return {"message": "API is up"}
