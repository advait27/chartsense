# Hugging Face API Client

## Overview

A simple, synchronous Python client for Hugging Face's Inference API supporting vision-language and text generation models.

## Features

- ✅ **Synchronous API calls** - No async complexity
- ✅ **Easy model swapping** - Change models via configuration
- ✅ **Graceful error handling** - Custom exceptions for different error types
- ✅ **Automatic retries** - Handles model loading and network errors
- ✅ **Free-tier compatible** - Works with HF free tier (~30 requests/hour)
- ✅ **Vision & text models** - Support for BLIP-2, LLaVA, Llama, Mistral

---

## Quick Start

### Installation

```bash
pip install requests python-dotenv
```

### Basic Usage

```python
from backend.core.hf_client import create_vision_client

# Create client
client = create_vision_client(api_key="hf_xxx")

# Query vision model
with open("chart.png", "rb") as f:
    image_bytes = f.read()

result = client.query_vision_model(
    image_bytes,
    "Describe the technical indicators in this trading chart"
)

print(result)
```

---

## Configuration Patterns

### Pattern 1: Convenience Functions

```python
from backend.core.hf_client import create_vision_client, create_text_client

# Vision model (BLIP-2 by default)
vision_client = create_vision_client("hf_xxx")

# Text model (Llama-2 by default)
text_client = create_text_client("hf_xxx")
```

### Pattern 2: Custom Configuration

```python
from backend.core.hf_client import HuggingFaceClient, HFConfig

config = HFConfig(
    api_key="hf_xxx",
    model_id="Salesforce/blip2-opt-2.7b",
    timeout=45,
    max_retries=3,
    retry_delay=2
)

client = HuggingFaceClient(config)
```

### Pattern 3: Easy Model Swapping

```python
# Swap vision models
vision_client = create_vision_client("hf_xxx", "llava-hf/llava-1.5-7b-hf")

# Swap text models
text_client = create_text_client("hf_xxx", "mistralai/Mistral-7B-Instruct-v0.2")
```

### Pattern 4: Using Backend Config

```python
from backend.config import HF_API_KEY, VISION_MODEL_ID
from backend.core.hf_client import create_vision_client

client = create_vision_client(HF_API_KEY, VISION_MODEL_ID)
```

---

## API Reference

### `HuggingFaceClient`

Main client class for HF Inference API.

#### Methods

##### `query_vision_model(image, prompt, model_id=None, parameters=None)`

Query a vision-language model.

**Args:**
- `image`: Image as bytes or base64 string
- `prompt`: Text prompt for the model
- `model_id`: Optional model override
- `parameters`: Optional model parameters

**Returns:** Model response as dictionary

**Example:**
```python
result = client.query_vision_model(
    image_bytes,
    "Describe the chart patterns and indicators"
)
```

##### `query_text_model(prompt, model_id=None, parameters=None)`

Query a text generation model.

**Args:**
- `prompt`: Text prompt
- `model_id`: Optional model override
- `parameters`: Optional parameters (max_new_tokens, temperature, etc.)

**Returns:** Generated text string

**Example:**
```python
result = client.query_text_model(
    "Analyze this market setup...",
    parameters={
        "max_new_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9
    }
)
```

##### `check_model_status(model_id=None)`

Check if a model is available.

**Returns:** Status dictionary

---

## Error Handling

### Exception Hierarchy

```
HFAPIError (base)
├── HFAuthenticationError (401)
├── HFModelNotFoundError (404)
├── HFRateLimitError (429)
└── HFModelLoadingError (503)
```

### Example

```python
from backend.core.hf_client import (
    HFAPIError,
    HFAuthenticationError,
    HFRateLimitError
)

try:
    result = client.query_vision_model(image, prompt)
except HFAuthenticationError:
    print("Invalid API key")
except HFRateLimitError:
    print("Rate limit exceeded - wait before retrying")
except HFAPIError as e:
    print(f"API error: {e}")
```

---

## Supported Models

### Vision-Language Models

| Model | ID | Best For |
|-------|-----|----------|
| BLIP-2 | `Salesforce/blip2-opt-2.7b` | General vision tasks ⭐ |
| LLaVA 1.5 | `llava-hf/llava-1.5-7b-hf` | Complex reasoning |
| BLIP | `Salesforce/blip-image-captioning-large` | Image captioning |

### Text Generation Models

| Model | ID | Best For |
|-------|-----|----------|
| Llama 2 | `meta-llama/Llama-2-7b-chat-hf` | General text ⭐ |
| Mistral | `mistralai/Mistral-7B-Instruct-v0.2` | Fast inference |
| FLAN-T5 | `google/flan-t5-large` | Smaller, faster |

---

## Configuration

### Environment Variables

```bash
# Required
HF_API_KEY=hf_xxx

# Optional (with defaults)
VISION_MODEL=Salesforce/blip2-opt-2.7b
REASONING_MODEL=meta-llama/Llama-2-7b-chat-hf
VISION_TIMEOUT=30
REASONING_TIMEOUT=30
MAX_RETRIES=2
RETRY_DELAY=2
```

### Backend Config Module

All configuration is centralized in [`backend/config.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/backend/config.py):

```python
from backend.config import (
    HF_API_KEY,
    VISION_MODEL_ID,
    REASONING_MODEL_ID,
    VISION_TIMEOUT,
    MAX_RETRIES
)
```

---

## Advanced Usage

### Custom Parameters

```python
# Vision model with custom parameters
result = client.query_vision_model(
    image_bytes,
    "Describe this chart",
    parameters={
        "max_length": 200
    }
)

# Text model with custom parameters
result = client.query_text_model(
    "Analyze...",
    parameters={
        "max_new_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
        "repetition_penalty": 1.1
    }
)
```

### Model Status Checking

```python
# Check if model is ready
status = client.check_model_status()

if status["available"]:
    print("Model is ready!")
else:
    print(f"Model unavailable: {status.get('error')}")
```

### Retry Logic

The client automatically retries on:
- Model loading errors (503)
- Network timeouts
- Connection errors

```python
config = HFConfig(
    api_key="hf_xxx",
    model_id="Salesforce/blip2-opt-2.7b",
    max_retries=3,      # Retry up to 3 times
    retry_delay=2       # Wait 2 seconds between retries
)
```

---

## Free Tier Limits

Hugging Face free tier limitations:
- **~30 requests per hour** per model
- **Cold start**: First request may take 20-30 seconds
- **Model loading**: Models may need to load if inactive

### Best Practices

1. **Check model status** before making requests
2. **Implement rate limiting** in your application
3. **Handle loading errors** gracefully
4. **Cache results** when possible
5. **Use retry logic** for transient errors

---

## Testing

### Run Tests

```bash
pytest tests/test_hf_client.py -v
```

### Test Coverage

- ✅ Configuration creation
- ✅ Client initialization
- ✅ Response handling (success/errors)
- ✅ Vision model queries
- ✅ Text model queries
- ✅ Error handling
- ✅ Retry logic
- ✅ Convenience functions

---

## Demo Script

Run the demo to see all features:

```bash
export HF_API_KEY=your_key_here
python scripts/demo_hf_client.py
```

Demo includes:
1. Configuration patterns
2. Model status checking
3. Vision model queries
4. Text model queries
5. Error handling

---

## Integration Example

### With Image Processor

```python
from backend.core.image_processor import preprocess_chart_image
from backend.core.hf_client import create_vision_client

# Preprocess image
processed_bytes, metadata = preprocess_chart_image(image_bytes)

# Query vision model
client = create_vision_client(api_key)
result = client.query_vision_model(
    processed_bytes,
    "Analyze this trading chart"
)
```

### With FastAPI

```python
from fastapi import FastAPI, UploadFile
from backend.core.hf_client import create_vision_client
from backend.config import HF_API_KEY

app = FastAPI()
vision_client = create_vision_client(HF_API_KEY)

@app.post("/analyze")
async def analyze(file: UploadFile):
    image_bytes = await file.read()
    
    result = vision_client.query_vision_model(
        image_bytes,
        "Describe the chart"
    )
    
    return {"analysis": result}
```

---

## Troubleshooting

### "Invalid API key"
- Check that `HF_API_KEY` is set correctly
- Verify key at https://huggingface.co/settings/tokens

### "Model is loading"
- First request may take 20-30 seconds
- Client will automatically retry
- Increase `max_retries` if needed

### "Rate limit exceeded"
- Free tier: ~30 requests/hour
- Wait before retrying
- Consider upgrading to paid tier

### "Model not found"
- Check model ID is correct
- Verify model is publicly accessible
- Some models require acceptance of terms

---

## Files

- [`hf_client.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/backend/core/hf_client.py) - Main implementation
- [`config.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/backend/config.py) - Configuration module
- [`test_hf_client.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/tests/test_hf_client.py) - Test suite
- [`demo_hf_client.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/scripts/demo_hf_client.py) - Demo script

---

**Version**: 1.0.0  
**Status**: Production-ready  
**License**: MIT
