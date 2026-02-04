# main.py
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

# Load your API key from environment variables
API_KEY = os.getenv("HONEYPOT_API_KEY", "default_key")

app = FastAPI(title="Agentic Honeypot API", version="1.0")

# Schemas
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[dict] = []
    metadata: Optional[Metadata] = None

class ScamResponse(BaseModel):
    status: str
    reply: str

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Honeypot API is running"}

# Honeypot endpoint
@app.post("/honeypot", response_model=ScamResponse)
async def honeypot(
    request: ScamRequest,
    x_api_key: str = Header(...)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Simple scam detection logic (you can replace this with AI/ML later)
    text = request.message.text.lower()
    if any(word in text for word in ["upi", "account", "blocked", "password"]):
        reply = "I already completed KYC last month."
    else:
        reply = "Thanks for the message."

    return {"status": "success", "reply": reply}


