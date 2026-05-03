#!/usr/bin/env python3
"""
AI Impact Assessment Module for Katsu DCF Engine

Adjusts DCF assumptions based on AI exposure and impact:
- AI revenue exposure (% of revenue from AI products)
- AI capex intensity (infrastructure spending)
- Industry AI adoption rates
- AI margin impact (efficiency gains vs. investment costs)

Sources:
- Company earnings calls (AI mentions, AI revenue guidance)
- Industry reports (AI adoption rates by sector)
- Capex breakdown (AI infrastructure vs. traditional)
"""

import yfinance as yf
from typing import Dict, Any, List, Tuple
from datetime import datetime
import re


class AIImpactAssessor:
    """
    Assesses AI impact on company valuations.
    """
    
    # AI exposure by sector (0-1 scale, 1 = highest AI exposure)
    SECTOR_AI_EXPOSURE = {
        'Technology': 0.95,
        'Communication Services': 0.85,
        'Consumer Discretionary': 0.70,
        'Healthcare': 0.65,
        'Financials': 0.60,
        'Industrials': 0.50,
        'Energy': 0.35,
        'Materials': 0.30,
        'Utilities': 0.25,
        'Real Estate': 0.20,
        'Consumer Staples': 0.25,
    }
    
    # AI growth premium by sector (additional growth rate due to AI)
    SECTOR_AI_GROWTH_PREMIUM = {
        'Technology': 0.08,      # +8% from AI
        'Communication Services': 0.06,
        'Consumer Discretionary': 0.04,
        'Healthcare': 0.05,
        'Financials': 0.03,
        'Industrials': 0.03,
        'Energy': 0.02,
        'Materials': 0.01,
        'Utilities': 0.01,
        'Real Estate': 0.01,
        'Consumer Staples': 0.01,
    }
    
    # Company-specific AI leaders (additional premium on top of sector)
    AI_LEADERS = {
        'NVDA': 0.15,    # NVIDIA: AI chip monopoly
        'MSFT': 0.10,    # Microsoft: Azure AI, OpenAI partnership
        'GOOGL': 0.10,   # Google: DeepMind, Gemini, AI search
        'META': 0.08,    # Meta: AI-driven ad targeting
        'AMZN': 0.08,    # Amazon: AWS AI, Alexa
        'AAPL': 0.06,    # Apple: Apple Intelligence, on-device AI
        'TSLA': 0.10,    # Tesla: FSD, Optimus, AI robotics
        'AMD': 0.12,     # AMD: AI GPUs
        'AVGO': 0.08,    # Broadcom: AI networking chips
        'CRM': 0.07,     # Salesforce: Einstein AI
        'ORCL': 0.06,    # Oracle: Cloud AI
        'ADBE': 0.07,    # Adobe: Firefly AI
        'NOW': 0.08,     # ServiceNow: AI workflow
        'PLTR': 0.10,    # Palantir: AI platforms
        'SNOW': 0.06,    # Snowflake: AI data cloud
    }
    
    def __init__(self):
        """Initialize AI impact assessor"""
        self._cache = {}
    
    def assess_ai_impact(self, ticker: str) -> Dict[str, Any]:
        """
        Assess AI impact on a company's valuation.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with AI impact metrics and adjusted assumptions
        """
        print(f"\n🤖 Assessing AI Impact for {ticker}...")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get sector
            sector = info.get('sector', 'Technology')
            industry = info.get('industry', 'Software')
            
            # Base AI exposure from sector
            base_ai_exposure = self.SECTOR_AI_EXPOSURE.get(sector, 0.50)
            base_ai_premium = self.SECTOR_AI_GROWTH_PREMIUM.get(sector, 0.03)
            
            # Company-specific AI leader premium
            ai_leader_premium = self.AI_LEADERS.get(ticker.upper(), 0.0)
            
            # Total AI growth premium
            total_ai_premium = base_ai_premium + ai_leader_premium
            
            # Assess AI maturity (based on public info)
            ai_maturity = self._assess_ai_maturity(ticker, info)
            
            # AI capex intensity (estimated % of revenue spent on AI infrastructure)
            ai_capex_intensity = self._estimate_ai_capex_intensity(ticker, sector)
            
            # AI margin impact (short-term pressure, long-term expansion)
            margin_impact = self._estimate_ai_margin_impact(ticker, ai_maturity)
            
            # Build result
            result = {
                'ticker': ticker,
                'sector': sector,
                'industry': industry,
                'ai_exposure_score': base_ai_exposure,
                'ai_leader_premium': ai_leader_premium,
                'total_ai_growth_premium': total_ai_premium,
                'ai_maturity_score': ai_maturity,
                'ai_capex_intensity': ai_capex_intensity,
                'ai_margin_impact_short_term': margin_impact['short_term'],
                'ai_margin_impact_long_term': margin_impact['long_term'],
                'is_ai_leader': ticker.upper() in self.AI_LEADERS,
                'ai_leader_tier': self._get_ai_leader_tier(ticker),
                'last_updated': datetime.now().isoformat()
            }
            
            # Print summary
            print(f"  Sector: {sector}")
            print(f"  AI Exposure Score: {base_ai_exposure:.0%}")
            if ai_leader_premium > 0:
                print(f"  ✓ AI Leader Premium: +{ai_leader_premium:.0%}")
            print(f"  Total AI Growth Premium: +{total_ai_premium:.0%}")
            print(f"  AI Maturity: {ai_maturity:.0%}")
            print(f"  AI Capex Intensity: {ai_capex_intensity:.0%} of revenue")
            
            return result
            
        except Exception as e:
            print(f"  ✗ Error assessing AI impact: {e}")
            return self._fallback_ai_assessment(ticker)
    
    def _assess_ai_maturity(self, ticker: str, info: Dict) -> float:
        """
        Assess company's AI maturity (0-1 scale).
        
        Based on:
        - AI product launches
        - AI R&D spending
        - AI partnerships/acquisitions
        - AI revenue disclosure
        """
        # Known AI maturity levels (simplified)
        ai_maturity_map = {
            'MSFT': 0.95,   # Copilot everywhere, OpenAI partner
            'GOOGL': 0.90,  # DeepMind, Gemini, AI-first search
            'NVDA': 0.98,   # AI chip monopoly, full stack
            'META': 0.85,   # Llama models, AI-driven ads
            'AMZN': 0.88,   # AWS AI, Alexa, AI logistics
            'AAPL': 0.75,   # Apple Intelligence, on-device AI (late but integrated)
            'TSLA': 0.85,   # FSD, Dojo, Optimus
            'AMD': 0.80,    # MI300 AI chips
            'CRM': 0.78,    # Einstein AI
            'ORCL': 0.72,   # Cloud AI
            'ADBE': 0.80,   # Firefly AI
            'NOW': 0.82,    # AI workflow
            'PLTR': 0.85,   # AI platforms
            'AVGO': 0.78,   # AI networking
        }
        
        return ai_maturity_map.get(ticker.upper(), 0.60)  # Default 60% maturity
    
    def _estimate_ai_capex_intensity(self, ticker: str, sector: str) -> float:
        """
        Estimate AI-related capex as % of revenue.
        
        AI infrastructure (data centers, GPUs) is capex-intensive.
        """
        # AI capex intensity by company type
        ai_capex_map = {
            'MSFT': 0.15,   # Azure AI infrastructure
            'GOOGL': 0.18,  # Massive AI data center buildout
            'META': 0.20,   # Zuckerberg: "Year of Efficiency" → AI infrastructure
            'AMZN': 0.16,   # AWS AI + logistics AI
            'NVDA': 0.08,   # Chip design (less capex than cloud providers)
            'AAPL': 0.06,   # On-device AI (less infrastructure needed)
            'TSLA': 0.12,   # Dojo supercomputer, factories
            'ORCL': 0.14,   # Cloud infrastructure
        }
        
        base_capex = ai_capex_map.get(ticker.upper(), 0.05)
        
        # Adjust for sector
        if sector == 'Technology':
            base_capex = max(base_capex, 0.08)
        
        return base_capex
    
    def _estimate_ai_margin_impact(self, ticker: str, ai_maturity: float) -> Dict[str, float]:
        """
        Estimate AI impact on operating margins.
        
        Short-term: Margin pressure from AI investments
        Long-term: Margin expansion from AI efficiency/revenue
        """
        # High maturity companies see faster margin expansion
        if ai_maturity >= 0.85:
            short_term = -0.02  # -2% margin pressure
            long_term = 0.05    # +5% margin expansion
        elif ai_maturity >= 0.70:
            short_term = -0.03
            long_term = 0.04
        else:
            short_term = -0.04
            long_term = 0.02
        
        return {
            'short_term': short_term,
            'long_term': long_term
        }
    
    def _get_ai_leader_tier(self, ticker: str) -> str:
        """Categorize AI leader tier"""
        ticker_upper = ticker.upper()
        
        if ticker_upper in ['NVDA', 'MSFT', 'GOOGL']:
            return 'Tier 1: AI Infrastructure Leaders'
        elif ticker_upper in ['META', 'AMZN', 'TSLA', 'AMD']:
            return 'Tier 2: AI Platform Leaders'
        elif ticker_upper in ['AAPL', 'CRM', 'ORCL', 'ADBE', 'NOW']:
            return 'Tier 3: AI Application Leaders'
        elif ticker_upper in self.AI_LEADERS:
            return 'Tier 4: AI Emerging'
        else:
            return 'Not Classified'
    
    def _fallback_ai_assessment(self, ticker: str) -> Dict[str, Any]:
        """Fallback AI assessment when data unavailable"""
        return {
            'ticker': ticker,
            'sector': 'Unknown',
            'ai_exposure_score': 0.50,
            'ai_leader_premium': 0.0,
            'total_ai_growth_premium': 0.03,
            'ai_maturity_score': 0.60,
            'ai_capex_intensity': 0.05,
            'ai_margin_impact_short_term': -0.03,
            'ai_margin_impact_long_term': 0.03,
            'is_ai_leader': False,
            'ai_leader_tier': 'Not Classified',
            'last_updated': datetime.now().isoformat()
        }
    
    def adjust_growth_for_ai(self, base_growth_rates: List[float], 
                            ai_assessment: Dict[str, Any]) -> List[float]:
        """
        Adjust growth rates based on AI impact.
        
        Args:
            base_growth_rates: Original analyst consensus growth rates
            ai_assessment: AI impact assessment results
            
        Returns:
            AI-adjusted growth rates
        """
        ai_premium = ai_assessment['total_ai_growth_premium']
        ai_maturity = ai_assessment['ai_maturity_score']
        
        # AI impact fades over time (strongest in near-term)
        adjusted_rates = []
        for i, rate in enumerate(base_growth_rates):
            # AI premium weighted by maturity and time
            year_weight = 1.0 - (i * 0.15)  # Years 1-5: 100%, 85%, 70%, 55%, 40%
            maturity_weight = ai_maturity
            
            ai_adjustment = ai_premium * year_weight * maturity_weight
            adjusted_rate = rate + ai_adjustment
            
            # Cap at reasonable maximum (50% growth)
            adjusted_rate = min(adjusted_rate, 0.50)
            
            adjusted_rates.append(adjusted_rate)
        
        return adjusted_rates
    
    def adjust_margins_for_ai(self, base_margin: float, 
                             ai_assessment: Dict[str, Any],
                             projection_year: int) -> float:
        """
        Adjust FCF margin based on AI impact.
        
        Args:
            base_margin: Current FCF margin
            ai_assessment: AI impact assessment
            projection_year: Year of projection (1-5)
            
        Returns:
            AI-adjusted margin
        """
        short_term_impact = ai_assessment['ai_margin_impact_short_term']
        long_term_impact = ai_assessment['ai_margin_impact_long_term']
        
        # Transition from short-term pressure to long-term expansion
        # Linear interpolation over 5 years
        transition_factor = (projection_year - 1) / 4.0  # 0% → 100% over 5 years
        
        margin_impact = short_term_impact + (long_term_impact - short_term_impact) * transition_factor
        
        adjusted_margin = base_margin + margin_impact
        
        # Keep within reasonable bounds
        adjusted_margin = max(0.05, min(0.50, adjusted_margin))
        
        return adjusted_margin


def get_ai_adjusted_dcf_inputs(ticker: str, base_inputs: Any) -> Tuple[Any, Dict[str, Any]]:
    """
    Convenience function to get AI-adjusted DCF inputs.
    
    Args:
        ticker: Stock ticker
        base_inputs: Original DCFInputs object
        
    Returns:
        Tuple of (adjusted_inputs, ai_assessment)
    """
    assessor = AIImpactAssessor()
    
    # Assess AI impact
    ai_assessment = assessor.assess_ai_impact(ticker)
    
    # Adjust growth rates
    adjusted_growth = assessor.adjust_growth_for_ai(
        base_inputs.revenue_growth_rates,
        ai_assessment
    )
    
    # Update inputs
    base_inputs.revenue_growth_rates = adjusted_growth
    
    # Adjust FCF margin for AI impact (use year 1 as base)
    base_margin = base_inputs.free_cash_flow / base_inputs.revenue if base_inputs.revenue > 0 else 0.25
    adjusted_margin = assessor.adjust_margins_for_ai(base_margin, ai_assessment, 1)
    
    # Recalculate FCF with adjusted margin
    base_inputs.free_cash_flow = base_inputs.revenue * adjusted_margin
    
    print(f"\n📊 AI-Adjusted Assumptions:")
    print(f"  Original Growth: {[f'{g:.1%}' for g in base_inputs.revenue_growth_rates]}")
    print(f"  AI-Adjusted Growth: {[f'{g:.1%}' for g in adjusted_growth]}")
    print(f"  AI Growth Premium: +{ai_assessment['total_ai_growth_premium']:.0%}")
    print(f"  FCF Margin: {base_margin:.1%} → {adjusted_margin:.1%} (AI-adjusted)")
    
    return base_inputs, ai_assessment


# Example usage
if __name__ == "__main__":
    assessor = AIImpactAssessor()
    
    # Test with tech companies
    tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META']
    
    for ticker in tickers:
        print(f"\n{'='*60}")
        assessment = assessor.assess_ai_impact(ticker)
        
        print(f"\n📋 AI Impact Summary: {ticker}")
        print(f"  AI Exposure: {assessment['ai_exposure_score']:.0%}")
        print(f"  AI Leader: {assessment['is_ai_leader']}")
        if assessment['is_ai_leader']:
            print(f"  Leader Tier: {assessment['ai_leader_tier']}")
        print(f"  AI Growth Premium: +{assessment['total_ai_growth_premium']:.0%}")
        print(f"  AI Maturity: {assessment['ai_maturity_score']:.0%}")
        print(f"  AI Capex: {assessment['ai_capex_intensity']:.0%} of revenue")
        print(f"  Margin Impact: {assessment['ai_margin_impact_short_term']:+.0%} (ST) → {assessment['ai_margin_impact_long_term']:+.0%} (LT)")
