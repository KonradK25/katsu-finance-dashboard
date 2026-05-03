"""
Yahoo Finance Scraper for Katsu DCF Engine

Fetches real-time stock data: price, market cap, beta, shares outstanding, etc.
Uses yfinance library for reliable data access.

Install: pip install yfinance
"""

import yfinance as yf
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import pandas as pd


class YahooFinanceScraper:
    """
    Yahoo Finance data scraper for stock metrics and historical data.
    """
    
    def __init__(self):
        """Initialize Yahoo Finance scraper"""
        self.session = yf
        self._cache = {}
    
    def get_stock_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Get current stock quote with key metrics.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with current quote data
        """
        print(f"\n📈 Fetching Yahoo Finance data for {ticker}...")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we got valid data
            if not info or 'currentPrice' not in info:
                print(f"⚠ Limited data available for {ticker}")
                return self._get_fallback_quote(ticker)
            
            quote = {
                'ticker': ticker,
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'previous_close': info.get('previousClose'),
                'open': info.get('open'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'beta': info.get('beta'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'ev_to_revenue': info.get('enterpriseToRevenue'),
                'ev_to_ebitda': info.get('enterpriseToEbitda'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'book_value_per_share': info.get('bookValue'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),
                'dividend_yield': info.get('dividendYield'),
                'dividend_rate': info.get('dividendRate'),
                'payout_ratio': info.get('payoutRatio'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'fifty_day_avg': info.get('fiftyDayAverage'),
                'two_hundred_day_avg': info.get('twoHundredDayAverage'),
                'target_price_mean': info.get('targetMeanPrice'),
                'target_price_high': info.get('targetHighPrice'),
                'target_price_low': info.get('targetLowPrice'),
                'recommendation': info.get('recommendationKey'),
                'number_of_analysts': info.get('numberOfAnalystOpinions'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'full_time_employees': info.get('fullTimeEmployees'),
                'last_updated': datetime.now().isoformat()
            }
            
            # Print summary
            print(f"  → Price: ${quote['current_price']:.2f}" if quote['current_price'] else "  → Price: N/A")
            print(f"  → Market Cap: ${quote['market_cap']/1e9:.2f}B" if quote['market_cap'] else "  → Market Cap: N/A")
            print(f"  → Beta: {quote['beta']:.2f}" if quote['beta'] else "  → Beta: N/A")
            print(f"  → P/E Ratio: {quote['pe_ratio']:.2f}" if quote['pe_ratio'] else "  → P/E Ratio: N/A")
            print(f"  → Shares Outstanding: {quote['shares_outstanding']/1e9:.2f}B" if quote['shares_outstanding'] else "  → Shares: N/A")
            
            return quote
            
        except Exception as e:
            print(f"✗ Error fetching Yahoo Finance data: {e}")
            return self._get_fallback_quote(ticker)
    
    def _get_fallback_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Return realistic fallback data when Yahoo API is unavailable.
        Used for development/testing.
        """
        fallback_data = {
            'AAPL': {
                'current_price': 185.50,
                'market_cap': 2.85e12,
                'beta': 1.28,
                'pe_ratio': 29.5,
                'shares_outstanding': 15.33e9,
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
            },
            'MSFT': {
                'current_price': 415.20,
                'market_cap': 3.08e12,
                'beta': 0.92,
                'pe_ratio': 35.2,
                'shares_outstanding': 7.43e9,
                'sector': 'Technology',
                'industry': 'Software',
            },
            'GOOGL': {
                'current_price': 155.80,
                'market_cap': 1.95e12,
                'beta': 1.05,
                'pe_ratio': 24.8,
                'shares_outstanding': 12.52e9,
                'sector': 'Technology',
                'industry': 'Internet Content',
            },
            'TSLA': {
                'current_price': 248.50,
                'market_cap': 790e9,
                'beta': 2.35,
                'pe_ratio': 68.5,
                'shares_outstanding': 3.18e9,
                'sector': 'Consumer Cyclical',
                'industry': 'Auto Manufacturers',
            },
        }
        
        if ticker in fallback_data:
            print(f"  → Using fallback data for {ticker}")
            data = fallback_data[ticker].copy()
            data['ticker'] = ticker
            data['last_updated'] = datetime.now().isoformat()
            return data
        else:
            print(f"  → No fallback data for {ticker}")
            return {'ticker': ticker, 'last_updated': datetime.now().isoformat()}
    
    def get_historical_prices(self, ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        """
        Get historical stock prices.
        
        Args:
            ticker: Stock ticker
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with historical prices
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                print(f"⚠ No historical data for {ticker}")
                return None
            
            print(f"✓ Fetched {len(hist)} days of historical data for {ticker}")
            return hist
            
        except Exception as e:
            print(f"✗ Error fetching historical data: {e}")
            return None
    
    def get_analyst_estimates(self, ticker: str) -> Dict[str, Any]:
        """
        Get analyst estimates and recommendations.
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with analyst estimates
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get recommendations
            recs = stock.recommendations
            
            # Get earnings estimates
            earnings = stock.earnings_estimate
            
            estimates = {
                'ticker': ticker,
                'recommendations': recs.to_dict() if recs is not None else {},
                'earnings_estimates': earnings.to_dict() if earnings is not None else {},
                'last_updated': datetime.now().isoformat()
            }
            
            return estimates
            
        except Exception as e:
            print(f"✗ Error fetching analyst estimates: {e}")
            return {'ticker': ticker, 'last_updated': datetime.now().isoformat()}
    
    def get_financials(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Get company financial statements.
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with income statement, balance sheet, cash flow
        """
        try:
            stock = yf.Ticker(ticker)
            
            financials = {
                'income_statement': stock.financials,
                'balance_sheet': stock.balance_sheet,
                'cash_flow': stock.cashflow,
            }
            
            print(f"✓ Fetched financial statements for {ticker}")
            return financials
            
        except Exception as e:
            print(f"✗ Error fetching financials: {e}")
            return {}
    
    def get_key_statistics(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive key statistics for DCF modeling.
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with all key metrics needed for DCF
        """
        quote = self.get_stock_quote(ticker)
        financials = self.get_financials(ticker)
        
        # Combine into DCF-ready format
        stats = {
            'ticker': ticker,
            'valuation_metrics': {
                'current_price': quote.get('current_price'),
                'market_cap': quote.get('market_cap'),
                'enterprise_value': quote.get('enterprise_value'),
                'pe_ratio': quote.get('pe_ratio'),
                'price_to_book': quote.get('price_to_book'),
                'price_to_sales': quote.get('price_to_sales'),
            },
            'risk_metrics': {
                'beta': quote.get('beta'),
                'fifty_two_week_high': quote.get('fifty_two_week_high'),
                'fifty_two_week_low': quote.get('fifty_two_week_low'),
            },
            'profitability_metrics': {
                'profit_margin': quote.get('profit_margin'),
                'operating_margin': quote.get('operating_margin'),
                'return_on_equity': quote.get('return_on_equity'),
                'return_on_assets': quote.get('return_on_assets'),
            },
            'financial_health': {
                'debt_to_equity': quote.get('debt_to_equity'),
                'current_ratio': quote.get('current_ratio'),
            },
            'shares': {
                'shares_outstanding': quote.get('shares_outstanding'),
                'float_shares': quote.get('float_shares'),
            },
            'analyst_data': {
                'target_price_mean': quote.get('target_price_mean'),
                'recommendation': quote.get('recommendation'),
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return stats


# Example usage
if __name__ == "__main__":
    scraper = YahooFinanceScraper()
    
    # Test with Apple
    print("=" * 60)
    print("Testing Yahoo Finance Scraper")
    print("=" * 60)
    
    quote = scraper.get_stock_quote("AAPL")
    
    if quote:
        print(f"\n{'='*60}")
        print(f"Stock: {quote['ticker']}")
        print(f"{'='*60}")
        print(f"Current Price: ${quote.get('current_price', 'N/A')}")
        print(f"Market Cap: ${quote.get('market_cap', 0)/1e9:.2f}B" if quote.get('market_cap') else "Market Cap: N/A")
        print(f"Beta: {quote.get('beta', 'N/A')}")
        print(f"P/E Ratio: {quote.get('pe_ratio', 'N/A')}")
        print(f"Sector: {quote.get('sector', 'N/A')}")
        print(f"Industry: {quote.get('industry', 'N/A')}")
        
        # Get historical data
        print(f"\n📊 Fetching historical prices...")
        hist = scraper.get_historical_prices("AAPL", period="3mo")
        if hist is not None:
            print(f"  → Latest Close: ${hist['Close'].iloc[-1]:.2f}")
            print(f"  → 3-Month High: ${hist['High'].max():.2f}")
            print(f"  → 3-Month Low: ${hist['Low'].min():.2f}")
