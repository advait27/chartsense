"""
Response Builder and Parser

This module converts raw AI model outputs into structured, dashboard-ready format.
Handles parsing, cleaning, and formatting for frontend consumption.

Author: Chartered
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
class TradingSignals:
    """Trading signal recommendations with specific levels"""
    signal_type: str  # "BUY", "SELL", "WAIT", "NO CLEAR SIGNAL"
    entry_level: Optional[str]  # e.g., "1.0850-1.0870"
    stop_loss: Optional[str]  # e.g., "1.0800 (50 pips)"
    take_profit_1: Optional[str]  # e.g., "1.0950 (100 pips)"
    take_profit_2: Optional[str]  # Optional second target
    risk_reward_ratio: Optional[str]  # e.g., "1:2"
    position_sizing: Optional[str]  # e.g., "Risk 1-2% of capital"
    timeframe_context: Optional[str]  # e.g., "Best for 4H-Daily timeframe"
    confidence_score: Optional[str]  # e.g., "High (75-85%)"


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
    trading_signals: TradingSignals
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
    
    # Section headers to look for - more flexible patterns
    SECTION_PATTERNS = {
        'market_structure': r'(?:###?\s*)?(?:\*\*)?(?:1\.?\s*)?Market Structure(?:\s+Assessment)?(?:\*\*)?',
        'momentum': r'(?:###?\s*)?(?:\*\*)?(?:2\.?\s*)?Momentum(?:\s+Analysis)?(?:\*\*)?',
        'regime': r'(?:###?\s*)?(?:\*\*)?(?:3\.?\s*)?(?:Market )?Regime(?:\s+Classification)?(?:\*\*)?',
        'strategy_bias': r'(?:###?\s*)?(?:\*\*)?(?:4\.?\s*)?Strategy Bias(?:\*\*)?',
        'approaches': r'(?:###?\s*)?(?:\*\*)?(?:5\.?\s*)?(?:Suitable )?Approaches?(?:\*\*)?',
        'invalidation': r'(?:###?\s*)?(?:\*\*)?(?:6\.?\s*)?Invalidation(?:\s+Conditions)?(?:\*\*)?',
        'trading_signals': r'(?:###?\s*)?(?:\*\*)?(?:7\.?\s*)?Trading Signals?(?:\*\*)?',
        'risks': r'(?:###?\s*)?(?:\*\*)?(?:8\.?\s*)?Risk(?:\s+Considerations)?(?:\*\*)?',
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
            trading_signals = self._parse_trading_signals(raw_output)
            risks = self._parse_risks(raw_output)
            
            return ReasoningAnalysis(
                market_structure=market_structure,
                momentum=momentum,
                regime=regime,
                strategy_bias=strategy_bias,
                suitable_approaches=approaches,
                invalidation=invalidation,
                trading_signals=trading_signals,
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
        
        # If section is empty, try to extract from context
        if not section or len(section) < 15:
            # Look for momentum-related content anywhere in text
            momentum_keywords = ['momentum', 'rsi', 'macd', 'moving average', 'indicator']
            for keyword in momentum_keywords:
                if keyword in text.lower():
                    # Extract surrounding context
                    pattern = rf'(.{{0,200}}{keyword}.{{0,200}})'
                    matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
                    sections = [m.group(1).strip() for m in matches]
                    if sections:
                        section = ' '.join(sections[:2])
                        break
        
        if not section or len(section) < 10:
            return MomentumAnalysis(
                assessment="Analysis details in market structure section",
                indicators=["Refer to chart description"],
                divergences=[],
                strength="Mixed"
            )
        
        # Clean the section
        section = re.sub(r'\n•\s+', ' ', section)
        
        # Determine strength from keywords
        strength = "Mixed"
        section_lower = section.lower()
        if "strong" in section_lower and "bearish" in section_lower:
            strength = "Strong Bearish"
        elif "strong" in section_lower and "bullish" in section_lower:
            strength = "Strong Bullish"
        elif "weak" in section_lower and "bearish" in section_lower:
            strength = "Weak Bearish"
        elif "weak" in section_lower and "bullish" in section_lower:
            strength = "Weak Bullish"
        
        return MomentumAnalysis(
            assessment=section[:500].strip(),
            indicators=["See description above"],
            divergences=[],
            strength=strength
        )
    
    def _parse_regime(self, text: str) -> RegimeClassification:
        """Parse market regime section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['regime'])
        
        # Enhanced fallback - look for regime keywords anywhere
        if not section or len(section) < 10:
            regime_keywords = ['trending', 'ranging', 'breakout', 'indecisive', 'consolidat']
            for keyword in regime_keywords:
                if keyword in text.lower():
                    pattern = rf'(.{{0,150}}{keyword}.{{0,150}})'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        section = match.group(1).strip()
                        break
        
        if not section or len(section) < 10:
            return RegimeClassification(
                regime="Indecisive",
                reasoning="See market structure analysis for details",
                volatility="Unknown"
            )
        
        # Clean the section
        section = re.sub(r'\n•\s+', ' ', section)
        
        # Extract regime classification with better matching
        regime = "Indecisive"
        section_lower = section.lower()
        if "trending" in section_lower and "bearish" in section_lower:
            regime = "Trending Bearish"
        elif "trending" in section_lower and "bullish" in section_lower:
            regime = "Trending Bullish"
        elif "trending" in section_lower:
            regime = "Trending"
        elif "ranging" in section_lower or "range" in section_lower:
            regime = "Ranging"
        elif "breakout" in section_lower:
            regime = "Breakout"
        
        # Extract volatility if mentioned
        volatility = "Unknown"
        if "volatility" in section_lower:
            if "high" in section_lower:
                volatility = "High"
            elif "low" in section_lower:
                volatility = "Low"
            elif "moderate" in section_lower:
                volatility = "Moderate"
        
        return RegimeClassification(
            regime=regime,
            reasoning=section[:400].strip(),
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
        
        # If no section found, extract from general text
        if not section or len(section) < 15:
            # Look for approach-related keywords
            approach_keywords = ['trend-following', 'mean-reversion', 'breakout', 'range trading', 'wait-and-see']
            for keyword in approach_keywords:
                if keyword.lower() in text.lower():
                    approaches.append({
                        "name": keyword.title(),
                        "rationale": "Mentioned in analysis"
                    })
            
            if approaches:
                return SuitableApproaches(approaches=approaches, recommended=None)
        
        # Try to extract structured approaches
        if section:
            # Look for numbered or bulleted approaches
            approach_patterns = [
                r'(?:[-•\d]+\.?\s*)([A-Z][a-z\-]+(?:\s+[A-Z][a-z\-]+)*)',
                r'(?:[-•]\s*)\*\*(.+?)\*\*',
            ]
            
            for pattern in approach_patterns:
                matches = re.finditer(pattern, section)
                for match in matches:
                    name = match.group(1).strip()
                    if len(name) > 3 and len(name) < 50:  # Reasonable length
                        # Extract rationale from following text
                        start = match.end()
                        end = min(start + 150, len(section))
                        rationale_text = section[start:end].split('\n')[0]
                        
                        approaches.append({
                            "name": name,
                            "rationale": rationale_text.strip() if rationale_text else "See analysis"
                        })
                
                if approaches:
                    break
        
        # Fallback: return default approaches based on strategy bias
        if not approaches:
            if "bullish" in text.lower():
                approaches = [
                    {"name": "Trend-following", "rationale": "Aligned with bullish bias"},
                    {"name": "Breakout trading", "rationale": "Look for continuation patterns"}
                ]
            elif "bearish" in text.lower():
                approaches = [
                    {"name": "Trend-following", "rationale": "Aligned with bearish bias"},
                    {"name": "Short selling", "rationale": "Consider downside opportunities"}
                ]
            else:
                approaches = [
                    {"name": "Wait-and-see", "rationale": "Await clearer signals"},
                    {"name": "Range trading", "rationale": "Trade within defined levels"}
                ]
        
        return SuitableApproaches(
            approaches=approaches[:3],
            recommended=approaches[0]["name"] if approaches else None
        )
    
    def _parse_invalidation(self, text: str) -> InvalidationConditions:
        """Parse invalidation conditions section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS['invalidation'])
        
        # Extract bullish invalidation
        bullish_invalidation = []
        bullish_patterns = [
            r'bullish.*?(?:invalidated|invalid|scenario).*?(?:if|:)\s*(.+?)(?=\n[\-•]|\nbear|$)',
            r'(?:if|when)\s+price\s+(?:breaks?|falls?|closes?)\s+below\s+(.+?)(?=\n|,|$)',
        ]
        
        for pattern in bullish_patterns:
            match = re.search(pattern, section or text, re.IGNORECASE | re.DOTALL)
            if match:
                condition = match.group(1).strip()
                if condition and len(condition) > 5:
                    bullish_invalidation.append(condition[:200])
                    break
        
        # Extract bearish invalidation
        bearish_invalidation = []
        bearish_patterns = [
            r'bearish.*?(?:invalidated|invalid|scenario).*?(?:if|:)\s*(.+?)(?=\n[\-•]|\nkey|$)',
            r'(?:if|when)\s+price\s+(?:breaks?|rises?|closes?)\s+above\s+(.+?)(?=\n|,|$)',
        ]
        
        for pattern in bearish_patterns:
            match = re.search(pattern, section or text, re.IGNORECASE | re.DOTALL)
            if match:
                condition = match.group(1).strip()
                if condition and len(condition) > 5:
                    bearish_invalidation.append(condition[:200])
                    break
        
        # Extract key levels
        key_levels = []
        key_patterns = [
            r'key.*?(?:decision|level|price).*?:?\s*(.+?)(?=\n|$)',
            r'(?:watch|monitor).*?level.*?:?\s*(.+?)(?=\n|$)',
        ]
        
        for pattern in key_patterns:
            match = re.search(pattern, section or text, re.IGNORECASE)
            if match:
                levels = match.group(1).strip()
                if levels and len(levels) > 5:
                    key_levels.append(levels[:150])
                    break
        
        # Smart fallbacks based on strategy bias
        if not bullish_invalidation:
            if "support" in text.lower():
                support_match = re.search(r'support.*?(?:at|near|around)\s+([\d,.]+)', text, re.IGNORECASE)
                if support_match:
                    bullish_invalidation = [f"Break below support at {support_match.group(1)}"]
        
        if not bearish_invalidation:
            if "resistance" in text.lower():
                resistance_match = re.search(r'resistance.*?(?:at|near|around)\s+([\d,.]+)', text, re.IGNORECASE)
                if resistance_match:
                    bearish_invalidation = [f"Break above resistance at {resistance_match.group(1)}"]
        
        return InvalidationConditions(
            bullish_invalidation=bullish_invalidation if bullish_invalidation else ["See key levels for invalidation zones"],
            bearish_invalidation=bearish_invalidation if bearish_invalidation else ["See key levels for invalidation zones"],
            key_levels=key_levels if key_levels else ["Refer to market structure section"]
        )
    
    def _parse_trading_signals(self, text: str) -> TradingSignals:
        """Parse trading signals section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS.get('signals', r'(?:\*\*)?(?:7\.?\s*)?Trading Signals?(?:\*\*)?'))
        
        # Fallback to searching for signal keywords if no section found
        if not section or len(section) < 20:
            signal_keywords = ['entry', 'stop loss', 'target', 'buy', 'sell']
            for keyword in signal_keywords:
                if keyword in text.lower():
                    pattern = rf'(.{{0,300}}{keyword}.{{0,300}})'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        section = match.group(1).strip()
                        break
        
        if not section or len(section) < 20:
            return self._generate_signals_from_bias(text)
        
        # Extract signal type with more patterns
        signal_type = "NO CLEAR SIGNAL"
        section_lower = section.lower()
        if any(word in section_lower for word in ["buy", "long", "bullish bias"]):
            signal_type = "BUY"
        elif any(word in section_lower for word in ["sell", "short", "bearish bias"]):
            signal_type = "SELL"
        elif "wait" in section_lower or "no clear signal" in section_lower:
            signal_type = "WAIT"
        
        # Extract entry level with multiple patterns
        entry_patterns = [
            r'(?:Entry|Entry Level|Entry Zone|Entry Point):?\s*(.+?)(?:\n|,|;|$)',
            r'(?:at|near|around)\s+([\d,.]+)',
        ]
        entry_level = None
        for pattern in entry_patterns:
            entry_level = self._extract_field(section, pattern)
            if entry_level and len(entry_level) > 3:
                break
        
        # Extract stop loss
        stop_patterns = [
            r'(?:Stop Loss|Stop|SL):?\s*(.+?)(?:\n|,|;|$)',
            r'(?:below|above)\s+([\d,.]+)',
        ]
        stop_loss = None
        for pattern in stop_patterns:
            stop_loss = self._extract_field(section, pattern)
            if stop_loss and len(stop_loss) > 3:
                break
        
        # Extract take profit targets
        tp_patterns = [
            r'(?:Take Profit|TP|Target)\s*(?:1|One)?:?\s*(.+?)(?:\n|,|;|$)',
            r'(?:Take Profit|TP|Target)\s*(?:2|Two):?\s*(.+?)(?:\n|,|;|$)',
        ]
        take_profit_1 = self._extract_field(section, tp_patterns[0])
        take_profit_2 = self._extract_field(section, tp_patterns[1])
        
        # Extract risk-reward
        risk_reward = self._extract_field(section, r'(?:Risk[- ]Reward|R:R|RR):?\s*(.+?)(?:\n|,|;|$)')
        
        # Extract position sizing
        position_sizing = self._extract_field(section, r'(?:Position Siz|Risk):?\s*(.+?)(?:\n|$)')
        
        # Extract timeframe
        timeframe_context = self._extract_field(section, r'(?:Timeframe|Time Frame|Best for):?\s*(.+?)(?:\n|$)')
        
        # Extract confidence
        confidence = self._extract_field(section, r'(?:Confidence|Probability):?\s*(.+?)(?:\n|$)')
        
        return TradingSignals(
            signal_type=signal_type,
            entry_level=entry_level or "See market structure section",
            stop_loss=stop_loss or "See invalidation conditions",
            take_profit_1=take_profit_1 or "See key resistance/support levels",
            take_profit_2=take_profit_2,
            risk_reward_ratio=risk_reward or "Monitor 1:2 minimum",
            position_sizing=position_sizing or "Risk 1-2% of capital per trade",
            timeframe_context=timeframe_context,
            confidence_score=confidence
        )
    
    def _generate_signals_from_bias(self, text: str) -> TradingSignals:
        """Generate basic signals from strategy bias when no explicit signals section"""
        # Extract bias from text
        signal_type = "WAIT"
        if "strong" in text.lower() and "bullish" in text.lower():
            signal_type = "BUY"
        elif "strong" in text.lower() and "bearish" in text.lower():
            signal_type = "SELL"
        elif "bullish" in text.lower() and "high" in text.lower():
            signal_type = "BUY"
        elif "bearish" in text.lower() and "high" in text.lower():
            signal_type = "SELL"
        
        return TradingSignals(
            signal_type=signal_type,
            entry_level="See key levels in Market Structure section",
            stop_loss="See invalidation conditions",
            take_profit_1="See key resistance/support levels",
            take_profit_2=None,
            risk_reward_ratio="Monitor 1:2 minimum",
            position_sizing="Risk 1-2% of capital per trade",
            timeframe_context=None,
            confidence_score="See Strategy Bias section"
        )
    
    def _parse_risks(self, text: str) -> RiskConsiderations:
        """Parse risk considerations section"""
        section = self._extract_section_by_pattern(text, self.SECTION_PATTERNS.get('risks', r'(?:\*\*)?(?:8\.?\s*)?Risk Considerations?(?:\*\*)?'))
        
        # Fallback: look anywhere in text for risk-related content
        if not section or len(section) < 20:
            risk_keywords = ['risk', 'caution', 'uncertainty', 'monitor']
            for keyword in risk_keywords:
                if keyword in text.lower():
                    pattern = rf'(.{{0,400}}{keyword}.{{0,400}})'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        section = match.group(1).strip()
                        break
        
        # Extract risks with improved patterns
        risks = []
        if section:
            # Try specific risk patterns first
            risk_patterns = [
                r'[-•*]\s*(.+?)(?:\n|$)',  # Bullet points
                r'(?:Risk|Caution|Warning):?\s*(.+?)(?:\n|$)',
                r'(?:may|could|might)\s+(.+?)(?:\n|$)',  # Uncertainty language
            ]
            risks = self._extract_list_items(section, patterns=risk_patterns)
        
        # Extract conflicting signals
        conflicting = []
        if section:
            conflicting_patterns = [
                r'(?:Conflict|Conflicting|Divergence):?\s*(.+?)(?:\n|$)',
                r'(?:however|but|although)\s+(.+?)(?:\n|$)',
            ]
            conflicting = self._extract_list_items(section, patterns=conflicting_patterns)
        
        # Extract monitoring points
        monitoring = []
        if section:
            monitoring_patterns = [
                r'(?:Monitor|Watch|Track|Check):?\s*(.+?)(?:\n|$)',
                r'(?:key level|important level):?\s*(.+?)(?:\n|$)',
            ]
            monitoring = self._extract_list_items(section, patterns=monitoring_patterns)
        
        # Extract uncertainty note
        uncertainty = None
        if section:
            uncertainty = self._extract_field(section, r'(?:Uncertainty|Acknowledgment|Disclaimer):?\s*(.+?)(?:\n\n|$)')
        
        # Smart defaults
        if not risks:
            risks = ["Market volatility risk", "Timing risk", "External factors may impact outcome"]
        
        if not monitoring:
            monitoring = ["Price action at key levels", "Volume confirmation", "Overall market conditions"]
        
        return RiskConsiderations(
            risks=risks[:5],
            conflicting_signals=conflicting[:3],
            monitoring_points=monitoring[:5],
            uncertainty_note=uncertainty or "Markets are inherently uncertain. This analysis is for educational purposes only."
        )
    
    # Helper methods
    
    def _extract_section(self, text: str, header: str) -> str:
        """Extract section by header name"""
        pattern = rf'{header}:?\s*\n(.+?)(?=\n\n|\n[A-Z]|\Z)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_section_by_pattern(self, text: str, pattern: str) -> str:
        """Extract section by regex pattern - more flexible matching"""
        # Try multiple pattern variations
        patterns_to_try = [
            # Match with markdown headers or numbered sections
            pattern + r':?\s*\n+(.+?)(?=\n+(?:\*\*)?(?:\d+\.|\#\#)|\Z)',
            # Match inline without newline requirement
            pattern + r':?\s*(.+?)(?=\n+(?:\*\*)?(?:\d+\.|\#\#)|\Z)',
            # Simpler fallback
            pattern + r'(.+?)(?=\n\n|\Z)',
        ]
        
        for p in patterns_to_try:
            match = re.search(p, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content and len(content) > 10:  # Valid content threshold
                    return content
        
        return ""
    
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
            trading_signals=TradingSignals(
                signal_type="WAIT",
                entry_level="Not available",
                stop_loss="Not available",
                take_profit_1="Not available",
                take_profit_2=None,
                risk_reward_ratio="Not available",
                position_sizing="Not available",
                timeframe_context=None,
                confidence_score="Not available"
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
