"""Quick integration test for the new HF client"""

import os
from dotenv import load_dotenv
from backend.core.hf_client import create_text_client, create_vision_client
from backend.config import VISION_MODEL_ID, REASONING_MODEL_ID, HF_API_KEY
from PIL import Image
import io

load_dotenv()

def test_text_model():
    print("\n=== Testing Text Model ===")
    print(f"Model: {REASONING_MODEL_ID}")
    
    client = create_text_client(HF_API_KEY, REASONING_MODEL_ID)
    
    try:
        result = client.query_text_model("Explain what a bar chart shows in one sentence.")
        print(f"✓ Success: {result[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_vision_model():
    print("\n=== Testing Vision Model ===")
    print(f"Model: {VISION_MODEL_ID}")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    client = create_vision_client(HF_API_KEY, VISION_MODEL_ID)
    
    try:
        result = client.query_vision_model(img_bytes, "Describe this image briefly.")
        print(f"✓ Success: {result[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing new HuggingFace integration...")
    
    text_ok = test_text_model()
    vision_ok = test_vision_model()
    
    print("\n=== Summary ===")
    print(f"Text Model: {'✓ PASS' if text_ok else '✗ FAIL'}")
    print(f"Vision Model: {'✓ PASS' if vision_ok else '✗ FAIL'}")
    
    if text_ok and vision_ok:
        print("\n🎉 All tests passed! The integration is working.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
