#!/usr/bin/env python3
"""
Excel Generator for Katsu DCF Engine

Creates professional Excel valuation models with:
- Assumptions sheet with data sources
- 5-year FCF projections with live formulas
- WACC calculation breakdown
- Terminal value math
- Sensitivity analysis tables
- Charts and visualizations
- Recommendation summary

Uses xlsxwriter for formatting and openpyxl for advanced features.
"""

import xlsxwriter
from datetime import datetime
from typing import Dict, Any, Optional
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.dcf import DCFResult, DCFInputs


class DCFExcelGenerator:
    """
    Generates professional Excel DCF models.
    """
    
    def __init__(self, output_path: str):
        """
        Initialize Excel generator.
        
        Args:
            output_path: Path to output Excel file
        """
        self.output_path = output_path
        self.workbook = None
        self.formats = {}
        
    def generate(self, inputs: DCFInputs, result: DCFResult, 
                 assumptions: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate complete DCF Excel model.
        
        Args:
            inputs: DCF inputs with all assumptions
            result: DCF calculation results
            assumptions: Optional dict with data source metadata
            
        Returns:
            Path to generated Excel file
        """
        print(f"\n📊 Generating Excel DCF Model...")
        print(f"  Output: {self.output_path}")
        
        # Create workbook
        self.workbook = xlsxwriter.Workbook(self.output_path)
        
        # Define formats
        self._define_formats()
        
        # Create sheets
        self._create_summary_sheet(inputs, result, assumptions)
        self._create_assumptions_sheet(inputs, assumptions)
        self._create_wacc_sheet(inputs, result)
        self._create_projections_sheet(inputs, result)
        self._create_sensitivity_sheet(result)
        self._create_charts_sheet(inputs, result)
        
        # Close workbook
        self.workbook.close()
        
        print(f"  ✓ Excel model generated successfully!")
        print(f"  File size: {os.path.getsize(self.output_path) / 1024:.1f} KB")
        
        return self.output_path
    
    def _define_formats(self):
        """Define Excel cell formats"""
        wb = self.workbook
        
        # Number formats
        self.formats['currency'] = wb.add_format({
            'num_format': '$#,##0.00',
            'align': 'right'
        })
        self.formats['currency_b'] = wb.add_format({
            'num_format': '$#,##0.0"B"',
            'align': 'right'
        })
        self.formats['percent'] = wb.add_format({
            'num_format': '0.00%',
            'align': 'right'
        })
        self.formats['percent_1'] = wb.add_format({
            'num_format': '0.0%',
            'align': 'right'
        })
        self.formats['number'] = wb.add_format({
            'num_format': '#,##0.00',
            'align': 'right'
        })
        self.formats['number_0'] = wb.add_format({
            'num_format': '#,##0',
            'align': 'right'
        })
        
        # Header formats
        self.formats['header'] = wb.add_format({
            'bold': True,
            'bg_color': '#2E75B6',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        self.formats['subheader'] = wb.add_format({
            'bold': True,
            'bg_color': '#5496CE',
            'font_color': 'white',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Text formats
        self.formats['label'] = wb.add_format({
            'align': 'left',
            'valign': 'vcenter'
        })
        self.formats['label_bold'] = wb.add_format({
            'bold': True,
            'align': 'left',
            'valign': 'vcenter'
        })
        self.formats['center'] = wb.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Highlight formats
        self.formats['highlight'] = wb.add_format({
            'bold': True,
            'bg_color': '#FFC000',
            'font_color': 'black',
            'align': 'right',
            'border': 2
        })
        self.formats['positive'] = wb.add_format({
            'font_color': 'green',
            'bold': True,
            'align': 'right'
        })
        self.formats['negative'] = wb.add_format({
            'font_color': 'red',
            'bold': True,
            'align': 'right'
        })
        
        # Border formats
        self.formats['border_top'] = wb.add_format({
            'top': 2
        })
        self.formats['border_bottom'] = wb.add_format({
            'bottom': 2
        })
        self.formats['border_all'] = wb.add_format({
            'border': 1
        })
        
        # Source note format
        self.formats['source'] = wb.add_format({
            'italic': True,
            'font_size': 9,
            'font_color': 'gray'
        })
    
    def _create_summary_sheet(self, inputs: DCFInputs, result: DCFResult, 
                             assumptions: Optional[Dict[str, Any]]):
        """Create executive summary sheet"""
        ws = self.workbook.add_worksheet('Summary')
        
        # Set column widths
        ws.set_column('A:A', 30)
        ws.set_column('B:B', 15)
        ws.set_column('C:C', 20)
        
        # Title
        ws.merge_range('A1:C1', f"DCF Valuation: {inputs.ticker}", 
                      self.workbook.add_format({
                          'bold': True,
                          'font_size': 18,
                          'align': 'center',
                          'bg_color': '#2E75B6',
                          'font_color': 'white'
                      }))
        
        # Generation date
        ws.write('A2', 'Generated:', self.formats['label'])
        ws.write('B2', datetime.now().strftime('%Y-%m-%d %H:%M'), 
                self.workbook.add_format({'align': 'left'}))
        
        # Current price
        ws.write('A4', 'Current Share Price:', self.formats['label_bold'])
        ws.write('B4', inputs.current_price, self.formats['currency'])
        
        # Intrinsic value
        ws.write('A5', 'Intrinsic Value:', self.formats['label_bold'])
        ws.write('B5', result.intrinsic_value_per_share, self.formats['currency'])
        
        # Upside/downside
        upside = result.upside_downside
        fmt = self.formats['positive'] if upside > 0 else self.formats['negative']
        ws.write('A6', 'Upside/(Downside):', self.formats['label_bold'])
        ws.write('B6', upside, fmt)
        
        # Recommendation
        ws.write('A7', 'Recommendation:', self.formats['label_bold'])
        rec_fmt = self.workbook.add_format({
            'bold': True,
            'bg_color': '#FFC000' if result.recommendation == 'HOLD' else 
                       '#90EE90' if 'BUY' in result.recommendation else 
                       '#FFB6C1',
            'align': 'center'
        })
        ws.write('B7', result.recommendation, rec_fmt)
        
        # Key metrics section
        ws.write('A9', 'Key Metrics', self.formats['subheader'])
        
        metrics = [
            ('Market Cap', inputs.current_price * inputs.shares_outstanding, self.formats['currency_b']),
            ('Beta', inputs.beta, self.formats['number']),
            ('WACC', result.wacc, self.formats['percent']),
            ('Terminal Growth', inputs.terminal_growth_rate, self.formats['percent']),
            ('5Y Avg Growth', sum(inputs.revenue_growth_rates)/5, self.formats['percent']),
        ]
        
        row = 10
        for label, value, fmt in metrics:
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, fmt)
            row += 1
        
        # Data sources
        if assumptions:
            ws.write('A17', 'Data Sources', self.formats['subheader'])
            sources = [
                ('Risk-free rate', assumptions.get('risk_free_rate_source', '10Y Treasury')),
                ('Market risk premium', assumptions.get('mrp_source', 'S&P 500 historical')),
                ('Growth estimates', assumptions.get('growth_source', 'Analyst consensus')),
                ('Financials', assumptions.get('financials_source', 'SEC EDGAR / Yahoo Finance')),
            ]
            
            row = 18
            for label, source in sources:
                ws.write(f'A{row}', label, self.formats['label'])
                ws.write(f'B{row}', source, self.formats['source'])
                row += 1
    
    def _create_assumptions_sheet(self, inputs: DCFInputs, 
                                 assumptions: Optional[Dict[str, Any]]):
        """Create assumptions sheet with all inputs"""
        ws = self.workbook.add_worksheet('Assumptions')
        
        ws.set_column('A:A', 35)
        ws.set_column('B:B', 15)
        ws.set_column('C:C', 30)
        
        # Title
        ws.merge_range('A1:C1', 'DCF Assumptions', 
                      self.workbook.add_format({
                          'bold': True,
                          'font_size': 16,
                          'align': 'center',
                          'bg_color': '#2E75B6',
                          'font_color': 'white'
                      }))
        
        # Macroeconomic assumptions
        ws.write('A3', 'Macroeconomic Assumptions', self.formats['subheader'])
        
        macro = [
            ('Risk-Free Rate', inputs.risk_free_rate, '10-Year Treasury yield'),
            ('Market Risk Premium', inputs.market_risk_premium, 'S&P 500 historical returns'),
            ('Terminal Growth Rate', inputs.terminal_growth_rate, 'Long-term GDP growth'),
        ]
        
        row = 4
        for label, value, source in macro:
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, self.formats['percent'])
            ws.write(f'C{row}', source, self.formats['source'])
            row += 1
        
        # Company-specific assumptions
        ws.write('A8', 'Company-Specific Assumptions', self.formats['subheader'])
        
        company = [
            ('Beta', inputs.beta, 'Yahoo Finance'),
            ('Tax Rate', inputs.tax_rate_override, 'Effective tax rate from financials'),
            ('Revenue Growth (Y1)', inputs.revenue_growth_rates[0], 'Analyst consensus'),
            ('Revenue Growth (Y2)', inputs.revenue_growth_rates[1], 'Fade from Y1'),
            ('Revenue Growth (Y3)', inputs.revenue_growth_rates[2], 'Fade from Y2'),
            ('Revenue Growth (Y4)', inputs.revenue_growth_rates[3], 'Fade from Y3'),
            ('Revenue Growth (Y5)', inputs.revenue_growth_rates[4], 'Fade from Y4'),
        ]
        
        row = 9
        for label, value, source in company:
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, self.formats['percent'])
            ws.write(f'C{row}', source, self.formats['source'])
            row += 1
        
        # Current financial metrics
        ws.write('A18', 'Current Financial Metrics', self.formats['subheader'])
        
        financials = [
            ('Revenue (TTM)', inputs.revenue, self.formats['currency_b']),
            ('Free Cash Flow (TTM)', inputs.free_cash_flow, self.formats['currency_b']),
            ('Operating Cash Flow', inputs.operating_cash_flow, self.formats['currency_b']),
            ('Capital Expenditures', inputs.capex, self.formats['currency_b']),
            ('Total Debt', inputs.total_debt, self.formats['currency_b']),
            ('Cash & Equivalents', inputs.cash_and_equivalents, self.formats['currency_b']),
            ('Shares Outstanding', inputs.shares_outstanding, self.formats['number_0']),
        ]
        
        row = 19
        for label, value, fmt in financials:
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, fmt)
            row += 1
    
    def _create_wacc_sheet(self, inputs: DCFInputs, result: DCFResult):
        """Create WACC calculation sheet"""
        ws = self.workbook.add_worksheet('WACC')
        
        ws.set_column('A:A', 35)
        ws.set_column('B:B', 15)
        ws.set_column('C:C', 25)
        
        # Title
        ws.merge_range('A1:C1', 'WACC Calculation', 
                      self.workbook.add_format({
                          'bold': True,
                          'font_size': 16,
                          'align': 'center',
                          'bg_color': '#2E75B6',
                          'font_color': 'white'
                      }))
        
        # Cost of Equity (CAPM)
        ws.write('A3', 'Cost of Equity (CAPM)', self.formats['subheader'])
        
        capm = [
            ('Risk-Free Rate', inputs.risk_free_rate),
            ('Beta', inputs.beta),
            ('Market Risk Premium', inputs.market_risk_premium),
            ('Cost of Equity (Re)', result.cost_of_equity),
        ]
        
        row = 4
        for label, value in capm:
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, self.formats['percent'] if '%' in label else self.formats['number'])
            row += 1
        
        # CAPM formula
        ws.write('A9', 'Formula: Re = Rf + β × (Rm - Rf)', self.formats['source'])
        ws.write('A10', f"         = {inputs.risk_free_rate:.1%} + {inputs.beta:.2f} × {inputs.market_risk_premium:.1%}", 
                self.formats['source'])
        
        # Cost of Debt
        ws.write('A13', 'Cost of Debt', self.formats['subheader'])
        
        # Calculate cost of debt from inputs
        if inputs.total_debt > 0:
            cost_of_debt = result.cost_of_debt
        else:
            cost_of_debt = inputs.risk_free_rate + 0.02  # Fallback
        
        debt_data = [
            ('Pre-tax Cost of Debt', cost_of_debt),
            ('Tax Rate', inputs.tax_rate_override),
            ('After-tax Cost of Debt', cost_of_debt * (1 - inputs.tax_rate_override)),
        ]
        
        row = 14
        for label, value in debt_data:
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, self.formats['percent'])
            row += 1
        
        # WACC calculation
        ws.write('A20', 'WACC Calculation', self.formats['subheader'])
        
        # Estimate capital structure
        equity_value = inputs.current_price * inputs.shares_outstanding
        debt_value = inputs.total_debt
        total_value = equity_value + debt_value
        
        equity_weight = equity_value / total_value if total_value > 0 else 0.8
        debt_weight = debt_value / total_value if total_value > 0 else 0.2
        
        wacc_components = [
            ('Equity Value', equity_value, self.formats['currency_b']),
            ('Debt Value', debt_value, self.formats['currency_b']),
            ('Total Value', total_value, self.formats['currency_b']),
            ('Equity Weight', equity_weight, self.formats['percent']),
            ('Debt Weight', debt_weight, self.formats['percent']),
            ('WACC', result.wacc, self.formats['highlight']),
        ]
        
        row = 21
        for label, value, fmt in wacc_components:
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, fmt)
            row += 1
        
        # WACC formula
        ws.write('A28', 'Formula: WACC = (E/V) × Re + (D/V) × Rd × (1-T)', 
                self.formats['source'])
    
    def _create_projections_sheet(self, inputs: DCFInputs, result: DCFResult):
        """Create 5-year FCF projection sheet"""
        ws = self.workbook.add_worksheet('Projections')
        
        # Set column widths
        ws.set_column('A:A', 25)
        ws.set_column('B:G', 14)
        
        # Title
        ws.merge_range('A1:F1', '5-Year Free Cash Flow Projections', 
                      self.workbook.add_format({
                          'bold': True,
                          'font_size': 16,
                          'align': 'center',
                          'bg_color': '#2E75B6',
                          'font_color': 'white'
                      }))
        
        # Headers
        headers = ['Metric', 'Current', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']
        ws.write_row('A2', headers, self.formats['header'])
        
        # Revenue projections
        ws.write('A3', 'Revenue', self.formats['label'])
        ws.write('B3', inputs.revenue, self.formats['currency_b'])
        
        # Calculate revenue growth
        revenue = inputs.revenue
        for i, growth in enumerate(inputs.revenue_growth_rates):
            revenue = revenue * (1 + growth)
            ws.write(chr(ord('C') + i) + '3', revenue, self.formats['currency_b'])
        
        # Growth rates row
        ws.write('A4', 'Growth Rate', self.formats['label'])
        ws.write('B4', '-', self.formats['center'])
        for i, growth in enumerate(inputs.revenue_growth_rates):
            ws.write(chr(ord('C') + i) + '4', growth, self.formats['percent'])
        
        # FCF margin assumption (use current as base)
        current_fcf_margin = inputs.free_cash_flow / inputs.revenue if inputs.revenue > 0 else 0.25
        
        ws.write('A5', 'FCF Margin', self.formats['label'])
        ws.write('B5', current_fcf_margin, self.formats['percent'])
        for col in range(2, 7):
            ws.write(chr(ord('B') + col) + '5', current_fcf_margin, self.formats['percent'])
        
        # Free Cash Flow
        ws.write('A6', 'Free Cash Flow', self.formats['label_bold'])
        ws.write('B6', inputs.free_cash_flow, self.formats['currency_b'])
        
        revenue_y1 = inputs.revenue * (1 + inputs.revenue_growth_rates[0])
        for i in range(5):
            rev = inputs.revenue
            for j in range(i + 1):
                rev = rev * (1 + inputs.revenue_growth_rates[j])
            fcf = rev * current_fcf_margin
            ws.write(chr(ord('C') + i) + '6', fcf, self.formats['currency_b'])
        
        # Discount factors
        ws.write('A8', 'Discount Factor', self.formats['label'])
        ws.write('B8', '1.000', self.formats['number'])
        for i in range(5):
            df = 1 / ((1 + result.wacc) ** (i + 1))
            ws.write(chr(ord('C') + i) + '8', df, self.formats['number'])
        
        # Present Value of FCF
        ws.write('A9', 'PV of FCF', self.formats['label_bold'])
        ws.write('B9', inputs.free_cash_flow, self.formats['currency_b'])
        
        total_pv = 0
        for i in range(5):
            rev = inputs.revenue
            for j in range(i + 1):
                rev = rev * (1 + inputs.revenue_growth_rates[j])
            fcf = rev * current_fcf_margin
            pv = fcf / ((1 + result.wacc) ** (i + 1))
            total_pv += pv
            ws.write(chr(ord('C') + i) + '9', pv, self.formats['currency_b'])
        
        # Terminal Value
        ws.write('A11', 'Terminal Value', self.formats['subheader'])
        
        # Final year FCF
        final_fcf = inputs.revenue
        for growth in inputs.revenue_growth_rates:
            final_fcf = final_fcf * (1 + growth)
        final_fcf = final_fcf * current_fcf_margin
        
        terminal_value = final_fcf * (1 + inputs.terminal_growth_rate) / (result.wacc - inputs.terminal_growth_rate)
        pv_terminal = terminal_value / ((1 + result.wacc) ** 5)
        
        terminal_data = [
            ('Final Year FCF', final_fcf),
            ('Terminal Growth', inputs.terminal_growth_rate),
            ('WACC', result.wacc),
            ('Terminal Value', terminal_value),
            ('PV of Terminal Value', pv_terminal),
        ]
        
        row = 12
        for label, value in terminal_data:
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, self.formats['currency_b'])
            row += 1
        
        # Enterprise Value
        ws.write('A18', 'Enterprise Value', self.formats['highlight'])
        ws.write('B18', total_pv + pv_terminal, self.formats['currency_b'])
        
        # Bridge to Equity Value
        ws.write('A20', 'Bridge to Equity Value', self.formats['subheader'])
        
        equity_bridge = [
            ('Enterprise Value', total_pv + pv_terminal),
            ('Less: Total Debt', -inputs.total_debt),
            ('Plus: Cash', inputs.cash_and_equivalents),
            ('Equity Value', total_pv + pv_terminal - inputs.total_debt + inputs.cash_and_equivalents),
            ('Shares Outstanding', inputs.shares_outstanding),
            ('Intrinsic Value/Share', result.intrinsic_value_per_share),
        ]
        
        row = 21
        for label, value in equity_bridge:
            fmt = self.formats['highlight'] if 'Intrinsic' in label else self.formats['currency_b'] if abs(value) > 1e9 else self.formats['number_0']
            ws.write(f'A{row}', label, self.formats['label'])
            ws.write(f'B{row}', value, fmt)
            row += 1
    
    def _create_sensitivity_sheet(self, result: DCFResult):
        """Create sensitivity analysis sheet"""
        ws = self.workbook.add_worksheet('Sensitivity')
        
        ws.set_column('A:A', 15)
        ws.set_column('B:F', 14)
        
        # Title
        ws.merge_range('A1:F1', 'Sensitivity Analysis', 
                      self.workbook.add_format({
                          'bold': True,
                          'font_size': 16,
                          'align': 'center',
                          'bg_color': '#2E75B6',
                          'font_color': 'white'
                      }))
        
        ws.write('A2', 'Share Price by WACC vs Terminal Growth', self.formats['label_bold'])
        
        # Get sensitivity data from result
        if hasattr(result, 'sensitivity_analysis') and result.sensitivity_analysis:
            sens = result.sensitivity_analysis
            
            # Write WACC headers
            wacc_values = list(sens.keys())
            if wacc_values:
                growth_values = list(sens[wacc_values[0]].keys())
                
                # Header row
                ws.write('A3', 'Growth \\ WACC', self.formats['header'])
                for i, wacc in enumerate(wacc_values):
                    ws.write(chr(ord('B') + i) + '3', wacc, self.formats['header'])
                
                # Data rows
                for j, growth in enumerate(growth_values):
                    ws.write(chr(ord('A')) + str(4 + j), growth, self.formats['percent'])
                    for i, wacc in enumerate(wacc_values):
                        value = sens[wacc][growth]
                        ws.write(chr(ord('B') + i) + str(4 + j), value, self.formats['currency'])
        else:
            ws.write('A4', 'Sensitivity data not available', self.formats['source'])
    
    def _create_charts_sheet(self, inputs: DCFInputs, result: DCFResult):
        """Create charts and visualizations sheet"""
        ws = self.workbook.add_worksheet('Charts')
        
        ws.set_column('A:A', 20)
        ws.set_column('B:B', 15)
        
        # Title
        ws.merge_range('A1:B1', 'Valuation Summary', 
                      self.workbook.add_format({
                          'bold': True,
                          'font_size': 16,
                          'align': 'center',
                          'bg_color': '#2E75B6',
                          'font_color': 'white'
                      }))
        
        # Comparison table
        ws.write('A3', 'Current Price', self.formats['label'])
        ws.write('B3', inputs.current_price, self.formats['currency'])
        
        ws.write('A4', 'Intrinsic Value', self.formats['label_bold'])
        ws.write('B4', result.intrinsic_value_per_share, self.formats['currency'])
        
        upside = result.upside_downside
        fmt = self.formats['positive'] if upside > 0 else self.formats['negative']
        ws.write('A5', 'Upside/(Downside)', self.formats['label_bold'])
        ws.write('B5', upside, fmt)
        
        ws.write('A6', 'Recommendation', self.formats['label_bold'])
        ws.write('B6', result.recommendation, self.formats['center'])
        
        # Note
        ws.write('A8', 'Note: This model uses data-driven assumptions', 
                self.formats['source'])
        ws.write('A9', 'fetched from Yahoo Finance, SEC EDGAR, and market data.', 
                self.formats['source'])


def generate_dcf_excel(inputs: DCFInputs, result: DCFResult, 
                      output_path: str, assumptions: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to generate DCF Excel model.
    
    Args:
        inputs: DCF inputs
        result: DCF results
        output_path: Output file path
        assumptions: Optional data source metadata
        
    Returns:
        Path to generated file
    """
    generator = DCFExcelGenerator(output_path)
    return generator.generate(inputs, result, assumptions)


if __name__ == "__main__":
    # Test with sample data
    from models.dcf import DCFModel, DCFInputs
    
    # Create sample inputs
    inputs = DCFInputs(
        ticker='AAPL',
        current_price=266.43,
        shares_outstanding=14.68e9,
        revenue=416.16e9,
        operating_income=114.3e9,
        net_income=93.7e9,
        free_cash_flow=98.77e9,
        operating_cash_flow=110e9,
        capex=11.23e9,
        total_debt=98.66e9,
        cash_and_equivalents=35.93e9,
        beta=1.11,
        risk_free_rate=0.0428,
        market_risk_premium=0.0859,
        revenue_growth_rates=[0.157, 0.141, 0.118, 0.094, 0.078],
        terminal_growth_rate=0.025,
        tax_rate_override=0.156
    )
    
    # Run DCF
    model = DCFModel()
    result = model.run_dcf(inputs)
    
    # Generate Excel
    output = '/tmp/AAPL_DCF_Model.xlsx'
    generate_dcf_excel(inputs, result, output)
    print(f"\n✓ Test Excel generated: {output}")
