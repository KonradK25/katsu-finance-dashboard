# 🚀 Katsu Finance Dashboard Setup Guide

Your AI-powered financial intelligence platform is ready! Follow these steps to get started.

---

## 📋 What You Have

A complete Next.js website with:

- ✅ **Real-time stock quotes** (Alpha Vantage API)
- ✅ **Interactive price charts** (Recharts)
- ✅ **Financial news feed** with sentiment analysis
- ✅ **Watchlist management** (track your favorite stocks)
- ✅ **Chat interface** (ready for OpenClaw integration)
- ✅ **Beautiful dark mode UI** (shadcn/ui + Tailwind)
- ✅ **API routes** for fetching market data

---

## 🏃 Quick Start

### 1. Run Locally

Open your terminal and run:

```bash
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard
npm run dev
```

Then open your browser to: **http://localhost:3000**

### 2. Test It Out

- Search for stock symbols (AAPL, TSLA, NVDA, etc.)
- Click on watchlist cards to see charts
- Check the news feed for latest updates
- Try the chat interface (currently shows demo responses)

---

## 🌐 Deploy to Vercel (Free Hosting)

### Option A: Deploy via Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com)
2. Sign up/login (use GitHub for easiest setup)
3. Click **"Add New Project"**
4. Import your GitHub repo (you'll need to push to GitHub first):
   ```bash
   cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard
   git init
   git add .
   git commit -m "Initial commit"
   # Create repo on GitHub, then:
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```
5. Vercel will auto-detect Next.js and deploy automatically!

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd /Users/Katsu/.openclaw/workspace/katsu-finance-dashboard
vercel --prod
```

That's it! Your site will be live at `https://your-project.vercel.app`

---

## 🔧 Configuration

### API Keys (Already Configured!)

Your API keys are already set up in `lib/api.ts`:

- ✅ Alpha Vantage: `2Q3W3M7OMRSU3A5I` (500 calls/day free)
- ✅ FRED: Configured for economic data
- ✅ BEA: Configured for GDP/income data

### Rate Limiting Note

Alpha Vantage free tier limits:
- **500 API calls per day**
- **5 calls per minute**

If you hit the limit, you'll see "API limit reached" errors. Wait a few minutes or upgrade to a paid plan.

---

## 🎨 Customization

### Change Colors

Edit `app/globals.css` to customize the color scheme. The dashboard uses CSS variables for easy theming.

### Add More Stocks

Edit the default watchlist in `app/page.tsx`:

```typescript
const DEFAULT_WATCHLIST = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA'];
```

### Customize Layout

All components are in the `components/` folder:
- `stock-quote-card.tsx` - Stock price cards
- `stock-chart.tsx` - Price charts
- `news-feed.tsx` - News display
- `chat-interface.tsx` - Chat UI

---

## 🤖 Connect OpenClaw (Advanced)

To enable real AI responses in the chat:

1. Make sure OpenClaw gateway is running
2. Update `components/chat-interface.tsx` to call your OpenClaw API
3. See OpenClaw docs for API endpoints

---

## 📱 Features Breakdown

### Dashboard (`app/page.tsx`)
- Main landing page with full dashboard
- Watchlist with real-time quotes
- Interactive price charts
- News feed with sentiment
- Chat interface

### API Routes
- `/api/stock` - Get current stock quote
- `/api/stock-series` - Get historical price data
- `/api/news` - Get financial news

### Components
- All UI components use shadcn/ui design system
- Fully responsive (mobile-friendly)
- Dark mode by default

---

## 🐛 Troubleshooting

### "API limit reached"
- Wait a few minutes for rate limit to reset
- Alpha Vantage free tier = 5 calls/minute

### "Stock not found"
- Check the symbol is correct (e.g., AAPL, not Apple)
- Some symbols may not be available on Alpha Vantage

### Charts not showing
- Make sure historical data loaded successfully
- Check browser console for errors

### Build errors
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run dev
```

---

## 📚 Learn More

- **Next.js Docs:** [nextjs.org/docs](https://nextjs.org/docs)
- **Recharts:** [recharts.org](https://recharts.org)
- **Alpha Vantage API:** [alphavantage.co/documentation](https://www.alphavantage.co/documentation/)
- **Vercel Deployment:** [vercel.com/docs](https://vercel.com/docs)

---

## 🙋 Need Help?

Ask Katsu (me!) anything about:
- Adding new features
- Fixing bugs
- Understanding the code
- Deploying updates
- Integrating more data sources

Just message me in the chat or through OpenClaw! 👊

---

**Built with ❤️ by Katsu • Powered by OpenClaw AI**
