"""
Hugging Face Inference API Client

This module provides a simple, synchronous client for interacting with
Hugging Face's Inference API for vision-language models.

Features:
- Synchronous API calls (no async complexity)
- Easy model swapping via configuration
- Graceful error handling with retries
- Free-tier compatible
- Support for vision-language models (BLIP-2, LLaVA, etc.)

Author: ChartSense
Version: 1.0.0
"""

import requests
import base64
import time
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported model types"""
    VISION_LANGUAGE = "vision-language"  # BLIP-2, LLaVA
    TEXT_GENERATION = "text-generation"   # Llama, Mistral


@dataclass
class HFConfig:
    """Configuration for Hugging Face API client"""
    api_key: str
    model_id: str
    timeout: int = 30
    max_retries: int = 2
    retry_delay: int = 2
    base_url: str = "https://api-inference.huggingface.co/models"


class HFAPIError(Exception):
    """Base exception for Hugging Face API errors"""
    pass


class HFAuthenticationError(HFAPIError):
    """Authentication failed"""
    pass


class HFModelNotFoundError(HFAPIError):
    """Model not found or not accessible"""
    pass


class HFRateLimitError(HFAPIError):
    """Rate limit exceeded"""
    pass


class HFModelLoadingError(HFAPIError):
    """Model is still loading"""
    pass


class HuggingFaceClient:
    """
    Client for Hugging Face Inference API.
    
    Supports vision-language models and text generation models.
    Handles errors gracefully with automatic retries.
    
    Example:
        >>> config = HFConfig(
        ...     api_key="hf_xxx",
        ...     model_id="Salesforce/blip2-opt-2.7b"
        ... )
        >>> client = HuggingFaceClient(config)
        >>> result = client.query_vision_model(image_bytes, "Describe this chart")
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
    
    def _get_model_url(self, model_id: Optional[str] = None) -> str:
        """
        Get the full API URL for a model.
        
        Args:
            model_id: Model ID (uses config default if None)
            
        Returns:
            Full API URL
        """
        model = model_id or self.config.model_id
        # Use inference-api subdomain for serverless inference
        return f"https://api-inference.huggingface.co/models/{model}"
    
    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response from API
            
        Returns:
            Parsed JSON response
            
        Raises:
            HFAuthenticationError: Invalid API key
            HFModelNotFoundError: Model not found
            HFRateLimitError: Rate limit exceeded
            HFModelLoadingError: Model still loading
            HFAPIError: Other API errors
        """
        # Success
        if response.status_code == 200:
            return response.json()
        
        # Authentication error
        if response.status_code == 401:
            raise HFAuthenticationError("Invalid API key")
        
        # Model not found
        if response.status_code == 404:
            raise HFModelNotFoundError(f"Model not found: {self.config.model_id}")
        
        # Rate limit
        if response.status_code == 429:
            raise HFRateLimitError("Rate limit exceeded. Free tier allows ~30 requests/hour")
        
        # Model loading
        if response.status_code == 503:
            try:
                error_data = response.json()
                if "loading" in error_data.get("error", "").lower():
                    estimated_time = error_data.get("estimated_time", "unknown")
                    raise HFModelLoadingError(
                        f"Model is loading. Estimated time: {estimated_time}s"
                    )
            except (ValueError, KeyError):
                pass
            raise HFAPIError(f"Service unavailable: {response.text}")
        
        # Other errors
        try:
            error_data = response.json()
            error_msg = error_data.get("error", response.text)
        except ValueError:
            error_msg = response.text
        
        raise HFAPIError(f"API error ({response.status_code}): {error_msg}")
    
    def _make_request(
        self,
        payload: Dict[str, Any],
        model_id: Optional[str] = None,
        retry_count: int = 0
    ) -> Any:
        """
        Make API request with retry logic.
        
        Args:
            payload: Request payload
            model_id: Model ID (uses config default if None)
            retry_count: Current retry attempt
            
        Returns:
            API response
            
        Raises:
            HFAPIError: If all retries fail
        """
        url = self._get_model_url(model_id)
        
        try:
            logger.debug(f"Making request to {url}")
            response = self.session.post(
                url,
                json=payload,
                timeout=self.config.timeout
            )
            
            return self._handle_response(response)
            
        except HFModelLoadingError as e:
            # Model is loading - retry after delay
            if retry_count < self.config.max_retries:
                logger.warning(f"Model loading, retrying in {self.config.retry_delay}s...")
                time.sleep(self.config.retry_delay)
                return self._make_request(payload, model_id, retry_count + 1)
            raise
            
        except (requests.Timeout, requests.ConnectionError) as e:
            # Network errors - retry
            if retry_count < self.config.max_retries:
                logger.warning(f"Network error, retrying in {self.config.retry_delay}s...")
                time.sleep(self.config.retry_delay)
                return self._make_request(payload, model_id, retry_count + 1)
            raise HFAPIError(f"Network error after {retry_count} retries: {str(e)}")
        
        except HFAPIError:
            # Don't retry on authentication, rate limit, or model not found errors
            raise
    
    def query_vision_model(
        self,
        image: Union[bytes, str],
        prompt: str,
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Query a vision-language model with an image and prompt.
        
        Args:
            image: Image as bytes or base64 string
            prompt: Text prompt for the model
            model_id: Model ID (uses config default if None)
            parameters: Optional model parameters
            
        Returns:
            Generated text description from the model
            
        Example:
            >>> with open("chart.png", "rb") as f:
            ...     image_bytes = f.read()
            >>> result = client.query_vision_model(
            ...     image_bytes,
            ...     "Describe the technical indicators in this chart"
            ... )
        """
        # Convert image to base64 if needed
        if isinstance(image, bytes):
            image_b64 = base64.b64encode(image).decode('utf-8')
        else:
            image_b64 = image
        
        # Build payload
        payload = {
            "inputs": {
                "image": image_b64,
                "text": prompt
            }
        }
        
        # Add optional parameters
        if parameters:
            payload["parameters"] = parameters
        
        logger.info(f"Querying vision model with prompt: {prompt[:50]}...")
        
        result = self._make_request(payload, model_id)
        
        logger.info("Vision model query successful")
        
        # Extract text from vision model response
        if isinstance(result, list) and len(result) > 0:
            first_item = result[0]
            if isinstance(first_item, dict):
                # Return the generated text if available
                return first_item.get("generated_text", "") or str(first_item)
            return str(first_item)
        elif isinstance(result, dict):
            # Try to extract text from common keys
            return (
                result.get("generated_text") or
                result.get("text") or
                result.get("caption") or
                str(result)
            )
        elif isinstance(result, str):
            return result
        
        return str(result)
    
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
            parameters: Optional model parameters (max_new_tokens, temperature, etc.)
            
        Returns:
            Generated text
            
        Example:
            >>> result = client.query_text_model(
            ...     "Based on this analysis: ...",
            ...     parameters={"max_new_tokens": 500, "temperature": 0.7}
            ... )
        """
        # Build payload
        payload = {
            "inputs": prompt
        }
        
        # Add optional parameters
        if parameters:
            payload["parameters"] = parameters
        
        logger.info(f"Querying text model with prompt: {prompt[:50]}...")
        
        result = self._make_request(payload, model_id)
        
        # Extract generated text - handle various response formats
        generated_text = ""
        
        if isinstance(result, list) and len(result) > 0:
            first_item = result[0]
            if isinstance(first_item, dict):
                generated_text = first_item.get("generated_text", "")
            else:
                generated_text = str(first_item)
        elif isinstance(result, dict):
            # Try multiple possible keys
            generated_text = (
                result.get("generated_text") or 
                result.get("text") or 
                result.get("output") or 
                str(result)
            )
        elif isinstance(result, str):
            generated_text = result
        else:
            generated_text = str(result)
        
        # Remove input prompt if model echoes it back
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        logger.info(f"Text model query successful ({len(generated_text)} chars)")
        return generated_text
    
    def check_model_status(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if a model is available and loaded.
        
        Args:
            model_id: Model ID (uses config default if None)
            
        Returns:
            Status information
        """
        url = self._get_model_url(model_id)
        
        try:
            response = self.session.get(url, timeout=5)
            return {
                "available": response.status_code == 200,
                "status_code": response.status_code,
                "model_id": model_id or self.config.model_id
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "model_id": model_id or self.config.model_id
            }


# Convenience functions for quick usage

def create_vision_client(api_key: str, model_id: str = "Salesforce/blip2-opt-2.7b", **kwargs) -> HuggingFaceClient:
    """
    Create a client configured for vision-language models.
    
    Args:
        api_key: Hugging Face API key
        model_id: Vision model ID
        **kwargs: Additional configuration (timeout, max_retries, etc.)
        
    Returns:
        Configured HuggingFaceClient
    """
    config = HFConfig(api_key=api_key, model_id=model_id, **kwargs)
    return HuggingFaceClient(config)


def create_text_client(api_key: str, model_id: str = "meta-llama/Llama-2-7b-chat-hf", **kwargs) -> HuggingFaceClient:
    """
    Create a client configured for text generation models.
    
    Args:
        api_key: Hugging Face API key
        model_id: Text model ID
        **kwargs: Additional configuration (timeout, max_retries, etc.)
        
    Returns:
        Configured HuggingFaceClient
    """
    config = HFConfig(api_key=api_key, model_id=model_id, **kwargs)
    return HuggingFaceClient(config)


# Example usage
if __name__ == "__main__":
    import os
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Get API key from environment
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        print("Error: HF_API_KEY environment variable not set")
        exit(1)
    
    # Example 1: Vision model
    print("\n=== Vision Model Example ===")
    vision_client = create_vision_client(api_key)
    
    # Check model status
    status = vision_client.check_model_status()
    print(f"Model status: {status}")
    
    # Query with sample image
    try:
        with open("sample_chart.png", "rb") as f:
            image_bytes = f.read()
        
        result = vision_client.query_vision_model(
            image_bytes,
            "Describe the technical indicators visible in this trading chart"
        )
        print(f"Vision result: {result}")
    except FileNotFoundError:
        print("Sample image not found, skipping vision example")
    except HFAPIError as e:
        print(f"API error: {e}")
    
    # Example 2: Text model
    print("\n=== Text Model Example ===")
    text_client = create_text_client(api_key)
    
    try:
        result = text_client.query_text_model(
            "Explain what a bullish divergence means in technical analysis.",
            parameters={"max_new_tokens": 200, "temperature": 0.7}
        )
        print(f"Text result: {result}")
    except HFAPIError as e:
        print(f"API error: {e}")
