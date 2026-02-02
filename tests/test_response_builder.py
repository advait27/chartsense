"""
Unit Tests for Response Parser

Tests parsing logic for vision and reasoning outputs.
"""

import pytest
from backend.core.response_builder import (
    ResponseParser,
    VisionAnalysis,
    ReasoningAnalysis,
    CompleteAnalysis,
    parse_complete_analysis
)


class TestResponseParser:
    """Test suite for ResponseParser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return ResponseParser()
    
    @pytest.fixture
    def sample_vision_output(self):
        """Sample vision model output"""
        return """
Chart Type: Candlestick chart, 4-hour timeframe

Price Structure:
- Uptrend with higher highs and higher lows
- Testing resistance at previous swing high
- Support at EMA 20

Technical Indicators:
- EMA 20 and EMA 50 sloping upward
- RSI at 68
- MACD positive but declining
- Volume declining

Visual Patterns:
- Higher lows pattern
- Consolidation near resistance
- Small-bodied candles

Momentum Signals:
- RSI showing bearish divergence
- MACD histogram declining
"""
    
    @pytest.fixture
    def sample_reasoning_output(self):
        """Sample reasoning model output"""
        return """
## 1. Market Structure Assessment

The chart displays an intact uptrend structure. Price is testing resistance.

Key levels:
- Support: EMA 20
- Resistance: Recent swing high

## 2. Momentum Analysis

Momentum indicators present a mixed picture.

RSI (68):
- Approaching overbought
- Showing bearish divergence

## 3. Market Regime Classification

Classification: Trending (Bullish) with Consolidation

Reasoning: Higher high/higher low structure defines bullish trend

Volatility: Moderate

## 4. Strategy Bias

Bias: Neutral to Bearish

Confidence Level: Medium

Reasoning:
- Bearish divergence on RSI
- Declining volume
- Multiple rejections at resistance

## 5. Suitable Approaches

A. Mean-Reversion Approach
Rationale: Bearish divergence suggests pullback

B. Wait-and-See Approach (Recommended)
Rationale: Conflicting signals suggest waiting

## 6. Invalidation Conditions

Bullish Scenario Invalidated If:
- Break below EMA 20
- Lower low forms

Bearish Scenario Invalidated If:
- Break above resistance with volume
- New higher high confirmed

Key Decision Levels:
- Upside: Resistance at swing high
- Downside: EMA 20 support

## 7. Risk Considerations

Potential Risks:
- Whipsaw risk near resistance
- Divergence may not lead to reversal

Conflicting Signals:
- Bearish momentum vs bullish structure

What to Monitor:
- Price action at resistance
- Volume behavior
- EMA 20 support
"""
    
    def test_parse_vision_output(self, parser, sample_vision_output):
        """Test vision output parsing"""
        result = parser.parse_vision_output(sample_vision_output)
        
        assert isinstance(result, VisionAnalysis)
        assert "Candlestick" in result.chart_type
        assert result.timeframe == "4-hour timeframe"
        assert len(result.indicators_detected) > 0
        assert len(result.visual_patterns) > 0
    
    def test_parse_vision_missing_sections(self, parser):
        """Test vision parsing with missing sections"""
        minimal_output = "Chart Type: Line chart"
        result = parser.parse_vision_output(minimal_output)
        
        assert isinstance(result, VisionAnalysis)
        assert result.chart_type == "Line chart"
        assert result.indicators_detected == []
    
    def test_parse_reasoning_output(self, parser, sample_reasoning_output):
        """Test reasoning output parsing"""
        result = parser.parse_reasoning_output(sample_reasoning_output)
        
        assert isinstance(result, ReasoningAnalysis)
        assert result.market_structure.trend_description
        assert result.regime.regime
        assert result.strategy_bias.bias
        assert len(result.suitable_approaches.approaches) > 0
    
    def test_parse_market_structure(self, parser, sample_reasoning_output):
        """Test market structure parsing"""
        result = parser.parse_reasoning_output(sample_reasoning_output)
        
        assert "uptrend" in result.market_structure.trend_description.lower()
        assert len(result.market_structure.key_levels) > 0
    
    def test_parse_momentum(self, parser, sample_reasoning_output):
        """Test momentum parsing"""
        result = parser.parse_reasoning_output(sample_reasoning_output)
        
        assert result.momentum.assessment
        assert len(result.momentum.indicators) > 0
    
    def test_parse_strategy_bias(self, parser, sample_reasoning_output):
        """Test strategy bias parsing"""
        result = parser.parse_reasoning_output(sample_reasoning_output)
        
        assert "Neutral" in result.strategy_bias.bias or "Bearish" in result.strategy_bias.bias
        assert result.strategy_bias.confidence in ["High", "Medium", "Low"]
        assert len(result.strategy_bias.reasoning) > 0
    
    def test_parse_invalidation(self, parser, sample_reasoning_output):
        """Test invalidation conditions parsing"""
        result = parser.parse_reasoning_output(sample_reasoning_output)
        
        assert len(result.invalidation.bullish_invalidation) > 0
        assert len(result.invalidation.bearish_invalidation) > 0
        assert len(result.invalidation.key_levels) > 0
    
    def test_parse_complete_analysis(self, sample_vision_output, sample_reasoning_output):
        """Test complete analysis parsing"""
        result = parse_complete_analysis(
            sample_vision_output,
            sample_reasoning_output,
            metadata={"test": "data"}
        )
        
        assert isinstance(result, CompleteAnalysis)
        assert isinstance(result.vision, VisionAnalysis)
        assert isinstance(result.reasoning, ReasoningAnalysis)
        assert result.metadata["test"] == "data"
    
    def test_to_streamlit_format(self, parser, sample_vision_output, sample_reasoning_output):
        """Test Streamlit format conversion"""
        analysis = parse_complete_analysis(sample_vision_output, sample_reasoning_output)
        result = parser.to_streamlit_format(analysis)
        
        assert "vision" in result
        assert "analysis" in result
        assert "metadata" in result
        assert "chart_info" in result["vision"]
        assert "market_structure" in result["analysis"]
        assert "strategy_bias" in result["analysis"]
    
    def test_graceful_error_handling(self, parser):
        """Test graceful handling of malformed input"""
        bad_input = "This is not a proper analysis output"
        
        # Should not raise exception
        vision_result = parser.parse_vision_output(bad_input)
        reasoning_result = parser.parse_reasoning_output(bad_input)
        
        assert isinstance(vision_result, VisionAnalysis)
        assert isinstance(reasoning_result, ReasoningAnalysis)
    
    def test_extract_list_items(self, parser):
        """Test list item extraction"""
        text = """
        - Item one
        - Item two
        * Item three
        1. Numbered item
        """
        
        items = parser._extract_list_items(text)
        assert len(items) >= 3
    
    def test_clean_markdown(self, parser):
        """Test markdown cleaning in list items"""
        text = "- **Bold item** with text"
        items = parser._extract_list_items(text)
        
        assert len(items) > 0
        assert "**" not in items[0]  # Bold markers should be removed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
