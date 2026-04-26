"""
Info page for Portfolio Analyzer app
Displays when user first opens the app or clicks "About"
"""

import streamlit as st


def render_info_page():
    """Display the info/about page inside the Streamlit app"""
    
    st.title("📊 About Portfolio Analyzer")
    st.markdown("---")
    
    st.markdown("""
    ### What is Portfolio Analyzer?
    
    **Portfolio Analyzer** is a smart, interactive tool for understanding your long-term investment portfolio. 
    Enter your holdings, and get instant insights into risk, return, and efficiency — all backed by live market data.
    
    Whether you're building wealth steadily or optimizing an existing portfolio, Portfolio Analyzer helps you:
    - **See the bigger picture** — how your assets work together
    - **Make informed decisions** — understand risk vs. return trade-offs for long-term growth
    - **Plan for the future** — test portfolio adjustments before committing to changes
    - **Compare fairly** — benchmark your performance against the market
    """)
    
    st.markdown("---")
    
    st.markdown("### How It Works")
    st.markdown("""
    Portfolio Analyzer guides you through a **6-step wizard**:
    
    1️⃣ **Portfolio Entry** — Enter your holdings by ticker or company name (ILS or USD)  
    2️⃣ **Data Retrieval & Audit** — Fetch live data and verify data quality  
    3️⃣ **Benchmark Selection** — Pick a benchmark (S&P 500, Nasdaq, TA-125, or custom)  
    4️⃣ **Metrics Dashboard** — View return, volatility, Sharpe ratio, and correlations  
    5️⃣ **What-If Engine** — Test portfolio changes and see instant impact  
    6️⃣ **Charts & Report** — Download a professional PDF report  
    """)
    
    st.markdown("---")
    
    st.markdown("### Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ✅ **Live Market Data**  
        Real-time prices from Yahoo Finance
        
        ✅ **Multi-Currency**  
        Work in ILS or USD (auto-converted)
        
        ✅ **Data Validation**  
        Flags problematic tickers automatically
        """)
    
    with col2:
        st.markdown("""
        ✅ **Long-Term Metrics**  
        Return, volatility, Sharpe ratio, correlation
        
        ✅ **Strategic Planning**  
        Test portfolio changes before implementing
        
        ✅ **PDF Reports**  
        Download professional analysis reports
        """)
    
    st.markdown("---")
    
    st.markdown("### Who Is This For?")
    st.markdown("""
    - **Long-Term Investors** — build and optimize wealth over years
    - **Retirement Planners** — understand your asset allocation risk
    - **Individual Portfolio Managers** — analyze and rebalance holdings
    - **Financial Learners** — explore portfolio theory interactively
    - **Anyone with investments** — get clarity and confidence in your holdings
    """)
    
    st.markdown("---")
    
    st.markdown("### Key Metrics Explained")
    
    with st.expander("📈 **Annualized Return (μ)** - Expected yearly gain"):
        st.markdown("""
        The average annual return your portfolio is expected to generate based on historical performance.
        
        - Higher return = potentially higher growth
        - Consider this in context with volatility and risk
        """)
    
    with st.expander("📊 **Annualized Volatility (σ)** - How much your returns fluctuate"):
        st.markdown("""
        A measure of how much your portfolio's value bounces around year to year.
        
        - Higher volatility = greater ups and downs
        - Lower volatility = more stable, predictable returns
        - Long-term investors can often tolerate higher volatility
        """)
    
    with st.expander("⚡ **Sharpe Ratio** - Return per unit of risk"):
        st.markdown("""
        Tells you how much return you're getting for each unit of risk you take.
        
        - Higher = better risk-adjusted returns
        - Useful for comparing portfolios fairly
        - Accounts for both return and volatility
        """)
    
    with st.expander("🔗 **Correlation Heatmap** - How your assets move together"):
        st.markdown("""
        Shows how different assets in your portfolio move in relation to each other.
        
        - Red = move together (high correlation, less diversification)
        - Green = move oppositely (low/negative correlation, good diversification)
        - White = neutral correlation
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Get Started Now
    
    Click **"1 · Portfolio Entry"** in the sidebar to begin analyzing your portfolio!
    
    **Questions?** Check out the [GitHub repository](https://github.com/galmem-sketch/portfolio-analyzer) 
    for more details and documentation.
    
    ---
    
    *Made with ❤️ for smart, long-term investing.*
    """)
