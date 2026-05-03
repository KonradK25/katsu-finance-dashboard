# 🎯 Katsu Finance Dashboard - Getting Started Guide

**Hey Konrad! Your finance dashboard is ready to go!** 🎉

---

## ⚡ Quick Start (30 Seconds)

### Step 1: Open Terminal
Press `Cmd + Space`, type "Terminal", and hit Enter.

### Step 2: Navigate to Your Project
Copy and paste this command:

```bash
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard
```

### Step 3: Start the Dashboard
Run this command:

```bash
npm run dev
```

### Step 4: Open in Browser
Once you see "Ready in Xms", open your browser and go to:

**→ http://localhost:3000**

---

## 🖥️ What You'll See

When you open the dashboard, you'll see:

1. **Top Bar** - Search any stock by symbol (AAPL, TSLA, NVDA, etc.)

2. **Watchlist Cards** - Pre-loaded with popular stocks:
   - AAPL (Apple)
   - MSFT (Microsoft)
   - GOOGL (Google)
   - AMZN (Amazon)
   - NVDA (NVIDIA)
   - TSLA (Tesla)

3. **Price Chart** - Click any stock card to see its 30-day price history

4. **News Feed** - Latest financial news with sentiment analysis (Bullish/Bearish)

5. **Chat Interface** - Ask questions about markets (currently demo mode)

---

## 📱 How to Use It

### Track a Stock
1. Type a stock symbol in the search bar (e.g., "META" for Facebook)
2. Press Enter or click the search icon
3. The stock is added to your watchlist
4. Click the card to see its chart and news

### View Different Stocks
- Click any watchlist card to switch to that stock
- The chart and news will update automatically

### Read News
- Scroll down to see latest financial news
- Green = Bullish (positive sentiment)
- Red = Bearish (negative sentiment)
- Yellow = Neutral
- Click "Read more" to open the full article

---

## 🌐 Put It Online (Free!)

Want to access your dashboard from anywhere? Deploy to Vercel:

### Option 1: Easiest (No Command Line)

1. Go to **github.com** and create a free account
2. Create a new repository called "katsu-finance"
3. Upload your project files (drag and drop)
4. Go to **vercel.com** and sign up with GitHub
5. Click "New Project" → Import your "katsu-finance" repo
6. Vercel will deploy it automatically!
7. You'll get a URL like: `https://katsu-finance.vercel.app`

### Option 2: With Terminal (If Comfortable)

```bash
# Install Vercel
npm install -g vercel

# Login
vercel login

# Deploy
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard
vercel --prod
```

---

## 🔧 Common Issues & Fixes

### "npm: command not found"
You need Node.js installed. Download it from: **nodejs.org** (get the LTS version)

### "Port 3000 already in use"
Another app is using port 3000. Either:
- Close other apps, or
- Run: `npm run dev -- -p 3001` (uses port 3001 instead)

### "API limit reached"
Alpha Vantage limits free users to 500 calls/day. Wait a few minutes and it will reset.

### Charts not loading
- Make sure you have internet connection
- Check if the stock symbol is correct
- Some symbols aren't available on Alpha Vantage

---

## 📊 What's Next?

### This Weekend Projects:

**1. Add More Stocks**
Edit the watchlist in `app/page.tsx` line 18:
```typescript
const DEFAULT_WATCHLIST = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'YOUR_SYMBOL'];
```

**2. Customize Colors**
Open `app/globals.css` and change the color values at the top.

**3. Add Economic Data**
I can help you add FRED/BEA charts for GDP, unemployment, inflation, etc.

**4. Enable AI Chat**
Connect the chat to OpenClaw so I can give you real investment analysis!

---

## 🙋 Need Help?

Just ask me! I can:
- ✅ Add new features
- ✅ Fix any bugs
- ✅ Explain how the code works
- ✅ Help you deploy online
- ✅ Connect more data sources

Message me anytime through OpenClaw or the dashboard chat! 👊

---

## 📁 Project Structure (For Reference)

```
katsu-finance-dashboard/
├── app/
│   ├── page.tsx          # Main dashboard page
│   ├── layout.tsx        # Site layout
│   ├── globals.css       # Styles/colors
│   └── api/
│       ├── stock/        # Stock quote API
│       ├── stock-series/ # Historical data API
│       └── news/         # News API
├── components/
│   ├── stock-chart.tsx   # Price chart component
│   ├── stock-quote-card.tsx  # Stock cards
│   ├── news-feed.tsx     # News display
│   └── chat-interface.tsx # Chat UI
├── lib/
│   ├── api.ts            # API configuration
│   └── utils.ts          # Helper functions
├── package.json          # Dependencies
└── README.md             # Full documentation
```

---

## 🎓 Learning Resources

Want to understand how it all works?

- **Next.js Basics:** https://nextjs.org/learn
- **React for Beginners:** https://react.dev/learn
- **TypeScript:** https://www.typescriptlang.org/docs/handbook/intro.html
- **Tailwind CSS:** https://tailwindcss.com/docs

---

**You're all set! Run `npm run dev` and start exploring your dashboard!** 🚀

Built with ❤️ by Katsu • Your Finance Expert 👊
