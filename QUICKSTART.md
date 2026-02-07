# ⚡ Quick Deploy - ChartSense

**Time to deploy**: ~10 minutes

## Prerequisites ✅
- [ ] GitHub account
- [ ] Netlify account (free)
- [ ] Hugging Face account (free)

---

## Step 1: Get Hugging Face API Key (2 min)

1. Go to https://huggingface.co
2. Sign up / Log in
3. Click profile → **Settings** → **Access Tokens**
4. **New token** → Name: `chartsense` → Permission: **Read**
5. **Copy token** (starts with `hf_`)

---

## Step 2: Prepare Repository (1 min)

```bash
# Make sure .env is NOT tracked
git rm --cached .env 2>/dev/null || true

# Add all production files
git add .

# Commit
git commit -m "Production ready deployment"

# Push to GitHub
git push origin main
```

---

## Step 3: Deploy to Netlify (5 min)

### 3a. Connect Repository
1. Go to https://app.netlify.com
2. **Add new site** → **Import an existing project**
3. Choose **GitHub**
4. Select your `chartsense` repository

### 3b. Configure Build (Auto-detected!)
These settings are in `netlify.toml` already:
- Base directory: `frontend-react`
- Build command: `npm ci && npm run build`
- Publish directory: `frontend-react/build`

Just click **Deploy**!

### 3c. Add Environment Variable
1. Go to **Site settings** → **Environment variables**
2. **Add a variable**
   - Key: `HF_API_KEY`
   - Value: [Your HF token from Step 1]
3. **Save**

### 3d. Trigger Redeploy
1. Go to **Deploys** tab
2. Click **Trigger deploy** → **Deploy site**
3. Wait 3-5 minutes

---

## Step 4: Verify (2 min)

✅ Check these:
- [ ] Site is live at `https://[your-site].netlify.app`
- [ ] Homepage loads
- [ ] Can upload an image
- [ ] Analysis works (might take 30-60s first time)
- [ ] No console errors

---

## 🎉 You're Live!

Share your link: `https://[your-site-name].netlify.app`

---

## 🔧 Optional: Custom Domain

1. **Site settings** → **Domain management**
2. **Add custom domain**
3. Follow DNS instructions
4. HTTPS automatic! 🔒

---

## 🐛 Troubleshooting

### Build fails
- Check build logs in Netlify
- Verify `package.json` is in `frontend-react/`
- Check Node version (should be 18)

### "HF_API_KEY not found"
- Go to Site settings → Environment variables
- Add `HF_API_KEY`
- Redeploy site

### Function timeout
- Normal for first request (cold start)
- Subsequent requests faster
- Function timeout set to 120s

### Still stuck?
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide
- Review Netlify function logs
- Check [SECURITY.md](SECURITY.md) for security issues

---

## 📝 Quick Commands Reference

```bash
# Local development
npm start                          # Frontend (port 3000)
uvicorn backend.api:app --reload  # Backend (port 8000)

# Deploy via CLI
netlify deploy --prod

# Check function logs
netlify functions:log analyze

# Environment variables
netlify env:set HF_API_KEY "your_key"
netlify env:list
```

---

## 💰 Cost

**Free Tier Limits** (Netlify + Hugging Face):
- ✅ 125k function requests/month
- ✅ 300 build minutes/month
- ✅ 100 GB bandwidth/month
- ✅ SSL certificate included

**Total Cost**: $0/month 🎉

---

## 🔐 Security Reminder

✅ Done:
- [x] `.env` not in git
- [x] API keys in Netlify env vars
- [x] HTTPS enabled
- [x] Security headers configured

❌ Never do:
- Never commit `.env`
- Never share API keys
- Never push secrets to GitHub

---

## 📚 Next Steps

1. ⭐ **Star the repo** on GitHub
2. 📖 Read [DEPLOYMENT.md](DEPLOYMENT.md) for advanced config
3. 🔒 Review [SECURITY.md](SECURITY.md)
4. 🎨 Customize branding
5. 📊 Monitor usage in Netlify dashboard

---

**Deployment time**: ~10 minutes  
**Monthly cost**: $0  
**Status**: Production Ready ✅

Questions? Check [DEPLOYMENT.md](DEPLOYMENT.md) or open an issue!
