# ✅ Pre-Deployment Checklist

Use this checklist before deploying to production.

## 🔒 Security

- [ ] `.env` file is in `.gitignore`
- [ ] `.env` is NOT committed to git (verify with `git ls-files | grep .env`)
- [ ] `.env.example` exists with template values (no real keys)
- [ ] All API keys stored in environment variables only
- [ ] Reviewed [SECURITY.md](SECURITY.md)

## 📝 Configuration

- [ ] `netlify.toml` configured correctly
- [ ] `HF_API_KEY` ready (from Hugging Face)
- [ ] Environment variables documented in `.env.production`
- [ ] Frontend `.env.production` configured
- [ ] Python dependencies in `requirements.txt` up to date
- [ ] Node dependencies in `package.json` up to date

## 🧪 Testing

- [ ] All Python tests pass (`pytest`)
- [ ] Backend API runs locally (`uvicorn backend.api:app`)
- [ ] Frontend runs locally (`npm start` in frontend-react/)
- [ ] Chart upload works
- [ ] AI analysis completes successfully
- [ ] Chat interface functional (if enabled)
- [ ] No console errors in browser

## 📁 Files

### Required Files ✅
- [ ] `README.md` - Project overview
- [ ] `DEPLOYMENT.md` - Deployment guide
- [ ] `SECURITY.md` - Security checklist
- [ ] `QUICKSTART.md` - Quick deploy guide
- [ ] `netlify.toml` - Netlify configuration
- [ ] `.env.example` - Environment template
- [ ] `requirements.txt` - Python dependencies
- [ ] `runtime.txt` - Python version
- [ ] `.gitignore` - Ignore patterns

### Backend Files ✅
- [ ] `backend/api.py` - FastAPI application
- [ ] `backend/config.py` - Configuration
- [ ] `backend/core/` - Core components
- [ ] `backend/services/` - Business logic
- [ ] `backend/utils/` - Utilities

### Frontend Files ✅
- [ ] `frontend-react/package.json` - Dependencies
- [ ] `frontend-react/public/` - Static assets
- [ ] `frontend-react/src/` - React components
- [ ] `frontend-react/.env.example` - Env template
- [ ] `frontend-react/.env.production` - Production config

### Netlify Files ✅
- [ ] `netlify/functions/analyze.py` - Analysis function
- [ ] `netlify/functions/requirements.txt` - Function dependencies

## 🚀 Git Repository

- [ ] All changes committed
- [ ] No uncommitted changes (`git status`)
- [ ] Pushed to GitHub (`git push origin main`)
- [ ] Repository is public (or Netlify has access if private)
- [ ] README has clear description

## 🌐 Netlify Setup

- [ ] Netlify account created
- [ ] Repository connected to Netlify
- [ ] Build settings configured (or using netlify.toml)
- [ ] `HF_API_KEY` environment variable set in Netlify
- [ ] Custom domain configured (optional)

## 📊 Functionality

### Core Features
- [ ] Image upload (drag & drop)
- [ ] Image preview displays
- [ ] Loading animation shows during analysis
- [ ] Analysis results display correctly
- [ ] Vision analysis section populated
- [ ] Reasoning analysis section populated
- [ ] Trading signals shown
- [ ] Error messages display properly

### Optional Features
- [ ] Chat interface works (if enabled)
- [ ] Risk calculator functional (if enabled)
- [ ] Mobile responsive
- [ ] Dark mode displays correctly

## 🎨 UI/UX

- [ ] Logo/branding correct
- [ ] Colors match theme
- [ ] Typography readable
- [ ] Buttons and interactions work
- [ ] Loading states clear
- [ ] Error states user-friendly
- [ ] Disclaimer visible
- [ ] Footer information correct

## 📱 Responsive Design

Test on:
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

## 🔍 Performance

- [ ] Images optimized
- [ ] No unnecessary console logs in production
- [ ] Bundle size reasonable (<2MB)
- [ ] Initial load time acceptable (<3s)
- [ ] Function timeout configured (120s)

## 📚 Documentation

- [ ] README.md complete
- [ ] DEPLOYMENT.md detailed
- [ ] SECURITY.md reviewed
- [ ] QUICKSTART.md tested
- [ ] Code comments adequate
- [ ] API endpoints documented

## ⚖️ Legal & Compliance

- [ ] Disclaimer visible and clear
- [ ] License file present (MIT)
- [ ] No copyrighted content without permission
- [ ] Privacy policy (if collecting user data)
- [ ] Terms of service (if required)

## 🎯 Post-Deployment

After deploying:
- [ ] Site accessible at Netlify URL
- [ ] Test full user flow
- [ ] Check function logs in Netlify
- [ ] Monitor for errors
- [ ] Share with test users
- [ ] Set up monitoring alerts

## 🐛 Known Issues

Document any known issues:
- [ ] List any bugs or limitations
- [ ] Add to GitHub Issues if needed
- [ ] Update README if critical

## 📈 Monitoring Setup

- [ ] Netlify analytics enabled (optional, paid)
- [ ] Function logs accessible
- [ ] Error tracking configured (optional)
- [ ] Uptime monitoring (optional)

## 💰 Cost Verification

- [ ] Using Netlify free tier
- [ ] HuggingFace free tier sufficient
- [ ] No unexpected charges
- [ ] Understand scaling costs

---

## Quick Verification Commands

Run these before deploying:

```bash
# Check git status
git status

# Verify .env not tracked
git ls-files | grep -E "^\.env$" && echo "❌ .env is tracked!" || echo "✅ .env not tracked"

# Check Python tests
pytest tests/ -v

# Check for security issues
# (install if needed: pip install safety)
safety check

# Check for outdated packages
pip list --outdated

# Frontend build test
cd frontend-react && npm run build && cd ..

# Check bundle size
cd frontend-react/build && du -sh * && cd ../..
```

---

## Score Your Readiness

Count your checkmarks:

- **70-80%**: Good to deploy to staging
- **80-90%**: Ready for production
- **90-100%**: Production ready with confidence! ✅

---

## Final Checks Before Deploy

1. ✅ All critical items checked above
2. ✅ Tests passing
3. ✅ No secrets in repository
4. ✅ Documentation complete
5. ✅ Emergency rollback plan (revert last commit)

---

**Ready?** 🚀

Follow [QUICKSTART.md](QUICKSTART.md) for deployment!

Or detailed guide in [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Last Updated**: February 7, 2026
