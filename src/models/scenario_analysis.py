#!/usr/bin/env python3
"""
Scenario Analysis Module for Katsu DCF Engine

Provides:
- Bear/Base/Bull case scenarios
- Market-implied assumptions calculator
- Sensitivity analysis matrix
- Valuation range visualization
"""

import sys
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.dcf import DCFModel, DCFInputs, DCFResult
from models.dcf_auto import run_auto_dcf


@dataclass
class Scenario:
    """Defines a valuation scenario"""
    name: str
    description: str
    wacc_override: float = None
    risk_free_rate: float = None
    market_risk_premium: float = None
    terminal_growth_rate: float = None
    revenue_growth_adjustment: float = 0.0  # Additive adjustment
    fcf_margin_adjustment: float = 0.0  # Additive adjustment
    projection_years: int = 5
    color: str = "#666666"


class ScenarioAnalyzer:
    """Analyzes multiple valuation scenarios"""
    
    # Pre-built scenarios
    BEAR_CASE = Scenario(
        name="🐻 Bear Case",
        description="Recession + High Rates + AI Disappointment",
        risk_free_rate=0.050,  # 5% (Fed fighting inflation)
        market_risk_premium=0.10,  # 10% (high risk aversion)
        terminal_growth_rate=0.015,  # 1.5% (near stagnation)
        revenue_growth_adjustment=-0.10,  # -10% growth hit
        fcf_margin_adjustment=-0.05,  # -5% margin compression
        projection_years=5,
        color="#dc3545"  # Red
    )
    
    BASE_CASE = Scenario(
        name="📊 Base Case",
        description="Current Data-Driven Assumptions",
        risk_free_rate=None,  # Use real-time data
        market_risk_premium=None,
        terminal_growth_rate=0.025,  # 2.5% (GDP-linked)
        revenue_growth_adjustment=0.0,
        fcf_margin_adjustment=0.0,
        projection_years=5,
        color="#1f77b4"  # Blue
    )
    
    BULL_CASE = Scenario(
        name="🐂 Bull Case",
        description="AI Boom + Rate Cuts + Productivity Surge",
        risk_free_rate=0.030,  # 3% (Fed cuts rates)
        market_risk_premium=0.065,  # 6.5% (low risk aversion)
        terminal_growth_rate=0.040,  # 4% (AI-driven productivity)
        revenue_growth_adjustment=0.15,  # +15% AI boost
        fcf_margin_adjustment=0.05,  # +5% margin expansion
        projection_years=7,  # Extended high-growth period
        color="#28a745"  # Green
    )
    
    def __init__(self, ticker: str):
        """Initialize with a ticker"""
        self.ticker = ticker.upper()
        self.base_inputs = None
        self.base_result = None
        self.scenarios = {}
        
    def run_base_case(self) -> Tuple[DCFInputs, DCFResult]:
        """Run base case with real-time data"""
        print(f"\n{'='*70}")
        print(f"📊 Running Base Case for {self.ticker}")
        print(f"{'='*70}")
        
        # Get real-time inputs
        inputs, ai_assessment = run_auto_dcf(self.ticker)
        self.base_inputs = inputs
        
        # Run DCF
        model = DCFModel()
        result = model.run_dcf(inputs)
        self.base_result = result
        
        print(f"\n✅ Base Case Complete:")
        print(f"   WACC: {result.wacc:.1%}")
        print(f"   Intrinsic Value: ${result.intrinsic_value_per_share:.2f}")
        print(f"   Current Price: ${inputs.current_price:.2f}")
        print(f"   Upside/(Downside): {(result.intrinsic_value_per_share / inputs.current_price - 1):+.1%}")
        
        return inputs, result
    
    def run_scenario(self, scenario: Scenario) -> Tuple[DCFInputs, DCFResult]:
        """Run a specific scenario"""
        print(f"\n{'-'*70}")
        print(f"{scenario.name}: {scenario.description}")
        print(f"{'-'*70}")
        
        if self.base_inputs is None:
            raise ValueError("Must run base case first")
        
        # Clone base inputs
        from copy import deepcopy
        inputs = deepcopy(self.base_inputs)
        
        # Apply scenario adjustments
        
        # 1. Adjust macro assumptions
        if scenario.risk_free_rate:
            inputs.risk_free_rate = scenario.risk_free_rate
            print(f"  → Risk-free rate: {inputs.risk_free_rate:.1%} ({scenario.risk_free_rate:.1%})")
        
        if scenario.market_risk_premium:
            inputs.market_risk_premium = scenario.market_risk_premium
            print(f"  → Market risk premium: {inputs.market_risk_premium:.1%}")
        
        # 2. Recalculate WACC
        inputs.wacc_override = None  # Clear override to recalculate
        model = DCFModel()
        wacc = model.calculate_wacc(
            inputs.beta,
            inputs.risk_free_rate,
            inputs.market_risk_premium,
            inputs.cost_of_debt or 0.05,
            inputs.tax_rate_override or 0.21,
            inputs.market_cap / inputs.current_price if inputs.current_price > 0 else 1e12,
            inputs.total_debt,
            inputs.cash_and_equivalents
        )
        
        if scenario.wacc_override:
            wacc = scenario.wacc_override
        
        print(f"  → Scenario WACC: {wacc:.1%}")
        
        # 3. Adjust growth rates
        if scenario.revenue_growth_adjustment != 0:
            original_growth = inputs.revenue_growth_rates.copy()
            adjusted_growth = []
            for i, g in enumerate(original_growth):
                # Growth adjustment fades over time
                fade_factor = 1.0 - (i * 0.15)
                adjustment = scenario.revenue_growth_adjustment * fade_factor
                adjusted_g = max(-0.10, min(0.80, g + adjustment))  # Cap between -10% and 80%
                adjusted_growth.append(adjusted_g)
            
            inputs.revenue_growth_rates = adjusted_growth
            print(f"  → Growth rates adjusted: {[f'{g:.1%}' for g in adjusted_growth]}")
        
        # 4. Adjust terminal growth
        if scenario.terminal_growth_rate:
            inputs.terminal_growth_rate = scenario.terminal_growth_rate
            print(f"  → Terminal growth: {inputs.terminal_growth_rate:.1%}")
        
        # 5. Adjust FCF margin
        if scenario.fcf_margin_adjustment != 0:
            base_margin = inputs.free_cash_flow / inputs.revenue if inputs.revenue > 0 else 0.25
            adjusted_margin = base_margin + scenario.fcf_margin_adjustment
            adjusted_margin = max(0.05, min(0.60, adjusted_margin))  # Cap 5%-60%
            inputs.free_cash_flow = inputs.revenue * adjusted_margin
            print(f"  → FCF margin: {base_margin:.1%} → {adjusted_margin:.1%}")
        
        # 6. Adjust projection years
        inputs.projection_years = scenario.projection_years
        
        # Run DCF with scenario inputs
        result = model.run_dcf(inputs)
        
        upside = (result.intrinsic_value_per_share / inputs.current_price - 1)
        recommendation = self._get_recommendation(upside)
        
        print(f"\n  📊 Scenario Result:")
        print(f"     Intrinsic Value: ${result.intrinsic_value_per_share:.2f}")
        print(f"     Current Price: ${inputs.current_price:.2f}")
        print(f"     Upside/(Downside): {upside:+.1%}")
        print(f"     Recommendation: {recommendation}")
        
        return inputs, result
    
    def calculate_market_implied(self) -> Dict[str, Any]:
        """
        Calculate what assumptions the market is implying at current price.
        
        Reverse-engineers:
        - Implied growth rates
        - Implied terminal growth
        - Implied FCF margins
        """
        print(f"\n{'='*70}")
        print(f"🎯 Market-Implied Assumptions for {self.ticker}")
        print(f"{'='*70}")
        
        if self.base_inputs is None or self.base_result is None:
            raise ValueError("Must run base case first")
        
        current_price = self.base_inputs.current_price
        model = DCFModel()
        
        # Iteratively find implied assumptions
        print(f"\n🔍 Reverse-engineering market expectations...")
        print(f"   Current Price: ${current_price:.2f}")
        
        # Try different growth scenarios to match current price
        best_fit = None
        min_error = float('inf')
        
        # Search space
        growth_multipliers = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
        terminal_rates = [0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07]
        margin_adjustments = [-0.05, -0.03, -0.01, 0.0, 0.02, 0.04, 0.06, 0.08, 0.10]
        
        from copy import deepcopy
        
        for gm in growth_multipliers:
            for tg in terminal_rates:
                for ma in margin_adjustments:
                    test_inputs = deepcopy(self.base_inputs)
                    
                    # Adjust growth
                    test_inputs.revenue_growth_rates = [
                        max(-0.10, min(0.80, g * gm)) 
                        for g in self.base_inputs.revenue_growth_rates
                    ]
                    
                    # Adjust terminal growth
                    test_inputs.terminal_growth_rate = tg
                    
                    # Adjust margin
                    base_margin = self.base_inputs.free_cash_flow / self.base_inputs.revenue if self.base_inputs.revenue > 0 else 0.25
                    adjusted_margin = base_margin + ma
                    adjusted_margin = max(0.05, min(0.60, adjusted_margin))
                    test_inputs.free_cash_flow = self.base_inputs.revenue * adjusted_margin
                    
                    # Run valuation
                    test_result = model.run_dcf(test_inputs)
                    
                    # Check error
                    error = abs(test_result.intrinsic_value_per_share - current_price)
                    
                    if error < min_error:
                        min_error = error
                        best_fit = {
                            'growth_multiplier': gm,
                            'terminal_growth': tg,
                            'margin_adjustment': ma,
                            'implied_value': test_result.intrinsic_value_per_share,
                            'adjusted_growth': test_inputs.revenue_growth_rates,
                            'adjusted_margin': adjusted_margin
                        }
        
        if best_fit:
            print(f"\n✅ Market-Implied Assumptions Found:")
            print(f"   To justify ${current_price:.2f}, market expects:")
            print(f"   • Revenue Growth: {[f'{g:.1%}' for g in best_fit['adjusted_growth']]}")
            print(f"     (Multiplier: {best_fit['growth_multiplier']:.1f}x analyst estimates)")
            print(f"   • Terminal Growth: {best_fit['terminal_growth']:.1%}")
            print(f"   • FCF Margin: {best_fit['adjusted_margin']:.1%} ({best_fit['margin_adjustment']:+.1%} adjustment)")
            print(f"   • Implied Value: ${best_fit['implied_value']:.2f} (vs. actual ${current_price:.2f})")
            print(f"   • Error: ${min_error:.2f} ({min_error/current_price:.1%})")
            
            # Reality check
            avg_implied_growth = sum(best_fit['adjusted_growth']) / len(best_fit['adjusted_growth'])
            print(f"\n🤔 Reality Check:")
            if avg_implied_growth > 0.30:
                print(f"   ⚠️  Market expects {avg_implied_growth:.1%} average growth - HISTORICALLY UNPRECEDENTED")
                print(f"      For context: AAPL's peak growth was ~35%, MSFT's was ~30%")
            elif avg_implied_growth > 0.20:
                print(f"   ⚠️  Market expects {avg_implied_growth:.1%} average growth - VERY OPTIMISTIC")
                print(f"      Requires sustained competitive advantage")
            elif avg_implied_growth > 0.12:
                print(f"   ✓ Market expects {avg_implied_growth:.1%} growth - AMBITIOUS BUT PLAUSIBLE")
            else:
                print(f"   ✓ Market expects {avg_implied_growth:.1%} growth - REASONABLE")
            
            if best_fit['terminal_growth'] > 0.04:
                print(f"   ⚠️  Terminal growth of {best_fit['terminal_growth']:.1%} assumes permanent outperformance")
                print(f"      Historical GDP growth: ~2.5%")
            
            return best_fit
        
        return None
    
    def run_sensitivity_matrix(self) -> Dict[str, Any]:
        """Generate WACC vs. Terminal Growth sensitivity matrix"""
        print(f"\n{'='*70}")
        print(f"📊 Sensitivity Analysis: WACC vs. Terminal Growth")
        print(f"{'='*70}")
        
        if self.base_inputs is None:
            raise ValueError("Must run base case first")
        
        model = DCFModel()
        from copy import deepcopy
        
        # Define ranges
        wacc_range = [0.12, 0.15, 0.18, 0.21, 0.24, 0.27, 0.30]
        terminal_range = [0.01, 0.02, 0.025, 0.03, 0.035, 0.04, 0.05]
        
        matrix = {}
        
        print(f"\n{'Terminal Growth':<18}", end="")
        for wacc in wacc_range:
            print(f"{wacc:.0%} WACC".ljust(12), end="")
        print()
        print("-" * (18 + 12 * len(wacc_range)))
        
        for tg in terminal_range:
            print(f"{tg:.1%}".ljust(18), end="")
            row = {}
            for wacc in wacc_range:
                test_inputs = deepcopy(self.base_inputs)
                test_inputs.wacc_override = wacc
                test_inputs.terminal_growth_rate = tg
                
                result = model.run_dcf(test_inputs)
                value = result.intrinsic_value_per_share
                
                row[f"{wacc:.0%}"] = value
                
                # Color coding
                current = self.base_inputs.current_price
                if value > current * 1.2:
                    symbol = "🟢"  # Strong buy
                elif value > current * 1.05:
                    symbol = "🟡"  # Buy
                elif value > current * 0.9:
                    symbol = "⚪"  # Hold
                else:
                    symbol = "🔴"  # Sell
                
                print(f"${value:>6.0f} {symbol}".ljust(12), end="")
            
            matrix[f"{tg:.1%}"] = row
            print()
        
        return matrix
    
    def _get_recommendation(self, upside: float) -> str:
        """Get recommendation based on upside"""
        if upside > 0.20:
            return "🟢 STRONG BUY"
        elif upside > 0.05:
            return "🟡 BUY"
        elif upside > -0.10:
            return "⚪ HOLD"
        elif upside > -0.25:
            return "🔴 SELL"
        else:
            return "🔴 STRONG SELL"
    
    def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all scenarios and return summary"""
        results = {}
        
        # Base case
        _, base_result = self.run_base_case()
        results['base'] = {
            'scenario': self.BASE_CASE,
            'result': base_result,
            'intrinsic_value': base_result.intrinsic_value_per_share
        }
        
        # Bear case
        _, bear_result = self.run_scenario(self.BEAR_CASE)
        results['bear'] = {
            'scenario': self.BEAR_CASE,
            'result': bear_result,
            'intrinsic_value': bear_result.intrinsic_value_per_share
        }
        
        # Bull case
        _, bull_result = self.run_scenario(self.BULL_CASE)
        results['bull'] = {
            'scenario': self.BULL_CASE,
            'result': bull_result,
            'intrinsic_value': bull_result.intrinsic_value_per_share
        }
        
        # Market-implied
        implied = self.calculate_market_implied()
        results['market_implied'] = implied
        
        # Sensitivity matrix
        sensitivity = self.run_sensitivity_matrix()
        results['sensitivity'] = sensitivity
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 SCENARIO ANALYSIS SUMMARY: {self.ticker}")
        print(f"{'='*70}")
        print(f"Current Price: ${self.base_inputs.current_price:.2f}")
        print(f"")
        print(f"{'Scenario':<25} {'Intrinsic Value':>18} {'Upside/Downside':>18} {'Recommendation':>20}")
        print(f"{'-'*70}")
        
        current = self.base_inputs.current_price
        
        for key in ['bear', 'base', 'bull']:
            r = results[key]
            iv = r['intrinsic_value']
            upside = (iv / current - 1)
            rec = self._get_recommendation(upside)
            print(f"{r['scenario'].name:<25} ${iv:>16.2f} {upside:>+17.1%} {rec:>20}")
        
        print(f"{'-'*70}")
        print(f"Valuation Range: ${results['bear']['intrinsic_value']:.2f} - ${results['bull']['intrinsic_value']:.2f}")
        print(f"Base Case: ${results['base']['intrinsic_value']:.2f}")
        
        return results


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Katsu DCF Scenario Analysis')
    parser.add_argument('--ticker', '-t', required=True, help='Stock ticker')
    parser.add_argument('--scenario', '-s', choices=['bear', 'base', 'bull', 'market-implied', 'all'], 
                       default='all', help='Specific scenario to run')
    
    args = parser.parse_args()
    
    analyzer = ScenarioAnalyzer(args.ticker)
    
    if args.scenario == 'all':
        analyzer.run_all_scenarios()
    elif args.scenario == 'base':
        analyzer.run_base_case()
    elif args.scenario == 'bear':
        analyzer.run_base_case()
        analyzer.run_scenario(ScenarioAnalyzer.BEAR_CASE)
    elif args.scenario == 'bull':
        analyzer.run_base_case()
        analyzer.run_scenario(ScenarioAnalyzer.BULL_CASE)
    elif args.scenario == 'market-implied':
        analyzer.run_base_case()
        analyzer.calculate_market_implied()


if __name__ == "__main__":
    main()
