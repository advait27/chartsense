"""
Netlify Serverless Function for Chart Analysis Chat

Handles follow-up questions about chart analysis using the reasoning model.
Session state is in-memory per function instance (may reset on cold start).
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.hf_client import HuggingFaceClient, HFConfig
from backend.config import REASONING_MODEL_ID, HF_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reuse client across invocations
_chat_client = None
_chat_sessions = {}


def get_chat_client():
    global _chat_client
    if _chat_client is None:
        _chat_client = HuggingFaceClient(HFConfig(
            model_id=REASONING_MODEL_ID,
            api_key=HF_API_KEY or "",
            timeout=60
        ))
    return _chat_client


def handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, DELETE, OPTIONS",
        "Content-Type": "application/json",
    }

    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}

    path = event.get("path", "")
    if "DELETE" in event.get("httpMethod", ""):
        # DELETE /api/chat/:session_id -> clear session
        parts = path.rstrip("/").split("/")
        session_id = parts[-1] if parts else None
        if session_id and session_id in _chat_sessions:
            del _chat_sessions[session_id]
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"success": True, "message": "Session cleared"}),
        }

    if event.get("httpMethod") != "POST":
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": "Method not allowed", "message": "Only POST is supported for chat"}),
        }

    try:
        body = event.get("body", "{}")
        if event.get("isBase64Encoded"):
            import base64
            body = base64.b64decode(body).decode("utf-8")
        data = json.loads(body)
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Invalid JSON", "message": str(e)}),
        }

    session_id = data.get("session_id") or f"session-{datetime.utcnow().timestamp()}"
    user_message = data.get("message", "").strip()
    analysis_context = data.get("analysis_context")

    if not user_message:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Missing message", "message": "Please provide a message"}),
        }

    if not HF_API_KEY:
        return {
            "statusCode": 503,
            "headers": headers,
            "body": json.dumps({
                "error": "Chat unavailable",
                "message": "HF_API_KEY is not configured. Set it in Netlify environment variables.",
            }),
        }

    if session_id not in _chat_sessions:
        _chat_sessions[session_id] = {
            "messages": [],
            "analysis_context": analysis_context,
            "created_at": datetime.utcnow().isoformat(),
        }
    session = _chat_sessions[session_id]
    if analysis_context is not None:
        session["analysis_context"] = analysis_context

    session["messages"].append({"role": "user", "content": user_message})

    context_summary = ""
    if session.get("analysis_context"):
        a = session["analysis_context"]
        context_summary = f"""
You are analyzing a trading chart with the following details:

**Chart Information:**
- Type: {a.get('vision', {}).get('chart_type', 'Unknown')}
- Timeframe: {a.get('vision', {}).get('timeframe', 'Unknown')}
- Price Structure: {a.get('vision', {}).get('price_structure', 'N/A')}

**Market Analysis:**
- Trend: {a.get('reasoning', {}).get('market_structure', {}).get('trend_description', 'N/A')}
- Momentum: {a.get('reasoning', {}).get('momentum', {}).get('assessment', 'N/A')}
- Market Regime: {a.get('reasoning', {}).get('regime', {}).get('regime', 'N/A')}
- Strategy Bias: {a.get('reasoning', {}).get('strategy_bias', {}).get('bias', 'Neutral')} (Confidence: {a.get('reasoning', {}).get('strategy_bias', {}).get('confidence', 'Medium')})

Please answer questions about this chart analysis in a helpful and insightful manner.
"""

    system = (
        context_summary + "\n\nYou are an expert trading analyst. Provide clear, actionable insights based on the chart analysis."
        if context_summary
        else "You are an expert trading analyst. Help users understand chart analysis and trading strategies."
    )

    recent = session["messages"][-10:]
    full_prompt = system + "\n\n"
    for msg in recent[:-1]:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        full_prompt += f"{role_label}: {msg['content']}\n\n"
    full_prompt += f"User: {user_message}\n\nAssistant:"

    try:
        client = get_chat_client()
        ai_response = client.query_text_model(
            prompt=full_prompt,
            parameters={"max_new_tokens": 1000, "temperature": 0.7},
        )
    except Exception as e:
        logger.error(f"Chat AI error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": "Failed to generate response",
                "message": str(e),
            }),
        }

    session["messages"].append({"role": "assistant", "content": ai_response})

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({
            "session_id": session_id,
            "response": ai_response,
            "timestamp": datetime.utcnow().isoformat(),
        }),
    }
