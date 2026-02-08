# 🚀 Production Deployment Guide

Complete guide to deploy ChartSense to production on Netlify.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Netlify Deployment](#netlify-deployment)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required Accounts
1. **GitHub Account** - For repository hosting
2. **Netlify Account** - For deployment (free tier available)
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

Set these in **Netlify Dashboard** → **Site Settings** → **Environment Variables**:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `HF_API_KEY` | ✅ Yes | Hugging Face API key | `hf_xxxxxxxxxxxxx` |
| `LOG_LEVEL` | ⭕ Optional | Logging verbosity | `INFO` (default) |
| `VISION_MODEL` | ⭕ Optional | Vision AI model | `Qwen/Qwen2.5-VL-7B-Instruct` |
| `REASONING_MODEL` | ⭕ Optional | Reasoning AI model | `meta-llama/Llama-3.3-70B-Instruct` |

### Frontend Environment Variables (Build-time)

These are set in `netlify.toml` and embedded during build:

```toml
REACT_APP_API_URL = "/.netlify/functions"
REACT_APP_ENABLE_CHAT = "true"
REACT_APP_VERSION = "1.0.0"
```

---

## Netlify Deployment

### Method 1: Direct GitHub Connection (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Production ready"
   git push origin main
   ```

2. **Connect to Netlify**
   - Go to [Netlify Dashboard](https://app.netlify.com)
   - Click **Add new site** → **Import an existing project**
   - Choose **GitHub** and authorize
   - Select your `chartsense` repository

3. **Configure Build Settings**
   - **Base directory**: `frontend-react`
   - **Build command**: `npm ci && npm run build`
   - **Publish directory**: `frontend-react/build`
   - **Functions directory**: `netlify/functions`
   
   ℹ️ These are already configured in `netlify.toml`

4. **Set Environment Variables**
   - In Netlify, go to **Site settings** → **Environment variables**
   - Click **Add a variable**
   - Add `HF_API_KEY` with your Hugging Face token
   - Add any optional variables

5. **Deploy**
   - Click **Deploy site**
   - Wait 3-5 minutes for build to complete
   - Your site will be live at `https://your-site-name.netlify.app`

### Method 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize site
netlify init

# Set environment variables
netlify env:set HF_API_KEY "your_actual_key_here"

# Deploy to production
netlify deploy --prod
```

---

## Post-Deployment

### 1. Verify Deployment

✅ **Test the following**:
- [ ] Homepage loads correctly
- [ ] Upload section is visible
- [ ] Try uploading a chart image
- [ ] Analysis completes successfully
- [ ] Chat interface works (if enabled)
- [ ] No console errors

### 2. Configure Custom Domain (Optional)

1. Go to **Domain settings** in Netlify
2. Click **Add custom domain**
3. Follow DNS configuration instructions
4. Enable HTTPS (automatic with Netlify)

### 3. Set Up Monitoring

1. **Function Monitoring**
   - Go to **Functions** tab in Netlify
   - Monitor invocations, errors, and duration
   
2. **Build Notifications**
   - **Settings** → **Build & deploy** → **Deploy notifications**
   - Add Slack/Email notifications

3. **Error Tracking** (Optional)
   - Integrate Sentry or similar
   - Add to frontend for client-side error tracking

---

## Troubleshooting

### Common Issues

#### 1. Build Fails
```
Error: Cannot find module 'react-scripts'
```
**Solution**: Make sure `package.json` is in `frontend-react/` and `netlify.toml` has correct base directory.

#### 2. Function Timeout
```
Error: Function timeout after 10 seconds
```
**Solution**: On the free tier, Netlify limits function duration (e.g. 26s). Analysis can take 30–60s. Options:
- Set `[functions."analyze"] timeout = 26` in `netlify.toml` (max on free tier)
- Upgrade to Netlify Pro for longer timeouts if needed
- Optimize model parameters or use a faster model for MVP

#### 3. CORS Errors
```
Access to fetch blocked by CORS policy
```
**Solution**: CORS is configured in `netlify.toml`. Ensure:
- Using `/.netlify/functions/analyze` endpoint
- Headers are correct in function response

#### 4. Missing Environment Variables
```
Error: HF_API_KEY not found
```
**Solution**:
1. Go to Netlify Dashboard
2. **Site settings** → **Environment variables**
3. Add `HF_API_KEY`
4. **Trigger deploy** to rebuild with new env vars

#### 5. Python Dependencies Missing
```
ModuleNotFoundError: No module named 'httpx'
```
**Solution**: Ensure `netlify/functions/requirements.txt` exists and contains all dependencies.

### Debug Mode

Enable detailed logging:
```bash
# Set in Netlify environment variables
LOG_LEVEL=DEBUG
```

View function logs:
```bash
netlify functions:log analyze
```

---

## Monitoring & Maintenance

### Performance Monitoring

**Netlify Analytics** (Paid feature):
- Real-time visitors
- Page views
- Top pages & resources

**Function Metrics** (Free):
- Invocations per day
- Average execution time
- Error rate

### Monthly Maintenance Checklist

- [ ] Review function error logs
- [ ] Check API usage (Hugging Face quota)
- [ ] Update dependencies for security patches
- [ ] Test core functionality
- [ ] Review and clean old deployments
- [ ] Check SSL certificate status

### Scaling Considerations

| Metric | Free Tier | Pro Tier Needed When... |
|--------|-----------|------------------------|
| Builds/month | 300 min | > 5 deployments/day |
| Function runs | 125k req/month | > 4k requests/day |
| Function duration | 100 hrs/month | Heavy AI processing |
| Bandwidth | 100 GB | > 3 GB/day traffic |

---

## Security Best Practices

### ✅ Implemented

- [x] Environment variables for sensitive data
- [x] `.env` excluded from git
- [x] Security headers (CSP, XSS protection)
- [x] HTTPS enforced
- [x] CORS configured
- [x] Input validation
- [x] Rate limiting (via Netlify)

### 🔒 Additional Recommendations

1. **Rotate API Keys Regularly**
   - Update `HF_API_KEY` every 90 days
   - Create new token, update in Netlify, delete old

2. **Enable DDoS Protection**
   - Use Netlify's built-in protection
   - Consider Cloudflare for additional layer

3. **Monitor Suspicious Activity**
   - Check function logs for unusual patterns
   - Set up alerts for error spikes

4. **Backup Strategy**
   - Code is in GitHub (version controlled)
   - Environment variables documented
   - Regular database backups (if added later)

---

## Cost Estimates

### Netlify (Free Tier)
- ✅ Frontend hosting: **FREE**
- ✅ Serverless functions: **FREE** (up to 125k req/month)
- ✅ SSL certificate: **FREE**
- ✅ CDN: **FREE**

### Hugging Face (Free Tier)
- ✅ API access: **FREE**
- ℹ️ Rate limits apply (check [pricing](https://huggingface.co/pricing))

### Expected Monthly Cost
- **Low traffic** (<1k users/month): **$0** ☑️
- **Medium traffic** (1k-10k users): **$0-$19** (Netlify Pro if needed)
- **High traffic** (>10k users): Consider dedicated backend

---

## Support & Resources

### Documentation
- [Netlify Docs](https://docs.netlify.com)
- [Hugging Face API Docs](https://huggingface.co/docs/api-inference)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)

### Getting Help
1. Check [Troubleshooting](#troubleshooting) section
2. Review Netlify function logs
3. Check GitHub Issues
4. Contact support via Netlify dashboard

---

## Deployment Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] `.env` file is NOT in repository
- [ ] `HF_API_KEY` set in Netlify
- [ ] Site deployed successfully
- [ ] All tests pass
- [ ] Chart upload works
- [ ] AI analysis completes
- [ ] Chat interface functional
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Performance acceptable (< 3s load)
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] Documentation reviewed

---

## 🎉 You're Live!

Once deployed, your ChartSense application will be available at:
```
https://your-site-name.netlify.app
```

Share with users and start analyzing charts! 📊

---

**Last Updated**: February 2026
**Version**: 1.0.0
