import streamlit as st
from core.benchmark import PRESETS
from core.data_fetcher import search_ticker_direct, search_ticker_query, download_benchmark


def render_benchmark_selector():
    """
    Step 3: Benchmark selection. Writes bench_ticker + bench_returns to session_state.
    """
    st.header("Step 3: Benchmark Selection")

    preset_options = list(PRESETS.keys()) + ["Custom Search"]
    choice = st.selectbox("Choose a benchmark index:", preset_options, key="bench_preset")

    custom_query = ""
    if choice == "Custom Search":
        custom_query = st.text_input("Search for index/ETF (e.g. Nasdaq, TA35):", key="bench_custom_query")

    col1, col2 = st.columns([1, 4])
    with col1:
        load_clicked = st.button("Load Benchmark →", type="primary")

    if load_clicked:
        if choice in PRESETS:
            ticker_to_try = PRESETS[choice]
        elif custom_query.strip():
            # Try direct first
            direct, _ = search_ticker_direct(custom_query)
            if direct:
                ticker_to_try = direct
            else:
                results = search_ticker_query(custom_query)
                if results:
                    ticker_to_try = results[0]["symbol"]
                else:
                    ticker_to_try = custom_query.strip().upper()
        else:
            st.error("Please select a preset or enter a custom query.")
            return

        with st.spinner(f"Fetching {ticker_to_try}..."):
            try:
                actual_ticker, bench_returns = download_benchmark(ticker_to_try)
                st.session_state["bench_ticker"] = actual_ticker
                st.session_state["bench_returns"] = bench_returns
                st.success(f"✅ Benchmark loaded: **{actual_ticker}**")
                st.session_state["step"] = 4
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
                st.info("TIP: If an index fails, try an ETF ticker instead (e.g. TAV35.TA for TA-35).")
