#!/usr/bin/env python3
"""
Demo script for image preprocessing pipeline

This script demonstrates the image preprocessing capabilities
with a sample chart image.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.image_processor import ImageProcessor, preprocess_chart_image
from PIL import Image
import io

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_chart():
    """Create a sample chart image for demonstration"""
    logger.info("Creating sample chart image...")
    
    # Create a simple chart-like image (1920x1080)
    img = Image.new('RGB', (1920, 1080), color='#1e1e1e')  # Dark background
    
    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def demo_validation():
    """Demonstrate image validation"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 1: Image Validation")
    logger.info("="*60)
    
    processor = ImageProcessor()
    
    # Test 1: Valid image
    valid_image = create_sample_chart()
    is_valid, error = processor.validate_image(valid_image)
    logger.info(f"✅ Valid image: {is_valid}, Error: {error}")
    
    # Test 2: Invalid image (too small)
    small_img = Image.new('RGB', (300, 200), color='white')
    buffer = io.BytesIO()
    small_img.save(buffer, format='PNG')
    is_valid, error = processor.validate_image(buffer.getvalue())
    logger.info(f"❌ Small image: {is_valid}, Error: {error}")
    
    # Test 3: Invalid format
    invalid_bytes = b"This is not an image"
    is_valid, error = processor.validate_image(invalid_bytes)
    logger.info(f"❌ Invalid format: {is_valid}, Error: {error}")


def demo_preprocessing():
    """Demonstrate full preprocessing pipeline"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 2: Full Preprocessing Pipeline")
    logger.info("="*60)
    
    # Create sample image
    image_bytes = create_sample_chart()
    logger.info(f"Original image size: {len(image_bytes)} bytes")
    
    # Preprocess
    processed_bytes, metadata = preprocess_chart_image(image_bytes)
    
    logger.info(f"\n📊 Preprocessing Results:")
    logger.info(f"  Original size: {metadata['original_size']}")
    logger.info(f"  Original format: {metadata['original_format']}")
    logger.info(f"  Steps applied: {', '.join(metadata['steps_applied'])}")
    
    if 'cropped_size' in metadata:
        logger.info(f"  Cropped size: {metadata['cropped_size']}")
    
    logger.info(f"  Final size: {metadata['final_size']}")
    logger.info(f"  Output format: {metadata['output_format']}")
    logger.info(f"  Output bytes: {metadata['output_size_bytes']}")
    logger.info(f"  Compression ratio: {metadata['compression_ratio']:.2f}x")


def demo_selective_processing():
    """Demonstrate selective preprocessing steps"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 3: Selective Processing")
    logger.info("="*60)
    
    processor = ImageProcessor()
    image_bytes = create_sample_chart()
    
    # Only resize, no UI removal or normalization
    logger.info("\n🔧 Processing with only resize...")
    processed_bytes, metadata = processor.preprocess(
        image_bytes,
        remove_ui=False,
        normalize=False,
        resize=True
    )
    logger.info(f"  Steps applied: {', '.join(metadata['steps_applied'])}")
    logger.info(f"  Final size: {metadata['final_size']}")
    
    # Only normalization
    logger.info("\n🔧 Processing with only normalization...")
    processed_bytes, metadata = processor.preprocess(
        image_bytes,
        remove_ui=False,
        normalize=True,
        resize=False
    )
    logger.info(f"  Steps applied: {', '.join(metadata['steps_applied'])}")


def demo_aggressive_cropping():
    """Demonstrate aggressive cropping mode"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 4: Aggressive Cropping")
    logger.info("="*60)
    
    image_bytes = create_sample_chart()
    
    # Normal cropping
    logger.info("\n📏 Normal cropping...")
    processed_bytes, metadata = preprocess_chart_image(
        image_bytes,
        aggressive_crop=False
    )
    logger.info(f"  Cropped size: {metadata.get('cropped_size', 'N/A')}")
    logger.info(f"  Final size: {metadata['final_size']}")
    
    # Aggressive cropping
    logger.info("\n📏 Aggressive cropping...")
    processed_bytes, metadata = preprocess_chart_image(
        image_bytes,
        aggressive_crop=True
    )
    logger.info(f"  Cropped size: {metadata.get('cropped_size', 'N/A')}")
    logger.info(f"  Final size: {metadata['final_size']}")


def demo_custom_configuration():
    """Demonstrate custom configuration"""
    logger.info("\n" + "="*60)
    logger.info("DEMO 5: Custom Configuration")
    logger.info("="*60)
    
    processor = ImageProcessor()
    
    # Customize settings
    logger.info("\n⚙️  Customizing processor settings...")
    processor.TARGET_WIDTH = 1280
    processor.TARGET_HEIGHT = 960
    processor.TOP_MARGIN_PERCENT = 0.08
    
    logger.info(f"  Target dimensions: {processor.TARGET_WIDTH}x{processor.TARGET_HEIGHT}")
    logger.info(f"  Top margin: {processor.TOP_MARGIN_PERCENT * 100}%")
    
    # Process
    image_bytes = create_sample_chart()
    processed_bytes, metadata = processor.preprocess(image_bytes)
    
    logger.info(f"\n📊 Results with custom settings:")
    logger.info(f"  Final size: {metadata['final_size']}")


def main():
    """Run all demos"""
    logger.info("🚀 Image Preprocessing Pipeline Demo")
    logger.info("="*60)
    
    try:
        demo_validation()
        demo_preprocessing()
        demo_selective_processing()
        demo_aggressive_cropping()
        demo_custom_configuration()
        
        logger.info("\n" + "="*60)
        logger.info("✅ All demos completed successfully!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
