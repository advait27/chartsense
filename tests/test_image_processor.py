"""
Unit Tests for Image Processor

Tests validation, cropping, normalization, and resizing functionality.
"""

import pytest
from PIL import Image
import io
from backend.core.image_processor import ImageProcessor, validate_chart_image, preprocess_chart_image


class TestImageProcessor:
    """Test suite for ImageProcessor class"""
    
    @pytest.fixture
    def processor(self):
        """Create ImageProcessor instance for tests"""
        return ImageProcessor()
    
    @pytest.fixture
    def sample_image_bytes(self):
        """Create a sample image for testing"""
        # Create a simple test image (800x600 RGB)
        img = Image.new('RGB', (800, 600), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @pytest.fixture
    def small_image_bytes(self):
        """Create a too-small image for testing"""
        img = Image.new('RGB', (300, 200), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_validate_valid_image(self, processor, sample_image_bytes):
        """Test validation passes for valid image"""
        is_valid, error = processor.validate_image(sample_image_bytes)
        assert is_valid is True
        assert error is None
    
    def test_validate_small_image(self, processor, small_image_bytes):
        """Test validation fails for too-small image"""
        is_valid, error = processor.validate_image(small_image_bytes)
        assert is_valid is False
        assert "too small" in error.lower()
    
    def test_validate_invalid_format(self, processor):
        """Test validation fails for invalid format"""
        # Create a text file pretending to be an image
        invalid_bytes = b"This is not an image"
        is_valid, error = processor.validate_image(invalid_bytes)
        assert is_valid is False
        assert error is not None
    
    def test_remove_ui_elements(self, processor, sample_image_bytes):
        """Test UI removal crops the image"""
        image = Image.open(io.BytesIO(sample_image_bytes))
        original_size = image.size
        
        cropped = processor.remove_ui_elements(image)
        
        # Cropped image should be smaller
        assert cropped.size[0] < original_size[0]
        assert cropped.size[1] < original_size[1]
    
    def test_normalize_contrast_brightness(self, processor, sample_image_bytes):
        """Test normalization doesn't fail"""
        image = Image.open(io.BytesIO(sample_image_bytes))
        
        normalized = processor.normalize_contrast_brightness(image)
        
        # Should return an image of same size
        assert normalized.size == image.size
        assert normalized.mode == 'RGB'
    
    def test_resize_for_model(self, processor, sample_image_bytes):
        """Test resizing to model dimensions"""
        image = Image.open(io.BytesIO(sample_image_bytes))
        
        resized = processor.resize_for_model(image)
        
        # Should be resized to target dimensions or smaller (aspect ratio maintained)
        assert resized.size[0] <= processor.TARGET_WIDTH
        assert resized.size[1] <= processor.TARGET_HEIGHT
    
    def test_preprocess_pipeline(self, processor, sample_image_bytes):
        """Test complete preprocessing pipeline"""
        processed_bytes, metadata = processor.preprocess(sample_image_bytes)
        
        # Should return bytes
        assert isinstance(processed_bytes, bytes)
        assert len(processed_bytes) > 0
        
        # Metadata should contain expected keys
        assert 'original_size' in metadata
        assert 'steps_applied' in metadata
        assert 'final_size' in metadata
        assert 'output_format' in metadata
        
        # Should have applied all steps
        assert 'ui_removal' in metadata['steps_applied']
        assert 'normalization' in metadata['steps_applied']
        assert 'resize' in metadata['steps_applied']
    
    def test_preprocess_selective_steps(self, processor, sample_image_bytes):
        """Test preprocessing with selective steps"""
        # Only resize, no UI removal or normalization
        processed_bytes, metadata = processor.preprocess(
            sample_image_bytes,
            remove_ui=False,
            normalize=False,
            resize=True
        )
        
        assert 'resize' in metadata['steps_applied']
        assert 'ui_removal' not in metadata['steps_applied']
        assert 'normalization' not in metadata['steps_applied']
    
    def test_convenience_function(self, sample_image_bytes):
        """Test convenience function works"""
        is_valid, error = validate_chart_image(sample_image_bytes)
        assert is_valid is True
        
        processed_bytes, metadata = preprocess_chart_image(sample_image_bytes)
        assert isinstance(processed_bytes, bytes)
        assert 'steps_applied' in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
