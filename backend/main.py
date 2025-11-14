"""
SocialGuard - Real-Time Trust Scoring & Just-In-Time Defense Platform
Backend API Service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import redis
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SocialGuard API",
    description="AI-Powered Social Engineering Defense Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
try:
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
    r = None

# In-memory cache fallback
cache = {}


class TrustEvent(BaseModel):
    """Event data for trust scoring"""
    event_id: str
    event_type: str  # email, chat, voice, web, mobile
    sender: Optional[str] = None
    recipient: Optional[str] = None
    content: Optional[str] = None
    domain_age_days: Optional[int] = 999
    lookalike_domain: bool = False
    spf_pass: bool = True
    dkim_pass: bool = True
    dmarc_pass: bool = True
    urgency_language: bool = False
    credential_request: bool = False
    payment_request: bool = False
    qr_code_present: bool = False
    after_hours: bool = False
    device_change: bool = False
    location_change: bool = False
    privilege_level: str = "standard"  # standard, elevated, admin
    in_org_graph: bool = True
    voice_synthetic_score: Optional[float] = 0.0
    metadata: Optional[Dict] = {}


class TrustScore(BaseModel):
    """Trust score response"""
    event_id: str
    score: int
    risk_level: str
    factors: List[str]
    timestamp: str


class NudgeResponse(BaseModel):
    """Nudge response for user"""
    event_id: str
    banner_color: str
    message: str
    action_required: str
    verification_method: Optional[str] = None


def calculate_trust_score(event: TrustEvent) -> Dict:
    """
    Calculate trust score based on multiple signals
    Score: 0-100 (100 = fully trusted, 0 = highly suspicious)
    """
    score = 100
    factors = []

    # Identity Signals
    if event.domain_age_days < 30:
        score -= 25
        factors.append(f"New domain (registered {event.domain_age_days} days ago)")

    if event.lookalike_domain:
        score -= 30
        factors.append("Lookalike domain detected")

    if not event.spf_pass:
        score -= 15
        factors.append("SPF validation failed")

    if not event.dkim_pass:
        score -= 15
        factors.append("DKIM validation failed")

    if not event.dmarc_pass:
        score -= 10
        factors.append("DMARC validation failed")

    # Content Analysis
    if event.urgency_language:
        score -= 15
        factors.append("Urgency/emotional manipulation detected")

    if event.credential_request:
        score -= 20
        factors.append("Requesting credentials or MFA codes")

    if event.payment_request:
        score -= 20
        factors.append("Payment or financial information requested")

    if event.qr_code_present:
        score -= 10
        factors.append("QR code present (potential ClickFix)")

    # Behavioral Patterns
    if not event.in_org_graph:
        score -= 15
        factors.append("Sender not in organizational graph")

    if event.device_change:
        score -= 10
        factors.append("Unusual device detected")

    if event.location_change:
        score -= 10
        factors.append("Geographic location mismatch")

    # Contextual Factors
    if event.after_hours and (event.payment_request or event.privilege_level in ["elevated", "admin"]):
        score -= 15
        factors.append("After-hours sensitive request")

    # Voice-specific
    if event.event_type == "voice" and event.voice_synthetic_score and event.voice_synthetic_score > 0.6:
        score -= 25
        factors.append(f"High likelihood of AI-generated voice ({event.voice_synthetic_score:.0%})")

    # Ensure score stays in valid range
    score = max(0, min(100, score))

    # Determine risk level
    if score < 40:
        risk_level = "HIGH"
    elif score < 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "event_id": event.event_id,
        "score": score,
        "risk_level": risk_level,
        "factors": factors,
        "timestamp": datetime.utcnow().isoformat()
    }


def get_nudge_response(trust_score: Dict, event_type: str) -> NudgeResponse:
    """
    Generate appropriate nudge based on trust score and event type
    """
    score = trust_score["score"]
    risk_level = trust_score["risk_level"]
    event_id = trust_score["event_id"]

    if score < 40:
        # HIGH RISK
        return NudgeResponse(
            event_id=event_id,
            banner_color="RED",
            message="⚠️ HIGH RISK: This interaction shows multiple suspicious indicators. Do not proceed without verification.",
            action_required="BLOCK",
            verification_method="dual_approval_callback"
        )
    elif score < 70:
        # MEDIUM RISK
        return NudgeResponse(
            event_id=event_id,
            banner_color="AMBER",
            message="⚡ CAUTION: This request shows suspicious patterns. Verify through an alternate channel before proceeding.",
            action_required="VERIFY",
            verification_method="callback_or_safeview"
        )
    else:
        # LOW RISK
        return NudgeResponse(
            event_id=event_id,
            banner_color="GREEN",
            message="✓ This interaction appears legitimate, but stay vigilant.",
            action_required="ALLOW",
            verification_method=None
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "SocialGuard API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.post("/calculate_trust_score", response_model=TrustScore)
async def calculate_score(event: TrustEvent):
    """
    Calculate trust score for an event
    """
    try:
        logger.info(f"Processing trust score for event: {event.event_id}")

        # Calculate trust score
        trust_score = calculate_trust_score(event)

        # Cache the result
        if r:
            r.setex(f"trust_score:{event.event_id}", 3600, json.dumps(trust_score))
        else:
            cache[event.event_id] = trust_score

        return TrustScore(**trust_score)

    except Exception as e:
        logger.error(f"Error calculating trust score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deliver_nudge", response_model=NudgeResponse)
async def deliver_nudge(event: TrustEvent):
    """
    Deliver just-in-time nudge based on trust score
    """
    try:
        logger.info(f"Delivering nudge for event: {event.event_id}")

        # Check cache first
        cached_score = None
        if r:
            cached = r.get(f"trust_score:{event.event_id}")
            if cached:
                cached_score = json.loads(cached)
        elif event.event_id in cache:
            cached_score = cache[event.event_id]

        # Calculate if not cached
        if not cached_score:
            cached_score = calculate_trust_score(event)

        # Generate nudge
        nudge = get_nudge_response(cached_score, event.event_type)

        return nudge

    except Exception as e:
        logger.error(f"Error delivering nudge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trust_score/{event_id}")
async def get_trust_score(event_id: str):
    """
    Retrieve cached trust score for an event
    """
    try:
        if r:
            cached = r.get(f"trust_score:{event_id}")
            if cached:
                return json.loads(cached)
        elif event_id in cache:
            return cache[event_id]

        raise HTTPException(status_code=404, detail="Trust score not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trust score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/user_feedback")
async def record_feedback(event_id: str, action: str, user_comment: Optional[str] = None):
    """
    Record user feedback for continuous learning
    """
    try:
        feedback = {
            "event_id": event_id,
            "action": action,  # reported_suspicious, ignored, confirmed_legit
            "user_comment": user_comment,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Store feedback
        if r:
            r.lpush("user_feedback", json.dumps(feedback))

        logger.info(f"Feedback recorded for event {event_id}: {action}")

        return {"status": "success", "message": "Feedback recorded"}

    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """
    Get system metrics and statistics
    """
    try:
        # This would be enhanced with actual metrics from a time-series database
        return {
            "total_events_processed": 0,
            "high_risk_events": 0,
            "medium_risk_events": 0,
            "low_risk_events": 0,
            "feedback_count": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
