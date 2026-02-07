# ChartSense 📊

AI-powered trading chart analysis tool powered by Qwen Vision and Llama reasoning models.

> **Live Demo**: [Coming Soon]

## 🎯 Overview

ChartSense analyzes TradingView chart screenshots using cutting-edge AI vision and reasoning models to provide:

- 📊 **Market Structure Analysis** - Trend identification and key levels
- 📈 **Momentum Assessment** - Indicator analysis and divergences
- 🎯 **Market Regime Classification** - Trending, ranging, or indecisive
- 💡 **Strategy Bias** - Bullish/bearish/neutral with confidence scores
- 🚨 **Invalidation Conditions** - Clear stop-loss scenarios
- 💬 **AI Chat Assistant** - Discuss analysis interactively

**⚠️ DISCLAIMER:** This tool provides decision-support only. Not financial advice. Do not use for trade execution.

---

## 🚀 Quick Start

### Option 1: Production (Netlify - Recommended)

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete production deployment guide.

**Quick Deploy to Netlify**:
1. Fork this repository
2. Connect to Netlify
3. Add `HF_API_KEY` environment variable
4. Deploy! 🎉

### Option 2: Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/chartsense.git
cd chartsense

# 2. Set up Python backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up React frontend
cd frontend-react
npm install

# 4. Configure environment
cp .env.example .env
# Edit .env and add your Hugging Face API key

# 5. Run development servers
# Terminal 1 - Backend API
cd backend
uvicorn api:app --reload

# Terminal 2 - React Frontend
cd frontend-react
npm start
```

Visit http://localhost:3000

---

## 📁 Project Structure

```
chartsense/
├── frontend-react/         # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.js         # Main app component
│   │   └── index.js       # Entry point
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
│
├── backend/               # Python backend
│   ├── api.py            # FastAPI REST API
│   ├── config.py         # Configuration
│   ├── core/             # Core functionality
│   │   ├── hf_client.py  # Hugging Face API client
│   │   ├── image_processor.py  # Image processing
│   │   └── response_builder.py # Response formatting
│   ├── services/         # Business logic
│   │   └── orchestrator.py  # Analysis orchestration
│   └── utils/            # Utilities
│       ├── safety.py     # Safety checks
│       └── rate_limiter.py  # Rate limiting
│
├── netlify/              # Netlify serverless functions
│   └── functions/
│       ├── analyze.py    # Chart analysis endpoint
│       └── requirements.txt
│
├── tests/                # Test suite
├── netlify.toml          # Netlify configuration
├── requirements.txt      # Python dependencies
├── DEPLOYMENT.md         # Production deployment guide
├── SECURITY.md          # Security checklist
└── README.md            # This file
```

---

## ✨ Features

### ✅ Current Features (Production Ready)

**Frontend**:
- 🎨 Modern React UI with dark mode
- 📤 Drag-and-drop image upload
- 🖼️ Image preview
- 📊 Comprehensive analysis display
- 💬 Interactive AI chat
- 📱 Fully responsive design
- ⚡ Real-time analysis

**Backend**:
- 🤖 Qwen 2.5 VL 7B for chart vision analysis
- 🧠 Llama 3.3 70B for reasoning and strategy
- 🔄 Automatic model fallback
- ⚡ Optimized for performance
## 🎮 Usage

1. **📸 Upload Chart**: Drag and drop a TradingView screenshot (PNG/JPG/WEBP)
2. **⏱️ Wait for AI**: Analysis takes 30-60 seconds
3. **📊 Review Results**: See comprehensive breakdown:
   - Vision Analysis (what AI sees)
   - Market Structure
   - Momentum Assessment
   - Regime Classification
   - Strategy Bias
   - Trading Signals
4. **💬 Chat with AI**: Ask follow-up questions about the analysis

---

## 🛠️ Technology Stack

**Frontend**:
- React 18
- Axios for HTTP
- Framer Motion for animations
- Lucide React for icons
- Modern CSS with custom dark theme

**Backend**:
- FastAPI (Python 3.11)
-  🧪 Development

### Running Tests

```bash
# Python backend tests
pytest tests/ -v

# Run specific test
pytest tests/test_hf_client.py -v

# With coverage
pytest --cov=backend tests/
```

### Code Quality

```bash
# Format Python code
black backend/ tests/

# Lint
ruff check backend/ tests/

# Type checking
mypy backend/
```

### Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run tests: `pytest`
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature/your-feature`
6. Create pull request

---

## 🚀 Deployment

### Production Deployment (Netlify)

**Quick Deploy**:
```⚠️ Disclaimer

**IMPORTANT: READ BEFORE USING**

This tool is for **educational and informational purposes only**. It does NOT constitute:
- Financial advice
- Investment advice
- Trading advice
- Professional consultation

**Key Points**:
- AI analysis may contain errors or biases
- Past performance doesn't guarantee future results
- Trading involves significant risk of loss
- Always do your own research (DYOR)
- Consult qualified financial advisors
- Never invest more than you can afford to lose

**Use at your own risk**. The creators assume no liability for trading losses.

---

## 📞 Support

### Getting Help

1. **📖 Documentation**: Review [DEPLOYMENT.md](DEPLOYMENT.md) and [SECURITY.md](SECURITY.md)
2. **🐛 Known Issues**: Check [GitHub Issues](https://github.com/yourusername/chartsense/issues)
3. **💬 Discussions**: Use [GitHub Discussions](https://github.com/yourusername/chartsense/discussions)
4. **📧 Contact**: Open an issue for bugs or questions

### Reporting Bugs

Include:
- Browser/OS version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Console errors

### Security Issues

**DO NOT** open public issues for security vulnerabilities.
See [SECURITY.md](SECURITY.md) for responsible disclosure process.

---

## 🙏 Acknowledgments

- **Hugging Face** - AI model hosting and inference
- **Qwen Team** - Vision model (Qwen2.5-VL)
- **Meta AI** - Reasoning model (Llama 3.3)
- **Netlify** - Hosting and deployment platform
- **React Community** - Frontend framework

---

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **API Docs**: `/api/docs` (development mode)
- **GitHub**: [Repository Link]

---

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Last Updated**: February 7, 2026

Built with ❤️ for the trading community
# 4. Deploy automatically happens on push!
```

**Detailed Guide**: See **[DEPLOYMENT.md](DEPLOYMENT.md)**

### Manual Deploy (Netlify CLI)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod
```

---

## 💰 Cost & Limits

### Free Tier (Recommended for MVP)

**Netlify**:
- 300 build minutes/month
- 125,000 function requests/month
- 100 GB bandwidth/month
- **Cost**: $0 ✅

**Hugging Face**:
- Rate limits apply (varies by model)
- Generous free tier
- **Cost**: $0 ✅

**Total Monthly Cost**: **$0** 🎉

### Scaling Needs

- **1k users/month**: Stay on free tier
- **10k users/month**: Consider Netlify Pro ($19/month)
- **100k+ users**: Need dedicated infrastructure

---

## 🔒 Security

### Best Practices Implemented

- ✅ Environment variables for secrets
- ✅ No sensitive data in repository
- ✅ HTTPS enforced
- ✅ Security headers configured
- ✅ Input validation
- ✅ CORS properly configured
- ✅ Rate limiting via Netlify
- ✅ Image size and type validation

See **[SECURITY.md](SECURITY.md)** for complete security checklist.

---

## 📊 Performance

**Target Metrics**:
- Page Load: < 2 seconds
- Analysis Time: 30-60 seconds (AI processing)
- Uptime: 99.9% (Netlify SLA)

**Optimizations**:
- CDN for static assets
- Serverless functions for backend
- Lazy loading images
- Code splitting

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

**Areas needing help**:
- Additional indicator support
- Mobile UI improvements
- Performance optimizations
- Documentation improvements

---

## 📝 Changelog

### v1.0.0 (2026-02-07) - Production Ready
- ✅ Full React frontend
- ✅ FastAPI backend with AI integration
- ✅ Netlify serverless deployment
- ✅ Production security hardening
- ✅ Comprehensive documentation

---

## ⚖️ License

MIT License - See [LICENSE](LICENSE) file for details.

---
### Getting Hugging Face API Key

1. Sign up at [huggingface.co](https://huggingface.co)
2. Go to **Settings** → **Access Tokens**
3. Click **New token**
4. Select **Read** permission
5. Copy token (starts with `hf_`)

**Cost**: Free tier available! 🎉

---

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete production deployment guide
- **[SECURITY.md](SECURITY.md)** - Security checklist and best practices
- **[backend/core/README_*.md](backend/core/)** - Component documentation
- **[PRD.txt](PRD.txt)** - Product requirements

---sults**: See structured analysis in 5 sections

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
