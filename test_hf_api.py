"""
Quick test script to check HuggingFace API connectivity
"""
import requests
import os
from dotenv import load_dotenv
import base64

load_dotenv()

API_KEY = os.getenv("HF_API_KEY")

# Test different endpoints with proper POST requests
test_cases = [
    {
        "name": "Vision Model - GET on router",
        "url": "https://router.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning",
        "method": "GET",
    },
    {
        "name": "Text Model - POST on router",
        "url": "https://router.huggingface.co/models/gpt2",
        "method": "POST",
        "data": {"inputs": "Hello, my name is"}
    },
    {
        "name": "Vision API (Serverless Inference)",
        "url": "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning",
        "method": "POST",
        "data": {"inputs": "test"}
    },
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("Testing HuggingFace API endpoints...\n")
print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}\n")

for test in test_cases:
    print(f"Test: {test['name']}")
    print(f"  URL: {test['url']}")
    try:
        if test["method"] == "GET":
            response = requests.get(test["url"], headers=headers, timeout=10)
        else:
            response = requests.post(test["url"], headers=headers, json=test.get("data"), timeout=30)
        
        print(f"  Status: {response.status_code}")
        if response.status_code >= 400:
            print(f"  Error: {response.text[:300]}")
        else:
            print(f"  ✓ Success: {response.text[:200]}")
    except Exception as e:
        print(f"  ✗ Exception: {e}")
    print()

print("\nChecking documentation...")
print("Try: https://huggingface.co/docs/api-inference/index")

