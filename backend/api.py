"""
FastAPI Backend for ChartSense

REST API wrapper for the ChartSense analysis system.
Provides endpoints for the React frontend.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import io
import sys
from pathlib import Path
from PIL import Image
import logging
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import existing backend components
from backend.services.orchestrator import ChartAnalysisOrchestrator
from backend.core.image_processor import ImageProcessor
from backend.core.hf_client import HuggingFaceClient, HFConfig
from backend.config import VISION_MODEL_ID, REASONING_MODEL_ID, HF_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ChartSense API",
    description="AI-Powered Trading Chart Analysis",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = ChartAnalysisOrchestrator(strict_safety=True)
image_processor = ImageProcessor()

# Initialize chat client
chat_config = HFConfig(
    model_id=REASONING_MODEL_ID,
    api_key=HF_API_KEY,
    timeout=60
)
chat_client = HuggingFaceClient(chat_config)

# Store chat sessions in memory (in production, use Redis or database)
chat_sessions: Dict[str, Dict] = {}


# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    analysis_context: Optional[Dict] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "ChartSense API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "vision": VISION_MODEL_ID,
            "reasoning": REASONING_MODEL_ID
        }
    }


@app.post("/api/analyze")
async def analyze_chart(chart: UploadFile = File(...)):
    """
    Analyze a trading chart image.
    
    Args:
        chart: Image file (PNG, JPG, JPEG, WEBP)
        
    Returns:
        JSON with complete analysis results
    """
    try:
        # Validate file type
        if not chart.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (PNG, JPG, JPEG, WEBP)"
            )
        
        # Read image file
        logger.info(f"Processing image: {chart.filename}")
        image_bytes = await chart.read()
        
        # Validate and process image
        try:
            # Open image to validate it
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()  # Verify it's a valid image
            
            # Validate image dimensions and format
            # Reopen after verify() since verify() closes the file
            image = Image.open(io.BytesIO(image_bytes))
            if image.size[0] < 100 or image.size[1] < 100:
                raise HTTPException(
                    status_code=400,
                    detail="Image is too small (minimum 100x100 pixels)"
                )
            
            # The orchestrator expects raw bytes
            processed_bytes = image_bytes
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process image: {str(e)}"
            )
        
        # Run analysis
        try:
            logger.info("Running chart analysis...")
            result = orchestrator.analyze_chart(processed_bytes)
            
            # Check if analysis succeeded
            if not result.success:
                raise HTTPException(
                    status_code=500,
                    detail=result.error_message or "Analysis failed"
                )
            
            # Extract the analysis data
            analysis = result.analysis
            
            # Format response for React frontend (matching the to_streamlit_format structure)
            response = {
                "vision": {
                    "chart_type": analysis.get("vision", {}).get("chart_info", {}).get("type", "Unknown"),
                    "timeframe": analysis.get("vision", {}).get("chart_info", {}).get("timeframe", "N/A"),
                    "price_structure": analysis.get("vision", {}).get("price_structure", "N/A"),
                    "indicators_detected": analysis.get("vision", {}).get("indicators", []),
                    "visual_patterns": analysis.get("vision", {}).get("patterns", []),
                    "momentum_signals": analysis.get("vision", {}).get("momentum", "N/A")
                },
                "reasoning": {
                    "market_structure": {
                        "trend_description": analysis.get("analysis", {}).get("market_structure", {}).get("trend", "N/A"),
                        "key_levels": analysis.get("analysis", {}).get("market_structure", {}).get("key_levels", ["Not specified"]),
                        "structural_notes": analysis.get("analysis", {}).get("market_structure", {}).get("notes", [])
                    },
                    "momentum": {
                        "assessment": analysis.get("analysis", {}).get("momentum", {}).get("assessment", "N/A"),
                        "indicators": analysis.get("analysis", {}).get("momentum", {}).get("indicators", ["Not specified"]),
                        "divergences": analysis.get("analysis", {}).get("momentum", {}).get("divergences", []),
                        "strength": analysis.get("analysis", {}).get("momentum", {}).get("strength", "Mixed")
                    },
                    "regime": {
                        "regime": analysis.get("analysis", {}).get("regime", {}).get("classification", "Indecisive"),
                        "reasoning": analysis.get("analysis", {}).get("regime", {}).get("reasoning", "N/A"),
                        "volatility": analysis.get("analysis", {}).get("regime", {}).get("volatility", "Moderate")
                    },
                    "strategy_bias": {
                        "bias": analysis.get("analysis", {}).get("strategy_bias", {}).get("bias", "Neutral"),
                        "confidence": analysis.get("analysis", {}).get("strategy_bias", {}).get("confidence", "Medium"),
                        "reasoning": analysis.get("analysis", {}).get("strategy_bias", {}).get("reasoning", ["Not specified"])
                    },
                    "suitable_approaches": {
                        "approaches": analysis.get("analysis", {}).get("approaches", {}).get("options", [])
                    },
                    "invalidation": {
                        "bullish_invalidation": analysis.get("analysis", {}).get("invalidation", {}).get("bullish", ["Not specified"]),
                        "bearish_invalidation": analysis.get("analysis", {}).get("invalidation", {}).get("bearish", ["Not specified"]),
                        "key_levels": analysis.get("analysis", {}).get("invalidation", {}).get("key_levels", ["Not specified"])
                    }
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "vision_model": VISION_MODEL_ID,
                    "reasoning_model": REASONING_MODEL_ID,
                    "image_filename": chart.filename,
                    "warnings": result.warnings
                }
            }
            
            logger.info("Analysis completed successfully")
            return JSONResponse(content=response)
            
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/chat")
async def chat_with_analysis(request: ChatRequest):
    """
    Chat endpoint for discussing chart analysis with context.
    
    Args:
        request: ChatRequest with session_id, message, and optional analysis_context
        
    Returns:
        JSON with AI response
    """
    try:
        session_id = request.session_id
        user_message = request.message
        
        # Initialize session if it doesn't exist
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                "messages": [],
                "analysis_context": request.analysis_context,
                "created_at": datetime.now().isoformat()
            }
        
        # Get session
        session = chat_sessions[session_id]
        
        # Update analysis context if provided
        if request.analysis_context:
            session["analysis_context"] = request.analysis_context
        
        # Build context-aware prompt
        context_summary = ""
        if session.get("analysis_context"):
            analysis = session["analysis_context"]
            context_summary = f"""
You are analyzing a trading chart with the following details:

**Chart Information:**
- Type: {analysis.get('vision', {}).get('chart_type', 'Unknown')}
- Timeframe: {analysis.get('vision', {}).get('timeframe', 'Unknown')}
- Price Structure: {analysis.get('vision', {}).get('price_structure', 'N/A')}

**Market Analysis:**
- Trend: {analysis.get('reasoning', {}).get('market_structure', {}).get('trend_description', 'N/A')}
- Momentum: {analysis.get('reasoning', {}).get('momentum', {}).get('assessment', 'N/A')}
- Market Regime: {analysis.get('reasoning', {}).get('regime', {}).get('regime', 'N/A')}
- Strategy Bias: {analysis.get('reasoning', {}).get('strategy_bias', {}).get('bias', 'Neutral')} (Confidence: {analysis.get('reasoning', {}).get('strategy_bias', {}).get('confidence', 'Medium')})

Please answer questions about this chart analysis in a helpful and insightful manner.
"""
        
        # Add user message to session
        session["messages"].append({
            "role": "user",
            "content": user_message
        })
        
        # Build conversation history for API
        messages = []
        
        # Add system prompt with context
        if context_summary:
            messages.append({
                "role": "system",
                "content": context_summary + "\n\nYou are an expert trading analyst. Provide clear, actionable insights based on the chart analysis."
            })
        else:
            messages.append({
                "role": "system",
                "content": "You are an expert trading analyst. Help users understand chart analysis and trading strategies."
            })
        
        # Add conversation history (last 10 messages to keep context manageable)
        recent_messages = session["messages"][-10:]
        messages.extend(recent_messages)
        
        # Get AI response using the HuggingFace API directly with proper message format
        try:
            # Build the full prompt with context
            full_prompt = messages[0]["content"] + "\n\n"
            
            # Add conversation history
            for msg in recent_messages[:-1]:  # Exclude the last message (current user message)
                role_label = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role_label}: {msg['content']}\n\n"
            
            # Add current user message
            full_prompt += f"User: {user_message}\n\nAssistant:"
            
            # Call the text model
            ai_response = chat_client.query_text_model(
                prompt=full_prompt,
                parameters={
                    "max_new_tokens": 1000,
                    "temperature": 0.7
                }
            )
            
            # Add AI response to session
            session["messages"].append({
                "role": "assistant",
                "content": ai_response
            })
            
            logger.info(f"Chat response generated for session {session_id}")
            
            return JSONResponse(content={
                "session_id": session_id,
                "response": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Chat AI error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate response: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return JSONResponse(content={
        "session_id": session_id,
        "messages": chat_sessions[session_id]["messages"],
        "created_at": chat_sessions[session_id]["created_at"]
    })


@app.delete("/api/chat/{session_id}")
async def clear_chat_session(session_id: str):
    """Clear a chat session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return JSONResponse(content={
        "success": True,
        "message": "Session cleared"
    })


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom error handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
