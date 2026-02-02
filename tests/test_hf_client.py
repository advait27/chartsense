"""
Unit Tests for Hugging Face Client

Tests API client functionality with mocked responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import base64
from backend.core.hf_client import (
    HuggingFaceClient,
    HFConfig,
    HFAPIError,
    HFAuthenticationError,
    HFModelNotFoundError,
    HFRateLimitError,
    HFModelLoadingError,
    create_vision_client,
    create_text_client
)


class TestHFConfig:
    """Test HFConfig dataclass"""
    
    def test_config_creation(self):
        """Test creating configuration"""
        config = HFConfig(
            api_key="test_key",
            model_id="test/model"
        )
        assert config.api_key == "test_key"
        assert config.model_id == "test/model"
        assert config.timeout == 30  # default
        assert config.max_retries == 2  # default


class TestHuggingFaceClient:
    """Test HuggingFaceClient class"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return HFConfig(
            api_key="test_key",
            model_id="Salesforce/blip2-opt-2.7b",
            timeout=10,
            max_retries=1
        )
    
    @pytest.fixture
    def client(self, config):
        """Create test client"""
        return HuggingFaceClient(config)
    
    def test_client_initialization(self, client, config):
        """Test client initializes correctly"""
        assert client.config == config
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test_key"
    
    def test_get_model_url(self, client):
        """Test URL generation"""
        url = client._get_model_url()
        assert url == "https://api-inference.huggingface.co/models/Salesforce/blip2-opt-2.7b"
        
        # Test with custom model
        url = client._get_model_url("custom/model")
        assert url == "https://api-inference.huggingface.co/models/custom/model"
    
    def test_handle_response_success(self, client):
        """Test successful response handling"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        
        result = client._handle_response(mock_response)
        assert result == {"result": "success"}
    
    def test_handle_response_auth_error(self, client):
        """Test authentication error handling"""
        mock_response = Mock()
        mock_response.status_code = 401
        
        with pytest.raises(HFAuthenticationError):
            client._handle_response(mock_response)
    
    def test_handle_response_not_found(self, client):
        """Test model not found error"""
        mock_response = Mock()
        mock_response.status_code = 404
        
        with pytest.raises(HFModelNotFoundError):
            client._handle_response(mock_response)
    
    def test_handle_response_rate_limit(self, client):
        """Test rate limit error"""
        mock_response = Mock()
        mock_response.status_code = 429
        
        with pytest.raises(HFRateLimitError):
            client._handle_response(mock_response)
    
    def test_handle_response_model_loading(self, client):
        """Test model loading error"""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.json.return_value = {
            "error": "Model is loading",
            "estimated_time": 20
        }
        
        with pytest.raises(HFModelLoadingError):
            client._handle_response(mock_response)
    
    @patch('backend.core.hf_client.requests.Session.post')
    def test_query_vision_model_success(self, mock_post, client):
        """Test successful vision model query"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "A trading chart"}]
        mock_post.return_value = mock_response
        
        # Test with bytes
        image_bytes = b"fake_image_data"
        result = client.query_vision_model(image_bytes, "Describe this chart")
        
        # Should now return the extracted text string, not the full response
        assert result == "A trading chart"
        assert isinstance(result, str)
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert "json" in call_kwargs
        assert "inputs" in call_kwargs["json"]
        assert "image" in call_kwargs["json"]["inputs"]
        assert "text" in call_kwargs["json"]["inputs"]
    
    @patch('backend.core.hf_client.requests.Session.post')
    def test_query_vision_model_with_base64(self, mock_post, client):
        """Test vision model query with base64 string"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": "success response"}
        mock_post.return_value = mock_response
        
        # Test with base64 string
        image_b64 = base64.b64encode(b"fake_image").decode('utf-8')
        result = client.query_vision_model(image_b64, "Test prompt")
        
        # Should extract text from response
        assert result == "success response"
        assert isinstance(result, str)
    
    @patch('backend.core.hf_client.requests.Session.post')
    def test_query_text_model_success(self, mock_post, client):
        """Test successful text model query"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "Analysis result"}]
        mock_post.return_value = mock_response
        
        result = client.query_text_model("Test prompt")
        
        assert result == "Analysis result"
    
    @patch('backend.core.hf_client.requests.Session.post')
    def test_query_with_parameters(self, mock_post, client):
        """Test query with custom parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "Result"}]
        mock_post.return_value = mock_response
        
        parameters = {"max_new_tokens": 500, "temperature": 0.7}
        client.query_text_model("Test", parameters=parameters)
        
        # Verify parameters were included
        call_kwargs = mock_post.call_args[1]
        assert "parameters" in call_kwargs["json"]
        assert call_kwargs["json"]["parameters"] == parameters
    
    @patch('backend.core.hf_client.requests.Session.post')
    @patch('backend.core.hf_client.time.sleep')
    def test_retry_on_model_loading(self, mock_sleep, mock_post, client):
        """Test retry logic when model is loading"""
        # First call: model loading
        mock_response_loading = Mock()
        mock_response_loading.status_code = 503
        mock_response_loading.json.return_value = {
            "error": "Model is loading",
            "estimated_time": 10
        }
        
        # Second call: success
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = [{"generated_text": "Success"}]
        
        mock_post.side_effect = [mock_response_loading, mock_response_success]
        
        result = client.query_text_model("Test")
        
        assert result == "Success"
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once()
    
    @patch('backend.core.hf_client.requests.Session.get')
    def test_check_model_status(self, mock_get, client):
        """Test model status check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        status = client.check_model_status()
        
        assert status["available"] is True
        assert status["status_code"] == 200


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_create_vision_client(self):
        """Test vision client creation"""
        client = create_vision_client("test_key")
        assert client.config.api_key == "test_key"
        assert "blip2" in client.config.model_id.lower()
    
    def test_create_text_client(self):
        """Test text client creation"""
        client = create_text_client("test_key")
        assert client.config.api_key == "test_key"
        assert "llama" in client.config.model_id.lower()
    
    def test_create_with_custom_model(self):
        """Test client creation with custom model"""
        client = create_vision_client("test_key", "custom/model")
        assert client.config.model_id == "custom/model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
