# Katsu DCF Engine 📊

Automated Discounted Cash Flow (DCF) modeling engine that pulls **real-time data** from SEC EDGAR, Yahoo Finance, and macroeconomic sources to generate professional Excel valuation models and interactive dashboards.

## ✨ Features

### Core Capabilities
- **📊 Data-Driven Assumptions** — No random guesses! Auto-fetches:
  - 10-Year Treasury yield (risk-free rate)
  - S&P 500 historical returns (market risk premium)
  - Analyst consensus growth estimates
  - Company effective tax rates
  - Cost of debt from financials
- **🔍 SEC EDGAR Integration** — Auto-fetch 10-K, 10-Q filings
- **📈 Yahoo Finance** — Real-time prices, market cap, beta, financials
- **📑 Excel Generation** — Professional 6-sheet DCF models with formulas & charts
- **🎛️ Interactive Dashboard** — Streamlit app for scenario analysis
- **📊 Sensitivity Analysis** — WACC/growth rate sensitivity tables & heatmaps

### Phase 2 Complete ✅
- [x] SEC EDGAR scraper (10-K/10-Q downloads)
- [x] Yahoo Finance scraper (real-time data)
- [x] Macro data scraper (Treasury yields, analyst estimates)
- [x] DCF calculation engine (WACC, FCF, terminal value)
- [x] Excel generator (professional output)
- [x] **Streamlit dashboard (interactive analysis)**

## 🚀 Quick Start

### Command Line

```bash
# Install dependencies
pip install -r requirements.txt

# Run DCF with auto-fetched real data
python3 src/models/dcf_auto.py -t AAPL -o AAPL_DCF.xlsx

# Custom ticker
python3 src/models/dcf_auto.py -t MSFT -o MSFT_DCF.xlsx
```

### Interactive Dashboard

```bash
# Launch dashboard
./run_dashboard.sh

# Or manually
cd src/dashboard
streamlit run app.py
```

Dashboard opens at: **http://localhost:8501**

## 📊 Dashboard Features

The Streamlit dashboard provides:

- **⚡ Real-Time Analysis** — Fetch live data for any ticker
- **🎛️ Assumption Editor** — Adjust WACC, growth rates, tax rates interactively
- **📈 Visual Charts** — FCF projections, valuation distributions
- **🔥 Sensitivity Heatmaps** — See how valuation changes across scenarios
- **💾 Excel Export** — Download professional Excel models directly
- **📚 Data Sources** — Full transparency on where assumptions come from

### Quick Select Stocks
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Alphabet)
- TSLA (Tesla)
- AMZN (Amazon)
- NVDA (NVIDIA)

## 📁 Project Structure

```
katsu-dcf/
├── src/
│   ├── main.py                  # CLI entry point
│   ├── models/
│   │   ├── dcf.py               # DCF calculation engine
│   │   └── dcf_auto.py          # Auto-fetch real data
│   ├── scrapers/
│   │   ├── sec_edgar_v2.py      # SEC filings downloader
│   │   ├── yahoo_finance.py     # Market data & financials
│   │   └── macro_data.py        # Treasury yields, analyst estimates
│   ├── excel/
│   │   └── generator.py         # Professional Excel output
│   └── dashboard/
│       └── app.py               # Streamlit interactive dashboard
├── data/
│   └── sec_filings/             # Downloaded 10-K/10-Q
├── requirements.txt
├── README.md
├── STATUS.md
└── run_dashboard.sh             # Dashboard launcher
```

## 🎯 Excel Output

Each Excel model includes **6 professional sheets**:

1. **Summary** — Executive summary with recommendation
2. **Assumptions** — All inputs with data sources cited
3. **WACC** — Detailed cost of capital breakdown
4. **Projections** — 5-year FCF forecasts with formulas
5. **Sensitivity** — WACC vs. growth matrix
6. **Charts** — Visual valuation summary

## 📈 Test Results

### Apple Inc. (AAPL) - Live Test

```
Current Price:     $266.43
Intrinsic Value:   $123.40
Downside:          -53.7%
Recommendation:    SELL
```

**Data-Driven Assumptions:**
- Risk-free rate: **4.28%** (10Y Treasury ^TNX)
- Market risk premium: **8.59%** (S&P 500 historical)
- Revenue growth: **15.7% → 7.8%** (Analyst consensus)
- Tax rate: **15.6%** (Apple's effective rate)
- FCF: **$98.77B** (Yahoo Finance)

**Key Insight:** Apple appears significantly overvalued at current prices based on DCF analysis with real-time data.

## 📚 Data Sources

| Source | Data | Status |
|--------|------|--------|
| **Yahoo Finance (^TNX)** | 10-Year Treasury yield | ✅ Live |
| **Yahoo Finance (^GSPC)** | S&P 500 historical returns | ✅ Live |
| **Yahoo Finance** | Analyst growth estimates | ✅ Live |
| **Yahoo Finance** | Company financials | ✅ Live |
| **SEC EDGAR** | 10-K, 10-Q filings | ✅ Downloads |
| Alpha Vantage | Economic indicators | 🔑 API ready |
| Bloomberg | Analyst estimates | 📅 Phase 3 |
| WSJ | News sentiment | 📅 Phase 3 |

## 🛠️ Requirements

- Python 3.9+
- Dependencies in `requirements.txt`
- Internet connection (for live data)

### Key Dependencies
```
streamlit>=1.30.0     # Dashboard
plotly>=5.18.0        # Charts
yfinance>=0.2.0       # Yahoo Finance
sec-edgar-downloader  # SEC filings
openpyxl>=3.1.0       # Excel
xlsxwriter>=3.1.0     # Excel
pandas>=2.0.0         # Data handling
```

## 🎓 Methodology

### DCF Calculation

1. **WACC Calculation** (CAPM)
   ```
   WACC = (E/V × Re) + (D/V × Rd × (1-T))
   Re = Rf + β × (Rm - Rf)
   ```

2. **FCF Projections** (5 years)
   - Revenue growth from analyst estimates
   - FCF margin based on historical

3. **Terminal Value** (Perpetuity Growth)
   ```
   TV = FCF₅ × (1+g) / (WACC - g)
   ```

4. **Intrinsic Value**
   ```
   Equity Value = PV(FCF) + PV(TV) - Debt + Cash
   Share Price = Equity Value / Shares Outstanding
   ```

### Recommendation Logic
- **BUY**: >20% upside to intrinsic value
- **HOLD**: 5-20% upside or within -10%
- **SELL**: >10% downside

## 📅 Roadmap

### Phase 3 (Future)
- [ ] Bloomberg API integration
- [ ] WSJ news sentiment analysis
- [ ] XBRL parsing for detailed SEC data
- [ ] Multi-company comparison tool
- [ ] Monte Carlo simulation for valuation ranges
- [ ] Automated report generation (PDF)

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. Not financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.

Valuations are only as good as their assumptions. While this engine uses real-time data, DCF models are sensitive to input assumptions, particularly WACC and terminal growth rates.

---

**Built by Katsu for Konrad** | Econ & Finance Toolkit  
**Phase 2 Status:** ✅ Complete | **Dashboard:** ✅ Live
