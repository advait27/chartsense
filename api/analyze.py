"""
Vercel Serverless Function for Chart Analysis

Handles chart image uploads and returns AI-powered analysis.
Compatible with Vercel's Python runtime.
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
import logging

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.orchestrator import ChartAnalysisOrchestrator
from backend.config import VISION_MODEL_ID, REASONING_MODEL_ID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize orchestrator (reuse across invocations)
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = ChartAnalysisOrchestrator(strict_safety=False)
    return orchestrator


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def _set_headers(self, status_code=200):
        """Set response headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self._set_headers(200)
        self.wfile.write(b'')
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON body
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Invalid JSON',
                    'message': 'Request body must be valid JSON'
                }).encode())
                return
            
            # Extract image data
            image_data = data.get('image')
            if not image_data:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Missing image data',
                    'message': 'Please provide image in base64 format'
                }).encode())
                return
            
            # Decode base64 image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Invalid base64',
                    'message': f'Failed to decode image: {str(e)}'
                }).encode())
                return
            
            # Validate image
            try:
                image = Image.open(BytesIO(image_bytes))
                image.verify()
                
                # Reopen after verify
                image = Image.open(BytesIO(image_bytes))
                if image.size[0] < 100 or image.size[1] < 100:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        'error': 'Image too small',
                        'message': 'Image must be at least 100x100 pixels'
                    }).encode())
                    return
            except Exception as e:
                logger.error(f"Image validation failed: {e}")
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Invalid image',
                    'message': f'Failed to process image: {str(e)}'
                }).encode())
                return
            
            # Run analysis
            logger.info("Starting chart analysis...")
            orch = get_orchestrator()
            result = orch.analyze_chart(image_bytes)
            
            if not result.success:
                logger.error(f"Analysis failed: {result.error_message}")
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    'error': 'Analysis failed',
                    'message': result.error_message or 'Unknown error occurred'
                }).encode())
                return
            
            # Format response
            from datetime import datetime
            analysis = result.analysis
            
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
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            }).encode())
    
    def do_GET(self):
        """Handle GET requests (health check)"""
        self._set_headers(200)
        self.wfile.write(json.dumps({
            'status': 'online',
            'service': 'ChartSense API',
            'version': '1.0.0'
        }).encode())
