"""
Prompt Templates for Trading Chart Analysis

This module contains structured prompt templates for vision and reasoning models.
Templates are designed to produce consistent, educational, non-predictive analysis.

Author: Chartered
Version: 1.0.0
"""

# ============================================================================
# VISION MODEL PROMPTS
# ============================================================================

VISION_SYSTEM_PROMPT = """You are a technical chart analysis assistant. Your role is to objectively describe what you see in trading charts without making predictions or recommendations."""

VISION_USER_PROMPT_TEMPLATE = """Analyze this trading chart and provide factual, objective description.

Focus on:
1. Chart Type & Timeframe (if visible)
2. Price Structure - trend, highs/lows, support/resistance levels
3. Technical Indicators - list all visible (MAs, RSI, MACD, volume, etc.)
4. Visual Patterns - formations or patterns
5. Momentum Signals - what indicators show

{context_section}

Be factual, objective, no predictions or trade suggestions. Use neutral language."""

VISION_CONTEXT_TEMPLATE = """
Additional Context:
- Timeframe: {timeframe}
- Asset: {asset}
"""


# ============================================================================
# REASONING MODEL PROMPTS
# ============================================================================

REASONING_SYSTEM_PROMPT = """You are a professional technical market analyst providing educational decision-support. You analyze chart descriptions and provide probabilistic assessments without making predictions or trade recommendations.

Your analysis must:
- Use probabilistic language ("suggests", "indicates", "may", "could")
- Focus on decision-support, not trade execution
- Define clear invalidation conditions
- Acknowledge uncertainty
- Be educational in tone

You must NEVER:
- Provide specific buy/sell orders
- Give exact price targets
- Make guarantees about outcomes
- Recommend trade execution"""

REASONING_USER_PROMPT_TEMPLATE = """Analyze this chart description and provide structured insights:

{vision_output}

## Required Analysis Sections

**1. Market Structure** - Trend, key levels, patterns (be specific)

**2. Momentum** - Indicator interpretation, divergences (if visible)

**3. Regime** - Classify: Trending Bullish/Bearish, Ranging, Breakout, or Indecisive (1-2 sentences)

**4. Strategy Bias** - State Bullish/Bearish/Neutral with confidence (High/Medium/Low) + 2-3 key points

**5. Approaches** - List 2-3 suitable strategies (trend-following, mean-reversion, etc.) with brief rationale

**6. Invalidation** - Specific levels/conditions that would invalidate bullish/bearish scenarios

**7. Trading Signals**
- Signal: BUY/SELL/WAIT/NO CLEAR SIGNAL
- Entry: [price zone]
- Stop: [price + pip distance if calculable]
- TP1: [target + pip distance]
- TP2: [optional second target]
- R:R: [ratio]
- Position: [sizing guidance]
- Timeframe: [best TF for setup]
- Confidence: High (70-85%), Medium (50-70%), Low (<50%)

**8. Risks** - Key uncertainties, conflicting signals, what to monitor

Be concise, specific, use probabilistic language. Provide numbers when available."""


# ============================================================================
# COMBINED PROMPT BUILDER
# ============================================================================

def build_vision_prompt(context: dict = None) -> str:
    """
    Build vision model prompt with optional context.
    
    Args:
        context: Optional dict with 'timeframe' and 'asset' keys
        
    Returns:
        Formatted vision prompt
    """
    if context and (context.get('timeframe') or context.get('asset')):
        context_section = VISION_CONTEXT_TEMPLATE.format(
            timeframe=context.get('timeframe', 'Not specified'),
            asset=context.get('asset', 'Not specified')
        )
    else:
        context_section = ""
    
    return VISION_USER_PROMPT_TEMPLATE.format(context_section=context_section)


def build_reasoning_prompt(vision_output: str, context: dict = None) -> str:
    """
    Build reasoning model prompt with vision output.
    
    Args:
        vision_output: Output from vision model
        context: Optional additional context
        
    Returns:
        Formatted reasoning prompt
    """
    return REASONING_USER_PROMPT_TEMPLATE.format(vision_output=vision_output)


def build_llama_prompt(vision_output: str) -> str:
    """
    Build Llama-2 formatted prompt with special tokens.
    
    Args:
        vision_output: Output from vision model
        
    Returns:
        Llama-2 formatted prompt
    """
    user_prompt = build_reasoning_prompt(vision_output)
    
    return f"""<s>[INST] <<SYS>>
{REASONING_SYSTEM_PROMPT}
<</SYS>>

{user_prompt} [/INST]"""


def build_mistral_prompt(vision_output: str) -> str:
    """
    Build Mistral formatted prompt with special tokens.
    
    Args:
        vision_output: Output from vision model
        
    Returns:
        Mistral formatted prompt
    """
    user_prompt = build_reasoning_prompt(vision_output)
    
    return f"""<s>[INST] {user_prompt} [/INST]"""


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Build vision prompt
    print("="*60)
    print("VISION PROMPT EXAMPLE")
    print("="*60)
    
    context = {
        "timeframe": "4H",
        "asset": "BTC/USD"
    }
    
    vision_prompt = build_vision_prompt(context)
    print(vision_prompt)
    
    # Example: Build reasoning prompt
    print("\n" + "="*60)
    print("REASONING PROMPT EXAMPLE")
    print("="*60)
    
    sample_vision_output = """
    Chart Type: Candlestick chart, 4-hour timeframe
    
    Price Structure:
    - Uptrend visible with higher highs and higher lows
    - Currently testing previous swing high resistance
    - Support at EMA 20 (blue line)
    - Resistance at recent swing high around current price
    
    Technical Indicators:
    - EMA 20 (blue) and EMA 50 (orange) both sloping upward
    - Price trading above both EMAs
    - RSI at 68, approaching overbought territory
    - MACD positive but histogram bars declining
    - Volume declining on recent rally
    
    Visual Patterns:
    - Higher lows pattern intact
    - Consolidation near resistance
    - Small-bodied candles with upper wicks recently
    
    Momentum Signals:
    - RSI showing bearish divergence (lower highs while price makes higher highs)
    - MACD histogram declining despite positive values
    - Volume not confirming the rally
    """
    
    reasoning_prompt = build_reasoning_prompt(sample_vision_output)
    print(reasoning_prompt)
