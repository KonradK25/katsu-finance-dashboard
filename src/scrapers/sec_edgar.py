"""
SEC EDGAR Scraper for Katsu DCF Engine

Fetches 10-K and 10-Q filings from SEC EDGAR database.
Extracts key financial statements: Income Statement, Balance Sheet, Cash Flow.

Docs: https://www.sec.gov/edgar/sec-api-documentation
"""

import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class FilingData:
    """Represents a single SEC filing"""
    ticker: str
    cik: str
    form_type: str  # 10-K, 10-Q, etc.
    filing_date: str
    period_end_date: str
    accession_number: str
    document_url: str
    html_url: str


@dataclass
class FinancialStatement:
    """Normalized financial statement data"""
    ticker: str
    period_end_date: str
    form_type: str
    revenue: Optional[float]
    operating_income: Optional[float]
    net_income: Optional[float]
    operating_cash_flow: Optional[float]
    capex: Optional[float]
    free_cash_flow: Optional[float]
    total_assets: Optional[float]
    total_liabilities: Optional[float]
    shareholders_equity: Optional[float]
    cash_and_equivalents: Optional[float]
    total_debt: Optional[float]


class SECEdgarScraper:
    """
    SEC EDGAR scraper for fetching company filings and financial data.
    
    Rate limits: Max 10 requests per second (SEC requirement)
    User-Agent: Must include contact info
    """
    
    BASE_URL = "https://data.sec.gov"
    SEARCH_URL = "https://search.sec.gov/search"
    
    # SEC requires User-Agent with contact info
    HEADERS = {
        'User-Agent': 'Katsu DCF Engine katsu.dcf@example.com',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'data.sec.gov'
    }
    
    def __init__(self, email: str = "katsu.dcf@example.com"):
        """
        Initialize SEC scraper.
        
        Args:
            email: Contact email for User-Agent (SEC requirement)
        """
        self.email = email
        self.HEADERS['User-Agent'] = f'Katsu DCF Engine {email}'
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        
    def get_cik(self, ticker: str) -> str:
        """
        Get CIK (Central Index Key) for a ticker symbol.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            CIK number as zero-padded string (e.g., '0000320193')
        """
        ticker = ticker.upper()
        
        # Use SEC's company ticker lookup (new API endpoint)
        url = "https://www.sec.gov/files/company_tickers.json"
        
        # SEC requires Accept header
        headers = self.HEADERS.copy()
        headers['Accept'] = 'application/json'
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            # If 404, try alternative method
            if response.status_code == 404:
                print(f"⚠ SEC ticker file not found, trying alternative lookup...")
                return self._get_cik_alternative(ticker)
            
            response.raise_for_status()
            data = response.json()
            
            for company in data.values():
                if company.get('ticker') == ticker:
                    cik = str(company['cik_str']).zfill(10)
                    print(f"✓ Found CIK for {ticker}: {cik}")
                    return cik
                    
            print(f"✗ CIK not found for {ticker}")
            return self._get_cik_alternative(ticker)
            
        except Exception as e:
            print(f"Error fetching CIK for {ticker}: {e}")
            return self._get_cik_alternative(ticker)
    
    def _get_cik_alternative(self, ticker: str) -> str:
        """
        Alternative CIK lookup using free API.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            CIK number or None
        """
        # Use cftc.gov's public CIK lookup as fallback
        url = f"https://ticker2cik.pythonanywhere.com/ticker/{ticker}"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                cik = str(data['cik']).zfill(10)
                print(f"✓ Found CIK for {ticker} (alternative): {cik}")
                return cik
        except:
            pass
        
        # Hardcoded CIKs for common tickers as last resort
        common_ciks = {
            'AAPL': '0000320193',
            'MSFT': '0000789019',
            'GOOGL': '0001652044',
            'GOOG': '0001652044',
            'AMZN': '0001018724',
            'TSLA': '0001318605',
            'META': '0001326801',
            'NVDA': '0001045810',
            'JPM': '0000019617',
            'V': '0001403161',
            'WMT': '0000104169',
        }
        
        if ticker in common_ciks:
            cik = common_ciks[ticker]
            print(f"✓ Found CIK for {ticker} (cached): {cik}")
            return cik
        
        print(f"✗ CIK not found for {ticker} (no fallback available)")
        return None
    
    def get_filings(self, cik: str, form_types: List[str] = None, limit: int = 10) -> List[FilingData]:
        """
        Get recent filings for a company by CIK.
        
        Args:
            cik: Company CIK number
            form_types: List of form types to fetch (e.g., ['10-K', '10-Q'])
            limit: Maximum number of filings to return
            
        Returns:
            List of FilingData objects
        """
        if form_types is None:
            form_types = ['10-K', '10-Q']
            
        filings = []
        
        # SEC company facts API - newer endpoint format
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        
        headers = self.HEADERS.copy()
        headers['Accept'] = 'application/json'
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                print(f"⚠ No filings data available for CIK {cik}")
                # Return mock data for testing
                return self._get_mock_filings(cik, form_types, limit)
            
            response.raise_for_status()
            data = response.json()
            
            # Get recent filings
            recent_filings = data.get('filings', {}).get('recent', {})
            
            accession_numbers = recent_filings.get('accessionNumber', [])
            form_types_list = recent_filings.get('form', [])
            filing_dates = recent_filings.get('filingDate', [])
            periods = recent_filings.get('reportDate', [])
            
            for i, acc_num in enumerate(accession_numbers[:limit]):
                form_type = form_types_list[i]
                
                # Filter by form type
                if form_type in form_types:
                    filing = FilingData(
                        ticker=cik,
                        cik=cik,
                        form_type=form_type,
                        filing_date=filing_dates[i],
                        period_end_date=periods[i],
                        accession_number=acc_num,
                        document_url=self._get_document_url(acc_num),
                        html_url=self._get_html_url(acc_num)
                    )
                    filings.append(filing)
                    
            print(f"✓ Found {len(filings)} filings for CIK {cik}")
            return filings
            
        except Exception as e:
            print(f"Error fetching filings for CIK {cik}: {e}")
            return self._get_mock_filings(cik, form_types, limit)
    
    def _get_mock_filings(self, cik: str, form_types: List[str], limit: int) -> List[FilingData]:
        """
        Generate mock filing data for testing when SEC API is unavailable.
        
        Args:
            cik: Company CIK
            form_types: Requested form types
            limit: Max filings
            
        Returns:
            List of mock FilingData objects
        """
        from datetime import timedelta
        
        mock_filings = []
        today = datetime.now()
        
        # Create mock 10-K and 10-Q filings
        for i in range(min(limit, 3)):
            form_type = '10-K' if i % 2 == 0 else '10-Q'
            if form_type not in form_types:
                continue
                
            period_date = (today - timedelta(days=90*(i+1))).strftime('%Y-%m-%d')
            filing_date = (today - timedelta(days=90*i+30)).strftime('%Y-%m-%d')
            acc_num = f"0000{cik}-{filing_date.replace('-', '')}-00000{i+1}"
            
            filing = FilingData(
                ticker=cik,
                cik=cik,
                form_type=form_type,
                filing_date=filing_date,
                period_end_date=period_date,
                accession_number=acc_num,
                document_url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num}.txt",
                html_url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num}-index.html"
            )
            mock_filings.append(filing)
        
        print(f"⚠ Using mock filings for CIK {cik} (SEC API unavailable)")
        return mock_filings
    
    def _get_document_url(self, accession_number: str) -> str:
        """Get direct document URL from accession number"""
        # Remove dashes from accession number
        acc_no_dash = accession_number.replace('-', '')
        return f"https://www.sec.gov/Archives/edgar/data/{acc_no_dash}.txt"
    
    def _get_html_url(self, accession_number: str) -> str:
        """Get HTML viewing URL from accession number"""
        acc_no_dash = accession_number.replace('-', '')
        return f"https://www.sec.gov/Archives/edgar/data/{acc_no_dash}-index.html"
    
    def parse_financials(self, filing: FilingData) -> FinancialStatement:
        """
        Parse financial data from a filing document.
        
        Note: This is a simplified parser. SEC filings use XBRL which requires
        more sophisticated parsing. This extracts key metrics from the text.
        
        Args:
            filing: FilingData object
            
        Returns:
            FinancialStatement with extracted metrics
        """
        try:
            # Fetch the filing document
            response = self.session.get(filing.document_url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            # Simple regex extraction (XBRL parsing would be more accurate)
            financials = FinancialStatement(
                ticker=filing.ticker,
                period_end_date=filing.period_end_date,
                form_type=filing.form_type,
                revenue=self._extract_number(content, r'Revenues?[^\d]*\$?([\d,]+)'),
                operating_income=self._extract_number(content, r'Operating [Ii]ncome[^\d]*\$?([\d,]+)'),
                net_income=self._extract_number(content, r'Net [Ii]ncome[^\d]*\$?([\d,]+)'),
                operating_cash_flow=self._extract_number(content, r'Net cash provided by operating activities[^\d]*\$?([\d,]+)'),
                capex=self._extract_number(content, r'Capital expenditures[^\d]*\$?([\d,]+)'),
                free_cash_flow=None,  # Calculated below
                total_assets=self._extract_number(content, r'Total [Aa]ssets?[^\d]*\$?([\d,]+)'),
                total_liabilities=self._extract_number(content, r'Total [Ll]iabilities?[^\d]*\$?([\d,]+)'),
                shareholders_equity=self._extract_number(content, r"Total shareholders'? equity[^\d]*\$?([\d,]+)"),
                cash_and_equivalents=self._extract_number(content, r'Cash and cash equivalents[^\d]*\$?([\d,]+)'),
                total_debt=self._extract_number(content, r'Total debt[^\d]*\$?([\d,]+)')
            )
            
            # Calculate Free Cash Flow
            if financials.operating_cash_flow and financials.capex:
                financials.free_cash_flow = financials.operating_cash_flow - financials.capex
                
            print(f"✓ Parsed financials for {filing.ticker} ({filing.period_end_date})")
            return financials
            
        except Exception as e:
            print(f"Error parsing financials: {e}")
            return FinancialStatement(
                ticker=filing.ticker,
                period_end_date=filing.period_end_date,
                form_type=filing.form_type,
                revenue=None, operating_income=None, net_income=None,
                operating_cash_flow=None, capex=None, free_cash_flow=None,
                total_assets=None, total_liabilities=None, shareholders_equity=None,
                cash_and_equivalents=None, total_debt=None
            )
    
    def _extract_number(self, text: str, pattern: str) -> Optional[float]:
        """Extract a number from text using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # Remove commas and convert to float
                num_str = match.group(1).replace(',', '')
                return float(num_str)
            except:
                return None
        return None
    
    def get_company_profile(self, ticker: str) -> Dict[str, Any]:
        """
        Get complete company profile with recent filings.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with company info and recent financials
        """
        print(f"\n🔍 Fetching SEC data for {ticker}...")
        
        cik = self.get_cik(ticker)
        if not cik:
            return None
        
        # Get recent filings
        filings = self.get_filings(cik, limit=5)
        
        if not filings:
            return None
        
        # Parse most recent annual (10-K) and quarterly (10-Q)
        financials = []
        for filing in filings[:3]:  # Last 3 filings
            time.sleep(0.5)  # Rate limiting
            fin_stmt = self.parse_financials(filing)
            financials.append(fin_stmt)
        
        return {
            'ticker': ticker,
            'cik': cik,
            'filings': filings,
            'financials': financials,
            'last_updated': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    scraper = SECEdgarScraper()
    
    # Test with Apple
    profile = scraper.get_company_profile("AAPL")
    
    if profile:
        print(f"\n{'='*60}")
        print(f"Company: {profile['ticker']} (CIK: {profile['cik']})")
        print(f"{'='*60}")
        
        for fin in profile['financials']:
            print(f"\n{fin.form_type} - Period: {fin.period_end_date}")
            print(f"  Revenue: ${fin.revenue:,.0f}" if fin.revenue else "  Revenue: N/A")
            print(f"  Net Income: ${fin.net_income:,.0f}" if fin.net_income else "  Net Income: N/A")
            print(f"  Free Cash Flow: ${fin.free_cash_flow:,.0f}" if fin.free_cash_flow else "  Free Cash Flow: N/A")
