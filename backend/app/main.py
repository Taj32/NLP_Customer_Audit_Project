# app/main.py
from fastapi import FastAPI
from routes import auth_routes, convo_routes

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(convo_routes.router, prefix="/conversations")

@app.get("/")
def root():
    return {"message": "Customer Satisfaction API is running"}