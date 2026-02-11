# ✅ Netlify Deployment Checklist

**Status**: Project is ready for Netlify deployment!

## Pre-Deployment Verification ✓

### ✅ Configuration Files
- [x] `netlify.toml` - Build and function settings configured
- [x] `netlify/functions/` - Serverless functions ready
- [x] `netlify/functions/requirements.txt` - Python dependencies listed
- [x] `netlify/functions/runtime.txt` - Python 3.11 specified
- [x] `.gitignore` - Sensitive files excluded (`.env`)
- [x] `frontend-react/package.json` - React dependencies configured

### ✅ Security
- [x] `.env` file is in `.gitignore` ✓
- [x] HF_API_KEY not committed to repository ✓
- [x] Environment variables documented

### ✅ Code Status
- [x] Git working tree is clean
- [x] All changes committed
- [x] Ready to push to GitHub

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub
```bash
# If you haven't already pushed
git push origin main
```

### Step 2: Deploy to Netlify

#### Option A: Netlify Dashboard (Recommended)
1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **GitHub** and authorize Netlify
4. Select repository: `advait27/chartsense`
5. Build settings (auto-detected from `netlify.toml`):
   - **Base directory**: `frontend-react`
   - **Build command**: `npm ci && npm run build`
   - **Publish directory**: `frontend-react/build`
   - **Functions directory**: `netlify/functions`
6. Click **"Deploy site"**

#### Option B: Netlify CLI
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod
```

### Step 3: Configure Environment Variables

⚠️ **CRITICAL**: Add your Hugging Face API key in Netlify

1. In Netlify dashboard, go to your site
2. Navigate to **Site settings** → **Environment variables**
3. Click **"Add a variable"**
4. Add the following:

| Variable Name | Value | Required |
|---------------|-------|----------|
| `HF_API_KEY` | `hf_xxxxxxxxxxxxx` | ✅ Yes |
| `LOG_LEVEL` | `INFO` | Optional |
| `VISION_MODEL` | `Qwen/Qwen2.5-VL-7B-Instruct` | Optional |
| `REASONING_MODEL` | `meta-llama/Llama-3.3-70B-Instruct` | Optional |

4. Click **"Save"**
5. Netlify will automatically redeploy with the new environment variables

### Step 4: Verify Deployment

Once deployed, Netlify will provide a URL like: `https://your-site-name.netlify.app`

Test the following:
- [ ] Frontend loads correctly
- [ ] Can upload a chart image
- [ ] Analysis returns results (tests HF_API_KEY)
- [ ] Chat function works

---

## 🔧 Post-Deployment Configuration

### Custom Domain (Optional)
1. In Netlify dashboard → **Domain settings**
2. Click **"Add custom domain"**
3. Follow DNS configuration instructions

### Function Logs
- View logs: Netlify dashboard → **Functions** tab
- Monitor errors and performance
- Check cold start times

### Performance Monitoring
- Netlify dashboard → **Analytics**
- Track function invocations
- Monitor bandwidth usage

---

## 📋 Environment Variables Reference

### Required
```bash
HF_API_KEY=hf_xxxxxxxxxxxxx    # Get from https://huggingface.co/settings/tokens
```

### Optional (with defaults)
```bash
LOG_LEVEL=INFO
VISION_MODEL=Qwen/Qwen2.5-VL-7B-Instruct
REASONING_MODEL=meta-llama/Llama-3.3-70B-Instruct
VISION_TIMEOUT=25
REASONING_TIMEOUT=45
TOTAL_TIMEOUT=75
```

---

## 🐛 Troubleshooting

### Build Fails
- Check build logs in Netlify dashboard
- Verify Node.js version (18) in logs
- Ensure all dependencies in `package.json`

### Functions Fail
- Check function logs in Netlify dashboard
- Verify `HF_API_KEY` is set in environment variables
- Check Python version is 3.11
- Verify `netlify/functions/requirements.txt` has all dependencies

### API Errors
- 503 Error: `HF_API_KEY` not set or invalid
- Timeout: Function execution exceeded 26s (free tier limit)
- 500 Error: Check function logs for Python errors

### Frontend Issues
- Clear browser cache
- Check browser console for errors
- Verify API URL in Network tab

---

## 📚 Additional Resources

- [Netlify Deploy Docs](https://docs.netlify.com/site-deploys/create-deploys/)
- [Netlify Functions](https://docs.netlify.com/functions/overview/)
- [Environment Variables](https://docs.netlify.com/environment-variables/overview/)
- [HuggingFace API](https://huggingface.co/docs/api-inference/index)

---

## 🎯 Quick Deploy Commands

```bash
# Full deployment flow
git add .
git commit -m "Ready for production"
git push origin main

# Then deploy via Netlify dashboard or:
netlify deploy --prod
```

---

## ✨ Your Next Steps

1. ✅ Push code to GitHub (`git push origin main`)
2. ✅ Connect repository to Netlify
3. ✅ Add `HF_API_KEY` in Netlify environment variables
4. ✅ Test deployment
5. 🎉 Share your deployed ChartSense app!

**Deployment URL**: Will be assigned by Netlify (e.g., `https://chartsense-ai.netlify.app`)

---

**Need help?** Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions or [QUICKSTART.md](./QUICKSTART.md) for a streamlined guide.
