from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import re

# ================= CONFIG =================
API_KEY = "MY_SECRET_API_KEY"

# ================= APP ====================
app = FastAPI(title="Agentic HoneyPot API")

# ================= MODELS =================
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class ScamRequest(BaseModel):
    sessionId: Optional[str] = None
    message: Message
    conversationHistory: Optional[List[Message]] = []
    metadata: Optional[dict] = None

# ================= MEMORY =================
sessions = {}

# ================= HELPERS =================
def detect_scam(text: str) -> bool:
    keywords = [
        "blocked", "suspended", "verify", "urgent",
        "upi", "bank", "account", "click", "link"
    ]
    return any(k in text.lower() for k in keywords)

def extract_intelligence(text: str, store: dict):
    upi = re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text)
    phone = re.findall(r"\+91\d{10}", text)
    link = re.findall(r"https?://\S+", text)

    store["upiIds"].extend(upi)
    store["phoneNumbers"].extend(phone)
    store["phishingLinks"].extend(link)

def agent_reply(history_len: int) -> str:
    replies = [
        "Why is my account being blocked?",
        "I already completed KYC last month.",
        "Which bank branch is this from?",
        "Can you explain what will happen if I don’t do this?",
        "I am outside right now, is there another way?"
    ]
    return replies[min(history_len, len(replies) - 1)]

# ================= ENDPOINT ===============
@app.post("/honeypot")
def honeypot(
    data: ScamRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session_id = data.sessionId or "default"

    if session_id not in sessions:
        sessions[session_id] = {
            "scamDetected": False,
            "messages": [],
            "intelligence": {
                "upiIds": [],
                "phoneNumbers": [],
                "phishingLinks": []
            }
        }

    session = sessions[session_id]
    text = data.message.text

    session["messages"].append(text)

    if detect_scam(text):
        session["scamDetected"] = True
        extract_intelligence(text, session["intelligence"])

      reply = agent_reply(len(session["messages"]))

    # FINAL CALLBACK CONDITION (simple rule for demo)
    if session["scamDetected"] and len(session["messages"]) >= 5:
        import requests

        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": len(session["messages"]),
            "extractedIntelligence": {
                "upiIds": session["intelligence"]["upiIds"],
                "phoneNumbers": session["intelligence"]["phoneNumbers"],
                "phishingLinks": session["intelligence"]["phishingLinks"],
                "bankAccounts": [],
                "suspiciousKeywords": ["blocked", "verify", "urgent"]
            },
            "agentNotes": "Used urgency and payment redirection tactics"
        }

        try:
            requests.post(
                "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
                json=payload,
                timeout=5
            )
        except:
            pass

    return {
        "status": "success",
        "reply": reply
    }
