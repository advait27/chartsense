"""
Response Builder and Parser

This module converts raw AI model outputs into structured, dashboard-ready format.
Handles parsing, cleaning, and formatting for frontend consumption.

Author: ChartSense
Version: 1.0.0
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StrategyBias(Enum):
    """Strategy bias classification"""
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"
    NEUTRAL_BULLISH = "Neutral to Bullish"
    NEUTRAL_BEARISH = "Neutral to Bearish"


class ConfidenceLevel(Enum):
    """Confidence level classification"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class MarketRegime(Enum):
    """Market regime classification"""
    TRENDING_BULLISH = "Trending (Bullish)"
    TRENDING_BEARISH = "Trending (Bearish)"
    RANGING = "Ranging"
    BREAKOUT = "Breakout"
    INDECISIVE = "Indecisive"


@dataclass
class VisionAnalysis:
    """Structured vision model output"""
    chart_type: str
    timeframe: Optional[str]
    price_structure: str
    indicators_detected: List[str]
    visual_patterns: List[str]
    momentum_signals: str
    raw_output: str


@dataclass
class MarketStructure:
    """Market structure assessment"""
    trend_description: str
    key_levels: List[str]
    structural_notes: List[str]


@dataclass
class MomentumAnalysis:
    """Momentum analysis"""
    assessment: str
    indicators: List[str]
    divergences: List[str]
    strength: str


@dataclass
class RegimeClassification:
    """Market regime classification"""
    regime: str
    reasoning: str
    volatility: str


@dataclass
class StrategyBiasAnalysis:
    """Strategy bias assessment"""
    bias: str
    confidence: str
    reasoning: List[str]


@dataclass
class SuitableApproaches:
    """Suitable trading approaches"""
    approaches: List[Dict[str, str]]  # [{"name": "...", "rationale": "..."}]
    recommended: Optional[str]


@dataclass
class InvalidationConditions:
    """Invalidation scenarios"""
    bullish_invalidation: List[str]
    bearish_invalidation: List[str]
    key_levels: List[str]


@dataclass
class RiskConsiderations:
    """Risk and uncertainty assessment"""
    risks: List[str]
    conflicting_signals: List[str]
    monitoring_points: List[str]
    uncertainty_note: str


@dataclass
class ReasoningAnalysis:
    """Complete structured reasoning output"""
    market_structure: MarketStructure
    momentum: MomentumAnalysis
    regime: RegimeClassification
    strategy_bias: StrategyBiasAnalysis
    suitable_approaches: SuitableApproaches
    invalidation: InvalidationConditions
    risks: RiskConsiderations
    raw_output: str


@dataclass
class CompleteAnalysis:
    """Complete analysis combining vision and reasoning"""
    vision: VisionAnalysis
    reasoning: ReasoningAnalysis
    metadata: Dict[str, Any]


class ResponseParser:
    """
    Parser for AI model outputs.
    
    Converts raw text into structured data suitable for dashboard display.
    Handles missing sections gracefully and cleans verbose language.
    """
    
    # Section headers to look for
    SECTION_PATTERNS = {
        'market_structure': r'(?:###?\s*)?(?:1\.?\s*)?Market Structure(?:\s+Assessment)?',
        'momentum': r'(?:###?\s*)?(?:2\.?\s*)?Momentum(?:\s+Analysis)?',
        'regime': r'(?:###?\s*)?(?:3\.?\s*)?Market Regime(?:\s+Classification)?',
        'strategy_bias': r'(?:###?\s*)?(?:4\.?\s*)?Strategy Bias',
        'approaches': r'(?:###?\s*)?(?:5\.?\s*)?Suitable Approaches?',
        'invalidation': r'(?:###?\s*)?(?:6\.?\s*)?Invalidation(?:\s+Conditions)?',
        'risks': r'(?:###?\s*)?(?:7\.?\s*)?Risk(?:\s+Considerations)?',
    }
    
    def __init__(self):
        """Initialize the parser"""
        self.logger = logging.getLogger(__name__)
    
    def parse_vision_output(self, raw_output: str) -> VisionAnalysis:
        """
        Parse vision model output into structured format.
        
        Args:
            raw_output: Raw text from vision model
            
        Returns:
            VisionAnalysis object
        """
        try:
            # Extract chart type and timeframe
            chart_type_line = self._extract_field(raw_output, r'Chart Type:?\s*(.+?)(?:\n|$)')
            
            # Try to extract timeframe from chart type line or separate field
            timeframe = None
            if chart_type_line and ',' in chart_type_line:
                parts = chart_type_line.split(',', 1)
                chart_type = parts[0].strip()
                timeframe = parts[1].strip()
            else:
                chart_type = chart_type_line
                timeframe = self._extract_field(raw_output, r'(?:Timeframe|Time frame):?\s*(.+?)(?:\n|$)')
            
            # Extract price structure
            price_structure = self._extract_section(raw_output, 'Price Structure')
            
            # Extract indicators
            indicators_section = self._extract_section(raw_output, 'Technical Indicators')
            indicators_detected = self._extract_list_items(indicators_section)
            
            # Extract visual patterns
            patterns_section = self._extract_section(raw_output, 'Visual Patterns')
            visual_patterns = self._extract_list_items(patterns_section)
            
            # Extract momentum signals
            momentum_signals = self._extract_section(raw_output, 'Momentum Signals')
            
            return VisionAnalysis(
                chart_type=chart_type or "Unknown",
                timeframe=timeframe,
                price_structure=price_structure or "Not available",
                indicators_detected=indicators_detected,
                visual_patterns=visual_patterns,
                momentum_signals=momentum_signals or "Not available",
                raw_output=raw_output
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing vision output: {e}")
            # Return minimal valid structure
            return VisionAnalysis(
                chart_type="Unknown",
                timeframe=None,
                price_structure="Parsing error",
                indicators_detected=[],
                visual_patterns=[],
                momentum_signals="Parsing error",
                raw_output=raw_output
            )
    
    def parse_reasoning_output(self, raw_output: str) -> ReasoningAnalysis:
        """
        Parse reasoning model output into structured format.
        
        Args:
            raw_output: Raw text from reasoning model
            
        Returns:
            ReasoningAnalysis object
        """
        try:
            # Parse each section
            market_structure = self._parse_market_structure(raw_output)
            momentum = self._parse_momentum(raw_output)
            regime = self._parse_regime(raw_output)
            strategy_bias = self._parse_strategy_bias(raw_output)
            approaches = self._parse_approaches(raw_output)
            invalidation = self._parse_invalidation(raw_output)
            risks = self._parse_risks(raw_output)
            
            return ReasoningAnalysis(
                market_structure=market_structure,
                momentum=momentum,
                regime=regime,
                strategy_bias=strategy_bias,
                suitable_approaches=approaches,
                invalidation=invalidation,
                risks=risks,
                raw_output=raw_output
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing reasoning output: {e}")
            # Return minimal valid structure
            return self._get_fallback_reasoning(raw_output)
    
    def _parse_market_structure(self, text: str) -> MarketStructure:
        """Parse market structure section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['market_structure'])
        
        if not section:
            return MarketStructure(
                trend_description="Not available",
                key_levels=["Not specified"],
                structural_notes=[]
            )
        
        # Clean the section - remove excessive bullet fragments
        section = re.sub(r'\n•\s+', '\n', section)
        
        # Just use the full section as trend description
        # Extract only explicit "Key Levels:" or "Support/Resistance:" subsections
        key_levels = []
        if 'key level' in section.lower() or 'support' in section.lower() or 'resistance' in section.lower():
            level_matches = re.findall(r'(?:around|near|at)\s+(\d+\.?\d*)', section, re.IGNORECASE)
            key_levels = [f"Level: {level}" for level in level_matches[:5]]
        
        return MarketStructure(
            trend_description=section.strip(),
            key_levels=key_levels if key_levels else ["See description above"],
            structural_notes=[]
        )
    
    def _parse_momentum(self, text: str) -> MomentumAnalysis:
        """Parse momentum analysis section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['momentum'])
        
        if not section:
            return MomentumAnalysis(
                assessment="Not available",
                indicators=["Not specified"],
                divergences=[],
                strength="Mixed"
            )
        
        # Clean the section
        section = re.sub(r'\n•\s+', '\n', section)
        
        # Determine strength from keywords
        strength = "Mixed"
        if "strong" in section.lower() and "bearish" in section.lower():
            strength = "Strong Bearish"
        elif "strong" in section.lower() and "bullish" in section.lower():
            strength = "Strong Bullish"
        elif "weak" in section.lower():
            strength = "Weak"
        
        return MomentumAnalysis(
            assessment=section.strip(),
            indicators=["See description above"],
            divergences=[],
            strength=strength
        )
    
    def _parse_regime(self, text: str) -> RegimeClassification:
        """Parse market regime section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['regime'])
        
        if not section:
            return RegimeClassification(
                regime="Indecisive",
                reasoning="Not available",
                volatility="Moderate"
            )
        
        # Clean the section
        section = re.sub(r'\n•\s+', '\n', section)
        
        # Extract regime classification
        regime = "Indecisive"
        for keyword in ["Trending Bearish", "Trending Bullish", "Ranging", "Breakout", "Indecisive"]:
            if keyword.lower() in section.lower():
                regime = keyword
                break
        
        # Extract volatility if mentioned
        volatility = "Moderate"
        volatility_match = re.search(r'volatility.*?(high|low|moderate)', section, re.IGNORECASE)
        if volatility_match:
            volatility = volatility_match.group(1).capitalize()
        
        return RegimeClassification(
            regime=regime,
            reasoning=section.strip(),
            volatility=volatility
        )
    
    def _parse_strategy_bias(self, text: str) -> StrategyBiasAnalysis:
        """Parse strategy bias section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['strategy_bias'])
        
        if not section:
            return StrategyBiasAnalysis(
                bias="Neutral",
                confidence="Medium",
                reasoning=["Not specified"]
            )
        
        # Clean the section
        section = re.sub(r'\n•\s+', '\n', section)
        
        # Extract bias
        bias = "Neutral"
        for keyword in ["Bullish", "Bearish", "Neutral"]:
            if keyword.lower() in section.lower():
                bias = keyword
                break
        
        # Extract confidence
        confidence = "Medium"
        confidence_match = re.search(r'confidence.*?(high|medium|low)', section, re.IGNORECASE)
        if confidence_match:
            confidence = confidence_match.group(1).capitalize()
        
        # Extract bullet points as reasoning
        reasoning_points = re.findall(r'[-•]\s+(.+?)(?:\n|$)', section)
        if not reasoning_points:
            reasoning_points = [section.strip()]
        
        return StrategyBiasAnalysis(
            bias=bias,
            confidence=confidence,
            reasoning=reasoning_points[:5]
        )
    
    def _parse_approaches(self, text: str) -> SuitableApproaches:
        """Parse suitable approaches section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['approaches'])
        
        approaches = []
        recommended = None
        
        # Look for approach patterns
        approach_patterns = [
            r'(?:##\s*)?([A-Z]\.)\s*(.+?)\s+Approach',
            r'[-•]\s*\*\*(.+?)\*\*'
        ]
        
        for pattern in approach_patterns:
            matches = re.finditer(pattern, section, re.MULTILINE)
            for match in matches:
                name = match.group(1) if len(match.groups()) > 1 else match.group(1)
                # Extract rationale (next few lines)
                start = match.end()
                end = min(start + 200, len(section))
                rationale_text = section[start:end]
                rationale = self._extract_field(rationale_text, r'(?:Rationale|Suitable if):?\s*(.+?)(?:\n|$)')
                
                approaches.append({
                    "name": name.strip(),
                    "rationale": rationale or "See details"
                })
                
                # Check if recommended
                if "recommended" in section[max(0, start-50):start+50].lower():
                    recommended = name.strip()
        
        return SuitableApproaches(
            approaches=approaches if approaches else [{"name": "Wait-and-see", "rationale": "Default approach"}],
            recommended=recommended
        )
    
    def _parse_invalidation(self, text: str) -> InvalidationConditions:
        """Parse invalidation conditions section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['invalidation'])
        
        if not section:
            return InvalidationConditions(
                bullish_invalidation=["Not specified"],
                bearish_invalidation=["Not specified"],
                key_levels=["Not specified"]
            )
        
        # Extract bullish invalidation - look for "Bullish" line
        bullish_invalidation = []
        bullish_match = re.search(r'bullish.*?(?:invalidated|scenario).*?if:?\s*(.+?)(?=\n-|\nbearish|key|$)', section, re.IGNORECASE | re.DOTALL)
        if bullish_match:
            bullish_text = bullish_match.group(1).strip()
            bullish_invalidation = [bullish_text] if bullish_text else []
        
        # Extract bearish invalidation
        bearish_invalidation = []
        bearish_match = re.search(r'bearish.*?(?:invalidated|scenario).*?if:?\s*(.+?)(?=\n-|\nkey|$)', section, re.IGNORECASE | re.DOTALL)
        if bearish_match:
            bearish_text = bearish_match.group(1).strip()
            bearish_invalidation = [bearish_text] if bearish_text else []
        
        # Extract key decision levels
        key_levels = []
        key_match = re.search(r'key.*?(?:decision|level).*?:?\s*(.+?)$', section, re.IGNORECASE | re.DOTALL)
        if key_match:
            key_text = key_match.group(1).strip()
            key_levels = [key_text] if key_text else []
        
        return InvalidationConditions(
            bullish_invalidation=bullish_invalidation if bullish_invalidation else ["Not specified"],
            bearish_invalidation=bearish_invalidation if bearish_invalidation else ["Not specified"],
            key_levels=key_levels if key_levels else ["Not specified"]
        )
    
    def _parse_risks(self, text: str) -> RiskConsiderations:
        """Parse risk considerations section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['risks'])
        
        # Extract risks
        risks = self._extract_list_items(section, patterns=[
            r'(?:Risk|Potential Risk):?\s*(.+?)(?:\n|$)'
        ])
        
        # Extract conflicting signals
        conflicting = self._extract_list_items(section, patterns=[
            r'(?:Conflict|Conflicting):?\s*(.+?)(?:\n|$)'
        ])
        
        # Extract monitoring points
        monitoring = self._extract_list_items(section, patterns=[
            r'(?:Monitor|Watch|What to monitor):?\s*(.+?)(?:\n|$)'
        ])
        
        # Extract uncertainty note
        uncertainty = self._extract_field(section, r'(?:Uncertainty|Acknowledgment):?\s*(.+?)(?:\n|$)')
        
        return RiskConsiderations(
            risks=risks[:5] if risks else ["Standard market risks apply"],
            conflicting_signals=conflicting[:3] if conflicting else [],
            monitoring_points=monitoring[:5] if monitoring else ["Price action", "Volume"],
            uncertainty_note=uncertainty or "Markets are inherently uncertain"
        )
    
    # Helper methods
    
    def _extract_section(self, text: str, header: str) -> str:
        """Extract section by header name"""
        pattern = rf'{header}:?\s*\n(.+?)(?=\n\n|\n[A-Z]|\Z)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_section_by_pattern(self, text: str, pattern: str) -> str:
        """Extract section by regex pattern - looks for next ### header or end of text"""
        # Match section header and capture until next ### header
        match = re.search(pattern + r':?\s*\n(.+?)(?=\n###\s+\d+\.|$)', text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Fallback: try simpler pattern
        match = re.search(pattern + r':?\s*(.+?)(?=\n###|\Z)', text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_subsection(self, text: str, pattern: str) -> str:
        """Extract subsection within a section"""
        match = re.search(pattern + r':?\s*\n(.+?)(?=\n\*\*|\n##|\Z)', text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """Extract single field value"""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _extract_first_paragraph(self, text: str) -> str:
        """Extract first paragraph from text"""
        paragraphs = text.split('\n\n')
        return paragraphs[0].strip() if paragraphs else ""
    
    def _extract_list_items(self, text: str, patterns: List[str] = None) -> List[str]:
        """Extract list items from text"""
        items = []
        
        # Default pattern: bullet points and numbered lists
        default_patterns = [
            r'[-•*]\s*(.+?)(?:\n|$)',
            r'\d+\.\s*(.+?)(?:\n|$)'
        ]
        
        patterns = patterns or default_patterns
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                item = match.group(1).strip()
                # Clean up markdown bold
                item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
                if item and len(item) > 3:  # Filter out very short items
                    items.append(item)
        
        return list(dict.fromkeys(items))  # Remove duplicates while preserving order
    
    def _get_fallback_reasoning(self, raw_output: str) -> ReasoningAnalysis:
        """Return fallback structure when parsing fails"""
        return ReasoningAnalysis(
            market_structure=MarketStructure(
                trend_description="Analysis unavailable",
                key_levels=["Parsing error"],
                structural_notes=[]
            ),
            momentum=MomentumAnalysis(
                assessment="Analysis unavailable",
                indicators=[],
                divergences=[],
                strength="Unknown"
            ),
            regime=RegimeClassification(
                regime="Indecisive",
                reasoning="Parsing error",
                volatility="Unknown"
            ),
            strategy_bias=StrategyBiasAnalysis(
                bias="Neutral",
                confidence="Low",
                reasoning=["Analysis unavailable due to parsing error"]
            ),
            suitable_approaches=SuitableApproaches(
                approaches=[{"name": "Wait-and-see", "rationale": "Analysis unavailable"}],
                recommended="Wait-and-see"
            ),
            invalidation=InvalidationConditions(
                bullish_invalidation=["Not available"],
                bearish_invalidation=["Not available"],
                key_levels=["Not available"]
            ),
            risks=RiskConsiderations(
                risks=["Analysis unavailable"],
                conflicting_signals=[],
                monitoring_points=[],
                uncertainty_note="Parsing error occurred"
            ),
            raw_output=raw_output
        )
    
    def to_dict(self, analysis: CompleteAnalysis) -> Dict[str, Any]:
        """
        Convert analysis to dictionary for JSON serialization.
        
        Args:
            analysis: CompleteAnalysis object
            
        Returns:
            Dictionary representation
        """
        return asdict(analysis)
    
    def to_streamlit_format(self, analysis: CompleteAnalysis) -> Dict[str, Any]:
        """
        Convert analysis to Streamlit-optimized format.
        
        Args:
            analysis: CompleteAnalysis object
            
        Returns:
            Dictionary optimized for Streamlit rendering
        """
        return {
            "vision": {
                "chart_info": {
                    "type": analysis.vision.chart_type,
                    "timeframe": analysis.vision.timeframe or "Not specified"
                },
                "price_structure": analysis.vision.price_structure,
                "indicators": analysis.vision.indicators_detected,
                "patterns": analysis.vision.visual_patterns,
                "momentum": analysis.vision.momentum_signals
            },
            "analysis": {
                "market_structure": {
                    "trend": analysis.reasoning.market_structure.trend_description,
                    "key_levels": analysis.reasoning.market_structure.key_levels,
                    "notes": analysis.reasoning.market_structure.structural_notes
                },
                "momentum": {
                    "assessment": analysis.reasoning.momentum.assessment,
                    "indicators": analysis.reasoning.momentum.indicators,
                    "divergences": analysis.reasoning.momentum.divergences,
                    "strength": analysis.reasoning.momentum.strength
                },
                "regime": {
                    "classification": analysis.reasoning.regime.regime,
                    "reasoning": analysis.reasoning.regime.reasoning,
                    "volatility": analysis.reasoning.regime.volatility
                },
                "strategy_bias": {
                    "bias": analysis.reasoning.strategy_bias.bias,
                    "confidence": analysis.reasoning.strategy_bias.confidence,
                    "reasoning": analysis.reasoning.strategy_bias.reasoning
                },
                "approaches": {
                    "options": analysis.reasoning.suitable_approaches.approaches,
                    "recommended": analysis.reasoning.suitable_approaches.recommended
                },
                "invalidation": {
                    "bullish": analysis.reasoning.invalidation.bullish_invalidation,
                    "bearish": analysis.reasoning.invalidation.bearish_invalidation,
                    "key_levels": analysis.reasoning.invalidation.key_levels
                },
                "risks": {
                    "risks": analysis.reasoning.risks.risks,
                    "conflicts": analysis.reasoning.risks.conflicting_signals,
                    "monitor": analysis.reasoning.risks.monitoring_points,
                    "uncertainty": analysis.reasoning.risks.uncertainty_note
                }
            },
            "metadata": analysis.metadata
        }


# Convenience function
def parse_complete_analysis(
    vision_output: str,
    reasoning_output: str,
    metadata: Dict[str, Any] = None
) -> CompleteAnalysis:
    """
    Parse complete analysis from vision and reasoning outputs.
    
    Args:
        vision_output: Raw vision model output
        reasoning_output: Raw reasoning model output
        metadata: Optional metadata
        
    Returns:
        CompleteAnalysis object
    """
    parser = ResponseParser()
    
    vision = parser.parse_vision_output(vision_output)
    reasoning = parser.parse_reasoning_output(reasoning_output)
    
    return CompleteAnalysis(
        vision=vision,
        reasoning=reasoning,
        metadata=metadata or {}
    )
