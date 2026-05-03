# 🚀 Deploy Katsu Finance Dashboard to the Web

This guide will help you deploy your dashboard so it runs **completely online**, independent of your local machine or OpenClaw.

---

## 🎯 **Deployment Options**

### **Option 1: Vercel (Easiest - FREE)** ⭐ RECOMMENDED

**Pros:**
- ✅ Free hosting for personal projects
- ✅ Automatic deployments from GitHub
- ✅ Global CDN (fast worldwide)
- ✅ Custom domain support
- ✅ HTTPS included
- ✅ No server management needed

**Cons:**
- Serverless functions have execution timeouts (good for our use case)

---

## 📋 **Step-by-Step: Deploy to Vercel**

### **Step 1: Push to GitHub**

Open Terminal and run these commands:

```bash
# Navigate to your project
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - Katsu Finance Dashboard"

# Create a new repository on GitHub:
# 1. Go to github.com
# 2. Click "+" → "New repository"
# 3. Name it: katsu-finance-dashboard
# 4. Make it Public or Private (your choice)
# 5. Click "Create repository"

# Connect your local repo to GitHub
git remote add origin https://github.com/YOUR_USERNAME/katsu-finance-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your GitHub username!**

---

### **Step 2: Deploy to Vercel**

#### **Method A: Deploy via Vercel Website (Easiest)**

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign up/Login** (use your GitHub account - easiest)
3. **Click "Add New Project"**
4. **Import your GitHub repository:**
   - Select "katsu-finance-dashboard" from the list
   - Click "Import"
5. **Configure Project:**
   - Framework Preset: Next.js (auto-detected)
   - Root Directory: `./` (leave as default)
   - Build Command: `npm run build`
   - Output Directory: `.next`
6. **Click "Deploy"**
7. **Wait 1-2 minutes** for deployment to complete
8. **Your site is LIVE!** 🎉

You'll get a URL like:
```
https://katsu-finance-dashboard.vercel.app
```

#### **Method B: Deploy via Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to project
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard

# Deploy
vercel --prod
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? (your username) **Enter**
- Link to existing project? **N**
- Project name? **katsu-finance-dashboard**
- Directory? **./** **Enter**
- Override settings? **N**

---

### **Step 3: Add Your API Keys to Vercel**

Your API keys are currently in `lib/api.ts`. For security, let's move them to environment variables:

#### **3a. Create `.env.local` file locally:**

```bash
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard
```

Create a file named `.env.local`:

```env
ALPHA_VANTAGE_KEY=2Q3W3M7OMRSU3A5I
FRED_KEY=21d934bc76b6214fb384542693fe02bc
BEA_KEY=28D77A5E-CC66-43D0-BD6D-C108FED47219
```

#### **3b. Update `lib/api.ts` to use environment variables:**

```typescript
// Replace the hardcoded keys with:
export const ALPHA_VANTAGE_KEY = process.env.ALPHA_VANTAGE_KEY || '2Q3W3M7OMRSU3A5I';
export const FRED_KEY = process.env.FRED_KEY || '21d934bc76b6214fb384542693fe02bc';
export const BEA_KEY = process.env.BEA_KEY || '28D77A5E-CC66-43D0-BD6D-C108FED47219';
```

#### **3c. Add Environment Variables to Vercel:**

1. Go to your project on Vercel
2. Click **"Settings"** tab
3. Click **"Environment Variables"**
4. Add each variable:
   - `ALPHA_VANTAGE_KEY` → `2Q3W3M7OMRSU3A5I`
   - `FRED_KEY` → `21d934bc76b6214fb384542693fe02bc`
   - `BEA_KEY` → `28D77A5E-CC66-43D0-BD6D-C108FED47219`
5. Click **"Save"**
6. **Redeploy** (go to Deployments → click menu → "Redeploy")

---

### **Step 4: Add a Custom Domain (Optional)**

Want your own domain like `finance.yourname.com`?

1. **Buy a domain** (Namecheap, GoDaddy, Google Domains, etc.)
2. **In Vercel:**
   - Go to your project → Settings → Domains
   - Add your domain: `yourdomain.com`
   - Follow DNS configuration instructions
3. **Update DNS records** at your domain registrar
4. **Wait 24-48 hours** for DNS propagation

Vercel provides **free HTTPS certificates** automatically!

---

## 🔧 **Important: API Rate Limits**

### **Alpha Vantage Free Tier:**
- **500 calls per day**
- **5 calls per minute**

### **Problem:**
If multiple people use your deployed site, you'll hit rate limits quickly!

### **Solutions:**

#### **Option 1: Upgrade Alpha Vantage (Recommended for Production)**
- **Pro Plan:** $69.99/month
- **5,000 calls/hour**
- **75 calls/minute**

#### **Option 2: Add Caching (Free)**
I can add Redis caching to reduce API calls. Let me know!

#### **Option 3: Use Multiple API Keys**
Create multiple free Alpha Vantage accounts and rotate keys.

---

## 🌐 **Your Deployed Site Will:**

✅ Run 24/7 on Vercel's servers  
✅ Be accessible from anywhere in the world  
✅ Work without your computer being on  
✅ Work without OpenClaw running  
✅ Have HTTPS encryption  
✅ Auto-deploy when you push to GitHub  
✅ Scale automatically  

---

## 📱 **Share Your Dashboard**

Once deployed, you can:
- Share the URL with anyone
- Access from phone, tablet, any computer
- Bookmark it in your browser
- Add it to your home screen (PWA)

---

## 🛠️ **Troubleshooting**

### **Build Fails:**
```bash
# Test build locally first
npm run build

# Check for errors
# Fix them, then push to GitHub
git add .
git commit -m "Fix build errors"
git push
```

### **API Errors After Deploy:**
- Make sure you added environment variables in Vercel
- Redeploy after adding variables
- Check Vercel logs: Project → Activity → Click deployment → View Logs

### **Site Shows "Application Error":**
- Check Vercel Function logs for errors
- Likely an API key issue or rate limit
- Wait a few minutes and refresh

---

## 🎉 **You're Done!**

Your dashboard is now:
- ✅ Hosted on the web
- ✅ Accessible from anywhere
- ✅ Running independently
- ✅ No need for your computer to be on
- ✅ No need for OpenClaw to be running

**Share your URL and enjoy!** 🚀

---

## 📊 **Next Steps (Optional)**

Want me to add:
- **Redis caching** to reduce API calls?
- **User authentication** so only you can access it?
- **Portfolio tracking** with a database?
- **Email alerts** for price changes?
- **Mobile app version**?

Just ask! 👊

---

**Need help with deployment?** Message me and I'll walk you through it step-by-step!
