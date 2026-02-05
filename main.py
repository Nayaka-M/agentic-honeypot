from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(
    title="Agentic Honeypot API",
    version="1.0.0",
    description="Scam interaction honeypot service"
)

# ---- Models ----

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
    conversationHistory: List[dict]
    metadata: Optional[Metadata] = None

class ScamResponse(BaseModel):
    status: str
    reply: str


# ---- Health Check ----

@app.get("/")
def health():
    return "OK"


# ---- Honeypot Endpoint ----

@app.post("/honeypot", response_model=ScamResponse)
def honeypot(
    payload: ScamRequest,
    x_api_key: str = Header(...)
):
    # API key validation
    if x_api_key != os.getenv("HONEYPOT_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")

    text = payload.message.text.lower()

    # VERY FAST rule-based reply (no delay)
    if "blocked" in text or "verify" in text:
        reply = "Why is my account being suspended?"
    elif "upi" in text or "bank" in text:
        reply = "Can you explain the issue in detail?"
    else:
        reply = "I already completed KYC last month."

    return {
        "status": "success",
        "reply": reply
    }


