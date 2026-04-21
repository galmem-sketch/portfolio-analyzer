"""
Portfolio Analyzer — Streamlit UI
Run: streamlit run app.py
"""
import sys
import os

# Allow bare imports of core/, ui/, utils/ without a package prefix
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from core.data_fetcher import download_portfolio_data, get_boi_interest_rate
from core.metrics import calculate_portfolio_metrics, align_benchmark, calculate_hypo_metrics
from core.portfolio import PortfolioConfig
from ui.portfolio_form import render_portfolio_form
from ui.benchmark_selector import render_benchmark_selector
from ui.what_if import render_what_if
from ui.charts import plot_efficiency, plot_bell_curve
from ui.tables import render_portfolio_table, render_hypo_table
from ui.report_pdf import build_report_html

plt.style.use('seaborn-v0_8-muted')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Analyzer",
    page_icon="📊",
    layout="wide",
)

# ── Session-state defaults ────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state["step"] = 1


# ── Sidebar progress indicator ────────────────────────────────────────────────
STEPS = [
    "1 · Portfolio Entry",
    "2 · Data Retrieval & Audit",
    "3 · Benchmark Selection",
    "4 · Metrics Dashboard",
    "5 · What-If Engine",
    "6 · Charts & Report",
]

with st.sidebar:
    st.title("Portfolio Analyzer")
    st.markdown("---")
    current_step = st.session_state["step"]

    # Steps that have been reached are clickable
    for i, label in enumerate(STEPS, start=1):
        if i < current_step:
            if st.button(f"✅ {label}", key=f"nav_{i}", use_container_width=True):
                st.session_state["step"] = i
                st.rerun()
        elif i == current_step:
            st.markdown(f"**▶ {label}**")
        else:
            st.markdown(f"⬜ {label}", help="Complete previous steps to unlock")

    st.markdown("---")
    if st.button("↺ Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ── Step dispatcher ───────────────────────────────────────────────────────────
step = st.session_state["step"]

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Portfolio Entry
# ─────────────────────────────────────────────────────────────────────────────
if step == 1:
    render_portfolio_form()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Data Retrieval & Audit
# ─────────────────────────────────────────────────────────────────────────────
elif step == 2:
    st.header("Step 2: Data Retrieval & Audit")
    config: PortfolioConfig = st.session_state["portfolio_config"]

    # Auto-fetch BOI rate if Cash is present and rf not yet set
    if config.has_cash and config.rf_annual_yield == 0.0:
        with st.spinner("Fetching Bank of Israel interest rate..."):
            auto_rf = get_boi_interest_rate()
        if auto_rf:
            st.success(f"Bank of Israel rate detected: **{auto_rf:.2%}**")
            config.rf_annual_yield = auto_rf
        else:
            rf_input = st.number_input(
                "Could not auto-fetch BOI rate. Enter Risk-Free Yield (%):",
                min_value=0.0, max_value=20.0, value=4.5, step=0.1, format="%.2f"
            )
            if st.button("Set Risk-Free Rate"):
                config.rf_annual_yield = rf_input / 100
                st.rerun()
            st.stop()

    stock_tickers = config.stock_tickers
    if not stock_tickers:
        st.info("Portfolio contains only Cash — no market data to download.")
        st.session_state["all_returns"] = pd.DataFrame()
        st.session_state["data"] = pd.DataFrame()
        st.session_state["years"] = 15.0
        st.session_state["step"] = 3
        st.rerun()

    # Download
    with st.spinner(f"Downloading data for: {', '.join(stock_tickers)}..."):
        data, problematic, history_report = download_portfolio_data(stock_tickers)

    st.session_state["data"] = data
    all_returns = data.pct_change()
    st.session_state["all_returns"] = all_returns

    # Audit display
    st.subheader("Data Quality Audit")
    if problematic:
        st.error(f"The following tickers had download issues: **{', '.join(problematic)}**")
        st.warning("Please resolve them below before continuing.")

        resolved_entries = list(config.entries)
        changes = False
        for p_ticker in problematic:
            st.markdown(f"**Problematic:** `{p_ticker}`")
            action = st.radio(f"Action for {p_ticker}:", ["Replace", "Remove"],
                               key=f"resolve_action_{p_ticker}", horizontal=True)
            if action == "Replace":
                new_q = st.text_input(f"New ticker/name to replace `{p_ticker}`:",
                                       key=f"resolve_q_{p_ticker}")
                if st.button(f"Apply replacement for {p_ticker}", key=f"resolve_btn_{p_ticker}"):
                    from core.data_fetcher import search_ticker_direct
                    direct, dname = search_ticker_direct(new_q)
                    if direct:
                        for entry in resolved_entries:
                            if entry.ticker == p_ticker:
                                entry.ticker = direct
                                entry.company_name = dname
                                changes = True
                                st.success(f"Replaced `{p_ticker}` → `{direct}`")
                                break
                    else:
                        st.error(f"Could not validate ticker '{new_q}'.")
            else:
                resolved_entries = [e for e in resolved_entries if e.ticker != p_ticker]
                changes = True

        if changes:
            new_config = config.rebuild_from_entries(resolved_entries)
            st.session_state["portfolio_config"] = new_config
            # Re-download
            with st.spinner("Re-downloading updated portfolio..."):
                data2, prob2, hr2 = download_portfolio_data(new_config.stock_tickers)
            st.session_state["data"] = data2
            st.session_state["all_returns"] = data2.pct_change()
            history_report = hr2
            problematic = prob2

        if problematic:
            st.stop()

    # Show audit results
    if history_report:
        shortest_ticker = min(history_report, key=history_report.get)
        h_years = history_report[shortest_ticker]
        st.session_state["years"] = h_years

        col1, col2 = st.columns(2)
        with col1:
            if h_years < 1:
                st.error(f"Insufficient data: {shortest_ticker} has < 1 year ({h_years:.1f} yrs).")
            elif h_years < 3:
                st.error(f"Low confidence: {shortest_ticker} only has {h_years:.1f} years.")
            elif h_years < 5:
                st.warning(f"{shortest_ticker} provides {h_years:.1f} years of history.")
            else:
                st.success(f"Robust history: {h_years:.1f} years. Shortest: **{shortest_ticker}**.")
        with col2:
            st.metric("Analysis Window", f"{h_years:.1f} years")
    else:
        st.session_state["years"] = 0.0

    # Portfolio summary table
    st.subheader("Portfolio Summary")
    st.markdown(render_portfolio_table(config.entries, config.mode), unsafe_allow_html=True)

    if st.button("Continue to Benchmark Selection →", type="primary"):
        st.session_state["step"] = 3
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Benchmark Selection
# ─────────────────────────────────────────────────────────────────────────────
elif step == 3:
    render_benchmark_selector()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Metrics Dashboard
# ─────────────────────────────────────────────────────────────────────────────
elif step == 4:
    st.header("Step 4: Metrics Dashboard")
    config: PortfolioConfig = st.session_state["portfolio_config"]
    all_returns: pd.DataFrame = st.session_state["all_returns"]
    bench_returns: pd.DataFrame = st.session_state["bench_returns"]
    bench_ticker: str = st.session_state["bench_ticker"]

    # Calculate metrics
    metrics = calculate_portfolio_metrics(config, all_returns)
    st.session_state["metrics"] = metrics

    port_mean = metrics["port_mean"]
    port_std = metrics["port_std"]
    calc_df = metrics["calc_df"]
    c_years = metrics["c_years"]

    b_mu, b_std = align_benchmark(bench_returns, calc_df.index)
    st.session_state["b_mu"] = b_mu
    st.session_state["b_std"] = b_std

    # Key metrics row
    st.subheader("Portfolio Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Expected Annual Yield (μ)", f"{port_mean:.2%}" if not np.isnan(port_mean) else "N/A")
    with col2:
        st.metric("Annualized Volatility (σ)", f"{port_std:.2%}" if not np.isnan(port_std) else "N/A")
    with col3:
        sharpe = metrics["sharpe"]
        st.metric("Sharpe Ratio", f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A")
    with col4:
        st.metric("Analysis Window", f"{c_years:.1f} years")

    st.caption(f"Benchmark: {bench_ticker} (aligned to portfolio window)")

    # Correlation heatmap
    baseline_tickers = config.stock_tickers
    if len(baseline_tickers) > 1:
        st.subheader("Correlation Heatmap")
        years = st.session_state.get("years", c_years)
        corr = all_returns[baseline_tickers].corr()
        n_tickers = len(baseline_tickers)
        cell_size = 1.8
        fig_corr, ax_corr = plt.subplots(figsize=(n_tickers * cell_size + 1.5, n_tickers * cell_size))
        sns.heatmap(corr, annot=True, cmap='RdYlGn', center=0, fmt=".2f",
                    linewidths=0.5, linecolor='white', ax=ax_corr, annot_kws={"size": 11})
        ax_corr.set_title(f"Correlation Heatmap ({years:.1f}-Year Shared Period)",
                          fontsize=11, fontweight='bold')
        col_hm, _ = st.columns([2, 3])
        with col_hm:
            st.pyplot(fig_corr)
        plt.close(fig_corr)

        # Covariance matrix
        with st.expander("Annualized Covariance Matrix"):
            cov = all_returns[baseline_tickers].cov() * 252
            st.dataframe(cov.style.background_gradient(cmap='coolwarm').format("{:.4f}"))
    elif len(baseline_tickers) == 1:
        st.info("Correlation analysis requires at least 2 non-Cash assets.")
    else:
        st.info("Only Cash detected — correlation analysis skipped.")

    if st.button("Continue to What-If Engine →", type="primary"):
        st.session_state["step"] = 5
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: What-If Engine
# ─────────────────────────────────────────────────────────────────────────────
elif step == 5:
    render_what_if()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Charts & Report
# ─────────────────────────────────────────────────────────────────────────────
elif step == 6:
    st.header("Step 6: Charts & Report")

    config: PortfolioConfig = st.session_state["portfolio_config"]
    all_returns: pd.DataFrame = st.session_state["all_returns"]
    bench_returns: pd.DataFrame = st.session_state["bench_returns"]
    bench_ticker: str = st.session_state["bench_ticker"]
    metrics: dict = st.session_state["metrics"]
    b_mu: float = st.session_state["b_mu"]
    b_std: float = st.session_state["b_std"]
    hypo_result = st.session_state.get("hypo_result")  # dict or None

    port_mean = metrics["port_mean"]
    port_std = metrics["port_std"]
    calc_df = metrics["calc_df"]
    c_years = metrics["c_years"]
    years = st.session_state.get("years", c_years)
    rf = config.rf_annual_yield

    # Re-align benchmark to actual window (or hypo window)
    if hypo_result:
        hypo_df = hypo_result["hypo_df"]
        common_idx = bench_returns.index.intersection(hypo_df.index)
        b_aligned = bench_returns.loc[common_idx]
        b_mu_plot = float(b_aligned.mean().iloc[0] * 252)
        b_std_plot = float(b_aligned.std().iloc[0] * np.sqrt(252))
        c_years_plot = hypo_result["h_years"]
    else:
        common_idx = bench_returns.index.intersection(calc_df.index)
        b_aligned = bench_returns.loc[common_idx]
        b_mu_plot = float(b_aligned.mean().iloc[0] * 252)
        b_std_plot = float(b_aligned.std().iloc[0] * np.sqrt(252))
        c_years_plot = c_years

    hypo_mu = hypo_result["hypo_mu"] if hypo_result else None
    hypo_sig = hypo_result["hypo_sig"] if hypo_result else None

    # ── Efficiency Plot ───────────────────────────────────────────────────────
    st.subheader("Portfolio Efficiency Analysis")
    fig_eff = plot_efficiency(
        port_mean=port_mean, port_std=port_std,
        bench_ticker=bench_ticker, b_mu=b_mu_plot, b_std=b_std_plot,
        rf=rf, c_years=c_years_plot,
        hypo_mu=hypo_mu, hypo_sig=hypo_sig,
    )
    st.pyplot(fig_eff)
    plt.close(fig_eff)

    # ── Bell Curve ────────────────────────────────────────────────────────────
    st.subheader("Annual Portfolio Performance Projection")
    title_years = hypo_result["h_years"] if hypo_result else years
    fig_bell = plot_bell_curve(
        port_mean=port_mean, port_std=port_std,
        bench_ticker=bench_ticker, b_mu=b_mu_plot, b_std=b_std_plot,
        rf=rf, title_years=title_years,
        hypo_mu=hypo_mu, hypo_sig=hypo_sig,
    )
    st.pyplot(fig_bell)
    plt.close(fig_bell)

    # ── Youngest asset diagnostic (Hebrew note preserved) ────────────────────
    if not calc_df.empty:
        first_valid = calc_df.apply(lambda x: x.first_valid_index())
        youngest = first_valid.idxmax()
        actual_years = len(calc_df) / 252
        if actual_years < 5:
            st.warning(
                f"Analysis based on only {actual_years:.1f} years (limited by **{youngest}**)."
            )

    # ── Report section ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Full Report")

    st.markdown("#### Current Portfolio Summary")
    st.markdown(render_portfolio_table(config.entries, config.mode), unsafe_allow_html=True)
    sharpe = metrics["sharpe"]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Expected Annual Yield (μ)", f"{port_mean:.2%}" if not np.isnan(port_mean) else "N/A")
    with col2:
        st.metric("Annualized Volatility (σ)", f"{port_std:.2%}" if not np.isnan(port_std) else "N/A")
    with col3:
        st.metric("Sharpe Ratio", f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A")

    if hypo_result:
        st.markdown("#### Hypothetical Portfolio Summary")
        st.markdown(
            render_hypo_table(
                hypo_result["combined_details"],
                config.mode,
                hypo_result["final_total_val"],
            ),
            unsafe_allow_html=True,
        )
        hypo_sharpe = (hypo_mu - rf) / hypo_sig if hypo_sig > 0 else np.nan
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("New Expected Yield (μ)", f"{hypo_mu:.2%}")
        with col2:
            st.metric("New Volatility (σ)", f"{hypo_sig:.2%}")
        with col3:
            st.metric("New Sharpe Ratio", f"{hypo_sharpe:.2f}" if not np.isnan(hypo_sharpe) else "N/A")

    st.success("Analysis complete. Use the sidebar to start over with a new portfolio.")

    # ── Report Download ───────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("Generate Report"):
        with st.spinner("Building report…"):
            html_bytes = build_report_html(
                config=config,
                metrics=metrics,
                bench_ticker=bench_ticker,
                b_mu_plot=b_mu_plot,
                b_std_plot=b_std_plot,
                c_years_plot=c_years_plot,
                years=years,
                hypo_result=hypo_result,
            )
        st.download_button(
            label="⬇ Download Report (open → Save as PDF)",
            data=html_bytes,
            file_name="portfolio_report.html",
            mime="text/html",
        )
