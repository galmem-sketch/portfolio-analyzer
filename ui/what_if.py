import streamlit as st
import yfinance as yf
from core.data_fetcher import search_ticker_direct, search_ticker_query
from core.metrics import calculate_hypo_metrics


def _do_hypo_search(i: int):
    """Run search for new asset i and write results into hypo_assets."""
    assets = st.session_state["hypo_assets"]
    e = assets[i]
    query = st.session_state[f"hypo_q_{i}"]
    e["query"] = query

    if not query.strip():
        return

    direct, dname = search_ticker_direct(query)
    if direct:
        e["ticker"] = direct
        e["company_name"] = dname
        e["search_results"] = []
        e["searched"] = True
    else:
        results = search_ticker_query(query)
        e["search_results"] = results
        e["searched"] = True
        if len(results) == 1:
            e["ticker"] = results[0]["symbol"]
            e["company_name"] = results[0].get("shortname", results[0]["symbol"])
            e["search_results"] = []


def render_what_if():
    """
    Step 5 (optional): What-If Engine — add new assets and compute hypothetical metrics.
    Writes hypo_result to session_state.
    """
    st.header("Step 5: What-If Engine (Optional)")

    config = st.session_state["portfolio_config"]
    all_returns = st.session_state["all_returns"]
    total_sum = sum(e.val for e in config.entries)

    run_hypo = st.checkbox("Build a multi-asset hypothetical scenario?", key="run_hypo_check")
    if not run_hypo:
        st.session_state["hypo_result"] = None
        if st.button("Skip → View Charts", type="primary"):
            st.session_state["step"] = 6
            st.rerun()
        return

    num_new = st.number_input("How many NEW securities to add?", min_value=1, max_value=20,
                               value=st.session_state.get("hypo_num_new", 1), step=1, key="hypo_num_new")

    new_assets_state = st.session_state.setdefault("hypo_assets", [
        {"query": "", "ticker": "", "company_name": "", "mode": "1", "amt": 0.0,
         "search_results": [], "searched": False}
        for _ in range(int(num_new))
    ])
    n = int(num_new)
    while len(new_assets_state) < n:
        new_assets_state.append({"query": "", "ticker": "", "company_name": "", "mode": "1", "amt": 0.0,
                                  "search_results": [], "searched": False})
    while len(new_assets_state) > n:
        new_assets_state.pop()

    for i in range(n):
        e = new_assets_state[i]
        st.markdown(f"**New Asset #{i + 1}**")

        st.text_input(
            f"Name/Ticker #{i + 1}",
            value=e["query"],
            key=f"hypo_q_{i}",
            placeholder="e.g. QQQ, Tesla, ^TA125.TA",
            label_visibility="collapsed",
            on_change=_do_hypo_search,
            args=(i,),
        )

        if e.get("searched") and e["search_results"]:
            opts = [f"{r['symbol']} — {r.get('shortname', r['symbol'])} ({r.get('exchDisp', '')})"
                    for r in e["search_results"]]
            opts = [f"Use exact input: {e['query'].upper()}"] + opts
            sel = st.selectbox(f"Select for new asset {i + 1}:", opts, key=f"hypo_sel_{i}")
            if sel.startswith("Use exact input:"):
                e["ticker"] = e["query"].strip().upper()
                e["company_name"] = e["ticker"]
            else:
                idx = opts.index(sel) - 1
                r = e["search_results"][idx]
                e["ticker"] = r["symbol"]
                e["company_name"] = r.get("shortname", r["symbol"])

        if e["ticker"]:
            st.caption(f"✅ {e['ticker']} ({e['company_name']})")

        e["mode"] = st.radio(
            f"Entry mode for {e['company_name'] or 'asset'}:",
            options=["1", "2"],
            format_func=lambda x: "Target % of new total" if x == "1" else "Cash amount to invest",
            horizontal=True,
            key=f"hypo_mode_{i}",
        )
        amt_label = "Target %" if e["mode"] == "1" else "Cash amount (₪/$)"
        e["amt"] = st.number_input(amt_label, min_value=0.0, value=float(e["amt"]),
                                    step=0.01, format="%.2f", key=f"hypo_amt_{i}")
        st.markdown("---")

    if st.button("Run Simulation →", type="primary"):
        # Auto-resolve any unresolved queries
        for e in new_assets_state:
            if not e["ticker"] and e["query"]:
                direct, dname = search_ticker_direct(e["query"])
                if direct:
                    e["ticker"] = direct
                    e["company_name"] = dname
                else:
                    e["ticker"] = e["query"].strip().upper()
                    e["company_name"] = e["ticker"]

        incomplete = [i + 1 for i, e in enumerate(new_assets_state) if not e["ticker"] or e["amt"] <= 0]
        if incomplete:
            st.error(f"New assets {incomplete} are missing a ticker or amount > 0.")
            return

        new_assets_data = []
        all_ok = True
        with st.spinner("Fetching data for new assets..."):
            for e in new_assets_state:
                try:
                    obj = yf.Ticker(e["ticker"])
                    hist = obj.history(period="max")["Close"]
                    if hasattr(hist.index, 'tz_localize'):
                        hist.index = hist.index.tz_localize(None)
                    if hist.empty:
                        raise ValueError(f"No data for {e['ticker']}")
                    new_assets_data.append({
                        "ticker": e["ticker"],
                        "company_name": e["company_name"],
                        "mode": e["mode"],
                        "amt": e["amt"],
                        "history_df": hist,
                    })
                except Exception as exc:
                    st.error(f"Could not fetch data for {e['ticker']}: {exc}")
                    all_ok = False

        if not all_ok:
            return

        try:
            result = calculate_hypo_metrics(all_returns, new_assets_data, config, total_sum)
            st.session_state["hypo_result"] = result
            st.success(f"✅ Simulation complete — {result['h_years']:.1f} years of shared history")
            st.metric("New Expected Yield", f"{result['hypo_mu']:.2%}")
            st.metric("New Volatility (σ)", f"{result['hypo_sig']:.2%}")
            st.session_state["step"] = 6
            st.rerun()
        except Exception as exc:
            st.error(f"Simulation failed: {exc}")
