"""
Image Preprocessing Pipeline for Trading Chart Screenshots

This module provides functions to preprocess TradingView chart screenshots
for AI model inference. It handles validation, cropping, normalization,
and resizing using rule-based approaches (no ML).

Author: Chartered
Version: 1.0.0
"""

from PIL import Image, ImageEnhance, ImageOps
import io
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Handles preprocessing of trading chart screenshots for AI analysis.
    
    Features:
    - Image validation (format, size, dimensions)
    - Rule-based cropping to remove UI elements
    - Contrast and brightness normalization
    - Resizing to model-friendly dimensions
    """
    
    # Image constraints
    MAX_SIZE_MB = 5
    MIN_WIDTH = 400
    MIN_HEIGHT = 300
    MAX_WIDTH = 4000
    MAX_HEIGHT = 3000
    
    # Target dimensions for AI models (maintains aspect ratio)
    TARGET_WIDTH = 1024
    TARGET_HEIGHT = 768
    
    # Cropping margins (percentage of image to remove from edges)
    # These are conservative estimates for TradingView UI elements
    TOP_MARGIN_PERCENT = 0.05    # Remove top toolbar (5%)
    BOTTOM_MARGIN_PERCENT = 0.03  # Remove bottom status bar (3%)
    LEFT_MARGIN_PERCENT = 0.02    # Remove left sidebar (2%)
    RIGHT_MARGIN_PERCENT = 0.02   # Remove right sidebar (2%)
    
    def __init__(self):
        """Initialize the image processor."""
        self.logger = logging.getLogger(__name__)
    
    def validate_image(self, image_bytes: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate image format, size, and dimensions.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if image passes all validations
            - error_message: None if valid, error description if invalid
        """
        try:
            # Check file size
            size_mb = len(image_bytes) / (1024 * 1024)
            if size_mb > self.MAX_SIZE_MB:
                return False, f"Image size ({size_mb:.2f}MB) exceeds {self.MAX_SIZE_MB}MB limit"
            
            # Try to open image
            try:
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                return False, f"Invalid image file: {str(e)}"
            
            # Validate format
            if image.format not in ["PNG", "JPEG"]:
                return False, f"Unsupported format: {image.format}. Only PNG and JPEG allowed"
            
            # Validate dimensions
            width, height = image.size
            
            if width < self.MIN_WIDTH or height < self.MIN_HEIGHT:
                return False, f"Image too small ({width}x{height}). Minimum: {self.MIN_WIDTH}x{self.MIN_HEIGHT}"
            
            if width > self.MAX_WIDTH or height > self.MAX_HEIGHT:
                return False, f"Image too large ({width}x{height}). Maximum: {self.MAX_WIDTH}x{self.MAX_HEIGHT}"
            
            # All validations passed
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def remove_ui_elements(self, image: Image.Image) -> Image.Image:
        """
        Remove TradingView UI elements using rule-based cropping.
        
        This function removes common UI elements like:
        - Top toolbar (drawing tools, indicators)
        - Bottom status bar (time, price info)
        - Left/right sidebars
        
        Args:
            image: PIL Image object
            
        Returns:
            Cropped PIL Image with UI elements removed
        """
        width, height = image.size
        
        # Calculate crop boundaries
        left = int(width * self.LEFT_MARGIN_PERCENT)
        top = int(height * self.TOP_MARGIN_PERCENT)
        right = width - int(width * self.RIGHT_MARGIN_PERCENT)
        bottom = height - int(height * self.BOTTOM_MARGIN_PERCENT)
        
        # Crop image
        cropped = image.crop((left, top, right, bottom))
        
        self.logger.info(f"Cropped image from {width}x{height} to {cropped.size[0]}x{cropped.size[1]}")
        
        return cropped
    
    def normalize_contrast_brightness(
        self, 
        image: Image.Image,
        contrast_factor: float = 1.2,
        brightness_factor: float = 1.1
    ) -> Image.Image:
        """
        Normalize contrast and brightness for better AI model performance.
        
        Trading charts often have varying contrast levels depending on
        the theme (dark/light mode). This normalization helps the AI
        model focus on patterns rather than color variations.
        
        Args:
            image: PIL Image object
            contrast_factor: Contrast enhancement factor (1.0 = no change)
            brightness_factor: Brightness enhancement factor (1.0 = no change)
            
        Returns:
            Enhanced PIL Image
        """
        # Enhance contrast
        contrast_enhancer = ImageEnhance.Contrast(image)
        image = contrast_enhancer.enhance(contrast_factor)
        
        # Enhance brightness
        brightness_enhancer = ImageEnhance.Brightness(image)
        image = brightness_enhancer.enhance(brightness_factor)
        
        # Auto-equalize to normalize histogram
        # This helps with both dark and light mode charts
        image = ImageOps.equalize(image.convert('RGB'))
        
        self.logger.info(f"Applied contrast ({contrast_factor}) and brightness ({brightness_factor}) normalization")
        
        return image
    
    def resize_for_model(
        self, 
        image: Image.Image,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        maintain_aspect_ratio: bool = True
    ) -> Image.Image:
        """
        Resize image to model-friendly dimensions.
        
        Most vision models work best with specific input sizes.
        This function resizes while maintaining aspect ratio to
        prevent distortion of chart patterns.
        
        Args:
            image: PIL Image object
            target_width: Target width (uses default if None)
            target_height: Target height (uses default if None)
            maintain_aspect_ratio: If True, resize to fit within target dimensions
            
        Returns:
            Resized PIL Image
        """
        target_width = target_width or self.TARGET_WIDTH
        target_height = target_height or self.TARGET_HEIGHT
        
        if maintain_aspect_ratio:
            # Calculate aspect ratio preserving dimensions
            image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            resized = image
        else:
            # Force resize to exact dimensions (may distort)
            resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        self.logger.info(f"Resized image to {resized.size[0]}x{resized.size[1]}")
        
        return resized
    
    def preprocess(
        self,
        image_bytes: bytes,
        remove_ui: bool = True,
        normalize: bool = True,
        resize: bool = True
    ) -> Tuple[bytes, dict]:
        """
        Complete preprocessing pipeline for chart screenshots.
        
        This is the main entry point that orchestrates all preprocessing steps:
        1. Validate image
        2. Remove UI elements (optional)
        3. Normalize contrast/brightness (optional)
        4. Resize to model dimensions (optional)
        
        Args:
            image_bytes: Raw image bytes
            remove_ui: Whether to crop UI elements
            normalize: Whether to normalize contrast/brightness
            resize: Whether to resize for model
            
        Returns:
            Tuple of (processed_image_bytes, metadata_dict)
            - processed_image_bytes: Preprocessed image as bytes
            - metadata_dict: Information about preprocessing steps
            
        Raises:
            ValueError: If image validation fails
        """
        # Step 1: Validate
        is_valid, error_msg = self.validate_image(image_bytes)
        if not is_valid:
            raise ValueError(f"Image validation failed: {error_msg}")
        
        # Load image and keep reference to ensure proper cleanup
        image_stream = io.BytesIO(image_bytes)
        image = Image.open(image_stream)
        original_size = image.size
        original_format = image.format
        
        # Load the image data to allow closing the stream
        image.load()
        
        metadata = {
            "original_size": original_size,
            "original_format": original_format,
            "steps_applied": []
        }
        
        # Step 2: Remove UI elements
        if remove_ui:
            image = self.remove_ui_elements(image)
            metadata["steps_applied"].append("ui_removal")
            metadata["cropped_size"] = image.size
        
        # Step 3: Normalize contrast and brightness
        if normalize:
            image = self.normalize_contrast_brightness(image)
            metadata["steps_applied"].append("normalization")
        
        # Step 4: Resize for model
        if resize:
            image = self.resize_for_model(image)
            metadata["steps_applied"].append("resize")
            metadata["final_size"] = image.size
        
        # Convert back to bytes
        output_buffer = io.BytesIO()
        
        # Preserve PNG format if original was PNG (better quality for charts with text)
        # Otherwise use JPEG for photos/complex images
        if original_format == 'PNG':
            image.save(output_buffer, format='PNG', optimize=True)
            output_format = 'PNG'
        else:
            # Use JPEG for other formats
            if image.mode in ('RGBA', 'LA', 'P'):
                # Convert to RGB if image has transparency
                image = image.convert('RGB')
            image.save(output_buffer, format='JPEG', quality=92, optimize=True)
            output_format = 'JPEG'
        
        processed_bytes = output_buffer.getvalue()
        
        metadata["output_format"] = output_format
        metadata["output_size_bytes"] = len(processed_bytes)
        metadata["compression_ratio"] = len(image_bytes) / len(processed_bytes)
        
        self.logger.info(f"Preprocessing complete. Original: {len(image_bytes)} bytes, "
                        f"Processed: {len(processed_bytes)} bytes "
                        f"(compression: {metadata['compression_ratio']:.2f}x)")
        
        # Close the image to free memory
        image.close()
        image_stream.close()
        
        return processed_bytes, metadata
    
    def preprocess_for_display(self, image_bytes: bytes) -> bytes:
        """
        Light preprocessing for display purposes only (no aggressive cropping).
        
        Use this when you want to show a cleaned-up version to the user
        without removing too much context.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Lightly processed image bytes
        """
        image_stream = io.BytesIO(image_bytes)
        image = Image.open(image_stream)
        image.load()
        
        # Only apply light normalization and resize
        image = self.normalize_contrast_brightness(image, contrast_factor=1.1, brightness_factor=1.05)
        image = self.resize_for_model(image)
        
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=95)
        result = output_buffer.getvalue()
        
        # Clean up
        image.close()
        image_stream.close()
        
        return result


# Convenience functions for quick usage

def validate_chart_image(image_bytes: bytes) -> Tuple[bool, Optional[str]]:
    """
    Quick validation function.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    processor = ImageProcessor()
    return processor.validate_image(image_bytes)


def preprocess_chart_image(
    image_bytes: bytes,
    aggressive_crop: bool = False,
    remove_ui: bool = True,
    normalize: bool = True,
    resize: bool = True
) -> Tuple[bytes, dict]:
    """
    Quick preprocessing function with sensible defaults.
    
    Args:
        image_bytes: Raw image bytes
        aggressive_crop: If True, applies more aggressive UI removal
        remove_ui: Whether to crop UI elements
        normalize: Whether to normalize contrast/brightness
        resize: Whether to resize for model
        
    Returns:
        Tuple of (processed_bytes, metadata)
    """
    processor = ImageProcessor()
    
    # Adjust cropping margins if aggressive mode
    if aggressive_crop:
        processor.TOP_MARGIN_PERCENT = 0.08
        processor.BOTTOM_MARGIN_PERCENT = 0.05
        processor.LEFT_MARGIN_PERCENT = 0.03
        processor.RIGHT_MARGIN_PERCENT = 0.03
    
    return processor.preprocess(
        image_bytes,
        remove_ui=remove_ui,
        normalize=normalize,
        resize=resize
    )


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Example: Process a chart image
    with open("sample_chart.png", "rb") as f:
        image_bytes = f.read()
    
    # Validate
    is_valid, error = validate_chart_image(image_bytes)
    if not is_valid:
        print(f"Validation failed: {error}")
        exit(1)
    
    # Preprocess
    processed_bytes, metadata = preprocess_chart_image(image_bytes)
    
    print(f"Preprocessing complete!")
    print(f"Original size: {metadata['original_size']}")
    print(f"Final size: {metadata['final_size']}")
    print(f"Steps applied: {', '.join(metadata['steps_applied'])}")
    print(f"Compression: {metadata['compression_ratio']:.2f}x")
    
    # Save processed image
    with open("processed_chart.jpg", "wb") as f:
        f.write(processed_bytes)
    print("Saved to processed_chart.jpg")
