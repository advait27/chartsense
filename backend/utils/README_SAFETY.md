# Safety Layer - Quick Reference

## 🎯 Quick Usage

```python
from backend.utils.safety import validate_and_sanitize

# Validate AI output
is_safe, sanitized_output, warnings = validate_and_sanitize(
    output=ai_text,
    confidence="Medium",
    strict_mode=True
)

if is_safe:
    display(sanitized_output)
else:
    display(sanitized_output)  # Contains blocked message
```

---

## ⚠️ Disclaimers

### Short (Top of Page)
```
⚠️ Educational purposes only. Not financial advice. 
Trading involves substantial risk.
```

### Full (Bottom of Page)
```
This analysis is for educational and informational purposes only. 
It is NOT financial advice, investment advice, or a recommendation 
to buy, sell, or hold any asset.
```

---

## 🚫 Prohibited Language

### Financial Advice
- ❌ "You should buy/sell"
- ❌ "I recommend buying"
- ✅ "Traders might consider..."

### Trade Instructions
- ❌ "Enter at $50,000"
- ❌ "Stop loss at $48,000"
- ✅ "Support appears near $50,000"

### Price Predictions
- ❌ "Will reach $60,000"
- ❌ "Price will be $X"
- ✅ "Could move toward $60,000"

### Guaranteed Outcomes
- ❌ "Guaranteed to work"
- ❌ "100% certain"
- ✅ "Suggests potential for..."

---

## ✅ Required Language

**Use Probabilistic Terms:**
- "may", "might", "could"
- "suggests", "indicates", "appears"
- "typically", "potentially", "possible"

**Confidence Levels:**
- High (0.8-1.0): Strong signals
- Medium (0.5-0.7): Mixed signals
- Low (0.0-0.4): Unclear → **BLOCKED**

**Minimum Threshold:** 0.3

---

## 🔧 Enforcement

### Basic Validation
```python
from backend.utils.safety import SafetyValidator

validator = SafetyValidator(strict_mode=True)
result = validator.validate_output(ai_text, confidence="Medium")

if result.level == SafetyLevel.BLOCKED:
    show_blocked_message()
elif result.level == SafetyLevel.WARNING:
    show_with_warnings(result.modified_output)
else:
    show_safe_output(result.modified_output)
```

### Disclaimer Injection
```python
from backend.utils.safety import inject_disclaimer

output = inject_disclaimer(text, position='both')
```

### Output Sanitization
```python
validator = SafetyValidator()
sanitized = validator.sanitize_output(unsafe_text)

# Replacements:
# "will" → "may"
# "should" → "could"
# "definitely" → "potentially"
# "guaranteed" → "possible"
```

---

## 🚨 Safe Failure Messages

### Low Confidence
```
Analysis Unavailable

The AI analysis did not meet our confidence threshold.

Try:
- Clearer chart image
- Ensure indicators are visible
- Provide context (timeframe, asset)
```

### Blocked Output
```
Analysis Blocked

Safety system detected:
- Financial Advice
- Trade Instructions
- Guaranteed Outcomes

This is a protective measure.
```

---

## 📊 Safety Check Flow

```
AI Output
    ↓
Check Prohibited Patterns
    ↓
Assess Confidence (≥ 0.3?)
    ↓
Inject Disclaimer
    ↓
├─ SAFE → Display
├─ WARNING → Sanitize + Display
└─ BLOCKED → Show failure message
```

---

## 📁 Files

- [`safety.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/backend/utils/safety.py) - Implementation
- [`test_safety.py`](file:///Users/advaitdharmadhikari/Documents/Personal%20Projects/chartsense/tests/test_safety.py) - Tests (19/19 passing)
- [`safety_governance.md`](file:///Users/advaitdharmadhikari/.gemini/antigravity/brain/813735fb-9a53-4334-9140-8fe5d686e605/safety_governance.md) - Full documentation

---

**Version**: 1.0.0  
**Test Coverage**: 19/19 passing (100%)  
**Status**: Production-ready
