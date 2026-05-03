"""
Macroeconomic Data Scraper for Katsu DCF Engine

Fetches real-time economic data to inform DCF assumptions:
- 10-Year Treasury yield (risk-free rate)
- S&P 500 historical returns (market risk premium)
- GDP growth rates
- Industry-specific data
- Inflation expectations

All data sourced from Yahoo Finance and public APIs.
"""

import yfinance as yf
import requests
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime, timedelta
import numpy as np


class MacroDataScraper:
    """
    Fetches macroeconomic data for DCF assumption calibration.
    """
    
    def __init__(self):
        """Initialize macro data scraper"""
        self.session = yf
        self._cache = {}
    
    def get_risk_free_rate(self) -> Dict[str, Any]:
        """
        Get current risk-free rate from 10-Year Treasury yield.
        
        Returns:
            Dictionary with current rate and metadata
        """
        print("  → Fetching 10-Year Treasury yield...")
        
        try:
            # Yahoo Finance ticker for 10-Year Treasury
            tnx = yf.Ticker("^TNX")
            hist = tnx.history(period="1d")
            
            if hist.empty:
                print("    ⚠ Treasury data unavailable, using fallback")
                return self._fallback_risk_free_rate()
            
            current_yield = hist['Close'].iloc[-1]
            
            # TNX is scaled by 10, so divide by 10
            rate = current_yield / 100.0
            
            result = {
                'rate': rate,
                'source': '10-Year Treasury (^TNX)',
                'value_percent': rate * 100,
                'last_updated': datetime.now().isoformat(),
                'raw_yield': current_yield
            }
            
            print(f"    ✓ Risk-free rate: {rate:.2%} (10Y Treasury)")
            return result
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._fallback_risk_free_rate()
    
    def _fallback_risk_free_rate(self) -> Dict[str, Any]:
        """Fallback risk-free rate when API fails"""
        rate = 0.045  # 4.5%
        return {
            'rate': rate,
            'source': 'Fallback (historical average)',
            'value_percent': rate * 100,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_market_risk_premium(self, period: str = "10y") -> Dict[str, Any]:
        """
        Calculate market risk premium from S&P 500 historical returns.
        
        Market Risk Premium = Expected Market Return - Risk-Free Rate
        
        Uses historical S&P 500 returns as proxy for expected market return.
        
        Args:
            period: Lookback period (5y, 10y, 20y, max)
            
        Returns:
            Dictionary with calculated premium
        """
        print(f"  → Calculating market risk premium ({period} historical)...")
        
        try:
            # Get S&P 500 data
            spy = yf.Ticker("^GSPC")
            hist = spy.history(period=period)
            
            if hist.empty or len(hist) < 60:
                print("    ⚠ Insufficient S&P 500 data, using fallback")
                return self._fallback_market_premium()
            
            # Calculate annualized return
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            
            # Calculate years
            days = (hist.index[-1] - hist.index[0]).days
            years = days / 365.25
            
            # Annualized return
            total_return = (end_price - start_price) / start_price
            annualized_return = (1 + total_return) ** (1 / years) - 1
            
            # Get current risk-free rate
            rf_data = self.get_risk_free_rate()
            rf_rate = rf_data['rate']
            
            # Market risk premium
            mrp = annualized_return - rf_rate
            
            # Sanity check: MRP typically 4-8%
            if mrp < 0.03 or mrp > 0.10:
                print(f"    ⚠ MRP {mrp:.1%} outside normal range, using blended estimate")
                mrp = 0.5 * mrp + 0.5 * 0.065  # Blend with historical average
            
            result = {
                'market_risk_premium': mrp,
                'expected_market_return': annualized_return,
                'risk_free_rate': rf_rate,
                'source': f'S&P 500 {period} historical',
                'annualized_market_return': annualized_return * 100,
                'calculation_period_years': years,
                'last_updated': datetime.now().isoformat()
            }
            
            print(f"    ✓ Market Risk Premium: {mrp:.2%}")
            print(f"      - Expected Market Return: {annualized_return:.2%}")
            print(f"      - Risk-Free Rate: {rf_rate:.2%}")
            return result
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._fallback_market_premium()
    
    def _fallback_market_premium(self) -> Dict[str, Any]:
        """Fallback market risk premium"""
        mrp = 0.065  # 6.5% historical average
        return {
            'market_risk_premium': mrp,
            'expected_market_return': 0.10,  # 10%
            'risk_free_rate': 0.045,
            'source': 'Fallback (historical average)',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_analyst_growth_estimates(self, ticker: str) -> Dict[str, Any]:
        """
        Get analyst consensus growth estimates for a company.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with growth estimates
        """
        print(f"  → Fetching analyst growth estimates for {ticker}...")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get various growth estimates
            estimates = {
                'revenue_growth_next_year': info.get('revenueGrowth'),
                'earnings_growth_next_year': info.get('earningsGrowth'),
                'revenue_growth_quarterly': info.get('revenueQuarterlyGrowth'),
                'earnings_growth_quarterly': info.get('earningsQuarterlyGrowth'),
            }
            
            # Check if we got data
            if not any(estimates.values()):
                print(f"    ⚠ No analyst estimates for {ticker}, using historical")
                return self._estimate_historical_growth(ticker)
            
            # Build growth rate projections (5 years)
            # Use analyst estimates for near-term, fade to terminal
            short_term_growth = estimates['revenue_growth_next_year'] or 0.05
            
            # Fade growth over 5 years
            growth_rates = [
                short_term_growth,
                short_term_growth * 0.90,
                short_term_growth * 0.75,
                short_term_growth * 0.60,
                short_term_growth * 0.50,
            ]
            
            # Ensure reasonable bounds (1% to 30%)
            growth_rates = [max(0.01, min(0.30, g)) for g in growth_rates]
            
            result = {
                'growth_rates': growth_rates,
                'source': 'Analyst consensus + fade',
                'short_term_growth': short_term_growth,
                'last_updated': datetime.now().isoformat()
            }
            
            print(f"    ✓ Revenue growth rates: {[f'{g:.1%}' for g in growth_rates]}")
            return result
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._estimate_historical_growth(ticker)
    
    def _estimate_historical_growth(self, ticker: str) -> Dict[str, Any]:
        """Estimate growth from historical financials"""
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            
            if financials is None or financials.empty:
                return self._fallback_growth_rates()
            
            # Get total revenue row
            if 'Total Revenue' in financials.index:
                revenue = financials.loc['Total Revenue']
            elif 'Total Revenues' in financials.index:
                revenue = financials.loc['Total Revenues']
            else:
                return self._fallback_growth_rates()
            
            # Calculate historical growth rates
            if len(revenue) >= 2:
                growth_rates = []
                for i in range(len(revenue) - 1):
                    if revenue.iloc[i+1] != 0:
                        growth = (revenue.iloc[i] - revenue.iloc[i+1]) / revenue.iloc[i+1]
                        growth_rates.append(growth)
                
                if growth_rates:
                    avg_growth = np.mean(growth_rates)
                    # Project forward with fade
                    projected = [
                        avg_growth,
                        avg_growth * 0.95,
                        avg_growth * 0.85,
                        avg_growth * 0.75,
                        avg_growth * 0.65,
                    ]
                    projected = [max(0.01, min(0.30, g)) for g in projected]
                    
                    print(f"    ✓ Historical avg growth: {avg_growth:.1%}")
                    return {
                        'growth_rates': projected,
                        'source': 'Historical revenue growth',
                        'historical_avg': avg_growth,
                        'last_updated': datetime.now().isoformat()
                    }
            
            return self._fallback_growth_rates()
            
        except Exception as e:
            print(f"    ✗ Error calculating historical growth: {e}")
            return self._fallback_growth_rates()
    
    def _fallback_growth_rates(self) -> Dict[str, Any]:
        """Fallback growth rates"""
        rates = [0.08, 0.07, 0.06, 0.05, 0.05]
        return {
            'growth_rates': rates,
            'source': 'Fallback (conservative estimates)',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_terminal_growth_rate(self, ticker: str = None) -> Dict[str, Any]:
        """
        Calculate appropriate terminal growth rate.
        
        Terminal growth should not exceed:
        - Long-term GDP growth
        - Long-term inflation + real GDP growth
        - Company's sustainable growth rate
        
        Args:
            ticker: Optional ticker for company-specific analysis
            
        Returns:
            Dictionary with terminal growth rate
        """
        print("  → Calculating terminal growth rate...")
        
        try:
            # Use long-term GDP growth expectations (~2-2.5% for US)
            # Can be enhanced with GDP-linked ETFs or economic data
            gdp_growth = 0.025  # 2.5% long-term nominal GDP
            
            # Adjust for inflation expectations (breakeven inflation from TIPS)
            # Simplified: use 2% inflation target + 0.5% real growth
            terminal_growth = 0.025
            
            # For specific companies, could adjust based on:
            # - Industry maturity
            # - Company lifecycle stage
            # - Competitive moat
            
            # For now, use conservative GDP-linked rate
            result = {
                'terminal_growth_rate': terminal_growth,
                'source': 'Long-term GDP growth expectations',
                'rationale': 'Perpetual growth cannot exceed economic growth',
                'last_updated': datetime.now().isoformat()
            }
            
            print(f"    ✓ Terminal growth rate: {terminal_growth:.2%}")
            return result
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return {
                'terminal_growth_rate': 0.025,
                'source': 'Fallback (GDP growth)',
                'last_updated': datetime.now().isoformat()
            }
    
    def get_effective_tax_rate(self, ticker: str) -> Dict[str, Any]:
        """
        Calculate company's effective tax rate from financials.
        
        Effective Tax Rate = Income Tax Expense / Pre-Tax Income
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with tax rate
        """
        print(f"  → Calculating effective tax rate for {ticker}...")
        
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            
            if financials is None or financials.empty:
                return self._fallback_tax_rate()
            
            # Get tax expense and pre-tax income
            tax_expense = None
            pretax_income = None
            
            for idx in financials.index:
                if 'Tax' in idx and 'Provision' in idx:
                    tax_expense = financials.loc[idx]
                elif 'Pretax' in idx or 'Pre-Tax' in idx:
                    pretax_income = financials.loc[idx]
            
            # Try alternative row names
            if tax_expense is None:
                for idx in financials.index:
                    if 'Income Tax' in idx:
                        tax_expense = financials.loc[idx]
                        break
            
            if pretax_income is None:
                for idx in financials.index:
                    if 'Income Before' in idx:
                        pretax_income = financials.loc[idx]
                        break
            
            if tax_expense is not None and pretax_income is not None and len(tax_expense) > 0:
                # Use most recent year
                recent_tax = tax_expense.iloc[0]
                recent_pretax = pretax_income.iloc[0]
                
                if recent_pretax != 0 and recent_pretax > 0:
                    effective_rate = abs(recent_tax) / recent_pretax
                    
                    # Sanity check: should be 10-40% typically
                    if 0.10 <= effective_rate <= 0.40:
                        print(f"    ✓ Effective tax rate: {effective_rate:.1%}")
                        return {
                            'tax_rate': effective_rate,
                            'source': 'Company financials (effective rate)',
                            'last_updated': datetime.now().isoformat()
                        }
            
            return self._fallback_tax_rate()
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._fallback_tax_rate()
    
    def _fallback_tax_rate(self) -> Dict[str, Any]:
        """Fallback tax rate"""
        return {
            'tax_rate': 0.21,  # US corporate tax rate
            'source': 'Fallback (US statutory rate)',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_cost_of_debt(self, ticker: str) -> Dict[str, Any]:
        """
        Estimate company's cost of debt from financials.
        
        Cost of Debt = Interest Expense / Total Debt
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Dictionary with cost of debt
        """
        print(f"  → Calculating cost of debt for {ticker}...")
        
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            
            if financials is None or balance_sheet is None:
                return self._fallback_cost_of_debt(ticker)
            
            # Get interest expense
            interest_expense = None
            for idx in financials.index:
                if 'Interest' in idx and ('Expense' in idx or 'Paid' in idx):
                    interest_expense = financials.loc[idx]
                    break
            
            # Get total debt
            total_debt = None
            for idx in balance_sheet.index:
                if 'Total Debt' in idx or 'Debt' in idx:
                    total_debt = balance_sheet.loc[idx]
                    break
            
            if interest_expense is not None and total_debt is not None:
                recent_interest = abs(interest_expense.iloc[0])
                recent_debt = total_debt.iloc[0]
                
                if recent_debt != 0 and recent_debt > 0:
                    cost_of_debt = recent_interest / recent_debt
                    
                    # Sanity check
                    if 0.01 <= cost_of_debt <= 0.20:
                        print(f"    ✓ Cost of debt: {cost_of_debt:.2%}")
                        return {
                            'cost_of_debt': cost_of_debt,
                            'source': 'Interest expense / Total debt',
                            'last_updated': datetime.now().isoformat()
                        }
            
            return self._fallback_cost_of_debt(ticker)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._fallback_cost_of_debt(ticker)
    
    def _fallback_cost_of_debt(self, ticker: str) -> Dict[str, Any]:
        """Fallback cost of debt based on risk-free rate + spread"""
        rf_data = self.get_risk_free_rate()
        rf_rate = rf_data['rate']
        
        # Add credit spread based on market conditions
        spread = 0.02  # 2% average spread
        cost_of_debt = rf_rate + spread
        
        return {
            'cost_of_debt': cost_of_debt,
            'source': 'Risk-free rate + credit spread',
            'risk_free_rate': rf_rate,
            'credit_spread': spread,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_gdp_growth(self) -> Dict[str, Any]:
        """
        Get US GDP growth rate from FRED API.
        Series: GDP = Gross Domestic Product (billions of dollars)
        Calculates YoY percent change.
        
        Returns:
            Dictionary with GDP growth data
        """
        print("  → Fetching GDP growth rate from FRED...")
        
        try:
            fred_key = "21d934bc76b6214fb384542693fe02bc"
            # Get latest 5 years of quarterly GDP data to calculate YoY growth
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key={fred_key}&file_type=json&sort_order=desc&limit=5"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                obs = data.get('observations', [])
                
                if obs and len(obs) >= 2:
                    # Most recent GDP
                    current_gdp = float(obs[0]['value'])
                    current_date = obs[0]['date']
                    
                    # GDP from 1 year ago (4 quarters back)
                    past_gdp = float(obs[4]['value']) if len(obs) > 4 else float(obs[-1]['value'])
                    
                    # Calculate YoY growth
                    gdp_growth = ((current_gdp - past_gdp) / past_gdp) * 100
                    
                    result = {
                        'gdp_growth_rate': gdp_growth / 100,
                        'gdp_growth_percent': gdp_growth,
                        'source': 'FRED (GDP - YoY calculation)',
                        'current_gdp': current_gdp,
                        'past_gdp': past_gdp,
                        'date': current_date,
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    print(f"    ✓ GDP Growth: {gdp_growth:.2f}% (as of {current_date})")
                    return result
            
            print(f"    ⚠ FRED API error (status: {response.status_code}), using fallback")
            return self._fallback_gdp_growth()
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._fallback_gdp_growth()
    
    def _fallback_gdp_growth(self) -> Dict[str, Any]:
        """Fallback GDP growth rate"""
        rate = 0.025  # 2.5% historical average
        return {
            'gdp_growth_rate': rate,
            'gdp_growth_percent': rate * 100,
            'source': 'Fallback (historical average)',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_inflation_rate(self) -> Dict[str, Any]:
        """
        Get current inflation rate (CPI YoY change) from FRED.
        Series: CPIAUCSL = Consumer Price Index for All Urban Consumers
        
        Returns:
            Dictionary with inflation data
        """
        print("  → Fetching inflation rate (CPI) from FRED...")
        
        try:
            fred_key = "21d934bc76b6214fb384542693fe02bc"
            
            # Get latest CPI value
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={fred_key}&file_type=json&sort_order=desc&limit=13"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                obs = data.get('observations', [])
                
                if obs and len(obs) >= 13:
                    # Most recent is first (descending order)
                    current_cpi = float(obs[0]['value'])
                    current_date = obs[0]['date']
                    
                    # 13th observation is 12 months ago
                    past_cpi = float(obs[12]['value'])
                    
                    # Calculate YoY inflation
                    inflation = ((current_cpi - past_cpi) / past_cpi) * 100
                    
                    result = {
                        'inflation_rate': inflation / 100,
                        'inflation_percent': inflation,
                        'source': 'FRED (CPIAUCSL - CPI YoY)',
                        'current_cpi': current_cpi,
                        'past_cpi': past_cpi,
                        'date': current_date,
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    print(f"    ✓ Inflation Rate: {inflation:.2f}% (as of {current_date})")
                    return result
            
            print(f"    ⚠ FRED API error (status: {response.status_code}), using fallback")
            return self._fallback_inflation()
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._fallback_inflation()
    
    def _fallback_inflation(self) -> Dict[str, Any]:
        """Fallback inflation rate"""
        rate = 0.03  # 3.0% target/average
        return {
            'inflation_rate': rate,
            'inflation_percent': rate * 100,
            'source': 'Fallback (Fed target)',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_gdp_history(self, years: int = 10) -> List[Dict[str, Any]]:
        """
        Get historical GDP growth rates from FRED for charting.
        
        Args:
            years: Number of years of history
            
        Returns:
            List of dicts with year and growth rate
        """
        print(f"  → Fetching {years}-year GDP history from FRED...")
        
        try:
            fred_key = "21d934bc76b6214fb384542693fe02bc"
            # Get quarterly GDP levels
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key={fred_key}&file_type=json"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                observations = data['observations']
                
                # Group by year and calculate YoY growth
                yearly_gdp = {}
                for obs in observations:
                    year = int(obs['date'][:4])
                    try:
                        value = float(obs['value'])
                        # Use Q4 value for each year (or latest available)
                        if year not in yearly_gdp or obs['date'] > yearly_gdp[year]['date']:
                            yearly_gdp[year] = {'value': value, 'date': obs['date']}
                    except:
                        continue
                
                # Calculate YoY growth for each year
                history = []
                sorted_years = sorted(yearly_gdp.keys())
                for i, year in enumerate(sorted_years[-years:]):
                    current = yearly_gdp[year]['value']
                    if i > 0:
                        prev_year = sorted_years[-years:][i-1]
                        prev = yearly_gdp[prev_year]['value']
                        growth = ((current - prev) / prev) * 100
                    else:
                        growth = 0.0
                    
                    history.append({
                        'year': year,
                        'gdp_growth': round(growth, 2)
                    })
                
                if history:
                    print(f"    ✓ Retrieved {len(history)} years of GDP data from FRED")
                    return history
            
            print("    ⚠ FRED API error, using fallback")
            return self._fallback_gdp_history(years)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._fallback_gdp_history(years)
    
    def _fallback_gdp_history(self, years: int = 10) -> List[Dict[str, Any]]:
        """Fallback GDP history with realistic data"""
        # Approximate US GDP growth rates (real data approximations)
        fallback_data = [
            {'year': 2015, 'gdp_growth': 3.1},
            {'year': 2016, 'gdp_growth': 1.7},
            {'year': 2017, 'gdp_growth': 2.3},
            {'year': 2018, 'gdp_growth': 3.0},
            {'year': 2019, 'gdp_growth': 2.3},
            {'year': 2020, 'gdp_growth': -2.8},  # COVID
            {'year': 2021, 'gdp_growth': 5.9},
            {'year': 2022, 'gdp_growth': 2.1},
            {'year': 2023, 'gdp_growth': 2.5},
            {'year': 2024, 'gdp_growth': 2.8},
        ]
        return fallback_data[-years:]
    
    def get_inflation_history(self, years: int = 10) -> List[Dict[str, Any]]:
        """
        Get historical inflation rates from FRED for charting.
        
        Args:
            years: Number of years of history
            
        Returns:
            List of dicts with year and inflation rate
        """
        print(f"  → Fetching {years}-year inflation history from FRED...")
        
        try:
            fred_key = "21d934bc76b6214fb384542693fe02bc"
            # CPIAUCSL = Consumer Price Index (monthly)
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={fred_key}&file_type=json"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                observations = data['observations']
                
                # Calculate YoY inflation for each year
                yearly_inflation = {}
                prev_year_cpi = {}
                
                for obs in observations:
                    date_str = obs['date']
                    year = int(date_str[:4])
                    month = int(date_str[5:7])
                    
                    try:
                        cpi = float(obs['value'])
                        
                        # Store December CPI for each year
                        if month == 12:
                            if year in prev_year_cpi:
                                # Calculate YoY inflation
                                inflation = ((cpi - prev_year_cpi[year]) / prev_year_cpi[year]) * 100
                                yearly_inflation[year] = round(inflation, 2)
                            prev_year_cpi[year + 1] = cpi
                    except:
                        continue
                
                # Convert to list format
                history = [
                    {'year': year, 'inflation': inflation}
                    for year, inflation in sorted(yearly_inflation.items())[-years:]
                ]
                
                if history:
                    print(f"    ✓ Retrieved {len(history)} years of inflation data from FRED")
                    return history
            
            print("    ⚠ FRED API error, using fallback")
            return self._fallback_inflation_history(years)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return self._fallback_inflation_history(years)
    
    def _fallback_inflation_history(self, years: int = 10) -> List[Dict[str, Any]]:
        """Fallback inflation history with realistic data"""
        # Approximate US inflation rates (CPI YoY, real data approximations)
        fallback_data = [
            {'year': 2015, 'inflation': 0.7},
            {'year': 2016, 'inflation': 2.1},
            {'year': 2017, 'inflation': 2.1},
            {'year': 2018, 'inflation': 1.9},
            {'year': 2019, 'inflation': 2.3},
            {'year': 2020, 'inflation': 1.4},
            {'year': 2021, 'inflation': 7.0},  # Post-COVID spike
            {'year': 2022, 'inflation': 6.5},
            {'year': 2023, 'inflation': 3.4},
            {'year': 2024, 'inflation': 2.9},
        ]
        return fallback_data[-years:]
    
    def get_all_dcf_assumptions(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch all macroeconomic and company-specific data for DCF assumptions.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Comprehensive dictionary with all DCF inputs
        """
        print(f"\n📊 Fetching data-driven assumptions for {ticker}...")
        print("=" * 60)
        
        assumptions = {
            'ticker': ticker,
            'fetched_at': datetime.now().isoformat(),
        }
        
        # Macroeconomic data
        print("\n📈 Macroeconomic Data:")
        rf_data = self.get_risk_free_rate()
        assumptions['risk_free_rate'] = rf_data['rate']
        
        mrp_data = self.get_market_risk_premium()
        assumptions['market_risk_premium'] = mrp_data['market_risk_premium']
        
        gdp_data = self.get_gdp_growth()
        assumptions['gdp_growth_rate'] = gdp_data['gdp_growth_rate']
        assumptions['gdp_growth_percent'] = gdp_data['gdp_growth_percent']
        
        inflation_data = self.get_inflation_rate()
        assumptions['inflation_rate'] = inflation_data['inflation_rate']
        assumptions['inflation_percent'] = inflation_data['inflation_percent']
        
        # Company-specific data
        print(f"\n🏢 Company-Specific Data ({ticker}):")
        growth_data = self.get_analyst_growth_estimates(ticker)
        assumptions['revenue_growth_rates'] = growth_data['growth_rates']
        
        terminal_data = self.get_terminal_growth_rate(ticker)
        assumptions['terminal_growth_rate'] = terminal_data['terminal_growth_rate']
        
        tax_data = self.get_effective_tax_rate(ticker)
        assumptions['tax_rate'] = tax_data['tax_rate']
        
        debt_data = self.get_cost_of_debt(ticker)
        assumptions['cost_of_debt'] = debt_data['cost_of_debt']
        
        print(f"\n{'='*60}")
        print("✅ Data-driven assumptions complete!")
        print(f"{'='*60}")
        
        return assumptions


# Example usage
if __name__ == "__main__":
    scraper = MacroDataScraper()
    
    # Test with Apple
    assumptions = scraper.get_all_dcf_assumptions("AAPL")
    
    print(f"\n📋 Summary of Assumptions for AAPL:")
    print(f"  Risk-free rate: {assumptions['risk_free_rate']:.2%}")
    print(f"  Market risk premium: {assumptions['market_risk_premium']:.2%}")
    print(f"  Revenue growth rates: {[f'{g:.1%}' for g in assumptions['revenue_growth_rates']]}")
    print(f"  Terminal growth rate: {assumptions['terminal_growth_rate']:.2%}")
    print(f"  Effective tax rate: {assumptions['tax_rate']:.1%}")
    print(f"  Cost of debt: {assumptions['cost_of_debt']:.2%}")
