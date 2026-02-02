"""
Unit Tests for Safety Validator

Tests safety checks, disclaimer injection, and output sanitization.
"""

import pytest
from backend.utils.safety import (
    SafetyValidator,
    SafeFailureHandler,
    SafetyLevel,
    ViolationType,
    validate_and_sanitize,
    inject_disclaimer,
    MANDATORY_DISCLAIMER,
    SHORT_DISCLAIMER
)


class TestSafetyValidator:
    """Test suite for SafetyValidator"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return SafetyValidator(strict_mode=True)
    
    def test_safe_output(self, validator):
        """Test that safe output passes validation"""
        safe_text = """
        The chart suggests a bullish trend with price above moving averages.
        RSI indicates momentum may be slowing. Traders might consider waiting
        for confirmation before taking action.
        """
        
        result = validator.validate_output(safe_text, confidence="Medium")
        
        assert result.level in [SafetyLevel.SAFE, SafetyLevel.WARNING]
        assert ViolationType.FINANCIAL_ADVICE not in result.violations
        assert ViolationType.TRADE_INSTRUCTION not in result.violations
    
    def test_financial_advice_detection(self, validator):
        """Test detection of financial advice"""
        advice_text = "You should buy this stock now"
        
        result = validator.validate_output(advice_text, confidence="High")
        
        assert ViolationType.FINANCIAL_ADVICE in result.violations
        assert result.level == SafetyLevel.BLOCKED
    
    def test_trade_instruction_detection(self, validator):
        """Test detection of trade instructions"""
        instruction_text = "Enter at $50,000 with stop loss at $48,000"
        
        result = validator.validate_output(instruction_text, confidence="High")
        
        assert ViolationType.TRADE_INSTRUCTION in result.violations
        assert result.level == SafetyLevel.BLOCKED
    
    def test_price_prediction_detection(self, validator):
        """Test detection of price predictions"""
        prediction_text = "Price will reach $60,000 by next week"
        
        result = validator.validate_output(prediction_text, confidence="High")
        
        assert ViolationType.PRICE_PREDICTION in result.violations
    
    def test_guaranteed_outcome_detection(self, validator):
        """Test detection of guaranteed outcomes"""
        guarantee_text = "This setup is guaranteed to work 100%"
        
        result = validator.validate_output(guarantee_text, confidence="High")
        
        assert ViolationType.GUARANTEED_OUTCOME in result.violations
        assert result.level == SafetyLevel.BLOCKED
    
    def test_low_confidence_blocking(self, validator):
        """Test that low confidence outputs are blocked"""
        low_conf_text = "The chart is unclear"
        
        result = validator.validate_output(low_conf_text, confidence="Low")
        
        assert ViolationType.LOW_CONFIDENCE in result.violations
        assert result.level == SafetyLevel.BLOCKED
    
    def test_disclaimer_injection(self, validator):
        """Test that disclaimer is injected when missing"""
        text_without_disclaimer = "This is a chart analysis"
        
        result = validator.validate_output(text_without_disclaimer, confidence="Medium")
        
        assert result.modified_output is not None
        assert "disclaimer" in result.modified_output.lower() or "not financial advice" in result.modified_output.lower()
    
    def test_existing_disclaimer_detection(self, validator):
        """Test that existing disclaimers are detected"""
        text_with_disclaimer = """
        This is for educational purposes only. Not financial advice.
        The chart shows an uptrend.
        """
        
        has_disclaimer = validator._has_disclaimer(text_with_disclaimer)
        assert has_disclaimer is True
    
    def test_confidence_assessment_high(self, validator):
        """Test confidence assessment for high confidence"""
        text = "The chart suggests upward momentum. This may indicate bullish sentiment."
        
        score = validator._assess_confidence(text, "High")
        
        assert score >= 0.8
    
    def test_confidence_assessment_low(self, validator):
        """Test confidence assessment for low confidence"""
        text = "The chart shows something"
        
        score = validator._assess_confidence(text, "Low")
        
        assert score < 0.5
    
    def test_sanitize_output(self, validator):
        """Test output sanitization"""
        unsafe_text = "Price will definitely break resistance"
        
        sanitized = validator.sanitize_output(unsafe_text)
        
        assert "will" not in sanitized.lower() or "may" in sanitized.lower()
        assert "definitely" not in sanitized.lower()
    
    def test_non_strict_mode(self):
        """Test non-strict mode allows warnings"""
        validator = SafetyValidator(strict_mode=False)
        
        advice_text = "You should consider buying"
        result = validator.validate_output(advice_text, confidence="Medium")
        
        # Should warn but not block in non-strict mode
        assert result.level == SafetyLevel.WARNING
        assert len(result.warnings) > 0


class TestSafeFailureHandler:
    """Test suite for SafeFailureHandler"""
    
    def test_low_confidence_message(self):
        """Test low confidence message generation"""
        message = SafeFailureHandler.get_low_confidence_message()
        
        assert "Analysis Unavailable" in message
        assert "confidence threshold" in message.lower()
    
    def test_error_message(self):
        """Test error message generation"""
        message = SafeFailureHandler.get_error_message()
        
        assert "Error" in message
        assert "try again" in message.lower()
    
    def test_blocked_message(self):
        """Test blocked message generation"""
        violations = [ViolationType.FINANCIAL_ADVICE, ViolationType.TRADE_INSTRUCTION]
        message = SafeFailureHandler.get_blocked_message(violations)
        
        assert "Blocked" in message
        assert "Financial Advice" in message
        assert "Trade Instruction" in message


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_validate_and_sanitize_safe(self):
        """Test validate_and_sanitize with safe output"""
        safe_text = "The chart suggests a potential uptrend. Traders might consider this."
        
        is_safe, output, warnings = validate_and_sanitize(safe_text, confidence="Medium")
        
        assert is_safe is True
        assert len(output) > 0
    
    def test_validate_and_sanitize_unsafe(self):
        """Test validate_and_sanitize with unsafe output"""
        unsafe_text = "You should buy now at $50,000. Guaranteed profit."
        
        is_safe, output, warnings = validate_and_sanitize(unsafe_text, confidence="High")
        
        assert is_safe is False
        assert "Blocked" in output
        assert len(warnings) > 0
    
    def test_inject_disclaimer_top(self):
        """Test disclaimer injection at top"""
        text = "This is analysis text"
        
        result = inject_disclaimer(text, position='top')
        
        assert SHORT_DISCLAIMER in result
        assert text in result
    
    def test_inject_disclaimer_both(self):
        """Test disclaimer injection at both positions"""
        text = "This is analysis text"
        
        result = inject_disclaimer(text, position='both')
        
        assert SHORT_DISCLAIMER in result
        assert MANDATORY_DISCLAIMER in result
        assert text in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
