# 🚀 Deploy Katsu Finance Dashboard to Vercel

## Quick Deploy Guide (10 minutes)

### Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Repository name: `katsu-finance-dashboard`
3. **Public** or **Private** (your choice)
4. **DO NOT** initialize with README (we already have code)
5. Click **Create repository**

### Step 2: Push Your Code to GitHub

Run these commands in your terminal:

```bash
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard

# Add your GitHub repo as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/katsu-finance-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Vercel

1. Go to https://vercel.com
2. Click **Sign Up** (use your GitHub account)
3. Click **Add New Project**
4. Select **Import Git Repository**
5. Find and select `katsu-finance-dashboard`
6. Click **Import**

### Step 4: Configure Environment Variables

In Vercel project settings:

1. Go to **Settings** → **Environment Variables**
2. Add these variables:

| Name | Value |
|------|-------|
| `ALPHA_VANTAGE_KEY` | `2Q3W3M7OMRSU3A5I` |
| `FRED_API_KEY` | `21d934bc76b6214fb384542693fe02bc` |
| `BEA_API_KEY` | `28D77A5E-CC66-43D0-BD6D-C108FED47219` |

3. Click **Save**

### Step 5: Deploy!

1. Click **Deploy** button
2. Wait 2-3 minutes for build
3. Vercel will give you a URL like: `https://katsu-finance-dashboard.vercel.app`
4. **Done!** 🎉

---

## 🎨 Customize Your Domain (Optional)

Want a custom domain like `katsu-finance.com`?

1. Buy domain from Namecheap, Google Domains, etc.
2. In Vercel: **Settings** → **Domains**
3. Add your domain
4. Update DNS records (Vercel gives you instructions)
5. SSL is automatic! 🔒

---

## 📊 Vercel Free Tier Limits

✅ **Perfect for your dashboard:**
- 100GB bandwidth/month (plenty!)
- Unlimited deployments
- Automatic HTTPS
- Automatic builds on git push

**You won't hit limits** unless you get thousands of daily visitors!

---

## 🔄 Updating Your Dashboard

After deployment, updates are automatic:

```bash
# Make changes to your code
git add .
git commit -m "Added new feature"
git push
```

Vercel will automatically rebuild and deploy in ~2 minutes!

---

## 🐛 Troubleshooting

### Build Fails
- Check **Deploy Logs** in Vercel dashboard
- Common issue: Missing environment variables
- Solution: Add all 3 API keys in Settings → Environment Variables

### API Errors After Deploy
- Verify API keys are correct in Vercel
- Check API rate limits (Alpha Vantage: 500/day)
- CoinGecko needs no key - works automatically!

### Site Shows "Build Error"
- Click **View Build Logs** in Vercel
- Look for errors in red
- Usually missing dependencies or TypeScript errors

---

## 🎯 Post-Deployment Checklist

- [ ] Dashboard loads at Vercel URL
- [ ] Stock prices show (not "Loading...")
- [ ] Crypto prices load
- [ ] Treasury yields display
- [ ] Charts render properly
- [ ] Mobile responsive (test on phone!)
- [ ] All navigation buttons work

---

## 📱 Share Your Dashboard!

Once deployed, you can:
- Share the link in your resume
- Show it in interviews ("I built this!")
- Access from any device
- Add it to your portfolio

**Pro tip:** Create a short demo video for your LinkedIn!

---

## 💡 Need Help?

- Vercel Docs: https://vercel.com/docs
- Next.js Deploy: https://nextjs.org/docs/deployment
- Vercel Discord: https://discord.com/invite/vercel

---

**You got this, Konrad!** 👊🚀

Your dashboard is production-ready. Time to show it to the world!
