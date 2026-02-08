"""
Netlify Serverless Function for Chart Analysis

Handles chart image uploads and returns AI-powered analysis.
"""

import json
import sys
import os
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
import logging

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.orchestrator import ChartAnalysisOrchestrator
from backend.config import VISION_MODEL_ID, REASONING_MODEL_ID, HF_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize orchestrator (reuse across invocations for better performance)
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = ChartAnalysisOrchestrator(strict_safety=False)
    return orchestrator


def handler(event, context):
    """
    Netlify function handler for chart analysis.
    
    Args:
        event: Netlify event object
        context: Netlify context object
        
    Returns:
        Response object with analysis results
    """
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    if not HF_API_KEY:
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                'error': 'Service unavailable',
                'message': 'HF_API_KEY is not set. Add it in Netlify Site settings → Environment variables.'
            })
        }

    try:
        # Validate HTTP method
        if event.get('httpMethod') != 'POST':
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Method not allowed',
                    'message': 'Only POST requests are supported'
                })
            }
        
        # Parse request body
        content_type = event.get('headers', {}).get('content-type', '')
        
        if 'multipart/form-data' in content_type:
            # Handle multipart form data (from frontend)
            body = event.get('body', '')
            if event.get('isBase64Encoded'):
                body = base64.b64decode(body)
            
            # Parse multipart data (simplified - in production use proper multipart parser)
            # For now, expect base64 encoded image in JSON
            logger.error("Multipart form data not fully supported yet")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid request format',
                    'message': 'Please send image as base64 JSON'
                })
            }
        else:
            # Handle JSON body with base64 image
            body = event.get('body', '{}')
            if event.get('isBase64Encoded'):
                body = base64.b64decode(body).decode('utf-8')
            
            data = json.loads(body)
            image_data = data.get('image')
            
            if not image_data:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Missing image data',
                        'message': 'Please provide image in base64 format'
                    })
                }
            
            # Decode base64 image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
        
        # Validate image
        try:
            image = Image.open(BytesIO(image_bytes))
            image.verify()
            
            # Reopen after verify
            image = Image.open(BytesIO(image_bytes))
            if image.size[0] < 100 or image.size[1] < 100:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Image too small',
                        'message': 'Image must be at least 100x100 pixels'
                    })
                }
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid image',
                    'message': f'Failed to process image: {str(e)}'
                })
            }
        
        # Run analysis
        logger.info("Starting chart analysis...")
        orch = get_orchestrator()
        result = orch.analyze_chart(image_bytes)
        
        if not result.success:
            logger.error(f"Analysis failed: {result.error_message}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Analysis failed',
                    'message': result.error_message or 'Unknown error occurred'
                })
            }
        
        # Format response
        analysis = result.analysis
        from datetime import datetime
        
        response_data = {
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
                },
                "trading_signals": {
                    "signal_type": analysis.get("analysis", {}).get("trading_signals", {}).get("signal_type", "WAIT"),
                    "entry_level": analysis.get("analysis", {}).get("trading_signals", {}).get("entry_level", "Not specified"),
                    "stop_loss": analysis.get("analysis", {}).get("trading_signals", {}).get("stop_loss", "Not specified"),
                    "take_profit_1": analysis.get("analysis", {}).get("trading_signals", {}).get("take_profit_1", "Not specified"),
                    "take_profit_2": analysis.get("analysis", {}).get("trading_signals", {}).get("take_profit_2"),
                    "risk_reward_ratio": analysis.get("analysis", {}).get("trading_signals", {}).get("risk_reward_ratio", "Not specified"),
                    "position_sizing": analysis.get("analysis", {}).get("trading_signals", {}).get("position_sizing", "Risk 1-2% of capital"),
                    "timeframe_context": analysis.get("analysis", {}).get("trading_signals", {}).get("timeframe_context"),
                    "confidence_score": analysis.get("analysis", {}).get("trading_signals", {}).get("confidence_score", "Medium")
                }
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "vision_model": VISION_MODEL_ID,
                "reasoning_model": REASONING_MODEL_ID,
                "warnings": result.warnings
            }
        }
        
        logger.info("Analysis completed successfully")
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data)
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Invalid JSON',
                'message': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
