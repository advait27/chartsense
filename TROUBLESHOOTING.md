# 🔧 Netlify Deployment Troubleshooting

## ❌ "Analysis Failed" Error

If you're seeing "Failed to analyze chart. Please try again" after deployment, follow these steps:

### Step 1: Check Health Endpoint

Visit your deployed site's health check endpoint:
```
https://your-site-name.netlify.app/api/health
```

This will show:
- ✅ If backend modules are loading correctly
- ✅ If environment variables are set
- ✅ Python version and imports status

### Step 2: Verify HF_API_KEY is Set

**This is the #1 cause of deployment issues!**

1. Go to Netlify Dashboard: https://app.netlify.com
2. Select your site
3. Go to **Site settings** → **Environment variables**
4. Check if `HF_API_KEY` is listed
   - ❌ **If NOT listed**: Add it now!
   - ✅ **If listed**: Verify the value is correct

#### How to Add HF_API_KEY:

1. Click **"Add a variable"**
2. Key: `HF_API_KEY`
3. Value: Your Hugging Face token (starts with `hf_`)
   - Get it from: https://huggingface.co/settings/tokens
   - Must have **Read** permission
4. Click **"Add variable"**
5. Netlify will automatically redeploy

### Step 3: Check Function Logs

View real-time function logs:

1. Go to Netlify Dashboard → Your site
2. Click **Functions** tab
3. Click on **analyze** function
4. View the logs for error messages

Common errors:
- `HF_API_KEY not set` → Add environment variable
- `KeyError: 'HF_API_KEY'` → Add environment variable
- `401 Unauthorized` → API key is invalid
- `ImportError` → Missing dependency (rarely happens)
- `Timeout` → Function took >26s (upgrade to Pro or optimize)

### Step 4: Test API Directly

Test the analyze endpoint directly with curl:

```bash
# Get a test image as base64
BASE64_IMAGE="data:image/png;base64,iVBORw0K..." # your base64 image

# Test the endpoint
curl -X POST https://your-site-name.netlify.app/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$BASE64_IMAGE\"}"
```

### Step 5: Check Build Logs

If functions aren't deploying:

1. Netlify Dashboard → **Deploys**
2. Click latest deploy
3. Scroll to **Function bundling** section
4. Verify Python dependencies installed correctly

---

## 🔍 Common Issues & Solutions

### Issue: "Service unavailable" or 503 Error

**Cause**: HF_API_KEY not set in Netlify

**Fix**:
1. Add HF_API_KEY in Netlify environment variables
2. Wait for automatic redeploy (~2 minutes)
3. Test again

### Issue: "Unauthorized" or 401 Error

**Cause**: Invalid or expired HF_API_KEY

**Fix**:
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with **Read** permission
3. Update HF_API_KEY in Netlify environment variables
4. Wait for redeploy

### Issue: Function Timeout

**Cause**: Analysis takes >26 seconds (free tier limit)

**Fix Options**:
1. Upgrade to Netlify Pro ($19/month) for longer timeouts
2. Use simpler images (smaller file size)
3. Optimize models (contact support)

### Issue: "Module not found" Error

**Cause**: Missing Python dependency

**Fix**:
1. Check `netlify/functions/requirements.txt`
2. Add missing package
3. Commit and push
4. Netlify will redeploy

### Issue: Import Errors (backend modules)

**Cause**: Path issues with backend imports

**Fix**: This should be automatic, but if you see import errors:
1. Verify `netlify/functions/analyze.py` has correct path setup
2. Check logs for specific import that failed
3. Verify backend modules are in repository

---

## ✅ Quick Validation Checklist

Before contacting support, verify:

- [ ] HF_API_KEY is set in Netlify environment variables
- [ ] HF_API_KEY starts with `hf_` and is at least 30 characters
- [ ] Latest code is pushed to GitHub
- [ ] Netlify has deployed latest commit
- [ ] Health check endpoint returns `"status": "ok"`
- [ ] No errors in function logs
- [ ] Site loads correctly (white screen = build issue)

---

## 📞 Still Having Issues?

### Get Diagnostic Info

1. Visit `/api/health` on your deployed site
2. Copy the JSON response
3. Check Netlify function logs for **analyze** function
4. Note exact error message

### Where to Get Help

1. **GitHub Issues**: https://github.com/advait27/chartsense/issues
2. **Netlify Support**: https://answers.netlify.com/
3. **HuggingFace Forum**: https://discuss.huggingface.co/

### Include This Info:

- Health check output (`/api/health`)
- Function logs from Netlify
- Exact error message
- Steps you've already tried

---

## 🎯 Most Common Fix

**90% of deployment issues are solved by:**

1. Adding `HF_API_KEY` to Netlify environment variables
2. Waiting 2-3 minutes for automatic redeploy
3. Testing again

### Quick Steps:

```bash
# 1. Get your HF token
# Visit: https://huggingface.co/settings/tokens

# 2. Add to Netlify
# Dashboard → Site settings → Environment variables → Add variable
# Key: HF_API_KEY
# Value: hf_xxxxxxxxxxxxx

# 3. Wait for redeploy (automatic)

# 4. Test health check
curl https://your-site-name.netlify.app/api/health

# 5. Try analysis again
```

That's it! 🎉
