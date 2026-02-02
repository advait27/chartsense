"""
Hugging Face Inference Client (Updated for 2026)

Uses the new router.huggingface.co API with chat completions.

Author: ChartSense
Version: 2.0.0
"""

import logging
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass
import base64
import re

logger = logging.getLogger(__name__)


# Custom Exceptions for backward compatibility
class HFAPIError(Exception):
    """Base exception for Hugging Face API errors"""
    pass


class HFAuthenticationError(HFAPIError):
    """Exception raised for authentication failures"""
    pass


class HFModelNotFoundError(HFAPIError):
    """Exception raised when model is not found"""
    pass


class HFRateLimitError(HFAPIError):
    """Exception raised when rate limit is exceeded"""
    pass


class HFModelLoadingError(HFAPIError):
    """Exception raised when model is loading"""
    pass


class HFTimeoutError(HFAPIError):
    """Exception raised when request times out"""
    pass


@dataclass
class HFConfig:
    """Configuration for Hugging Face API client"""
    api_key: str
    model_id: str
    timeout: int = 30
    max_retries: int = 2
    retry_delay: int = 2


class HuggingFaceClient:
    """
    Client for Hugging Face Router API (2026).
    
    Uses the new router.huggingface.co endpoint with chat completions.
    """
    
    def __init__(self, config: HFConfig):
        """
        Initialize the Hugging Face client.
        
        Args:
            config: HFConfig object with API credentials and settings
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        })
        
        logger.info(f"Initialized HF client for model: {config.model_id}")
    
    def _clean_thinking_tags(self, text: str) -> str:
        """Remove <think>...</think> tags from DeepSeek model outputs."""
        # Remove everything between <think> and </think>
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        return cleaned.strip()
    
    def query_vision_model(
        self,
        image: bytes,
        prompt: str,
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Query a vision-language model with an image.
        
        For vision models, we'll use chat completions with image input.
        
        Args:
            image: Image as bytes
            prompt: Text prompt for the model
            model_id: Model ID (uses config default if None)
            parameters: Optional model parameters
            
        Returns:
            Generated text description from the model
        """
        model = model_id or self.config.model_id
        
        logger.info(f"Querying vision model: {model}")
        
        # Encode image to base64
        image_b64 = base64.b64encode(image).decode('utf-8')
        
        # Use chat completions API with vision
        url = "https://router.huggingface.co/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=self.config.timeout)
            
            if response.status_code == 200:
                result = response.json()
                output = result["choices"][0]["message"]["content"]
                logger.info(f"Vision model query successful ({len(output)} chars)")
                return output
            else:
                error_msg = response.text
                logger.error(f"Vision API error ({response.status_code}): {error_msg}")
                if response.status_code == 404:
                    raise HFModelNotFoundError(f"Model not found: {model}")
                else:
                    raise HFAPIError(f"Model not available: {model}")
                
        except requests.Timeout:
            logger.error("Vision model query timed out")
            raise HFTimeoutError(f"Request timed out for model: {model}")
        except (HFAPIError, HFModelNotFoundError, HFTimeoutError):
            raise
        except Exception as e:
            logger.error(f"Vision model query failed: {e}")
            raise HFAPIError(f"Model not found: {model}")
    
    def query_text_model(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Query a text generation model.
        
        Args:
            prompt: Text prompt for the model
            model_id: Model ID (uses config default if None)
            parameters: Optional model parameters
            
        Returns:
            Generated text
        """
        model = model_id or self.config.model_id
        
        logger.info(f"Querying text model: {model}")
        
        url = "https://router.huggingface.co/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": parameters.get("max_new_tokens", 500) if parameters else 500,
            "temperature": parameters.get("temperature", 0.7) if parameters else 0.7,
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=self.config.timeout)
            
            if response.status_code == 200:
                result = response.json()
                output = result["choices"][0]["message"]["content"]
                # Clean thinking tags for reasoning models
                output = self._clean_thinking_tags(output)
                logger.info(f"Text model query successful ({len(output)} chars)")
                return output
            else:
                error_msg = response.text
                logger.error(f"Text API error ({response.status_code}): {error_msg}")
                if response.status_code == 404:
                    raise HFModelNotFoundError(f"Model not found: {model}")
                else:
                    raise HFAPIError(f"Model not available: {model}")
                
        except requests.Timeout:
            logger.error("Text model query timed out")
            raise HFTimeoutError(f"Request timed out for model: {model}")
        except (HFAPIError, HFModelNotFoundError, HFTimeoutError):
            raise
        except Exception as e:
            logger.error(f"Text model query failed: {e}")
            raise HFAPIError(f"Model not found: {model}")


# Convenience functions

def create_vision_client(api_key: str, model_id: str, **kwargs) -> HuggingFaceClient:
    """Create a client configured for vision-language models."""
    config = HFConfig(api_key=api_key, model_id=model_id, **kwargs)
    return HuggingFaceClient(config)


def create_text_client(api_key: str, model_id: str, **kwargs) -> HuggingFaceClient:
    """Create a client configured for text generation models."""
    config = HFConfig(api_key=api_key, model_id=model_id, **kwargs)
    return HuggingFaceClient(config)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        print("Error: HF_API_KEY environment variable not set")
        exit(1)
    
    # Test with a known working model
    print("\n=== Testing Text Model ===")
    text_client = create_text_client(api_key, "deepseek-ai/DeepSeek-R1")
    
    try:
        result = text_client.query_text_model("What is 2+2?")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
