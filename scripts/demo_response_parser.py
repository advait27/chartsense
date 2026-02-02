#!/usr/bin/env python3
"""
Demo script for Response Parser

Demonstrates parsing AI outputs into structured format.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.response_builder import (
    ResponseParser,
    parse_complete_analysis
)
import json


# Sample outputs
SAMPLE_VISION_OUTPUT = """
Chart Type: Candlestick chart, 4-hour timeframe

Price Structure:
- Uptrend visible with higher highs and higher lows
- Currently testing previous swing high resistance
- Support identified at EMA 20 (blue line below price)
- Resistance at recent swing high near current price level

Technical Indicators:
- EMA 20 (blue line) sloping upward, below price
- EMA 50 (orange line) sloping upward, below EMA 20
- RSI indicator showing reading of approximately 68
- MACD histogram positive but declining in height
- Volume bars declining over the last 5-6 candles

Visual Patterns:
- Series of higher lows maintaining uptrend structure
- Consolidation pattern forming near resistance
- Recent candles showing small bodies with upper wicks
- Lower highs on RSI while price makes higher highs (divergence pattern)

Momentum Signals:
- RSI approaching 70 level (overbought zone)
- MACD histogram bars getting shorter despite remaining positive
- Volume declining during recent price advance
- Price action showing indecision with small-bodied candles
"""

SAMPLE_REASONING_OUTPUT = """
## 1. Market Structure Assessment

The chart displays an intact uptrend structure characterized by higher highs and higher lows. Price is currently testing resistance at the previous swing high.

Key levels:
- **Primary Support**: EMA 20, currently acting as dynamic support
- **Secondary Support**: EMA 50, providing additional structural support
- **Resistance**: Recent swing high at current price level

The structure suggests the uptrend remains valid while price holds above the EMA 20.

## 2. Momentum Analysis

Momentum indicators present a mixed picture.

**RSI (68):**
- Approaching overbought territory but not yet extreme
- Showing bearish divergence (lower highs on RSI while price makes higher highs)
- This divergence suggests weakening buying pressure

**MACD:**
- Remains positive, confirming the uptrend
- Histogram declining, indicating momentum is slowing

**Volume:**
- Declining during the recent rally
- Lower volume on upward moves typically suggests weakening conviction

The combination of these signals suggests momentum is waning.

## 3. Market Regime Classification

Classification: Trending (Bullish) with Consolidation

Reasoning: The higher high/higher low structure defines a bullish trend. However, price is consolidating near resistance rather than breaking out.

Volatility: Moderate volatility with recent compression

## 4. Strategy Bias

Bias: Neutral to Bearish

Confidence Level: Medium

Reasoning:
- Bearish divergence on RSI indicates weakening momentum
- Declining volume on rally suggests lack of conviction
- Multiple rejections at resistance show strong selling pressure
- MACD histogram declining despite positive values

## 5. Suitable Approaches

A. Mean-Reversion Approach
Rationale: Bearish divergence and overbought RSI suggest potential pullback

B. Wait-and-See Approach ⭐ (Recommended)
Rationale: Conflicting signals suggest waiting for clarity

C. Breakout Approach
Rationale: If resistance breaks with volume, trend could accelerate

D. Trend-Following (Cautious)
Rationale: Trend is still technically intact

## 6. Invalidation Conditions

Bullish Scenario Invalidated If:
- Price breaks and closes below EMA 20 with conviction
- Lower low forms, breaking the higher-low structure
- Volume expands on downward move

Bearish Scenario Invalidated If:
- Price breaks above resistance with strong volume
- RSI resets and moves higher with price
- New higher high confirmed with momentum support

Key Decision Levels:
- Upside: Resistance at current swing high
- Downside: EMA 20 support
- Critical: Most recent higher low

## 7. Risk Considerations

Potential Risks:
- Whipsaw risk near resistance can produce false breakouts
- Divergence may not lead to reversal
- Strong trends can persist longer than expected

Conflicting Signals:
- Bearish momentum indicators vs. bullish trend structure
- Declining volume could mean either distribution or low participation

What to Monitor:
- Price action at resistance
- Volume behavior on next significant move
- EMA 20 support level
- RSI behavior and divergence continuation

Uncertainty Acknowledgment:
This analysis is based on current visible information. Markets can behave unpredictably, and no analysis guarantees outcomes.
"""


def demo_basic_parsing():
    """Demo basic parsing functionality"""
    print("="*60)
    print("DEMO 1: Basic Parsing")
    print("="*60)
    
    parser = ResponseParser()
    
    # Parse vision output
    print("\n📊 Parsing Vision Output...")
    vision = parser.parse_vision_output(SAMPLE_VISION_OUTPUT)
    
    print(f"\nChart Type: {vision.chart_type}")
    print(f"Timeframe: {vision.timeframe}")
    print(f"\nIndicators Detected ({len(vision.indicators_detected)}):")
    for indicator in vision.indicators_detected[:3]:
        print(f"  - {indicator}")
    
    print(f"\nVisual Patterns ({len(vision.visual_patterns)}):")
    for pattern in vision.visual_patterns[:3]:
        print(f"  - {pattern}")
    
    # Parse reasoning output
    print("\n\n🧠 Parsing Reasoning Output...")
    reasoning = parser.parse_reasoning_output(SAMPLE_REASONING_OUTPUT)
    
    print(f"\nMarket Regime: {reasoning.regime.regime}")
    print(f"Strategy Bias: {reasoning.strategy_bias.bias}")
    print(f"Confidence: {reasoning.strategy_bias.confidence}")
    
    print(f"\nKey Levels ({len(reasoning.market_structure.key_levels)}):")
    for level in reasoning.market_structure.key_levels:
        print(f"  - {level}")


def demo_complete_analysis():
    """Demo complete analysis parsing"""
    print("\n" + "="*60)
    print("DEMO 2: Complete Analysis")
    print("="*60)
    
    analysis = parse_complete_analysis(
        SAMPLE_VISION_OUTPUT,
        SAMPLE_REASONING_OUTPUT,
        metadata={"timeframe": "4H", "asset": "BTC/USD"}
    )
    
    print(f"\n📈 Asset: {analysis.metadata.get('asset')}")
    print(f"⏰ Timeframe: {analysis.metadata.get('timeframe')}")
    
    print(f"\n📊 Vision Analysis:")
    print(f"  Chart: {analysis.vision.chart_type}")
    print(f"  Indicators: {len(analysis.vision.indicators_detected)} detected")
    print(f"  Patterns: {len(analysis.vision.visual_patterns)} identified")
    
    print(f"\n🧠 Reasoning Analysis:")
    print(f"  Regime: {analysis.reasoning.regime.regime}")
    print(f"  Bias: {analysis.reasoning.strategy_bias.bias}")
    print(f"  Confidence: {analysis.reasoning.strategy_bias.confidence}")
    print(f"  Approaches: {len(analysis.reasoning.suitable_approaches.approaches)} suggested")


def demo_streamlit_format():
    """Demo Streamlit format conversion"""
    print("\n" + "="*60)
    print("DEMO 3: Streamlit Format")
    print("="*60)
    
    parser = ResponseParser()
    analysis = parse_complete_analysis(
        SAMPLE_VISION_OUTPUT,
        SAMPLE_REASONING_OUTPUT,
        metadata={"timeframe": "4H", "asset": "BTC/USD"}
    )
    
    streamlit_data = parser.to_streamlit_format(analysis)
    
    print("\n📱 Streamlit-Optimized Format:")
    print(f"\nStructure:")
    print(f"  - vision")
    print(f"    - chart_info")
    print(f"    - price_structure")
    print(f"    - indicators")
    print(f"    - patterns")
    print(f"    - momentum")
    print(f"  - analysis")
    print(f"    - market_structure")
    print(f"    - momentum")
    print(f"    - regime")
    print(f"    - strategy_bias")
    print(f"    - approaches")
    print(f"    - invalidation")
    print(f"    - risks")
    print(f"  - metadata")
    
    # Show strategy bias section
    bias_data = streamlit_data["analysis"]["strategy_bias"]
    print(f"\n📊 Strategy Bias Section:")
    print(f"  Bias: {bias_data['bias']}")
    print(f"  Confidence: {bias_data['confidence']}")
    print(f"  Reasoning ({len(bias_data['reasoning'])} points):")
    for reason in bias_data['reasoning'][:2]:
        print(f"    - {reason}")


def demo_approaches_parsing():
    """Demo approaches parsing"""
    print("\n" + "="*60)
    print("DEMO 4: Approaches Parsing")
    print("="*60)
    
    analysis = parse_complete_analysis(
        SAMPLE_VISION_OUTPUT,
        SAMPLE_REASONING_OUTPUT
    )
    
    approaches = analysis.reasoning.suitable_approaches
    
    print(f"\n🎯 Suitable Approaches ({len(approaches.approaches)}):")
    for approach in approaches.approaches:
        is_recommended = approach['name'] == approaches.recommended
        marker = " ⭐ (Recommended)" if is_recommended else ""
        print(f"\n  {approach['name']}{marker}")
        print(f"  Rationale: {approach['rationale']}")


def demo_invalidation_parsing():
    """Demo invalidation conditions parsing"""
    print("\n" + "="*60)
    print("DEMO 5: Invalidation Conditions")
    print("="*60)
    
    analysis = parse_complete_analysis(
        SAMPLE_VISION_OUTPUT,
        SAMPLE_REASONING_OUTPUT
    )
    
    invalidation = analysis.reasoning.invalidation
    
    print("\n🔴 Bullish Scenario Invalidated If:")
    for condition in invalidation.bullish_invalidation:
        print(f"  - {condition}")
    
    print("\n🟢 Bearish Scenario Invalidated If:")
    for condition in invalidation.bearish_invalidation:
        print(f"  - {condition}")
    
    print("\n🎯 Key Decision Levels:")
    for level in invalidation.key_levels:
        print(f"  - {level}")


def demo_json_export():
    """Demo JSON export"""
    print("\n" + "="*60)
    print("DEMO 6: JSON Export")
    print("="*60)
    
    parser = ResponseParser()
    analysis = parse_complete_analysis(
        SAMPLE_VISION_OUTPUT,
        SAMPLE_REASONING_OUTPUT,
        metadata={"timeframe": "4H", "asset": "BTC/USD"}
    )
    
    # Convert to dict
    data_dict = parser.to_dict(analysis)
    
    # Export to JSON
    json_output = json.dumps(data_dict, indent=2)
    
    print("\n📄 JSON Output (first 500 chars):")
    print(json_output[:500] + "...")
    
    print(f"\n✅ Full JSON length: {len(json_output)} characters")


def main():
    """Run all demos"""
    print("🚀 Response Parser Demo")
    print("="*60)
    
    try:
        demo_basic_parsing()
        demo_complete_analysis()
        demo_streamlit_format()
        demo_approaches_parsing()
        demo_invalidation_parsing()
        demo_json_export()
        
        print("\n" + "="*60)
        print("✅ All demos completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
