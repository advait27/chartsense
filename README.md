# Chartered 📊

AI-powered trading chart analysis tool for decision support.

## Overview

Chartered analyzes TradingView chart screenshots using AI vision and reasoning models to provide:
- Market structure analysis
- Momentum assessment
- Market regime identification
- Strategy bias (bullish/bearish/neutral)
- Invalidation conditions

**⚠️ DISCLAIMER:** This tool provides decision-support only. Not financial advice. Do not use for trade execution.

## Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to project directory
cd chartered

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Hugging Face API key
```

### 2. Get Hugging Face API Key

1. Sign up at [huggingface.co](https://huggingface.co)
2. Go to Settings → Access Tokens
3. Create a new token with "Read" permissions
4. Copy token to `.env` file

### 3. Run Application

**Option 1: Frontend Only (with mock data)**
```bash
streamlit run frontend/app.py
```

**Option 2: Full Stack (when backend is ready)**
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
streamlit run frontend/app.py
```

## Project Structure

```
chartered/
├── frontend/           # Streamlit UI
│   ├── app.py         # Main application
│   └── config.py      # Frontend config
├── backend/           # FastAPI backend (to be implemented)
├── requirements.txt   # Python dependencies
├── .env.example      # Environment template
└── README.md         # This file
```

## Features

### Current (MVP)
- ✅ Image upload (drag-and-drop or click)
- ✅ Image preview
- ✅ Trader-friendly dark mode UI
- ✅ Structured analysis output
- ✅ Mock data for testing UI
- ✅ Persistent disclaimers

### Coming Soon
- 🔄 Backend API integration
- 🔄 Real AI model analysis
- 🔄 Analysis history
- 🔄 Export results

## Usage

1. **Upload Chart**: Drag and drop a TradingView screenshot (PNG/JPG)
2. **Add Context** (optional): Specify timeframe and asset
3. **Analyze**: Click "Analyze Chart" button
4. **Review Results**: See structured analysis in 5 sections

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI (planned)
- **AI Models**: Hugging Face Inference API
  - Vision: BLIP-2 or LLaVA
  - Reasoning: Llama-2 or Mistral
- **Image Processing**: Pillow

## Configuration

Edit `.env` file:

```bash
HF_API_KEY=your_key_here          # Required for AI models
BACKEND_URL=http://localhost:8000  # Backend API URL
LOG_LEVEL=INFO                     # Logging level
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
# Format code
black .

# Lint
ruff check .
```

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add `HF_API_KEY` to secrets
4. Deploy

### Docker (Coming Soon)
```bash
docker-compose up
```

## Limitations (Free Tier)

- Hugging Face API: ~30 requests/hour per model
- Processing time: 30-60 seconds per chart
- No persistent storage (session-based only)

## Support

For issues or questions:
1. Check existing issues on GitHub
2. Review documentation
3. Create new issue with details

## License

MIT License - See LICENSE file

## Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice, investment advice, trading advice, or any other sort of advice. You should not treat any of the tool's content as such. Do your own research and consult with a qualified financial advisor before making any investment decisions.

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-28
