"""
Prompt Templates for Trading Chart Analysis

This module contains structured prompt templates for vision and reasoning models.
Templates are designed to produce consistent, educational, non-predictive analysis.

Author: ChartSense
Version: 1.0.0
"""

# ============================================================================
# VISION MODEL PROMPTS
# ============================================================================

VISION_SYSTEM_PROMPT = """You are a technical chart analysis assistant. Your role is to objectively describe what you see in trading charts without making predictions or recommendations."""

VISION_USER_PROMPT_TEMPLATE = """Analyze this trading chart image and provide a factual, objective description.

Focus on:
1. **Chart Type & Timeframe**: Identify candlestick/line chart and timeframe if visible
2. **Price Structure**: Describe trend direction, swing highs/lows, support/resistance levels
3. **Technical Indicators**: List all visible indicators (moving averages, RSI, MACD, volume, etc.)
4. **Visual Patterns**: Describe any chart patterns or formations
5. **Momentum Signals**: Describe what momentum indicators show (if present)

Rules:
- Be factual and objective
- Describe only what is visible
- Do not predict future prices
- Do not suggest trades
- Use neutral language

{context_section}

Provide your analysis in a structured format."""

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

REASONING_USER_PROMPT_TEMPLATE = """Based on the following technical chart description, provide a structured market analysis.

## Chart Description
{vision_output}

## Your Analysis

Provide a clear, structured analysis with these sections:

### 1. Market Structure Assessment
Describe the trend, key support/resistance levels, and any notable patterns. Be specific with price levels where visible.

### 2. Momentum Analysis  
Interpret available momentum indicators. Note any divergences or confirmations. If indicators aren't visible, state this clearly.

### 3. Market Regime Classification
Classify as: Trending Bullish, Trending Bearish, Ranging, Breakout, or Indecisive.
Explain your classification in 2-3 sentences.

### 4. Strategy Bias
State your bias (Bullish/Bearish/Neutral) with confidence level (High/Medium/Low).
Provide 2-3 supporting points.

### 5. Suitable Approaches
Suggest 2-3 general trading approaches (e.g., trend-following, mean-reversion, wait-and-see).
Briefly explain why each may be suitable.

### 6. Invalidation Conditions
- Bullish scenario would be invalidated if: [specific levels/conditions]
- Bearish scenario would be invalidated if: [specific levels/conditions]
- Key decision levels: [specific price levels]

### 7. Trading Signals
Based on your analysis, provide specific trading recommendations:
- **Signal Type**: BUY / SELL / WAIT / NO CLEAR SIGNAL
- **Entry Level**: [specific price zone or "See key levels above"]
- **Stop Loss**: [specific price level with pip distance if calculable, e.g., "1.0800 (50 pips)"]
- **Take Profit 1**: [first target price with pip distance]
- **Take Profit 2**: [optional second target] (if applicable)
- **Risk-Reward Ratio**: [e.g., "1:2" or "Estimated 1:2.5"]
- **Position Sizing**: [e.g., "Risk 1-2% of capital" or specific guidance]
- **Timeframe Context**: [best timeframe for this setup]
- **Confidence Score**: [High (70-85%), Medium (50-70%), Low (<50%)]

### 8. Risk Considerations
- Highlight potential risks or uncertainties
- Note any conflicting signals
- Mention what to monitor

## Output Format
Use clear headings and bullet points. Be concise but thorough. Provide specific numbers when available.

## Critical Reminders
- Use probabilistic language ("suggests", "may indicate", "could signal")
- Provide specific levels but acknowledge they are suggested zones, not guarantees
- Focus on education and decision-support
- Acknowledge uncertainty where it exists
- Trading signals are for educational purposes only

Provide your analysis now:"""


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
