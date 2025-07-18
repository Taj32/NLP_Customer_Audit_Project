# api_uploader.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")
LOGIN_ENDPOINT = f"{API_URL}/auth/login"
CONVO_ENDPOINT = f"{API_URL}/conversations/"

def get_token(email, password):
    payload = {"email": email, "password": password}
    response = requests.post(LOGIN_ENDPOINT, json=payload)
    response.raise_for_status()
    return response.json()["access_token"]  # Adjust if your token key is named differently

def post_conversation(token, transcript, sentiment, emotions, summary):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "transcript": transcript,
        "sentiment_score": sentiment,
        "emotion_scores": emotions,
        "summary": summary,
    }
    
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    
    print("stopping before posting conversation [[TESTING]]")
    #return None #temporarily stopping here
    response = requests.post(CONVO_ENDPOINT, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
