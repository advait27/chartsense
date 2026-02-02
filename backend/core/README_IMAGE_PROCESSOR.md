# Image Preprocessing Pipeline

## Overview

The image preprocessing pipeline prepares TradingView chart screenshots for AI model inference by:

1. **Validating** image format, size, and dimensions
2. **Removing** UI elements (toolbars, sidebars) using rule-based cropping
3. **Normalizing** contrast and brightness for consistent analysis
4. **Resizing** to model-friendly dimensions while maintaining aspect ratio

## Features

### ✅ Image Validation
- Format check (PNG/JPEG only)
- Size limit enforcement (max 5MB)
- Dimension validation (400x300 to 4000x3000)

### ✅ UI Element Removal
- Rule-based cropping (no ML required)
- Removes top toolbar (5%)
- Removes bottom status bar (3%)
- Removes left/right sidebars (2% each)
- Configurable margins for aggressive cropping

### ✅ Normalization
- Contrast enhancement (1.2x default)
- Brightness adjustment (1.1x default)
- Histogram equalization for dark/light mode charts

### ✅ Resizing
- Target dimensions: 1024x768 (configurable)
- Maintains aspect ratio to prevent distortion
- High-quality LANCZOS resampling

## Usage

### Basic Usage

```python
from backend.core.image_processor import preprocess_chart_image

# Load your chart screenshot
with open("chart.png", "rb") as f:
    image_bytes = f.read()

# Preprocess
processed_bytes, metadata = preprocess_chart_image(image_bytes)

# Save processed image
with open("processed_chart.jpg", "wb") as f:
    f.write(processed_bytes)

print(f"Original: {metadata['original_size']}")
print(f"Final: {metadata['final_size']}")
print(f"Compression: {metadata['compression_ratio']:.2f}x")
```

### Advanced Usage

```python
from backend.core.image_processor import ImageProcessor

processor = ImageProcessor()

# Validate first
is_valid, error = processor.validate_image(image_bytes)
if not is_valid:
    print(f"Validation failed: {error}")
    exit(1)

# Preprocess with custom options
processed_bytes, metadata = processor.preprocess(
    image_bytes,
    remove_ui=True,      # Remove UI elements
    normalize=True,      # Normalize contrast/brightness
    resize=True          # Resize to model dimensions
)
```

### Aggressive Cropping

For charts with more UI elements:

```python
from backend.core.image_processor import preprocess_chart_image

processed_bytes, metadata = preprocess_chart_image(
    image_bytes,
    aggressive_crop=True  # More aggressive UI removal
)
```

### Custom Configuration

```python
from backend.core.image_processor import ImageProcessor

processor = ImageProcessor()

# Customize cropping margins
processor.TOP_MARGIN_PERCENT = 0.08
processor.BOTTOM_MARGIN_PERCENT = 0.05
processor.LEFT_MARGIN_PERCENT = 0.03
processor.RIGHT_MARGIN_PERCENT = 0.03

# Customize target dimensions
processor.TARGET_WIDTH = 1280
processor.TARGET_HEIGHT = 960

# Process
processed_bytes, metadata = processor.preprocess(image_bytes)
```

## API Reference

### `ImageProcessor` Class

Main class for image preprocessing operations.

#### Methods

##### `validate_image(image_bytes: bytes) -> Tuple[bool, Optional[str]]`
Validates image format, size, and dimensions.

**Returns:**
- `(True, None)` if valid
- `(False, error_message)` if invalid

##### `remove_ui_elements(image: Image.Image) -> Image.Image`
Removes TradingView UI elements using rule-based cropping.

##### `normalize_contrast_brightness(image: Image.Image, contrast_factor: float = 1.2, brightness_factor: float = 1.1) -> Image.Image`
Normalizes contrast and brightness.

##### `resize_for_model(image: Image.Image, target_width: int = None, target_height: int = None, maintain_aspect_ratio: bool = True) -> Image.Image`
Resizes image to model-friendly dimensions.

##### `preprocess(image_bytes: bytes, remove_ui: bool = True, normalize: bool = True, resize: bool = True) -> Tuple[bytes, dict]`
Complete preprocessing pipeline.

**Returns:**
- `processed_bytes`: Preprocessed image as JPEG bytes
- `metadata`: Dictionary with preprocessing information

### Convenience Functions

##### `validate_chart_image(image_bytes: bytes) -> Tuple[bool, Optional[str]]`
Quick validation function.

##### `preprocess_chart_image(image_bytes: bytes, aggressive_crop: bool = False) -> Tuple[bytes, dict]`
Quick preprocessing with sensible defaults.

## Metadata Output

The preprocessing pipeline returns metadata about the operations:

```python
{
    "original_size": (1920, 1080),
    "original_format": "PNG",
    "steps_applied": ["ui_removal", "normalization", "resize"],
    "cropped_size": (1843, 1026),
    "final_size": (1024, 576),
    "output_format": "JPEG",
    "output_size_bytes": 245678,
    "compression_ratio": 3.45
}
```

## Configuration

### Default Settings

```python
# Image constraints
MAX_SIZE_MB = 5
MIN_WIDTH = 400
MIN_HEIGHT = 300
MAX_WIDTH = 4000
MAX_HEIGHT = 3000

# Target dimensions
TARGET_WIDTH = 1024
TARGET_HEIGHT = 768

# Cropping margins (percentage)
TOP_MARGIN_PERCENT = 0.05     # 5%
BOTTOM_MARGIN_PERCENT = 0.03  # 3%
LEFT_MARGIN_PERCENT = 0.02    # 2%
RIGHT_MARGIN_PERCENT = 0.02   # 2%
```

## Testing

Run the test suite:

```bash
pytest tests/test_image_processor.py -v
```

Tests cover:
- ✅ Valid image validation
- ✅ Invalid format rejection
- ✅ Size limit enforcement
- ✅ UI element removal
- ✅ Normalization
- ✅ Resizing
- ✅ Complete pipeline
- ✅ Selective step processing

## Performance

Typical processing times (on M1 Mac):
- Validation: ~5ms
- UI removal: ~10ms
- Normalization: ~50ms
- Resizing: ~30ms
- **Total: ~100ms** for 1920x1080 image

## Best Practices

1. **Always validate** before preprocessing
2. **Use aggressive cropping** for screenshots with heavy UI
3. **Maintain aspect ratio** to preserve chart patterns
4. **Monitor compression ratio** to ensure quality
5. **Log metadata** for debugging and optimization

## Limitations

- **Rule-based cropping**: May not work perfectly for all TradingView layouts
- **Fixed margins**: Assumes standard TradingView UI positioning
- **No ML detection**: Cannot intelligently detect UI elements
- **JPEG output**: Lossy compression (90% quality by default)

## Future Enhancements

- [ ] ML-based UI detection
- [ ] Adaptive cropping based on content
- [ ] Support for multiple chart platforms
- [ ] Watermark removal
- [ ] Text extraction for metadata

## Examples

### Before Preprocessing
- Size: 1920x1080 (2.1MB PNG)
- Contains toolbars, sidebars, status bars
- Variable contrast depending on theme

### After Preprocessing
- Size: 1024x576 (245KB JPEG)
- Clean chart area only
- Normalized contrast and brightness
- Ready for AI model inference

## Integration with Backend

```python
# In FastAPI endpoint
from backend.core.image_processor import ImageProcessor

processor = ImageProcessor()

@app.post("/api/analyze-chart")
async def analyze_chart(request: AnalysisRequest):
    # Decode base64 image
    image_bytes = base64.b64decode(request.image)
    
    # Preprocess
    processed_bytes, metadata = processor.preprocess(image_bytes)
    
    # Send to AI model
    vision_output = await vision_service.analyze(processed_bytes)
    
    # Return analysis
    return {"analysis": vision_output, "preprocessing": metadata}
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-28
