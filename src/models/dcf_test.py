#!/usr/bin/env python3
"""
Test script for DCF Model
"""

import sys
import os

# Add parent directory to path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, src_dir)

from models.dcf import DCFModel, DCFInputs

# Create sample inputs (Apple Inc.)
inputs = DCFInputs(
    ticker="AAPL",
    current_price=258.83,
    shares_outstanding=14.68e9,
    revenue=391035e6,
    operating_income=125670e6,
    net_income=100913e6,
    free_cash_flow=107295e6,
    operating_cash_flow=118254e6,
    capex=10959e6,
    total_debt=106628e6,
    cash_and_equivalents=29943e6,
    beta=1.11,
    projection_years=5,
    revenue_growth_rates=[0.08, 0.07, 0.06, 0.05, 0.05],
    terminal_growth_rate=0.025
)

# Run DCF
model = DCFModel()
result = model.run_dcf(inputs)

# Show sensitivity table
print("\n📊 Sensitivity Analysis (Share Price by WACC vs Terminal Growth)")
header = "Growth \\ WACC"
print("{:<15}".format(header), end="")
for wacc in result.wacc_range:
    print("{:<12}".format("{:.1%}".format(wacc)), end="")
print()

for i, growth in enumerate(result.growth_range):
    print("{:<15}".format("{:.1%}".format(growth)), end="")
    for j, wacc in enumerate(result.wacc_range):
        price = result.sensitivity_table[i][j]
        if price:
            print("{:<12}".format("${:.2f}".format(price)), end="")
        else:
            print("N/A         ", end="")
    print()
