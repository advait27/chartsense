"""
Chartered Main Application

Simple end-to-end chart analysis application.
For MVP: Direct function calls without FastAPI.

Author: Chartered
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.orchestrator import ChartAnalysisOrchestrator, AnalysisResult
from backend.utils.safety import SafeFailureHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class CharteredApp:
    """
    Main Chartered application.
    
    Provides simple interface for chart analysis.
    """
    
    def __init__(self):
        """Initialize application"""
        self.orchestrator = ChartAnalysisOrchestrator(strict_safety=False)
        logger.info("Chartered application initialized")
    
    def analyze_chart_from_file(
        self,
        image_path: str,
        timeframe: Optional[str] = None,
        asset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze chart from image file.
        
        Args:
            image_path: Path to chart image
            timeframe: Optional timeframe (e.g., "4H")
            asset: Optional asset (e.g., "BTC/USD")
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Load image
            logger.info(f"Loading image: {image_path}")
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Analyze
            return self.analyze_chart(image_bytes, timeframe, asset)
            
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            return {
                "success": False,
                "error": f"Image file not found: {image_path}",
                "analysis": None
            }
        except Exception as e:
            logger.error(f"Failed to load image: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to load image: {str(e)}",
                "analysis": None
            }
    
    def analyze_chart(
        self,
        image_bytes: bytes,
        timeframe: Optional[str] = None,
        asset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze chart from image bytes.
        
        Args:
            image_bytes: Raw image bytes
            timeframe: Optional timeframe
            asset: Optional asset
            
        Returns:
            Dictionary with analysis results
        """
        # Build context
        context = {}
        if timeframe:
            context["timeframe"] = timeframe
        if asset:
            context["asset"] = asset
        
        # Run analysis
        logger.info("Starting chart analysis")
        result = self.orchestrator.analyze_chart(image_bytes, context)
        
        # Format response
        if result.success:
            logger.info("Analysis completed successfully")
            return {
                "success": True,
                "analysis": result.analysis,
                "warnings": result.warnings,
                "metadata": result.metadata,
                "error": None
            }
        else:
            logger.error(f"Analysis failed: {result.error_message}")
            
            # Determine appropriate error message
            if "safety" in result.error_message.lower():
                error_display = SafeFailureHandler.get_blocked_message([])
            elif "confidence" in result.error_message.lower():
                error_display = SafeFailureHandler.get_low_confidence_message()
            else:
                error_display = SafeFailureHandler.get_error_message()
            
            return {
                "success": False,
                "analysis": None,
                "warnings": result.warnings,
                "metadata": result.metadata,
                "error": error_display
            }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for CLI usage"""
    print("="*60)
    print("Chartered - AI-Powered Chart Analysis")
    print("="*60)
    
    # Check arguments
    if len(sys.argv) < 2:
        print("\nUsage: python main.py <path_to_chart_image> [timeframe] [asset]")
        print("\nExamples:")
        print("  python main.py chart.png")
        print("  python main.py chart.png 4H")
        print("  python main.py chart.png 4H BTC/USD")
        print("\n")
        return 1
    
    image_path = sys.argv[1]
    timeframe = sys.argv[2] if len(sys.argv) > 2 else None
    asset = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Initialize app
    app = CharteredApp()
    
    # Analyze
    print(f"\n📊 Analyzing: {Path(image_path).name}")
    if timeframe:
        print(f"⏰ Timeframe: {timeframe}")
    if asset:
        print(f"💰 Asset: {asset}")
    print()
    
    result = app.analyze_chart_from_file(image_path, timeframe, asset)
    
    # Display results
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    if result["success"]:
        print("\n✅ Analysis Complete\n")
        
        analysis = result["analysis"]
        
        # Vision summary
        vision = analysis.get("vision", {})
        print("📊 Chart Information:")
        chart_info = vision.get("chart_info", {})
        print(f"  Type: {chart_info.get('type', 'Unknown')}")
        print(f"  Timeframe: {chart_info.get('timeframe', 'Not specified')}")
        
        # Indicators
        indicators = vision.get("indicators", [])
        if indicators:
            print(f"\n  Indicators ({len(indicators)}):")
            for ind in indicators[:3]:
                print(f"    - {ind}")
            if len(indicators) > 3:
                print(f"    ... and {len(indicators) - 3} more")
        
        # Strategy bias
        reasoning = analysis.get("analysis", {})
        bias_data = reasoning.get("strategy_bias", {})
        if bias_data:
            print(f"\n🎯 Strategy Bias:")
            print(f"  {bias_data.get('bias', 'N/A')} (Confidence: {bias_data.get('confidence', 'N/A')})")
        
        # Market regime
        regime = reasoning.get("regime", {})
        if regime:
            print(f"\n📈 Market Regime:")
            print(f"  {regime.get('classification', 'N/A')}")
        
        # Approaches
        approaches = reasoning.get("approaches", {})
        if approaches and approaches.get("options"):
            print(f"\n💡 Suggested Approaches ({len(approaches['options'])}):")
            for approach in approaches["options"][:2]:
                marker = " ⭐" if approach["name"] == approaches.get("recommended") else ""
                print(f"  - {approach['name']}{marker}")
        
        # Warnings
        if result["warnings"]:
            print(f"\n⚠️  Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        
        print("\n💡 Tip: Use the Streamlit frontend for full interactive analysis")
        
    else:
        print("\n❌ Analysis Failed\n")
        print(result["error"])
        
        if result["warnings"]:
            print(f"\n⚠️  Additional Information:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
    
    print("\n" + "="*60)
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
