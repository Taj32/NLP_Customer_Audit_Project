# backend/app/main.py
from fastapi import FastAPI
from app.routes import auth_routes
from app.routes import convo_routes

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(convo_routes.router, prefix="/conversations")

@app.get("/")
def root():
    return {"message": "API is up"}
