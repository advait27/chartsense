"""
Chart Analysis Orchestrator

Coordinates the entire analysis pipeline from image upload to final output.

Pipeline Flow:
1. Image Preprocessing (validate, crop, normalize)
2. Vision Analysis (extract chart elements)
3. Reasoning Analysis (interpret elements)
4. Response Building (structure output)
5. Safety Validation (check compliance)

Author: Chartered
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from io import BytesIO
from PIL import Image

from backend.core.image_processor import ImageProcessor, preprocess_chart_image
from backend.core.hf_client import HuggingFaceClient, create_vision_client, create_text_client
from backend.prompts.vision_prompts import build_vision_prompt, build_reasoning_prompt, build_llama_prompt
from backend.core.response_builder import ResponseParser, parse_complete_analysis
from backend.utils.safety import SafetyValidator, SafeFailureHandler, SafetyLevel
from backend.config import (
    VISION_MODEL_ID as VISION_MODEL,
    REASONING_MODEL_ID as REASONING_MODEL,
    VISION_TIMEOUT,
    REASONING_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    HF_API_KEY
)

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of complete chart analysis"""
    success: bool
    analysis: Optional[Dict[str, Any]]
    error_message: Optional[str]
    warnings: list
    metadata: Dict[str, Any]


class ChartAnalysisOrchestrator:
    """
    Orchestrates the complete chart analysis pipeline.
    
    Coordinates:
    - Image preprocessing
    - Vision model analysis
    - Reasoning model analysis
    - Response parsing
    - Safety validation
    """
    
    def __init__(
        self,
        vision_model: str = VISION_MODEL,
        reasoning_model: str = REASONING_MODEL,
        strict_safety: bool = True
    ):
        """
        Initialize orchestrator.
        
        Args:
            vision_model: Vision model ID
            reasoning_model: Reasoning model ID
            strict_safety: Whether to use strict safety mode
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.image_processor = ImageProcessor()
        self.vision_client = create_vision_client(
            api_key=HF_API_KEY,
            model_id=vision_model,
            timeout=VISION_TIMEOUT,
            max_retries=MAX_RETRIES,
            retry_delay=RETRY_DELAY
        )
        self.reasoning_client = create_text_client(
            api_key=HF_API_KEY,
            model_id=reasoning_model,
            timeout=REASONING_TIMEOUT,
            max_retries=MAX_RETRIES,
            retry_delay=RETRY_DELAY
        )
        self.response_parser = ResponseParser()
        self.safety_validator = SafetyValidator(strict_mode=strict_safety)
        
        self.logger.info(f"Orchestrator initialized with vision={vision_model}, reasoning={reasoning_model}")
    
    def analyze_chart(
        self,
        image_bytes: bytes,
        context: Optional[Dict[str, str]] = None
    ) -> AnalysisResult:
        """
        Analyze a trading chart image end-to-end.
        
        Args:
            image_bytes: Raw image bytes
            context: Optional context (timeframe, asset, etc.)
            
        Returns:
            AnalysisResult with success status and data
        """
        context = context or {}
        
        # Sanitize context inputs to prevent injection attacks
        sanitized_context = self._sanitize_context(context)
        
        warnings = []
        metadata = {
            "vision_model": self.vision_client.config.model_id,
            "reasoning_model": self.reasoning_client.config.model_id,
            **sanitized_context
        }
        
        try:
            # Step 1: Preprocess image
            self.logger.info("Step 1/5: Preprocessing image")
            processed_image, preprocessing_metadata = self._preprocess_image(image_bytes)
            metadata.update(preprocessing_metadata)
            
            # Step 2: Vision analysis
            self.logger.info("Step 2/5: Running vision analysis")
            vision_output = self._run_vision_analysis(processed_image, sanitized_context)
            
            # Step 3: Reasoning analysis
            self.logger.info("Step 3/5: Running reasoning analysis")
            reasoning_output = self._run_reasoning_analysis(vision_output)
            
            # Step 4: Parse and structure response
            self.logger.info("Step 4/5: Parsing and structuring response")
            structured_analysis = self._parse_response(vision_output, reasoning_output, metadata)
            
            # Step 5: Safety validation
            self.logger.info("Step 5/5: Validating safety compliance")
            safe_analysis, safety_warnings = self._validate_safety(structured_analysis)
            warnings.extend(safety_warnings)
            
            if safe_analysis is None:
                # Analysis was blocked
                return AnalysisResult(
                    success=False,
                    analysis=None,
                    error_message="Analysis blocked due to safety concerns",
                    warnings=warnings,
                    metadata=metadata
                )
            
            self.logger.info("Analysis completed successfully")
            return AnalysisResult(
                success=True,
                analysis=safe_analysis,
                error_message=None,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return AnalysisResult(
                success=False,
                analysis=None,
                error_message=str(e),
                warnings=warnings,
                metadata=metadata
            )
    
    def _preprocess_image(self, image_bytes: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """
        Preprocess chart image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (processed_image_bytes, metadata)
        """
        try:
            # Process image
            processed_bytes, metadata = preprocess_chart_image(
                image_bytes,
                remove_ui=True,
                normalize=True,
                resize=True
            )
            
            self.logger.info(f"Image preprocessed: {metadata.get('original_size')} -> {metadata.get('final_size')}")
            return processed_bytes, metadata
            
        except Exception as e:
            self.logger.error(f"Image preprocessing failed: {str(e)}")
            raise ValueError(f"Image preprocessing failed: {str(e)}")
    
    def _run_vision_analysis(self, image_bytes: bytes, context: Dict[str, str]) -> str:
        """
        Run vision model analysis.
        
        Args:
            image_bytes: Processed image bytes
            context: Analysis context
            
        Returns:
            Vision model output text
        """
        try:
            # Build vision prompt
            vision_prompt = build_vision_prompt(context)
            
            # Query vision model
            self.logger.info(f"Querying vision model: {self.vision_client.config.model_id}")
            vision_result = self.vision_client.query_vision_model(
                image=image_bytes,
                prompt=vision_prompt
            )
            
            # Ensure we have a string output
            if not isinstance(vision_result, str):
                self.logger.warning(f"Vision model returned non-string type: {type(vision_result)}")
                vision_result = str(vision_result)
            
            self.logger.info(f"Vision analysis complete ({len(vision_result)} chars)")
            return vision_result
            
        except Exception as e:
            self.logger.error(f"Vision analysis failed: {str(e)}")
            raise RuntimeError(f"Vision analysis failed: {str(e)}")
    
    def _run_reasoning_analysis(self, vision_output: str) -> str:
        """
        Run reasoning model analysis.
        
        Args:
            vision_output: Output from vision model
            
        Returns:
            Reasoning model output text
        """
        try:
            # Build reasoning prompt
            reasoning_prompt = build_reasoning_prompt(vision_output)
            
            # Format for specific model if needed
            if "llama" in self.reasoning_client.config.model_id.lower():
                reasoning_prompt = build_llama_prompt(vision_output)
            
            # Query reasoning model
            self.logger.info(f"Querying reasoning model: {self.reasoning_client.config.model_id}")
            reasoning_output = self.reasoning_client.query_text_model(
                prompt=reasoning_prompt
            )
            
            self.logger.info(f"Reasoning analysis complete ({len(reasoning_output)} chars)")
            return reasoning_output
            
        except Exception as e:
            self.logger.error(f"Reasoning analysis failed: {str(e)}")
            raise RuntimeError(f"Reasoning analysis failed: {str(e)}")
    
    def _parse_response(
        self,
        vision_output: str,
        reasoning_output: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse and structure AI outputs.
        
        Args:
            vision_output: Vision model output
            reasoning_output: Reasoning model output
            metadata: Analysis metadata
            
        Returns:
            Structured analysis dictionary
        """
        try:
            # Parse complete analysis
            complete_analysis = parse_complete_analysis(
                vision_output=vision_output,
                reasoning_output=reasoning_output,
                metadata=metadata
            )
            
            # Convert to Streamlit-optimized format
            structured = self.response_parser.to_streamlit_format(complete_analysis)
            
            self.logger.info("Response parsed and structured successfully")
            return structured
            
        except Exception as e:
            self.logger.error(f"Response parsing failed: {str(e)}")
            raise RuntimeError(f"Response parsing failed: {str(e)}")
    
    def _validate_safety(
        self,
        analysis: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], list]:
        """
        Validate analysis for safety compliance.
        
        Args:
            analysis: Structured analysis
            
        Returns:
            Tuple of (safe_analysis or None, warnings)
        """
        try:
            # Extract key text for validation
            reasoning_text = analysis.get("analysis", {})
            
            # Get strategy bias confidence
            confidence = reasoning_text.get("strategy_bias", {}).get("confidence", "Medium")
            
            # Combine all text sections for validation
            text_to_validate = self._extract_text_for_validation(reasoning_text)
            
            # Validate
            result = self.safety_validator.validate_output(
                output=text_to_validate,
                confidence=confidence,
                include_disclaimer=False  # We'll add disclaimer in frontend
            )
            
            if result.level == SafetyLevel.BLOCKED:
                self.logger.warning(f"Analysis blocked: {result.violations}")
                return None, result.warnings
            
            if result.level == SafetyLevel.WARNING:
                self.logger.warning(f"Analysis has warnings: {result.warnings}")
                # Sanitize problematic sections
                analysis = self._sanitize_analysis(analysis)
            
            return analysis, result.warnings
            
        except Exception as e:
            self.logger.error(f"Safety validation failed: {str(e)}")
            # On error, block to be safe
            return None, [f"Safety validation error: {str(e)}"]
    
    def _extract_text_for_validation(self, reasoning: Dict[str, Any]) -> str:
        """Extract all text from reasoning for safety validation"""
        text_parts = []
        
        # Market structure
        if "market_structure" in reasoning:
            text_parts.append(reasoning["market_structure"].get("trend", ""))
        
        # Momentum
        if "momentum" in reasoning:
            text_parts.append(reasoning["momentum"].get("assessment", ""))
        
        # Strategy bias
        if "strategy_bias" in reasoning:
            text_parts.append(reasoning["strategy_bias"].get("bias", ""))
            text_parts.extend(reasoning["strategy_bias"].get("reasoning", []))
        
        # Approaches
        if "approaches" in reasoning:
            for approach in reasoning["approaches"].get("options", []):
                text_parts.append(approach.get("rationale", ""))
        
        return " ".join(text_parts)
    
    def _sanitize_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize analysis text for safety"""
        # For MVP, just return as-is
        # In production, could sanitize specific fields
        return analysis
    
    def _sanitize_context(self, context: Dict[str, str]) -> Dict[str, str]:
        """Sanitize context inputs to prevent injection attacks"""
        sanitized = {}
        
        # Whitelist of allowed context keys
        allowed_keys = {'timeframe', 'asset', 'description'}
        
        for key, value in context.items():
            if key not in allowed_keys:
                self.logger.warning(f"Ignoring unknown context key: {key}")
                continue
            
            if not isinstance(value, str):
                self.logger.warning(f"Converting non-string context value for {key}")
                value = str(value)
            
            # Limit length
            if len(value) > 200:
                self.logger.warning(f"Truncating long context value for {key}")
                value = value[:200]
            
            # Remove potentially dangerous characters
            # Allow alphanumeric, spaces, and common trading symbols
            import re
            value = re.sub(r'[^a-zA-Z0-9\s\-_/.,():]', '', value)
            
            if value.strip():
                sanitized[key] = value.strip()
        
        return sanitized


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def analyze_chart_simple(
    image_bytes: bytes,
    timeframe: Optional[str] = None,
    asset: Optional[str] = None
) -> AnalysisResult:
    """
    Simple function to analyze a chart.
    
    Args:
        image_bytes: Raw image bytes
        timeframe: Optional timeframe (e.g., "4H", "1D")
        asset: Optional asset name (e.g., "BTC/USD")
        
    Returns:
        AnalysisResult
    """
    orchestrator = ChartAnalysisOrchestrator()
    
    context = {}
    if timeframe:
        context["timeframe"] = timeframe
    if asset:
        context["asset"] = asset
    
    return orchestrator.analyze_chart(image_bytes, context)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("Chart Analysis Orchestrator - Demo")
    print("="*60)
    
    # Check if image path provided
    if len(sys.argv) < 2:
        print("\nUsage: python orchestrator.py <path_to_chart_image>")
        print("\nExample:")
        print("  python orchestrator.py sample_chart.png")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    
    if not image_path.exists():
        print(f"\n❌ Error: Image not found: {image_path}")
        sys.exit(1)
    
    print(f"\n📊 Analyzing chart: {image_path.name}")
    
    # Load image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Analyze
    result = analyze_chart_simple(
        image_bytes=image_bytes,
        timeframe="4H",
        asset="BTC/USD"
    )
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    print(f"\n✅ Success: {result.success}")
    
    if result.success:
        print(f"\n📊 Analysis Available:")
        print(f"  - Vision: {len(result.analysis.get('vision', {}))} sections")
        print(f"  - Reasoning: {len(result.analysis.get('analysis', {}))} sections")
        
        # Show strategy bias
        bias_data = result.analysis.get('analysis', {}).get('strategy_bias', {})
        if bias_data:
            print(f"\n🎯 Strategy Bias:")
            print(f"  - Bias: {bias_data.get('bias', 'N/A')}")
            print(f"  - Confidence: {bias_data.get('confidence', 'N/A')}")
        
        # Show warnings
        if result.warnings:
            print(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  - {warning}")
    else:
        print(f"\n❌ Error: {result.error_message}")
        if result.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
    
    print(f"\n📋 Metadata:")
    for key, value in result.metadata.items():
        print(f"  - {key}: {value}")
    
    print("\n" + "="*60)
