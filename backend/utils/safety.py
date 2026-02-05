"""
Safety and Governance Layer for Chartered

This module provides safety guardrails, disclaimer injection, and output validation
to ensure responsible AI usage and legal compliance.

Author: Chartered
Version: 1.0.0
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety check result levels"""
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


class ViolationType(Enum):
    """Types of safety violations"""
    FINANCIAL_ADVICE = "financial_advice"
    TRADE_INSTRUCTION = "trade_instruction"
    PRICE_PREDICTION = "price_prediction"
    GUARANTEED_OUTCOME = "guaranteed_outcome"
    LOW_CONFIDENCE = "low_confidence"
    MISSING_DISCLAIMER = "missing_disclaimer"


@dataclass
class SafetyCheckResult:
    """Result of safety validation"""
    level: SafetyLevel
    violations: List[ViolationType]
    warnings: List[str]
    modified_output: Optional[str]
    confidence_score: float


# ============================================================================
# DISCLAIMER TEXT
# ============================================================================

MANDATORY_DISCLAIMER = """
⚠️ **IMPORTANT DISCLAIMER**

This analysis is for **educational and informational purposes only**. It is NOT financial advice, investment advice, or a recommendation to buy, sell, or hold any asset.

**Key Points:**
- This is a decision-support tool, not a trading system
- No predictions or guarantees are made about future price movements
- Past patterns do not guarantee future results
- Trading involves substantial risk of loss
- Always conduct your own research and consult with qualified financial professionals
- The creators of this tool are not responsible for any trading decisions or losses

**By using this tool, you acknowledge that:**
- You understand the risks involved in trading
- You will not rely solely on this analysis for trading decisions
- You take full responsibility for your own trading actions
"""

SHORT_DISCLAIMER = """
⚠️ **Educational purposes only. Not financial advice. Trading involves substantial risk.**
"""

FOOTER_DISCLAIMER = """
---
*This analysis is provided for educational purposes only and should not be considered financial advice. Always do your own research and consult with qualified professionals before making trading decisions.*
"""


# ============================================================================
# PROHIBITED PATTERNS
# ============================================================================

# Patterns that indicate financial advice
FINANCIAL_ADVICE_PATTERNS = [
    r'\b(?:you should|I recommend|I suggest|I advise)\s+(?:buy|sell|short|long|enter|exit)',
    r'\b(?:buy|sell|short|long)\s+(?:now|immediately|at|here)',
    r'\bI\s+(?:recommend|suggest|advise)\s+(?:buying|selling|shorting)',
    r'\b(?:this is|it\'s)\s+a\s+(?:buy|sell)\b',
]

# Patterns that indicate trade instructions
TRADE_INSTRUCTION_PATTERNS = [
    r'\b(?:enter|exit|buy|sell|short|long)\s+at\s+[\$\d]',
    r'\bstop\s+loss\s+at\s+[\$\d]',
    r'\btake\s+profit\s+at\s+[\$\d]',
    r'\bposition\s+size:?\s+\d+',
    r'\brisk\s+[\$\d]+\s+to\s+make\s+[\$\d]',
    r'\btarget:?\s+[\$\d]',
]

# Patterns that indicate price predictions
PRICE_PREDICTION_PATTERNS = [
    r'\bwill\s+(?:reach|hit|go to|move to)\s+[\$\d]',
    r'\bprice\s+will\s+(?:be|reach|hit)',
    r'\b(?:going|heading)\s+to\s+[\$\d]',
    r'\bexpect\s+(?:price|it)\s+to\s+(?:reach|hit|be)',
    r'\b(?:definitely|certainly|guaranteed)\s+(?:will|going to)',
]

# Patterns that indicate guaranteed outcomes
GUARANTEED_OUTCOME_PATTERNS = [
    r'\b(?:guaranteed|certain|definitely|100%|sure thing)',
    r'\b(?:will definitely|will certainly|must|cannot fail)',
    r'\b(?:always|never)\s+(?:works|fails|happens)',
    r'\bno\s+risk\b',
    r'\brisk-free\b',
]

# Required probabilistic language
REQUIRED_PROBABILISTIC_TERMS = [
    'may', 'might', 'could', 'suggests', 'indicates', 'appears',
    'typically', 'often', 'sometimes', 'potentially', 'possible'
]


# ============================================================================
# SAFETY VALIDATOR
# ============================================================================

class SafetyValidator:
    """
    Validates AI outputs for safety and compliance.
    
    Checks for:
    - Financial advice language
    - Trade instructions
    - Price predictions
    - Guaranteed outcomes
    - Confidence levels
    - Disclaimer presence
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize safety validator.
        
        Args:
            strict_mode: If True, blocks outputs with violations. If False, only warns.
        """
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
    
    def validate_output(
        self,
        output: str,
        confidence: Optional[str] = None,
        include_disclaimer: bool = True
    ) -> SafetyCheckResult:
        """
        Validate AI output for safety compliance.
        
        Args:
            output: AI-generated text to validate
            confidence: Confidence level (High/Medium/Low)
            include_disclaimer: Whether to inject disclaimer
            
        Returns:
            SafetyCheckResult with validation results
        """
        violations = []
        warnings = []
        modified_output = output
        
        # Check for financial advice
        if self._contains_financial_advice(output):
            violations.append(ViolationType.FINANCIAL_ADVICE)
            warnings.append("Output contains language that may be interpreted as financial advice")
        
        # Check for trade instructions
        if self._contains_trade_instructions(output):
            violations.append(ViolationType.TRADE_INSTRUCTION)
            warnings.append("Output contains specific trade instructions")
        
        # Check for price predictions
        if self._contains_price_predictions(output):
            violations.append(ViolationType.PRICE_PREDICTION)
            warnings.append("Output contains price predictions")
        
        # Check for guaranteed outcomes
        if self._contains_guaranteed_outcomes(output):
            violations.append(ViolationType.GUARANTEED_OUTCOME)
            warnings.append("Output contains language suggesting guaranteed outcomes")
        
        # Check confidence level
        confidence_score = self._assess_confidence(output, confidence)
        if confidence_score < 0.3:
            violations.append(ViolationType.LOW_CONFIDENCE)
            warnings.append("Analysis confidence is too low for safe display")
        
        # Check for disclaimer
        if include_disclaimer and not self._has_disclaimer(output):
            violations.append(ViolationType.MISSING_DISCLAIMER)
            modified_output = self._inject_disclaimer(output)
        
        # Determine safety level
        if violations and self.strict_mode:
            # In strict mode, only block on critical violations, not low confidence
            if any(v in violations for v in [
                ViolationType.FINANCIAL_ADVICE,
                ViolationType.TRADE_INSTRUCTION,
                ViolationType.GUARANTEED_OUTCOME
            ]):
                level = SafetyLevel.BLOCKED
            else:
                level = SafetyLevel.WARNING
        elif violations:
            level = SafetyLevel.WARNING
        else:
            level = SafetyLevel.SAFE
        
        return SafetyCheckResult(
            level=level,
            violations=violations,
            warnings=warnings,
            modified_output=modified_output,
            confidence_score=confidence_score
        )
    
    def _contains_financial_advice(self, text: str) -> bool:
        """Check if text contains financial advice language"""
        for pattern in FINANCIAL_ADVICE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                self.logger.warning(f"Financial advice pattern detected: {pattern}")
                return True
        return False
    
    def _contains_trade_instructions(self, text: str) -> bool:
        """Check if text contains specific trade instructions"""
        for pattern in TRADE_INSTRUCTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                self.logger.warning(f"Trade instruction pattern detected: {pattern}")
                return True
        return False
    
    def _contains_price_predictions(self, text: str) -> bool:
        """Check if text contains price predictions"""
        for pattern in PRICE_PREDICTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                self.logger.warning(f"Price prediction pattern detected: {pattern}")
                return True
        return False
    
    def _contains_guaranteed_outcomes(self, text: str) -> bool:
        """Check if text contains guaranteed outcome language"""
        for pattern in GUARANTEED_OUTCOME_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                self.logger.warning(f"Guaranteed outcome pattern detected: {pattern}")
                return True
        return False
    
    def _assess_confidence(self, text: str, confidence: Optional[str]) -> float:
        """
        Assess confidence level of analysis.
        
        Returns score from 0.0 to 1.0
        """
        # Start with base score from explicit confidence level
        if confidence:
            confidence_lower = confidence.lower()
            if 'high' in confidence_lower:
                base_score = 0.8
            elif 'medium' in confidence_lower:
                base_score = 0.5
            elif 'low' in confidence_lower:
                base_score = 0.2
            else:
                base_score = 0.5
        else:
            base_score = 0.5
        
        # Check for probabilistic language (increases confidence in safety)
        probabilistic_count = sum(
            1 for term in REQUIRED_PROBABILISTIC_TERMS
            if term in text.lower()
        )
        
        # Adjust score based on probabilistic language
        if probabilistic_count >= 3:
            base_score = min(1.0, base_score + 0.2)
        elif probabilistic_count == 0:
            base_score = max(0.0, base_score - 0.3)
        
        return base_score
    
    def _has_disclaimer(self, text: str) -> bool:
        """Check if text already contains a disclaimer"""
        disclaimer_indicators = [
            'disclaimer',
            'not financial advice',
            'educational purposes only',
            'not investment advice'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in disclaimer_indicators)
    
    def _inject_disclaimer(self, text: str, position: str = 'top') -> str:
        """
        Inject disclaimer into text.
        
        Args:
            text: Original text
            position: 'top', 'bottom', or 'both'
            
        Returns:
            Text with disclaimer injected
        """
        if position == 'top':
            return f"{SHORT_DISCLAIMER}\n\n{text}\n\n{FOOTER_DISCLAIMER}"
        elif position == 'bottom':
            return f"{text}\n\n{MANDATORY_DISCLAIMER}"
        else:  # both
            return f"{SHORT_DISCLAIMER}\n\n{text}\n\n{MANDATORY_DISCLAIMER}"
    
    def sanitize_output(self, text: str) -> str:
        """
        Sanitize output by replacing prohibited language.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        sanitized = text
        
        # Replace "will" with "may"
        sanitized = re.sub(r'\bwill\b', 'may', sanitized, flags=re.IGNORECASE)
        
        # Replace "should" with "could"
        sanitized = re.sub(r'\bshould\b', 'could', sanitized, flags=re.IGNORECASE)
        
        # Replace "definitely" with "potentially"
        sanitized = re.sub(r'\bdefinitely\b', 'potentially', sanitized, flags=re.IGNORECASE)
        
        # Replace "guaranteed" with "possible"
        sanitized = re.sub(r'\bguaranteed\b', 'possible', sanitized, flags=re.IGNORECASE)
        
        self.logger.info("Output sanitized for safety compliance")
        return sanitized


# ============================================================================
# SAFE FAILURE HANDLER
# ============================================================================

class SafeFailureHandler:
    """
    Handles safe failure scenarios when AI confidence is low or errors occur.
    """
    
    @staticmethod
    def get_low_confidence_message() -> str:
        """Return message for low confidence scenarios"""
        return """
## Analysis Unavailable

The AI analysis for this chart did not meet our confidence threshold for safe display.

**Possible Reasons:**
- Chart image quality is insufficient
- Indicators or patterns are unclear
- Conflicting signals make analysis unreliable
- Timeframe or context is ambiguous

**What You Can Do:**
1. Try uploading a clearer chart image
2. Ensure all indicators are visible
3. Provide additional context (timeframe, asset)
4. Try a different chart or timeframe

**Remember:** Even when analysis is available, it should only be used as one input among many in your decision-making process. Always conduct thorough research and consult with qualified professionals.
"""
    
    @staticmethod
    def get_error_message() -> str:
        """Return message for error scenarios"""
        return """
## Analysis Error

We encountered an error while analyzing this chart. Please try again.

**If the problem persists:**
- Check that your image is a valid PNG or JPG file
- Ensure the image is a trading chart screenshot
- Verify the file size is under 5MB
- Try a different chart image

**Note:** This tool is for educational purposes only and should not be relied upon for trading decisions.
"""
    
    @staticmethod
    def get_blocked_message(violations: List[ViolationType]) -> str:
        """Return message when output is blocked due to violations"""
        violation_names = [v.value.replace('_', ' ').title() for v in violations]
        
        return f"""
## Analysis Blocked

The AI-generated analysis was blocked due to safety concerns.

**Detected Issues:**
{chr(10).join(f'- {v}' for v in violation_names)}

**Why This Happens:**
Our safety system detected language that could be misinterpreted as financial advice, trade instructions, or guaranteed predictions. We block such outputs to ensure responsible AI usage.

**What This Means:**
- The AI model generated content that doesn't meet our safety standards
- This is a protective measure, not an error
- You can try analyzing a different chart

**Remember:** Chartered is an educational tool for learning technical analysis concepts, not a trading system or financial advisor.
"""


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_and_sanitize(
    output: str,
    confidence: Optional[str] = None,
    strict_mode: bool = True
) -> Tuple[bool, str, List[str]]:
    """
    Validate and sanitize AI output.
    
    Args:
        output: AI-generated text
        confidence: Confidence level
        strict_mode: Whether to use strict validation
        
    Returns:
        Tuple of (is_safe, sanitized_output, warnings)
    """
    validator = SafetyValidator(strict_mode=strict_mode)
    result = validator.validate_output(output, confidence)
    
    if result.level == SafetyLevel.BLOCKED:
        return False, SafeFailureHandler.get_blocked_message(result.violations), result.warnings
    
    # Sanitize if warnings present
    if result.warnings:
        sanitized = validator.sanitize_output(result.modified_output or output)
        return True, sanitized, result.warnings
    
    return True, result.modified_output or output, []


def inject_disclaimer(text: str, position: str = 'both') -> str:
    """
    Inject disclaimer into text.
    
    Args:
        text: Original text
        position: 'top', 'bottom', or 'both'
        
    Returns:
        Text with disclaimer
    """
    validator = SafetyValidator()
    return validator._inject_disclaimer(text, position)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example 1: Safe output
    print("="*60)
    print("EXAMPLE 1: Safe Output")
    print("="*60)
    
    safe_output = """
    The chart suggests a bullish trend with price above key moving averages.
    RSI indicates momentum may be slowing. Traders might consider waiting
    for a pullback to support before taking action.
    """
    
    is_safe, result, warnings = validate_and_sanitize(safe_output, confidence="Medium")
    print(f"Safe: {is_safe}")
    print(f"Warnings: {warnings}")
    print(f"\nOutput:\n{result[:200]}...")
    
    # Example 2: Unsafe output (financial advice)
    print("\n" + "="*60)
    print("EXAMPLE 2: Unsafe Output (Blocked)")
    print("="*60)
    
    unsafe_output = """
    You should buy now at $50,000. Set stop loss at $48,000 and
    take profit at $55,000. This will definitely work.
    """
    
    is_safe, result, warnings = validate_and_sanitize(unsafe_output, confidence="High")
    print(f"Safe: {is_safe}")
    print(f"Warnings: {warnings}")
    print(f"\nOutput:\n{result[:200]}...")
    
    # Example 3: Low confidence
    print("\n" + "="*60)
    print("EXAMPLE 3: Low Confidence")
    print("="*60)
    
    low_conf_output = "The chart is unclear."
    
    is_safe, result, warnings = validate_and_sanitize(low_conf_output, confidence="Low")
    print(f"Safe: {is_safe}")
    print(f"Warnings: {warnings}")
    print(f"\nOutput:\n{result[:200]}...")
