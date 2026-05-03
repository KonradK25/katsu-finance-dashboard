#!/usr/bin/env python3
"""
DCF Model with Auto-Fetched Data-Driven Assumptions

This version automatically fetches real-time macroeconomic and company data
to inform DCF assumptions instead of using hardcoded defaults.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.dcf import DCFModel, DCFInputs
from scrapers.macro_data import MacroDataScraper
from scrapers.yahoo_finance import YahooFinanceScraper
from scrapers.sec_edgar_v2 import SECEdgarScraper
from scrapers.ai_impact import AIImpactAssessor, get_ai_adjusted_dcf_inputs
from excel.generator import generate_dcf_excel


def run_auto_dcf(ticker: str) -> DCFInputs:
    """
    Run DCF with automatically fetched data-driven assumptions.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        DCFInputs with real data
    """
    print(f"\n{'='*60}")
    print(f"🚀 Katsu DCF Engine - Data-Driven Valuation")
    print(f"{'='*60}")
    print(f"Ticker: {ticker}")
    print(f"{'='*60}\n")
    
    # Step 1: Fetch macroeconomic data
    print("📊 Step 1/4: Fetching macroeconomic data...")
    macro = MacroDataScraper()
    assumptions = macro.get_all_dcf_assumptions(ticker)
    
    # Step 2: Fetch company market data
    print(f"\n📈 Step 2/4: Fetching {ticker} market data...")
    yahoo = YahooFinanceScraper()
    quote = yahoo.get_stock_quote(ticker)
    
    # Extract key metrics early
    current_price = quote.get('current_price', 0)
    shares_outstanding = quote.get('shares_outstanding', 0)
    beta = quote.get('beta', 1.0)
    market_cap = quote.get('market_cap', 0)
    
    # Step 3: Fetch company financials
    print(f"\n💰 Step 3/4: Fetching {ticker} financials...")
    sec = SECEdgarScraper()
    sec_profile = sec.get_company_profile(ticker)
    
    # Try to get financials from SEC, fallback to Yahoo
    if sec_profile and sec_profile.get('financials') and sec_profile['financials'][0].revenue:
        latest_financials = sec_profile['financials'][0]
        print("  → Using SEC financial data")
    else:
        print("  → SEC data unavailable, using Yahoo Finance financials...")
        # Get financials from Yahoo
        yahoo_financials = yahoo.get_financials(ticker)
        
        # Create mock financial metrics from Yahoo data
        if yahoo_financials and 'income_statement' in yahoo_financials:
            income_stmt = yahoo_financials['income_statement']
            cash_flow = yahoo_financials.get('cash_flow', None)
            balance_sheet = yahoo_financials.get('balance_sheet', None)
            
            # Extract most recent values (in millions typically)
            from scrapers.sec_edgar_v2 import FinancialMetrics
            
            revenue_val = income_stmt.loc['Total Revenue'].iloc[0] if 'Total Revenue' in income_stmt.index else 0
            operating_income_val = income_stmt.loc['Operating Income'].iloc[0] if 'Operating Income' in income_stmt.index else 0
            net_income_val = income_stmt.loc['Net Income'].iloc[0] if 'Net Income' in income_stmt.index else 0
            
            # Get cash flow metrics
            ocf = 0
            capex_val = 0
            fcf_val = 0
            if cash_flow is not None:
                ocf = cash_flow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cash_flow.index else 0
                capex_val = abs(cash_flow.loc['Capital Expenditure'].iloc[0]) if 'Capital Expenditure' in cash_flow.index else 0
                fcf_val = ocf - capex_val
            
            # Get balance sheet metrics
            total_debt_val = 0
            cash_val = 0
            if balance_sheet is not None:
                total_debt_val = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet.index else 0
                cash_val = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0] if 'Cash And Cash Equivalents' in balance_sheet.index else 0
            
            latest_financials = FinancialMetrics(
                ticker=ticker,
                period='TTM',
                form_type='10-K',
                revenue=revenue_val,
                operating_income=operating_income_val,
                net_income=net_income_val,
                free_cash_flow=fcf_val,
                operating_cash_flow=ocf,
                capex=capex_val,
                total_debt=total_debt_val,
                cash_and_equivalents=cash_val,
                shares_outstanding=shares_outstanding
            )
            print(f"  ✓ Loaded Yahoo Finance financials")
        else:
            print("  ⚠ No financial data available")
            latest_financials = None
    
    # Step 4: Build DCF inputs with real data
    print(f"\n🧮 Step 4/4: Building DCF model with real data...")
    
    # Get financial metrics from SEC or fallback
    if latest_financials:
        revenue = latest_financials.revenue or 0
        free_cash_flow = latest_financials.free_cash_flow or 0
        operating_cash_flow = latest_financials.operating_cash_flow or 0
        capex = latest_financials.capex or 0
        total_debt = latest_financials.total_debt or 0
        cash = latest_financials.cash_and_equivalents or 0
        operating_income = latest_financials.operating_income or 0
        net_income = latest_financials.net_income or 0
    else:
        # Fallback estimates
        revenue = 0
        free_cash_flow = 0
        operating_cash_flow = 0
        capex = 0
        total_debt = 0
        cash = 0
        operating_income = 0
        net_income = 0
    
    # Create DCF inputs with REAL data
    inputs = DCFInputs(
        ticker=ticker,
        current_price=current_price,
        shares_outstanding=shares_outstanding,
        revenue=revenue,
        operating_income=operating_income,
        net_income=net_income,
        free_cash_flow=free_cash_flow,
        operating_cash_flow=operating_cash_flow,
        capex=capex,
        total_debt=total_debt,
        cash_and_equivalents=cash,
        beta=beta,
        
        # REAL data-driven assumptions
        risk_free_rate=assumptions['risk_free_rate'],
        market_risk_premium=assumptions['market_risk_premium'],
        revenue_growth_rates=assumptions['revenue_growth_rates'],
        terminal_growth_rate=assumptions['terminal_growth_rate'],
        tax_rate_override=assumptions['tax_rate'],
    )
    
    print(f"\n✅ DCF Inputs built with real-time data!")
    
    # Step 5: Assess AI impact and adjust assumptions
    print(f"\n🤖 Step 5/5: Assessing AI impact...")
    ai_assessor = AIImpactAssessor()
    ai_assessment = ai_assessor.assess_ai_impact(ticker)
    
    # Adjust growth rates for AI impact
    original_growth = inputs.revenue_growth_rates.copy()
    adjusted_growth = ai_assessor.adjust_growth_for_ai(original_growth, ai_assessment)
    inputs.revenue_growth_rates = adjusted_growth
    
    # Adjust FCF margin for AI impact
    base_margin = inputs.free_cash_flow / inputs.revenue if inputs.revenue > 0 else 0.25
    adjusted_margin = ai_assessor.adjust_margins_for_ai(base_margin, ai_assessment, 1)
    inputs.free_cash_flow = inputs.revenue * adjusted_margin
    
    print(f"\n📊 AI-Adjusted Assumptions:")
    print(f"  Original Growth: {[f'{g:.1%}' for g in original_growth]}")
    print(f"  AI-Adjusted Growth: {[f'{g:.1%}' for g in adjusted_growth]}")
    print(f"  AI Growth Premium: +{ai_assessment['total_ai_growth_premium']:.0%}")
    print(f"  FCF Margin: {base_margin:.1%} → {adjusted_margin:.1%} (AI-adjusted)")
    print(f"  AI Leader: {ai_assessment['is_ai_leader']} ({ai_assessment['ai_leader_tier']})")
    
    return inputs, ai_assessment


def main():
    """Main function to run auto DCF"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Katsu DCF Engine - Data-Driven Valuation')
    parser.add_argument('--ticker', '-t', required=True, help='Stock ticker symbol')
    parser.add_argument('--wacc', '-w', type=float, default=None, help='Override WACC')
    parser.add_argument('--output', '-o', type=str, default=None, help='Output Excel file path')
    
    args = parser.parse_args()
    
    # Build inputs with real data and AI adjustments
    inputs, ai_assessment = run_auto_dcf(args.ticker)
    
    # Allow WACC override
    if args.wacc:
        inputs.wacc_override = args.wacc
    
    # Run DCF
    model = DCFModel()
    result = model.run_dcf(inputs)
    
    # Print detailed summary
    print(f"\n{'='*60}")
    print(f"📊 DCF VALUATION COMPLETE: {args.ticker}")
    print(f"{'='*60}")
    print(f"\n📈 Market Data:")
    print(f"  Current Price: ${inputs.current_price:.2f}")
    print(f"  Market Cap: ${inputs.current_price * inputs.shares_outstanding/1e9:.2f}B")
    print(f"  Beta: {inputs.beta:.2f}")
    
    print(f"\n💰 Financial Metrics (Most Recent Period):")
    print(f"  Revenue: ${inputs.revenue/1e9:.2f}B")
    print(f"  Free Cash Flow: ${inputs.free_cash_flow/1e9:.2f}B")
    print(f"  Total Debt: ${inputs.total_debt/1e9:.2f}B")
    print(f"  Cash: ${inputs.cash_and_equivalents/1e9:.2f}B")
    
    print(f"\n📋 Data-Driven Assumptions:")
    print(f"  Risk-Free Rate: {inputs.risk_free_rate:.2%} (10Y Treasury)")
    print(f"  Market Risk Premium: {inputs.market_risk_premium:.2%} (S&P 500 historical)")
    print(f"  Revenue Growth: {[f'{g:.1%}' for g in inputs.revenue_growth_rates]} (Analyst estimates)")
    print(f"  Terminal Growth: {inputs.terminal_growth_rate:.2%} (GDP-linked)")
    print(f"  Tax Rate: {inputs.tax_rate_override:.1%} (Effective rate)")
    
    print(f"\n🎯 Valuation Results:")
    print(f"  WACC: {result.wacc:.2%}")
    print(f"  Intrinsic Value: ${result.intrinsic_value_per_share:.2f}")
    print(f"  Current Price: ${result.current_price:.2f}")
    print(f"  Upside/(Downside): {result.upside_downside:+.1%}")
    print(f"  Recommendation: {result.recommendation}")
    
    print(f"\n📊 Sensitivity Analysis:")
    print(f"  See table above for WACC vs Growth matrix")
    
    print(f"\n{'='*60}")
    print(f"✅ Valuation complete! Data sources:")
    print(f"  - Macroeconomic: Yahoo Finance (^TNX, ^GSPC)")
    print(f"  - Company: SEC EDGAR (10-K/10-Q), Yahoo Finance")
    print(f"  - Analyst estimates: Yahoo Finance consensus")
    print(f"{'='*60}")
    
    # Generate Excel output
    if args.output:
        print(f"\n📊 Generating Excel model...")
        excel_path = generate_dcf_excel(inputs, result, args.output)
        print(f"  ✓ Excel saved to: {excel_path}")
    
    print(f"\n")
    
    return result


if __name__ == "__main__":
    main()
