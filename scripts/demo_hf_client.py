#!/usr/bin/env python3
"""
Demo script for Hugging Face API client

This script demonstrates how to use the HF client for vision and text models.
Requires HF_API_KEY environment variable to be set.
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.hf_client import (
    HuggingFaceClient,
    HFConfig,
    create_vision_client,
    create_text_client,
    HFAPIError
)
from backend.config import HF_API_KEY, VISION_MODEL_ID, REASONING_MODEL_ID

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_configuration():
    """Demonstrate different configuration patterns"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 1: Configuration Patterns")
    logger.info("="*60)
    
    # Pattern 1: Using convenience function
    logger.info("\n📝 Pattern 1: Convenience function")
    client1 = create_vision_client(HF_API_KEY)
    logger.info(f"  Model: {client1.config.model_id}")
    logger.info(f"  Timeout: {client1.config.timeout}s")
    
    # Pattern 2: Using HFConfig
    logger.info("\n📝 Pattern 2: Custom configuration")
    config = HFConfig(
        api_key=HF_API_KEY,
        model_id=VISION_MODEL_ID,
        timeout=45,
        max_retries=3
    )
    client2 = HuggingFaceClient(config)
    logger.info(f"  Model: {client2.config.model_id}")
    logger.info(f"  Timeout: {client2.config.timeout}s")
    logger.info(f"  Max retries: {client2.config.max_retries}")
    
    # Pattern 3: Easy model swapping
    logger.info("\n📝 Pattern 3: Model swapping")
    models = [
        "Salesforce/blip2-opt-2.7b",
        "llava-hf/llava-1.5-7b-hf"
    ]
    for model in models:
        client = create_vision_client(HF_API_KEY, model)
        logger.info(f"  Created client for: {model}")


def demo_model_status():
    """Demonstrate model status checking"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 2: Model Status Checking")
    logger.info("="*60)
    
    client = create_vision_client(HF_API_KEY)
    
    # Check vision model
    logger.info("\n🔍 Checking vision model status...")
    status = client.check_model_status()
    logger.info(f"  Model: {status['model_id']}")
    logger.info(f"  Available: {status['available']}")
    logger.info(f"  Status code: {status.get('status_code', 'N/A')}")
    
    # Check text model
    logger.info("\n🔍 Checking text model status...")
    text_client = create_text_client(HF_API_KEY)
    status = text_client.check_model_status()
    logger.info(f"  Model: {status['model_id']}")
    logger.info(f"  Available: {status['available']}")


def demo_vision_model():
    """Demonstrate vision model usage"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 3: Vision Model Query")
    logger.info("="*60)
    
    if not HF_API_KEY:
        logger.warning("⚠️  HF_API_KEY not set, skipping vision demo")
        return
    
    client = create_vision_client(HF_API_KEY)
    
    # Create a simple test image
    from PIL import Image
    import io
    
    logger.info("\n📊 Creating sample chart image...")
    img = Image.new('RGB', (800, 600), color='#1e1e1e')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    
    logger.info(f"  Image size: {len(image_bytes)} bytes")
    
    # Query the model
    try:
        logger.info("\n🤖 Querying vision model...")
        logger.info("  (This may take 20-30 seconds on first call)")
        
        result = client.query_vision_model(
            image_bytes,
            "Describe what you see in this image"
        )
        
        logger.info("\n✅ Vision model response:")
        logger.info(f"  {result}")
        
    except HFAPIError as e:
        logger.error(f"❌ API error: {e}")


def demo_text_model():
    """Demonstrate text model usage"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 4: Text Model Query")
    logger.info("="*60)
    
    if not HF_API_KEY:
        logger.warning("⚠️  HF_API_KEY not set, skipping text demo")
        return
    
    client = create_text_client(HF_API_KEY)
    
    prompt = """Based on this chart analysis:
- Price is above EMA 20 and EMA 50
- RSI is at 68 (approaching overbought)
- Volume is declining on recent rally

Provide a brief market analysis and strategy bias."""
    
    try:
        logger.info("\n🤖 Querying text model...")
        logger.info("  (This may take 20-30 seconds on first call)")
        
        result = client.query_text_model(
            prompt,
            parameters={
                "max_new_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )
        
        logger.info("\n✅ Text model response:")
        logger.info(f"  {result}")
        
    except HFAPIError as e:
        logger.error(f"❌ API error: {e}")


def demo_error_handling():
    """Demonstrate error handling"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 5: Error Handling")
    logger.info("="*60)
    
    # Test with invalid API key
    logger.info("\n🔧 Testing with invalid API key...")
    client = create_vision_client("invalid_key")
    
    try:
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        client.query_vision_model(buffer.getvalue(), "Test")
    except HFAPIError as e:
        logger.info(f"  ✅ Caught expected error: {type(e).__name__}")
        logger.info(f"     Message: {e}")
    
    # Test with non-existent model
    logger.info("\n🔧 Testing with non-existent model...")
    client = create_vision_client(HF_API_KEY, "fake/model-does-not-exist")
    
    try:
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        client.query_vision_model(buffer.getvalue(), "Test")
    except HFAPIError as e:
        logger.info(f"  ✅ Caught expected error: {type(e).__name__}")
        logger.info(f"     Message: {e}")


def main():
    """Run all demos"""
    logger.info("🚀 Hugging Face API Client Demo")
    logger.info("="*60)
    
    if not HF_API_KEY:
        logger.error("❌ HF_API_KEY environment variable not set")
        logger.info("\nTo run this demo:")
        logger.info("1. Get API key from https://huggingface.co/settings/tokens")
        logger.info("2. Set environment variable: export HF_API_KEY=your_key")
        logger.info("3. Run this script again")
        return 1
    
    try:
        demo_configuration()
        demo_model_status()
        demo_error_handling()
        
        # Only run model queries if user confirms (to avoid rate limits)
        logger.info("\n" + "="*60)
        response = input("\n⚠️  Run actual model queries? This will use API quota (y/N): ")
        if response.lower() == 'y':
            demo_vision_model()
            demo_text_model()
        else:
            logger.info("Skipping model query demos")
        
        logger.info("\n" + "="*60)
        logger.info("✅ All demos completed!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
