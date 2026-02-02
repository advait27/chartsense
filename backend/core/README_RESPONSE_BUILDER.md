# Response Parser - Documentation

## Overview

The response parser converts raw AI model outputs into structured, dashboard-ready format. It handles inconsistent formatting, missing sections, and prepares data for Streamlit rendering.

---

## 🎯 Key Features

- ✅ **Structured Data Classes** - Type-safe output format
- ✅ **Regex-Based Parsing** - Flexible section extraction
- ✅ **Graceful Error Handling** - Fallback structures for malformed input
- ✅ **Markdown Cleaning** - Removes verbose formatting
- ✅ **Streamlit Optimization** - Dashboard-ready output format
- ✅ **Consistent Headings** - Enforces standard section names

---

## 📊 Data Structures

### Vision Analysis

```python
@dataclass
class VisionAnalysis:
    chart_type: str                    # "Candlestick chart"
    timeframe: Optional[str]           # "4H"
    price_structure: str               # Description of trend, levels
    indicators_detected: List[str]     # ["EMA 20", "RSI", "MACD"]
    visual_patterns: List[str]         # ["Higher lows", "Consolidation"]
    momentum_signals: str              # Description of momentum
    raw_output: str                    # Original AI output
```

### Reasoning Analysis

```python
@dataclass
class ReasoningAnalysis:
    market_structure: MarketStructure
    momentum: MomentumAnalysis
    regime: RegimeClassification
    strategy_bias: StrategyBiasAnalysis
    suitable_approaches: SuitableApproaches
    invalidation: InvalidationConditions
    risks: RiskConsiderations
    raw_output: str
```

### Complete Analysis

```python
@dataclass
class CompleteAnalysis:
    vision: VisionAnalysis
    reasoning: ReasoningAnalysis
    metadata: Dict[str, Any]
```

---

## 🚀 Quick Usage

### Basic Parsing

```python
from backend.core.response_builder import parse_complete_analysis

# Parse both outputs
analysis = parse_complete_analysis(
    vision_output=vision_model_output,
    reasoning_output=reasoning_model_output,
    metadata={"timeframe": "4H", "asset": "BTC/USD"}
)

# Access structured data
print(analysis.vision.chart_type)
print(analysis.reasoning.strategy_bias.bias)
print(analysis.reasoning.regime.regime)
```

### Streamlit Format

```python
from backend.core.response_builder import ResponseParser

parser = ResponseParser()

# Convert to Streamlit-optimized format
streamlit_data = parser.to_streamlit_format(analysis)

# Use in Streamlit
st.write(streamlit_data["analysis"]["strategy_bias"]["bias"])
st.write(streamlit_data["analysis"]["strategy_bias"]["confidence"])
```

---

## 📋 Section Parsing

### Vision Sections

The parser extracts these sections from vision output:

1. **Chart Type & Timeframe**
   - Pattern: `Chart Type: Candlestick chart, 4-hour timeframe`
   - Splits on comma to separate type and timeframe

2. **Price Structure**
   - Extracts entire section after "Price Structure:" header
   - Preserves multi-line descriptions

3. **Technical Indicators**
   - Extracts list items from "Technical Indicators" section
   - Returns: `["EMA 20", "RSI at 68", "MACD positive"]`

4. **Visual Patterns**
   - Extracts list items from "Visual Patterns" section
   - Returns: `["Higher lows", "Consolidation"]`

5. **Momentum Signals**
   - Extracts entire section after "Momentum Signals:" header

### Reasoning Sections

The parser extracts these 7 sections:

1. **Market Structure** → `MarketStructure`
   - Trend description (first paragraph)
   - Key levels (support/resistance)
   - Structural notes

2. **Momentum** → `MomentumAnalysis`
   - Assessment (first paragraph)
   - Indicators mentioned
   - Divergences
   - Strength classification

3. **Regime** → `RegimeClassification`
   - Classification (Trending/Ranging/etc.)
   - Reasoning
   - Volatility

4. **Strategy Bias** → `StrategyBiasAnalysis`
   - Bias (Bullish/Bearish/Neutral)
   - Confidence (High/Medium/Low)
   - Reasoning points

5. **Suitable Approaches** → `SuitableApproaches`
   - List of approaches with rationales
   - Recommended approach (if marked)

6. **Invalidation** → `InvalidationConditions`
   - Bullish invalidation conditions
   - Bearish invalidation conditions
   - Key decision levels

7. **Risks** → `RiskConsiderations`
   - Risk list
   - Conflicting signals
   - Monitoring points
   - Uncertainty note

---

## 🔧 Advanced Usage

### Custom Parser

```python
from backend.core.response_builder import ResponseParser

parser = ResponseParser()

# Parse vision only
vision = parser.parse_vision_output(vision_text)
print(vision.indicators_detected)

# Parse reasoning only
reasoning = parser.parse_reasoning_output(reasoning_text)
print(reasoning.strategy_bias.bias)
```

### Convert to Dictionary

```python
# For JSON serialization
data_dict = parser.to_dict(analysis)

# For API response
import json
json_output = json.dumps(data_dict, indent=2)
```

### Access Nested Data

```python
# Strategy bias
bias = analysis.reasoning.strategy_bias.bias
confidence = analysis.reasoning.strategy_bias.confidence
reasoning = analysis.reasoning.strategy_bias.reasoning

# Invalidation conditions
bullish_invalid = analysis.reasoning.invalidation.bullish_invalidation
bearish_invalid = analysis.reasoning.invalidation.bearish_invalidation

# Approaches
for approach in analysis.reasoning.suitable_approaches.approaches:
    print(f"{approach['name']}: {approach['rationale']}")
```

---

## 🛡️ Error Handling

### Graceful Degradation

The parser handles errors gracefully:

```python
# Malformed input
bad_output = "This is not a proper analysis"

# Still returns valid structure
analysis = parser.parse_vision_output(bad_output)
# Returns: VisionAnalysis with default values

reasoning = parser.parse_reasoning_output(bad_output)
# Returns: ReasoningAnalysis with fallback structure
```

### Fallback Values

When sections are missing:
- Vision: Returns empty lists, "Not available" strings
- Reasoning: Returns minimal valid structure
- No exceptions raised - always returns valid dataclass

---

## 📊 Streamlit Integration

### Display Strategy Bias

```python
import streamlit as st

data = parser.to_streamlit_format(analysis)
bias_data = data["analysis"]["strategy_bias"]

# Display with color coding
bias = bias_data["bias"]
if "Bullish" in bias:
    st.success(f"**Strategy Bias:** {bias}")
elif "Bearish" in bias:
    st.error(f"**Strategy Bias:** {bias}")
else:
    st.info(f"**Strategy Bias:** {bias}")

st.write(f"**Confidence:** {bias_data['confidence']}")

# Display reasoning
for reason in bias_data["reasoning"]:
    st.write(f"- {reason}")
```

### Display Invalidation Conditions

```python
data = parser.to_streamlit_format(analysis)
invalidation = data["analysis"]["invalidation"]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Bullish Invalidated If:")
    for condition in invalidation["bullish"]:
        st.write(f"- {condition}")

with col2:
    st.subheader("Bearish Invalidated If:")
    for condition in invalidation["bearish"]:
        st.write(f"- {condition}")
```

### Display Approaches

```python
data = parser.to_streamlit_format(analysis)
approaches = data["analysis"]["approaches"]

st.subheader("Suitable Trading Approaches")

for approach in approaches["options"]:
    is_recommended = approach["name"] == approaches["recommended"]
    
    if is_recommended:
        st.success(f"**{approach['name']}** ⭐ (Recommended)")
    else:
        st.write(f"**{approach['name']}**")
    
    st.write(f"*{approach['rationale']}*")
    st.write("")
```

---

## 🧪 Testing

### Run Tests

```bash
pytest tests/test_response_builder.py -v
```

### Test Coverage

- ✅ Vision output parsing
- ✅ Reasoning output parsing
- ✅ Missing sections handling
- ✅ Malformed input handling
- ✅ Complete analysis parsing
- ✅ Streamlit format conversion
- ✅ List item extraction
- ✅ Markdown cleaning

**Result: 12/12 tests passing**

---

## 📁 Files

- [`response_builder.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/backend/core/response_builder.py) - Implementation
- [`test_response_builder.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/tests/test_response_builder.py) - Tests

---

## 💡 Best Practices

1. **Always use parse_complete_analysis()** for full pipeline
2. **Check for empty lists** before displaying
3. **Use Streamlit format** for dashboard rendering
4. **Log raw_output** for debugging
5. **Handle None values** in timeframe and optional fields

---

**Version**: 1.0.0  
**Status**: Production-ready  
**Test Coverage**: 100%
