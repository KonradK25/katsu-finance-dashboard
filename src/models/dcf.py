"""
DCF (Discounted Cash Flow) Calculation Engine for Katsu DCF

Implements professional DCF valuation methodology:
- Free Cash Flow projections
- WACC calculation (CAPM)
- Terminal Value (Perpetuity Growth Method)
- Intrinsic Value per Share
- Sensitivity Analysis

Author: Katsu DCF Engine
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from datetime import datetime


@dataclass
class DCFInputs:
    """Input parameters for DCF calculation"""
    
    # Company Data
    ticker: str
    current_price: float
    shares_outstanding: float
    
    # Financial Data (in millions)
    revenue: float
    operating_income: float
    net_income: float
    free_cash_flow: float
    operating_cash_flow: float
    capex: float
    total_debt: float
    cash_and_equivalents: float
    
    # Market Data
    beta: float
    risk_free_rate: float = 0.045  # 10Y Treasury ~4.5%
    market_risk_premium: float = 0.065  # Historical average ~6.5%
    
    # Assumptions (can be overridden)
    projection_years: int = 5
    revenue_growth_rates: List[float] = field(default_factory=lambda: [0.08, 0.07, 0.06, 0.05, 0.05])
    terminal_growth_rate: float = 0.025  # Long-term GDP growth ~2.5%
    
    # Optional overrides
    wacc_override: Optional[float] = None
    tax_rate_override: Optional[float] = None


@dataclass
class DCFResult:
    """Results from DCF valuation"""
    
    # Basic Info
    ticker: str
    valuation_date: str
    current_price: float
    
    # Key Outputs
    intrinsic_value_per_share: float
    upside_downside: float  # % difference from current price
    recommendation: str  # "BUY", "HOLD", "SELL"
    
    # WACC Components
    wacc: float
    cost_of_equity: float
    cost_of_debt: float
    tax_rate: float
    equity_weight: float
    debt_weight: float
    
    # Projections
    projection_years: int
    fcf_projections: List[float]  # Year-by-year FCF
    pv_fcf_projections: List[float]  # Present value of each year's FCF
    terminal_value: float
    pv_terminal_value: float
    
    # Valuation Summary
    enterprise_value: float
    equity_value: float
    implied_share_price: float
    
    # Sensitivity Analysis
    sensitivity_table: List[List[float]]  # WACC vs Growth matrix
    wacc_range: List[float]
    growth_range: List[float]
    
    # Assumptions Used
    assumptions: Dict[str, Any]
    
    # Metrics
    npv: float  # Net Present Value
    margin_of_safety: float  # % buffer


class DCFModel:
    """
    Professional DCF Valuation Model
    
    Methodology:
    1. Project Free Cash Flows (5-10 years)
    2. Calculate WACC using CAPM
    3. Discount FCFs to present value
    4. Calculate Terminal Value (Perpetuity Growth)
    5. Sum PV of FCFs + PV of Terminal Value
    6. Derive Equity Value and Intrinsic Share Price
    """
    
    # Default assumptions
    DEFAULT_RISK_FREE_RATE = 0.045  # 10Y Treasury
    DEFAULT_MARKET_RISK_PREMIUM = 0.065
    DEFAULT_TERMINAL_GROWTH = 0.025
    DEFAULT_TAX_RATE = 0.21  # US Corporate tax rate
    
    def __init__(self):
        """Initialize DCF Model"""
        pass
    
    def calculate_wacc(self, inputs: DCFInputs) -> Tuple[float, float, float, float, float]:
        """
        Calculate Weighted Average Cost of Capital (WACC)
        
        WACC = (E/V × Re) + (D/V × Rd × (1-T))
        
        Where:
        - E = Market value of equity
        - D = Market value of debt
        - V = E + D (Total value)
        - Re = Cost of equity (CAPM)
        - Rd = Cost of debt
        - T = Tax rate
        
        Returns:
            Tuple of (WACC, Cost of Equity, Cost of Debt, Tax Rate, Equity Weight)
        """
        # Use override if provided
        if inputs.wacc_override:
            return (
                inputs.wacc_override,
                inputs.wacc_override,  # Simplified
                0.0,  # Not calculated
                inputs.tax_rate_override or self.DEFAULT_TAX_RATE,
                1.0  # 100% equity
            )
        
        # Calculate Cost of Equity using CAPM
        # Re = Rf + β × (Rm - Rf)
        cost_of_equity = inputs.risk_free_rate + inputs.beta * inputs.market_risk_premium
        
        # Estimate Cost of Debt (simplified: use risk-free rate + spread based on beta)
        # Higher beta = riskier company = higher cost of debt
        credit_spread = 0.02 + (inputs.beta - 1.0) * 0.01  # Base 2% + adjustment
        cost_of_debt = inputs.risk_free_rate + max(0, credit_spread)
        
        # Tax rate
        tax_rate = inputs.tax_rate_override or self.DEFAULT_TAX_RATE
        
        # Calculate weights (using market values)
        market_cap = inputs.current_price * inputs.shares_outstanding
        enterprise_value = market_cap + inputs.total_debt - inputs.cash_and_equivalents
        
        if enterprise_value <= 0:
            # Edge case: company has more cash than value
            equity_weight = 1.0
            debt_weight = 0.0
        else:
            equity_weight = market_cap / enterprise_value
            debt_weight = (inputs.total_debt - inputs.cash_and_equivalents) / enterprise_value
            debt_weight = max(0, debt_weight)  # Can't be negative
        
        # Calculate WACC
        wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
        
        return wacc, cost_of_equity, cost_of_debt, tax_rate, equity_weight
    
    def project_free_cash_flows(self, inputs: DCFInputs) -> List[float]:
        """
        Project Free Cash Flows for projection period
        
        Methodology:
        1. Grow revenue by assumed rates
        2. Apply operating margin to get operating income
        3. Tax-adjust to get NOPAT
        4. Add back D&A (estimated)
        5. Subtract CapEx and change in working capital
        
        Simplified approach: Grow FCF directly by revenue growth rates
        """
        fcf_projections = []
        current_fcf = inputs.free_cash_flow
        
        for i in range(inputs.projection_years):
            growth_rate = inputs.revenue_growth_rates[i] if i < len(inputs.revenue_growth_rates) else inputs.revenue_growth_rates[-1]
            
            # Grow FCF (simplified: assumes FCF grows with revenue)
            projected_fcf = current_fcf * (1 + growth_rate)
            fcf_projections.append(projected_fcf)
            current_fcf = projected_fcf
        
        return fcf_projections
    
    def calculate_terminal_value(self, inputs: DCFInputs, final_fcf: float, wacc: float) -> float:
        """
        Calculate Terminal Value using Perpetuity Growth Method
        
        TV = FCF_n × (1 + g) / (WACC - g)
        
        Where:
        - FCF_n = Final year projected FCF
        - g = Terminal growth rate
        - WACC = Weighted Average Cost of Capital
        
        Constraints:
        - g must be < WACC (otherwise formula breaks)
        - g typically 2-3% (long-term GDP growth)
        """
        # Ensure growth rate is less than WACC
        terminal_growth = min(inputs.terminal_growth_rate, wacc - 0.01)
        
        # Perpetuity Growth Formula
        terminal_value = final_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
        
        return terminal_value
    
    def discount_cash_flows(self, cash_flows: List[float], wacc: float) -> List[float]:
        """
        Discount future cash flows to present value
        
        PV = CF_t / (1 + WACC)^t
        """
        pv_flows = []
        for t, cf in enumerate(cash_flows, start=1):
            pv = cf / ((1 + wacc) ** t)
            pv_flows.append(pv)
        return pv_flows
    
    def build_sensitivity_table(self, inputs: DCFInputs, base_wacc: float, 
                                 base_fcf_projections: List[float]) -> Tuple[List[List[float]], List[float], List[float]]:
        """
        Build sensitivity analysis table (WACC vs Terminal Growth)
        
        Returns:
            Tuple of (table, wacc_range, growth_range)
        """
        wacc_range = [base_wacc - 0.02, base_wacc - 0.01, base_wacc, 
                      base_wacc + 0.01, base_wacc + 0.02]
        growth_range = [0.015, 0.02, 0.025, 0.03, 0.035]
        
        table = []
        final_fcf = base_fcf_projections[-1]
        
        for wacc in wacc_range:
            row = []
            for growth in growth_range:
                # Calculate terminal value
                if wacc > growth:
                    tv = final_fcf * (1 + growth) / (wacc - growth)
                    pv_tv = tv / ((1 + wacc) ** inputs.projection_years)
                    pv_fcf = sum(self.discount_cash_flows(base_fcf_projections, wacc))
                    
                    # Calculate implied share price
                    enterprise_value = pv_fcf + pv_tv
                    equity_value = enterprise_value - inputs.total_debt + inputs.cash_and_equivalents
                    share_price = equity_value / inputs.shares_outstanding
                    row.append(share_price)
                else:
                    row.append(None)  # Invalid: growth >= WACC
            table.append(row)
        
        return table, wacc_range, growth_range
    
    def generate_recommendation(self, intrinsic_value: float, current_price: float) -> Tuple[str, float]:
        """
        Generate investment recommendation based on margin of safety
        
        Returns:
            Tuple of (recommendation, upside/downside %)
        """
        upside = (intrinsic_value - current_price) / current_price
        
        if upside > 0.20:  # >20% upside
            recommendation = "BUY"
        elif upside > 0.05:  # >5% upside
            recommendation = "HOLD"
        elif upside > -0.10:  # Within -10%
            recommendation = "HOLD"
        else:
            recommendation = "SELL"
        
        return recommendation, upside
    
    def run_dcf(self, inputs: DCFInputs) -> DCFResult:
        """
        Run complete DCF valuation
        
        Args:
            inputs: DCFInputs with all financial data and assumptions
            
        Returns:
            DCFResult with valuation outputs
        """
        print(f"\n🧮 Running DCF Valuation for {inputs.ticker}...")
        
        # Step 1: Calculate WACC
        print("  → Calculating WACC...")
        wacc, cost_of_equity, cost_of_debt, tax_rate, equity_weight = self.calculate_wacc(inputs)
        debt_weight = 1.0 - equity_weight
        
        print(f"    WACC: {wacc:.2%}")
        print(f"    Cost of Equity: {cost_of_equity:.2%}")
        print(f"    Cost of Debt: {cost_of_debt:.2%} (after-tax: {cost_of_debt * (1-tax_rate):.2%})")
        
        # Step 2: Project Free Cash Flows
        print(f"  → Projecting FCF for {inputs.projection_years} years...")
        fcf_projections = self.project_free_cash_flows(inputs)
        
        for i, fcf in enumerate(fcf_projections, start=1):
            print(f"    Year {i}: ${fcf/1e9:.2f}B")
        
        # Step 3: Discount FCFs to Present Value
        print("  → Discounting cash flows...")
        pv_fcf_projections = self.discount_cash_flows(fcf_projections, wacc)
        total_pv_fcf = sum(pv_fcf_projections)
        
        # Step 4: Calculate Terminal Value
        print("  → Calculating Terminal Value...")
        terminal_value = self.calculate_terminal_value(inputs, fcf_projections[-1], wacc)
        pv_terminal_value = self.discount_cash_flows([terminal_value], wacc)[0]
        
        print(f"    Terminal Value: ${terminal_value/1e9:.2f}B")
        print(f"    PV of Terminal Value: ${pv_terminal_value/1e9:.2f}B")
        
        # Step 5: Calculate Enterprise Value and Equity Value
        enterprise_value = total_pv_fcf + pv_terminal_value
        equity_value = enterprise_value - inputs.total_debt + inputs.cash_and_equivalents
        
        # Step 6: Calculate Intrinsic Share Price
        intrinsic_value_per_share = equity_value / inputs.shares_outstanding
        
        # Step 7: Generate Recommendation
        recommendation, upside = self.generate_recommendation(intrinsic_value_per_share, inputs.current_price)
        
        # Step 8: Build Sensitivity Table
        print("  → Building sensitivity analysis...")
        sensitivity_table, wacc_range, growth_range = self.build_sensitivity_table(
            inputs, wacc, fcf_projections
        )
        
        # Compile results
        result = DCFResult(
            ticker=inputs.ticker,
            valuation_date=datetime.now().strftime("%Y-%m-%d"),
            current_price=inputs.current_price,
            intrinsic_value_per_share=intrinsic_value_per_share,
            upside_downside=upside,
            recommendation=recommendation,
            wacc=wacc,
            cost_of_equity=cost_of_equity,
            cost_of_debt=cost_of_debt,
            tax_rate=tax_rate,
            equity_weight=equity_weight,
            debt_weight=debt_weight,
            projection_years=inputs.projection_years,
            fcf_projections=fcf_projections,
            pv_fcf_projections=pv_fcf_projections,
            terminal_value=terminal_value,
            pv_terminal_value=pv_terminal_value,
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            implied_share_price=intrinsic_value_per_share,
            sensitivity_table=sensitivity_table,
            wacc_range=wacc_range,
            growth_range=growth_range,
            assumptions={
                'risk_free_rate': inputs.risk_free_rate,
                'market_risk_premium': inputs.market_risk_premium,
                'terminal_growth_rate': inputs.terminal_growth_rate,
                'revenue_growth_rates': inputs.revenue_growth_rates,
            },
            npv=equity_value - (inputs.current_price * inputs.shares_outstanding),
            margin_of_safety=upside
        )
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"DCF Valuation Summary: {inputs.ticker}")
        print(f"{'='*60}")
        print(f"Current Share Price: ${inputs.current_price:.2f}")
        print(f"Intrinsic Value: ${intrinsic_value_per_share:.2f}")
        print(f"Upside/(Downside): {upside:+.1%}")
        print(f"Recommendation: {recommendation}")
        print(f"{'='*60}")
        
        return result

