# 🚀 Vercel Deployment Guide

Complete guide to deploy ChartSense to production on Vercel.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Vercel Deployment](#vercel-deployment)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required Accounts
1. **GitHub Account** - For repository hosting
2. **Vercel Account** - For deployment (free tier available at [vercel.com](https://vercel.com))
3. **Hugging Face Account** - For AI API access (free tier available)

### Required Tools (for local development)
- Node.js 18+
- Python 3.11+
- Git

---

## Quick Start

### Step 1: Get Your Hugging Face API Key

1. Sign up at [huggingface.co](https://huggingface.co)
2. Go to **Settings** → **Access Tokens**
3. Click **New token**
4. Name it `chartsense-production`
5. Select **Read** permission
6. Copy the token (starts with `hf_...`)

⚠️ **Important**: Keep this key secure! Never commit it to GitHub.

---

## Environment Variables

### Required Environment Variables

Set these in **Vercel Dashboard** → **Project Settings** → **Environment Variables**:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `HF_API_KEY` | ✅ Yes | Hugging Face API key | `hf_xxxxxxxxxxxxx` |
| `LOG_LEVEL` | ⭕ Optional | Logging verbosity | `INFO` (default) |
| `VISION_MODEL` | ⭕ Optional | Vision AI model | `Qwen/Qwen2.5-VL-7B-Instruct` |
| `REASONING_MODEL` | ⭕ Optional | Reasoning AI model | `meta-llama/Llama-3.3-70B-Instruct` |

### Build Environment Variables (Automatic)

These are set in `vercel.json` and applied during build:

```json
{
  "REACT_APP_API_URL": "/api",
  "PYTHON_VERSION": "3.11",
  "NODE_VERSION": "18"
}
```

---

## Vercel Deployment

### Method 1: Vercel Dashboard (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click **Add New** → **Project**
   - Click **Import** next to your GitHub repository
   - Authorize Vercel to access your repo if needed

3. **Configure Project**
   - **Framework Preset**: Vercel will auto-detect React
   - **Root Directory**: Leave as `./` (root)
   - **Build Command**: `cd frontend-react && npm ci && npm run build`
   - **Output Directory**: `frontend-react/build`
   - **Install Command**: `npm install --prefix frontend-react`
   
   ℹ️ These are configured in `vercel.json` already!

4. **Set Environment Variables**
   - Click **Environment Variables**
   - Add `HF_API_KEY`:
     - **Name**: `HF_API_KEY`
     - **Value**: Your Hugging Face token
     - **Environment**: All (Production, Preview, Development)
   - Click **Add**

5. **Deploy**
   - Click **Deploy**
   - Wait 2-4 minutes for build to complete
   - Your site will be live at `https://your-project.vercel.app`

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Set environment variables
vercel env add HF_API_KEY
# Enter your HF API key when prompted
# Choose: Production, Preview, and Development
```

### Method 3: GitHub Integration (Auto-Deploy)

1. Connect Vercel to your GitHub repo (Method 1)
2. Every push to `main` automatically deploys to production
3. Pull requests automatically get preview deployments
4. Instant rollbacks available

---

## Post-Deployment

### 1. Verify Deployment

✅ **Test the following**:
- [ ] Homepage loads at your Vercel URL
- [ ] Upload section is visible
- [ ] Try uploading a chart image
- [ ] Analysis completes (30-60 seconds)
- [ ] Chat interface works (if enabled)
- [ ] No console errors in browser
- [ ] Check `/api/analyze` returns {"status": "online"}

### 2. Configure Custom Domain (Optional)

1. Go to **Project Settings** → **Domains**
2. Click **Add Domain**
3. Enter your domain (e.g., `chartsense.com`)
4. Follow DNS configuration instructions
5. Vercel automatically provisions SSL certificate

### 3. Configure Production Settings

**In Project Settings**:
- **Environment Variables**: Review all variables
- **Git**: Configure auto-deploy branches
- **Deployment Protection**: Enable password protection if needed
- **Analytics**: Enable Web Analytics (optional, free)

---

## Vercel-Specific Features

### Automatic HTTPS
✅ SSL certificates automatically provisioned and renewed

### Edge Network
✅ Global CDN with 100+ edge locations

### Instant Rollbacks
```bash
# View deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-url]
```

### Preview Deployments
- Every PR gets a unique preview URL
- Test changes before merging
- Share with team for review

### Environment Variables per Environment
- **Production**: Live site
- **Preview**: Pull request previews
- **Development**: Local development

---

## Project Structure

```
chartsense/
├── api/                      # Vercel serverless functions
│   ├── analyze.py           # Chart analysis endpoint
│   └── requirements.txt     # Python dependencies
│
├── frontend-react/          # React application
│   ├── src/
│   ├── public/
│   ├── build/               # Build output (created)
│   └── package.json
│
├── backend/                 # Shared Python backend
│   ├── core/
│   ├── services/
│   └── utils/
│
└── vercel.json             # Vercel configuration
```

---

## Troubleshooting

### Common Issues

#### 1. Build Fails - Module Not Found
```
Error: Cannot find module 'react-scripts'
```
**Solution**: 
```bash
# Update vercel.json build settings
# Ensure correct working directory
cd frontend-react && npm ci && npm run build
```

#### 2. Python Function Timeout
```
Error: FUNCTION_INVOCATION_TIMEOUT
```
**Solution**: Function timeout is set to 120s in `vercel.json`. If still timing out:
- Check Vercel plan limits (Hobby: 10s, Pro: 60s, Enterprise: 900s)
- Optimize model parameters
- Consider upgrading plan for longer timeouts

**Note**: Free tier has 10s limit. Upgrade to Pro ($20/month) for 60s timeout needed for AI processing.

#### 3. Environment Variables Not Working
```
Error: HF_API_KEY not found
```
**Solution**:
1. Go to Vercel Dashboard
2. **Project Settings** → **Environment Variables**
3. Add `HF_API_KEY` for all environments
4. **Redeploy** (Vercel → Deployments → Redeploy)

#### 4. CORS Errors
```
Access to fetch blocked by CORS policy
```
**Solution**: CORS is configured in `vercel.json` headers. Ensure:
- Using `/api/analyze` endpoint
- Headers include Access-Control-Allow-Origin: *

#### 5. 404 on API Routes
```
GET /api/analyze 404
```
**Solution**: 
- Verify `api/analyze.py` exists
- Check `vercel.json` routes configuration
- Redeploy project

#### 6. Python Dependencies Missing
```
ModuleNotFoundError: No module named 'httpx'
```
**Solution**: Ensure `api/requirements.txt` exists with all dependencies.

### Debug Mode

View function logs:
```bash
# Real-time logs
vercel logs

# Filter by function
vercel logs --follow

# View specific deployment
vercel logs [deployment-url]
```

Or in dashboard:
- Go to **Project** → **Deployments** → Click deployment
- View **Function Logs** tab

---

## Monitoring & Maintenance

### Vercel Analytics (Free)

Enable in Project Settings:
- **Real User Monitoring** (RUM)
- **Web Vitals**
- **Page Views**
- **Top Pages**

### Function Metrics

Available in dashboard:
- Invocations per day
- Average execution time
- Error rate
- Cold starts vs. warm starts

### Deployment Notifications

Set up in **Project Settings** → **Git**:
- Slack notifications
- Email notifications
- Webhook integrations

---

## Performance Optimization

### Edge Functions (Optional Upgrade)

For better performance:
- Deploy functions to edge network
- Reduce latency globally
- Available on Pro plan

### Caching Strategy

Configured in `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

---

## Cost Breakdown

### Vercel Pricing

| Plan | Cost | Limits |
|------|------|--------|
| **Hobby** (Free) | $0 | 100 GB bandwidth, 100 build hours, 10s function timeout ⚠️ |
| **Pro** | $20/user/month | 1 TB bandwidth, 400 build hours, 60s function timeout ✅ |
| **Enterprise** | Custom | Unlimited, 900s function timeout |

### Hugging Face (Free Tier)
- ✅ API access: **FREE**
- Rate limits apply

### ⚠️ Important Note

**AI processing requires 30-60 seconds**, but Hobby plan has **10s timeout**.

**Recommendation**: 
- Start with Hobby plan for testing
- **Upgrade to Pro ($20/month) for production use**
- Pro plan gives 60s timeout needed for AI models

### Expected Monthly Cost
- **Testing**: $0 (Hobby tier, may timeout)
- **Production**: $20 (Pro tier required for AI processing)
- **High Traffic**: Pro tier handles most use cases

---

## Security Best Practices

### ✅ Implemented

- [x] Environment variables for sensitive data
- [x] `.env` excluded from git
- [x] Security headers (CSP, XSS protection)
- [x] HTTPS enforced
- [x] CORS configured
- [x] Input validation

### 🔒 Additional Recommendations

1. **Enable Deployment Protection**
   - Password protect preview deployments
   - Restrict access to staging

2. **Use Vercel Firewall** (Pro+)
   - DDoS protection
   - Rate limiting
   - IP allowlist/blocklist

3. **Rotate API Keys Regularly**
   - Update `HF_API_KEY` every 90 days

---

## Comparison: Vercel vs Netlify

| Feature | Vercel | Netlify |
|---------|--------|---------|
| Python Functions | ✅ Yes | ✅ Yes |
| Free Tier Timeout | ⚠️ 10s | ✅ 10s (configurable) |
| Pro Tier Timeout | ✅ 60s | ✅ 26s |
| Free Builds | 100 hrs/month | 300 min/month |
| Free Bandwidth | 100 GB | 100 GB |
| Best For | Next.js, React | Static sites, JAMstack |
| **For AI Apps** | ⚠️ Pro plan needed | ✅ Works on free tier |

**Note**: For CharSense specifically, **Netlify may be better for free tier** due to flexible function timeouts.

---

## Support & Resources

### Documentation
- [Vercel Docs](https://vercel.com/docs)
- [Hugging Face API Docs](https://huggingface.co/docs/api-inference)
- [Python on Vercel](https://vercel.com/docs/functions/serverless-functions/runtimes/python)

### Getting Help
1. Check [Troubleshooting](#troubleshooting) section
2. Review Vercel function logs
3. Check GitHub Issues
4. Vercel Community Forum

---

## Deployment Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] `.env` file is NOT in repository
- [ ] `HF_API_KEY` set in Vercel
- [ ] Site deployed successfully
- [ ] All tests pass
- [ ] Chart upload works
- [ ] AI analysis completes
- [ ] Chat interface functional
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] **Vercel Pro plan active** (for production)

---

## 🎉 You're Live!

Once deployed, your ChartSense application will be available at:
```
https://your-project.vercel.app
```

Or your custom domain if configured.

---

## Quick Commands Reference

```bash
# Deploy to production
vercel --prod

# View deployments
vercel ls

# View logs
vercel logs --follow

# Set environment variable
vercel env add HF_API_KEY

# Remove deployment
vercel rm [deployment-url]

# Open project in browser
vercel open

# Check deployment status
vercel inspect [deployment-url]
```

---

**Last Updated**: February 7, 2026  
**Version**: 1.0.0  
**Platform**: Vercel
