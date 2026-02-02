"""
Backend Configuration

Central configuration for all backend services including
Hugging Face API, timeouts, and model settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# Hugging Face API Configuration
# ============================================================================

# API Authentication
HF_API_KEY = os.getenv("HF_API_KEY", "")

# Vision Model Configuration
VISION_MODEL_ID = os.getenv("VISION_MODEL", "Qwen/Qwen2.5-VL-7B-Instruct")
VISION_MODEL_ALTERNATIVES = [
    "Qwen/Qwen2.5-VL-7B-Instruct",                # Qwen 2.5 VL (WORKING)
    "Qwen/Qwen2.5-VL-72B-Instruct",               # Qwen 2.5 VL 72B (larger)
    "mistralai/Pixtral-12B-2409",                 # Pixtral (multimodal)
]

# Text/Reasoning Model Configuration
REASONING_MODEL_ID = os.getenv("REASONING_MODEL", "deepseek-ai/DeepSeek-R1")
REASONING_MODEL_ALTERNATIVES = [
    "deepseek-ai/DeepSeek-R1",                    # DeepSeek R1 (WORKING - reasoning)
    "meta-llama/Llama-3.3-70B-Instruct",          # Llama 3.3 70B
    "Qwen/Qwen2.5-72B-Instruct",                  # Qwen 2.5 72B
    "meta-llama/Meta-Llama-3.1-8B-Instruct",      # Llama 3.1 8B (fallback)
]

# ============================================================================
# API Timeouts and Retries
# ============================================================================

# Timeouts (seconds)
VISION_TIMEOUT = int(os.getenv("VISION_TIMEOUT", "30"))
REASONING_TIMEOUT = int(os.getenv("REASONING_TIMEOUT", "120"))
TOTAL_TIMEOUT = int(os.getenv("TOTAL_TIMEOUT", "150"))

# Retry Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))

# ============================================================================
# Image Processing Configuration
# ============================================================================

# Image Constraints
MAX_IMAGE_SIZE_MB = 5
MIN_IMAGE_WIDTH = 400
MIN_IMAGE_HEIGHT = 300
MAX_IMAGE_WIDTH = 4000
MAX_IMAGE_HEIGHT = 3000

# Preprocessing Settings
REMOVE_UI_ELEMENTS = True
NORMALIZE_IMAGES = True
RESIZE_FOR_MODEL = True

# Target Dimensions for AI Models
TARGET_IMAGE_WIDTH = 1024
TARGET_IMAGE_HEIGHT = 768

# ============================================================================
# Model Parameters
# ============================================================================

# Vision Model Parameters
VISION_PARAMETERS = {
    # No additional parameters needed for BLIP-2
}

# Reasoning Model Parameters
REASONING_PARAMETERS = {
    "max_new_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": True,
    "repetition_penalty": 1.1
}

# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# API Server Configuration
# ============================================================================

# Server Settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"

# CORS Settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ============================================================================
# Feature Flags
# ============================================================================

# Enable/disable features
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "false").lower() == "true"
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"

# ============================================================================
# Validation
# ============================================================================

def validate_config():
    """Validate critical configuration settings"""
    errors = []
    
    if not HF_API_KEY:
        errors.append("HF_API_KEY is not set")
    
    if VISION_TIMEOUT < 10:
        errors.append("VISION_TIMEOUT should be at least 10 seconds")
    
    if REASONING_TIMEOUT < 10:
        errors.append("REASONING_TIMEOUT should be at least 10 seconds")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True


# Validate on import (can be disabled for testing)
if os.getenv("SKIP_CONFIG_VALIDATION", "false").lower() != "true":
    validate_config()
