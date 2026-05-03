# ⚡ Quick Deploy Checklist

## ✅ **Ready to Deploy in 5 Minutes!**

### **1. Push to GitHub** (2 minutes)

```bash
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard

# Initialize git
git init
git add .
git commit -m "Ready for deployment"

# Create repo on github.com (your username)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/katsu-finance-dashboard.git
git branch -M main
git push -u origin main
```

---

### **2. Deploy to Vercel** (2 minutes)

**Option A - Via Website:**
1. Go to [vercel.com](https://vercel.com)
2. Login with GitHub
3. Click "Add New Project"
4. Select `katsu-finance-dashboard`
5. Click "Deploy"

**Option B - Via CLI:**
```bash
npm install -g vercel
vercel login
vercel --prod
```

---

### **3. Add API Keys** (1 minute)

In Vercel Dashboard:
1. Settings → Environment Variables
2. Add these three:
   - `ALPHA_VANTAGE_KEY` = `2Q3W3M7OMRSU3A5I`
   - `FRED_KEY` = `21d934bc76b6214fb384542693fe02bc`
   - `BEA_KEY` = `28D77A5E-CC66-43D0-BD6D-C108FED47219`
3. Redeploy

---

## 🎉 **Done!**

Your site will be live at: `https://katsu-finance-dashboard.vercel.app`

---

## 📋 **What Changed:**

✅ API keys moved to environment variables  
✅ `.env.local` created for local development  
✅ `.gitignore` protects your secrets  
✅ Code ready for production deployment  

---

## 🆘 **Need Help?**

See full instructions in: `DEPLOY.md`

Or ask Katsu (your finance expert AI) for step-by-step help! 👊
