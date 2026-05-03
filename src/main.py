#!/usr/bin/env python3
"""
Katsu DCF Engine - Main Entry Point

Command-line interface for generating DCF models.

Usage:
    python src/main.py --ticker AAPL
    python src/main.py --ticker MSFT --wacc 0.08 --growth 0.05
"""

import click
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.sec_edgar import SECEdgarScraper


@click.command()
@click.option('--ticker', '-t', required=True, help='Stock ticker symbol (e.g., AAPL, MSFT)')
@click.option('--wacc', '-w', default=None, type=float, help='WACC override (default: auto-calculate)')
@click.option('--growth', '-g', default=None, type=float, help='Terminal growth rate override (default: auto-calculate)')
@click.option('--years', '-y', default=5, type=int, help='Projection years (default: 5)')
@click.option('--output-dir', '-o', default='../output', help='Output directory for Excel files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(ticker, wacc, growth, years, output_dir, verbose):
    """
    Katsu DCF Engine - Generate automated DCF valuation models.
    
    Fetches financial data from SEC EDGAR and Yahoo Finance,
    then generates a professional Excel DCF model.
    """
    ticker = ticker.upper()
    
    click.echo(f"\n{'='*60}")
    click.echo(f"🚀 Katsu DCF Engine")
    click.echo(f"{'='*60}")
    click.echo(f"Ticker: {ticker}")
    click.echo(f"Projection Years: {years}")
    if wacc:
        click.echo(f"WACC: {wacc:.2%} (override)")
    if growth:
        click.echo(f"Terminal Growth: {growth:.2%} (override)")
    click.echo(f"{'='*60}\n")
    
    # Step 1: Fetch SEC data
    click.echo("📊 Step 1/4: Fetching SEC EDGAR data...")
    scraper = SECEdgarScraper()
    profile = scraper.get_company_profile(ticker)
    
    if not profile:
        click.echo("❌ Failed to fetch SEC data. Check ticker symbol.")
        sys.exit(1)
    
    click.echo(f"✓ Found {len(profile['filings'])} recent filings")
    click.echo(f"✓ Parsed {len(profile['financials'])} financial statements\n")
    
    # Display extracted financials
    click.echo("📋 Recent Financial Data:")
    click.echo("-" * 60)
    for fin in profile['financials']:
        click.echo(f"{fin.form_type} ({fin.period_end_date}):")
        if fin.revenue:
            click.echo(f"  • Revenue: ${fin.revenue/1e9:.2f}B")
        if fin.net_income:
            click.echo(f"  • Net Income: ${fin.net_income/1e9:.2f}B")
        if fin.free_cash_flow:
            click.echo(f"  • Free Cash Flow: ${fin.free_cash_flow/1e9:.2f}B")
    click.echo("")
    
    # TODO: Step 2: Fetch Yahoo Finance data
    click.echo("📈 Step 2/4: Fetching Yahoo Finance data... (TODO)")
    click.echo("   → Current price, market cap, beta, historicals\n")
    
    # TODO: Step 3: Calculate DCF
    click.echo("🧮 Step 3/4: Calculating DCF valuation... (TODO)")
    click.echo("   → FCF projections, WACC, terminal value\n")
    
    # TODO: Step 4: Generate Excel
    click.echo("📝 Step 4/4: Generating Excel model... (TODO)")
    output_path = os.path.join(output_dir, f"{ticker}_DCF_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    click.echo(f"   → Output: {output_path}\n")
    
    click.echo("✅ SEC data fetch complete!")
    click.echo("\n⏭️  Next steps:")
    click.echo("   1. Implement Yahoo Finance scraper")
    click.echo("   2. Build DCF calculation engine")
    click.echo("   3. Create Excel generator")
    click.echo("")


if __name__ == '__main__':
    main()
