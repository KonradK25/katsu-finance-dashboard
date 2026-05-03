#!/usr/bin/env python3
"""
Streamlit Dashboard for Katsu DCF Engine

Interactive DCF valuation dashboard with:
- Real-time data fetching
- Adjustable assumptions
- Visual charts and sensitivity analysis
- Multi-company comparison
- Excel export
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.dcf import DCFModel, DCFInputs
from models.dcf_auto import run_auto_dcf
from scrapers.macro_data import MacroDataScraper
from scrapers.yahoo_finance import YahooFinanceScraper
from scrapers.ai_impact import AIImpactAssessor
from excel.generator import generate_dcf_excel


# Page configuration
st.set_page_config(
    page_title="Katsu DCF Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'ticker' not in st.session_state:
        st.session_state.ticker = 'AAPL'
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'inputs' not in st.session_state:
        st.session_state.inputs = None
    if 'assumptions' not in st.session_state:
        st.session_state.assumptions = None


def fetch_company_data(ticker: str):
    """Fetch all data for a ticker"""
    with st.spinner(f"📊 Fetching data for {ticker}..."):
        try:
            # Run auto DCF with real data and AI assessment
            inputs, ai_assessment = run_auto_dcf(ticker)
            
            # Run DCF calculation
            model = DCFModel()
            result = model.run_dcf(inputs)
            
            # Fetch assumptions metadata
            macro = MacroDataScraper()
            assumptions = macro.get_all_dcf_assumptions(ticker)
            
            st.session_state.ticker = ticker
            st.session_state.inputs = inputs
            st.session_state.result = result
            st.session_state.assumptions = assumptions
            st.session_state.ai_assessment = ai_assessment
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error fetching data for {ticker}: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return False


def render_header():
    """Render main header"""
    st.markdown('<p class="main-header">📊 Katsu DCF Engine</p>', unsafe_allow_html=True)
    st.markdown("### Interactive Discounted Cash Flow Valuation Dashboard")
    st.markdown("---")


def render_sidebar():
    """Render sidebar with controls"""
    with st.sidebar:
        st.header("🎯 Controls")
        
        # Ticker input
        ticker = st.text_input(
            "Stock Ticker",
            value=st.session_state.ticker,
            placeholder="e.g., AAPL, MSFT, GOOGL",
            help="Enter a stock ticker symbol"
        )
        
        # Analyze button
        if st.button("🚀 Run DCF Analysis", type="primary", use_container_width=True):
            if ticker:
                fetch_company_data(ticker.upper())
                st.rerun()
        
        st.markdown("---")
        
        # Quick tickers
        st.subheader("⚡ Quick Select")
        cols = st.columns(2)
        tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA"]
        for i, ticker_symbol in enumerate(tickers):
            col_idx = i % 2
            if cols[col_idx].button(ticker_symbol, key=f"btn_{ticker_symbol}", use_container_width=True):
                fetch_company_data(ticker_symbol)
                st.rerun()
        
        st.markdown("---")
        
        # Export options
        st.subheader("💾 Export")
        if st.session_state.result:
            if st.button("📊 Download Excel", use_container_width=True):
                ticker = st.session_state.ticker
                output_path = f"/tmp/{ticker}_DCF_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                generate_dcf_excel(
                    st.session_state.inputs,
                    st.session_state.result,
                    output_path
                )
                
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Now",
                        data=f,
                        file_name=f"{ticker}_DCF_Model.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        
        st.markdown("---")
        
        # Info
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Katsu DCF Engine** performs professional discounted cash flow valuations using:
        
        - ✅ Real-time market data (Yahoo Finance)
        - ✅ SEC EDGAR filings (10-K, 10-Q)
        - ✅ Live Treasury yields
        - ✅ Analyst growth estimates
        - ✅ Professional Excel output
        
        **Data Sources:**
        - 10Y Treasury (^TNX)
        - S&P 500 (^GSPC)
        - Company financials
        - Analyst consensus
        """)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_economic_data():
    """Fetch and cache economic data"""
    macro = MacroDataScraper()
    return {
        'gdp_current': macro.get_gdp_growth(),
        'inflation_current': macro.get_inflation_rate(),
        'gdp_history': macro.get_gdp_history(10),
        'inflation_history': macro.get_inflation_history(10)
    }


def render_economic_data():
    """Render GDP and Inflation charts"""
    st.subheader("🌍 Economic Data")
    
    with st.spinner("Fetching economic data from FRED..."):
        data = get_economic_data()
    
    gdp_current = data['gdp_current']
    inflation_current = data['inflation_current']
    gdp_history = data['gdp_history']
    inflation_history = data['inflation_history']
    
    # Display current metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="GDP Growth (YoY)",
            value=f"{gdp_current['gdp_growth_percent']:.2f}%",
            delta=f"vs {gdp_current['source']}"
        )
    with col2:
        st.metric(
            label="Inflation Rate (CPI YoY)",
            value=f"{inflation_current['inflation_percent']:.2f}%",
            delta=f"vs {inflation_current['source']}"
        )
    
    st.markdown("---")
    
    # GDP History Chart
    st.markdown("#### 📈 GDP Growth History")
    gdp_df = pd.DataFrame(gdp_history)
    if not gdp_df.empty:
        fig_gdp = px.bar(
            gdp_df, 
            x='year', 
            y='gdp_growth',
            title='US GDP Growth Rate (Annual, %)',
            labels={'year': 'Year', 'gdp_growth': 'GDP Growth (%)'},
            color='gdp_growth',
            color_continuous_scale='RdYlGn'
        )
        fig_gdp.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Year",
            yaxis_title="GDP Growth (%)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_gdp, use_container_width=True)
    else:
        st.warning("GDP history data unavailable")
    
    st.markdown("---")
    
    # Inflation History Chart
    st.markdown("#### 📊 Inflation History")
    inflation_df = pd.DataFrame(inflation_history)
    if not inflation_df.empty:
        fig_inflation = px.line(
            inflation_df,
            x='year',
            y='inflation',
            title='US Inflation Rate (CPI, Annual %)',
            labels={'year': 'Year', 'inflation': 'Inflation (%)'},
            markers=True
        )
        fig_inflation.add_hline(
            y=2.0, 
            line_dash="dash", 
            line_color="green",
            annotation_text="Fed Target (2%)"
        )
        fig_inflation.update_layout(
            height=400,
            xaxis_title="Year",
            yaxis_title="Inflation Rate (%)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_inflation, use_container_width=True)
    else:
        st.warning("Inflation history data unavailable")
    
    st.markdown("---")


def render_valuation_summary():
    """Render main valuation summary cards"""
    if not st.session_state.result:
        return
    
    result = st.session_state.result
    inputs = st.session_state.inputs
    ticker = st.session_state.ticker
    
    st.subheader(f"📈 {ticker} Valuation Summary")
    
    # Create metric cards
    cols = st.columns(4)
    
    with cols[0]:
        st.metric(
            label="Current Price",
            value=f"${inputs.current_price:.2f}",
            delta=None
        )
    
    with cols[1]:
        st.metric(
            label="Intrinsic Value",
            value=f"${result.intrinsic_value_per_share:.2f}",
            delta=None
        )
    
    with cols[2]:
        upside = result.upside_downside * 100
        delta_color = "normal" if upside > 0 else "inverse"
        st.metric(
            label="Upside/(Downside)",
            value=f"{upside:+.1f}%",
            delta=f"{upside:+.1f}%",
            delta_color=delta_color
        )
    
    with cols[3]:
        # Recommendation with color
        rec = result.recommendation
        if "BUY" in rec:
            rec_emoji = "🟢"
        elif "HOLD" in rec:
            rec_emoji = "🟡"
        else:
            rec_emoji = "🔴"
        
        st.metric(
            label="Recommendation",
            value=f"{rec_emoji} {rec}",
            delta=None
        )


def render_assumptions_editor():
    """Render interactive assumptions editor"""
    if not st.session_state.inputs:
        return
    
    inputs = st.session_state.inputs
    ticker = st.session_state.ticker
    
    with st.expander("📝 Adjust Assumptions (Advanced)", expanded=False):
        st.markdown("**Modify DCF assumptions to see how valuation changes**")
        
        cols = st.columns(3)
        
        with cols[0]:
            risk_free = st.slider(
                "Risk-Free Rate (%)",
                min_value=0.0,
                max_value=10.0,
                value=inputs.risk_free_rate * 100,
                step=0.1,
                key="rf_slider"
            )
            
            mrp = st.slider(
                "Market Risk Premium (%)",
                min_value=2.0,
                max_value=15.0,
                value=inputs.market_risk_premium * 100,
                step=0.1,
                key="mrp_slider"
            )
            
            beta = st.number_input(
                "Beta (β)",
                min_value=0.0,
                max_value=5.0,
                value=inputs.beta,
                step=0.01,
                key="beta_input"
            )
        
        with cols[1]:
            st.markdown("##### Revenue Growth Rates")
            growth_rates = []
            for i in range(5):
                val = st.number_input(
                    f"Year {i+1} Growth (%)",
                    min_value=-50.0,
                    max_value=100.0,
                    value=inputs.revenue_growth_rates[i] * 100,
                    step=0.5,
                    key=f"growth_{i}"
                )
                growth_rates.append(val / 100)
            
            terminal_growth = st.slider(
                "Terminal Growth (%)",
                min_value=0.0,
                max_value=5.0,
                value=inputs.terminal_growth_rate * 100,
                step=0.1,
                key="terminal_slider"
            )
        
        with cols[2]:
            tax_rate = st.slider(
                "Tax Rate (%)",
                min_value=0.0,
                max_value=50.0,
                value=inputs.tax_rate_override * 100,
                step=0.5,
                key="tax_slider"
            )
            
            # Recalculate with new assumptions
            if st.button("🔄 Recalculate with New Assumptions", use_container_width=True):
                # Update inputs
                inputs.risk_free_rate = risk_free / 100
                inputs.market_risk_premium = mrp / 100
                inputs.beta = beta
                inputs.revenue_growth_rates = growth_rates
                inputs.terminal_growth_rate = terminal_growth / 100
                inputs.tax_rate_override = tax_rate / 100
                
                # Recalculate
                model = DCFModel()
                result = model.run_dcf(inputs)
                
                st.session_state.result = result
                st.session_state.inputs = inputs
                st.success("✅ Valuation recalculated!")
                st.rerun()


def render_wacc_breakdown():
    """Render WACC calculation breakdown"""
    if not st.session_state.result:
        return
    
    result = st.session_state.result
    inputs = st.session_state.inputs
    
    st.subheader("🧮 WACC Calculation Breakdown")
    
    cols = st.columns(2)
    
    with cols[0]:
        st.markdown("##### Cost of Equity (CAPM)")
        st.latex(r"R_e = R_f + \beta \times (R_m - R_f)")
        
        capm_data = {
            "Risk-Free Rate (Rf)": f"{inputs.risk_free_rate:.1%}",
            "Beta (β)": f"{inputs.beta:.2f}",
            "Market Risk Premium": f"{inputs.market_risk_premium:.1%}",
            "Cost of Equity (Re)": f"{result.cost_of_equity:.1%}"
        }
        
        capm_df = pd.DataFrame({
            "Component": list(capm_data.keys()),
            "Value": list(capm_data.values())
        })
        st.table(capm_df)
    
    with cols[1]:
        st.markdown("##### WACC Formula")
        st.latex(r"\text{WACC} = \frac{E}{V} \times R_e + \frac{D}{V} \times R_d \times (1-T)")
        
        # Calculate weights
        equity_value = inputs.current_price * inputs.shares_outstanding
        debt_value = inputs.total_debt
        total_value = equity_value + debt_value
        
        equity_weight = equity_value / total_value if total_value > 0 else 0.8
        debt_weight = debt_value / total_value if total_value > 0 else 0.2
        
        wacc_data = {
            "Equity Weight (E/V)": f"{equity_weight:.1%}",
            "Debt Weight (D/V)": f"{debt_weight:.1%}",
            "Cost of Equity": f"{result.cost_of_equity:.1%}",
            "Cost of Debt (after-tax)": f"{result.cost_of_debt * (1-result.tax_rate):.1%}",
            "**WACC**": f"**{result.wacc:.1%}**"
        }
        
        wacc_df = pd.DataFrame({
            "Component": list(wacc_data.keys()),
            "Value": list(wacc_data.values())
        })
        st.table(wacc_df)


def render_fcf_projections():
    """Render FCF projection chart"""
    if not st.session_state.result:
        return
    
    result = st.session_state.result
    inputs = st.session_state.inputs
    
    st.subheader("💰 5-Year Free Cash Flow Projections")
    
    # Calculate FCF projections
    fcf_margin = inputs.free_cash_flow / inputs.revenue if inputs.revenue > 0 else 0.25
    
    years = ['Current'] + [f'Year {i+1}' for i in range(5)]
    fcf_values = [inputs.free_cash_flow]
    
    revenue = inputs.revenue
    for growth in inputs.revenue_growth_rates:
        revenue = revenue * (1 + growth)
        fcf = revenue * fcf_margin
        fcf_values.append(fcf)
    
    # Create chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=[v/1e9 for v in fcf_values],
        name='Free Cash Flow',
        marker_color='#1f77b4',
        text=[f'${v/1e9:.1f}B' for v in fcf_values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Free Cash Flow Projections (5 Years)',
        xaxis_title='Year',
        yaxis_title='FCF ($ Billions)',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show data table
    with st.expander("📊 View Projection Data"):
        df = pd.DataFrame({
            'Year': years,
            'FCF ($B)': [round(v/1e9, 2) for v in fcf_values],
            'Growth Rate': ['-',] + [f'{g:.1%}' for g in inputs.revenue_growth_rates]
        })
        st.dataframe(df, use_container_width=True)


def render_sensitivity_analysis():
    """Render sensitivity analysis heatmap"""
    if not st.session_state.result:
        return
    
    result = st.session_state.result
    inputs = st.session_state.inputs
    
    st.subheader("📊 Sensitivity Analysis")
    st.markdown("Intrinsic value across different WACC and terminal growth assumptions")
    
    # Get sensitivity data
    if hasattr(result, 'sensitivity_table') and result.sensitivity_table:
        sens_data = result.sensitivity_table
        wacc_range = result.wacc_range
        growth_range = result.growth_range
        
        # Create heatmap dataframe
        df = pd.DataFrame(
            sens_data,
            index=[f'{g:.1%}' for g in growth_range],
            columns=[f'{w:.1%}' for w in wacc_range]
        )
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=df.values,
            x=df.columns,
            y=df.index,
            colorscale='RdYlGn',
            text=df.round(2),
            texttemplate='$%{text}',
            textfont={"size": 10},
            hovertemplate='WACC: %{x}<br>Growth: %{y}<br>Value: $%{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Intrinsic Value Sensitivity Matrix',
            xaxis_title='WACC',
            yaxis_title='Terminal Growth Rate',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Highlight current assumptions
        st.markdown(f"**Current assumptions highlighted:** WACC {result.wacc:.1%}, Terminal Growth {inputs.terminal_growth_rate:.1%}")


def render_valuation_distribution():
    """Render valuation distribution chart"""
    if not st.session_state.result:
        return
    
    result = st.session_state.result
    inputs = st.session_state.inputs
    
    st.subheader("📈 Valuation Range Analysis")
    
    # Get sensitivity data for distribution
    if hasattr(result, 'sensitivity_table') and result.sensitivity_table:
        all_values = []
        for row in result.sensitivity_table:
            all_values.extend(row)
        
        min_val = min(all_values)
        max_val = max(all_values)
        current_val = result.intrinsic_value_per_share
        market_price = inputs.current_price
        
        # Create distribution chart
        fig = go.Figure()
        
        # Add range bar
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=current_val,
            delta={'reference': market_price, 'valueformat': '$.2f'},
            number={'prefix': '$', 'valueformat': '.2f'},
            title={'text': "Intrinsic Value vs Market Price"}
        ))
        
        # Add range visualization
        fig.add_trace(go.Scatter(
            x=[min_val, current_val, max_val, market_price],
            y=[0.5, 0.5, 0.5, 0.5],
            mode='markers+text',
            marker=dict(size=15, color=['gray', 'green', 'gray', 'red']),
            text=['Min', f'${current_val:.2f}', 'Max', f'${market_price:.2f}'],
            textposition='top center',
            name='Valuation Range'
        ))
        
        fig.update_layout(
            height=300,
            xaxis={'visible': False},
            yaxis={'visible': False},
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        cols = st.columns(4)
        with cols[0]:
            st.metric("Minimum Value", f"${min_val:.2f}")
        with cols[1]:
            st.metric("Intrinsic Value", f"${current_val:.2f}")
        with cols[2]:
            st.metric("Maximum Value", f"${max_val:.2f}")
        with cols[3]:
            st.metric("Market Price", f"${market_price:.2f}")


def render_data_sources():
    """Render data sources information"""
    if not st.session_state.assumptions:
        return
    
    st.subheader("📚 Data Sources")
    
    assumptions = st.session_state.assumptions
    ticker = st.session_state.ticker
    
    cols = st.columns(2)
    
    with cols[0]:
        st.markdown("##### Macroeconomic Data")
        st.markdown(f"""
        - **Risk-Free Rate:** {assumptions['risk_free_rate']:.2%} (10-Year Treasury ^TNX)
        - **Market Risk Premium:** {assumptions['market_risk_premium']:.2%} (S&P 500 ^GSPC historical)
        - **Terminal Growth:** {assumptions['terminal_growth_rate']:.2%} (Long-term GDP expectations)
        """)
    
    with cols[1]:
        st.markdown("##### Company Data")
        st.markdown(f"""
        - **Ticker:** {ticker}
        - **Revenue Growth:** Analyst consensus (Yahoo Finance)
        - **Tax Rate:** {assumptions['tax_rate']:.1%} (Effective rate from financials)
        - **Cost of Debt:** {assumptions['cost_of_debt']:.2%} (Interest/Debt ratio)
        - **Financials:** SEC EDGAR + Yahoo Finance
        """)


def main():
    """Main dashboard application"""
    # Initialize session state
    init_session_state()
    
    # Render UI
    render_header()
    render_sidebar()
    
    # Economic Data Dashboard (always visible)
    render_economic_data()
    st.markdown("---")
    
    if st.session_state.result:
        # Main content
        render_valuation_summary()
        st.markdown("---")
        
        # Charts and analysis
        col1, col2 = st.columns(2)
        with col1:
            render_fcf_projections()
        with col2:
            render_sensitivity_analysis()
        
        st.markdown("---")
        
        # WACC and assumptions
        render_wacc_breakdown()
        st.markdown("---")
        
        render_valuation_distribution()
        st.markdown("---")
        
        # Assumptions editor
        render_assumptions_editor()
        st.markdown("---")
        
        # Data sources
        render_data_sources()
        
    else:
        # Welcome message
        st.info("👈 Select a ticker from the sidebar or enter one above to begin analysis")
        
        # Example tickers
        st.markdown("### Popular Stocks to Analyze")
        
        examples = [
            ("AAPL", "Apple Inc.", "Technology"),
            ("MSFT", "Microsoft Corporation", "Technology"),
            ("GOOGL", "Alphabet Inc.", "Technology"),
            ("TSLA", "Tesla Inc.", "Automotive"),
            ("AMZN", "Amazon.com Inc.", "E-commerce"),
            ("NVDA", "NVIDIA Corporation", "Semiconductors")
        ]
        
        cols = st.columns(3)
        for i, (ticker, name, sector) in enumerate(examples):
            col_idx = i % 3
            with cols[col_idx]:
                st.markdown(f"""
                **{ticker}** - {name}  
                _Sector: {sector}_
                """)


if __name__ == "__main__":
    main()
