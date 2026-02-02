# Prompt Templates - Quick Reference

## 🎯 Quick Usage

```python
from backend.prompts.vision_prompts import (
    build_vision_prompt,
    build_reasoning_prompt
)

# 1. Build vision prompt
context = {"timeframe": "4H", "asset": "BTC/USD"}
vision_prompt = build_vision_prompt(context)

# 2. Query vision model
vision_output = vision_client.query_vision_model(image_bytes, vision_prompt)

# 3. Build reasoning prompt
reasoning_prompt = build_reasoning_prompt(vision_output)

# 4. Query reasoning model
analysis = reasoning_client.query_text_model(reasoning_prompt)
```

---

## 📋 Vision Prompt Structure

**Purpose**: Extract objective facts from chart image

**Sections**:
1. Chart Type & Timeframe
2. Price Structure
3. Technical Indicators
4. Visual Patterns
5. Momentum Signals

**Rules**:
- Factual only
- No predictions
- Neutral language

---

## 🧠 Reasoning Prompt Structure

**Purpose**: Provide structured market analysis

**Required Sections** (7):
1. **Market Structure Assessment** - Trend, support/resistance
2. **Momentum Analysis** - Indicators, divergences
3. **Market Regime Classification** - Trending/Ranging/Breakout/Indecisive
4. **Strategy Bias** - Bullish/Bearish/Neutral with confidence
5. **Suitable Approaches** - General strategies (not trades)
6. **Invalidation Conditions** - What invalidates each scenario
7. **Risk Considerations** - Risks, conflicts, what to monitor

---

## ✅ Language Guidelines

### Probabilistic (Good)
- "suggests"
- "may indicate"
- "could signal"
- "appears to be"
- "typically associated with"

### Predictive (Bad)
- "will"
- "definitely"
- "guaranteed"
- "always"
- "proves"

### Decision-Support (Good)
- "suitable approaches include"
- "traders might consider"
- "this setup may favor"

### Trade Execution (Bad)
- "buy at"
- "sell at"
- "enter here"
- "stop loss at"

---

## 🔧 Model-Specific Formatting

### Llama-2
```python
from backend.prompts.vision_prompts import build_llama_prompt

prompt = build_llama_prompt(vision_output)
# Format: <s>[INST] <<SYS>>...
```

### Mistral
```python
from backend.prompts.vision_prompts import build_mistral_prompt

prompt = build_mistral_prompt(vision_output)
# Format: <s>[INST] ...
```

---

## 📊 Output Quality Checklist

### Vision Output Must:
- [ ] Describe only visible elements
- [ ] Use neutral language
- [ ] List all indicators
- [ ] No predictions

### Reasoning Output Must:
- [ ] Include all 7 sections
- [ ] Use probabilistic language
- [ ] No buy/sell orders
- [ ] No price targets
- [ ] Acknowledge uncertainty
- [ ] Educational tone

---

## 📁 Files

- [`vision_prompts.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/backend/prompts/vision_prompts.py) - Implementation
- [`prompt_templates.md`](file:///Users/advaitdharmadhikari/.gemini/antigravity/brain/813735fb-9a53-4334-9140-8fe5d686e605/prompt_templates.md) - Full documentation

---

**Version**: 1.0.0  
**Compliance**: Educational, non-predictive, decision-support only
