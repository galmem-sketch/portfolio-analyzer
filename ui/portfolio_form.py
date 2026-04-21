import streamlit as st
from core.data_fetcher import search_ticker_direct, search_ticker_query
from core.portfolio import AssetEntry, PortfolioConfig


def _do_search(i: int):
    """Run search for asset i and write results into entries_state."""
    entries_state = st.session_state["entries_state"]
    e = entries_state[i]
    query = st.session_state[f"query_{i}"]
    e["query"] = query

    if not query.strip():
        return

    if query.strip().lower() == "cash":
        cash_used = any(
            j != i and entries_state[j]["ticker"] == "Cash"
            for j in range(len(entries_state))
        )
        if not cash_used:
            e["ticker"] = "Cash"
            e["company_name"] = "Cash"
            e["search_results"] = []
            e["searched"] = True
        else:
            e["search_results"] = []
            e["searched"] = True
            e["cash_duplicate"] = True
        return

    e["cash_duplicate"] = False
    direct_ticker, direct_name = search_ticker_direct(query)
    if direct_ticker:
        e["ticker"] = direct_ticker
        e["company_name"] = direct_name
        e["search_results"] = []
        e["searched"] = True
    else:
        results = search_ticker_query(query)
        e["search_results"] = results
        e["searched"] = True
        # If only one result, auto-select it
        if len(results) == 1:
            e["ticker"] = results[0]["symbol"]
            e["company_name"] = results[0].get("shortname", results[0]["symbol"])
            e["search_results"] = []


def render_portfolio_form():
    """
    Renders Step 1: mode selection + asset entry form.
    Writes to st.session_state['portfolio_config'] and advances step on submit.
    """
    st.header("Step 1: Portfolio Entry")

    mode = st.radio(
        "How would you like to describe your portfolio?",
        options=["1", "2"],
        format_func=lambda x: "By securities value (₪/$)" if x == "1" else "By % from total portfolio",
        key="mode_radio",
        horizontal=True,
    )

    num_assets = st.number_input(
        "How many total assets (including Cash)?",
        min_value=1, max_value=50,
        value=st.session_state.get("num_assets_input", 3),
        step=1, key="num_assets_input",
    )

    st.markdown("---")
    st.subheader("Asset Entry")
    st.caption("Type a name or ticker and press **Enter** — results appear automatically.")

    entries_state = st.session_state.setdefault("entries_state", [
        {"query": "", "ticker": "", "company_name": "", "val": 0.0,
         "search_results": [], "searched": False, "cash_duplicate": False}
        for _ in range(int(num_assets))
    ])

    n = int(num_assets)
    while len(entries_state) < n:
        entries_state.append({"query": "", "ticker": "", "company_name": "", "val": 0.0,
                               "search_results": [], "searched": False, "cash_duplicate": False})
    while len(entries_state) > n:
        entries_state.pop()

    for i in range(n):
        e = entries_state[i]
        st.markdown(f"**Asset {i + 1}**")

        st.text_input(
            f"Name / Ticker {i + 1}",
            value=e["query"],
            key=f"query_{i}",
            placeholder="e.g. Apple, AAPL, or type Cash",
            label_visibility="collapsed",
            on_change=_do_search,
            args=(i,),
        )

        # Cash duplicate warning
        if e.get("cash_duplicate"):
            st.error("Cash is already in the portfolio.")

        # Show search results as a selectbox when there are multiple matches
        if e.get("searched") and e["search_results"]:
            options = [f"{r['symbol']} — {r.get('shortname', r['symbol'])} ({r.get('exchDisp', '')})"
                       for r in e["search_results"]]
            options = [f"Use exact input: {e['query'].upper()}"] + options
            choice = st.selectbox(f"Select result for asset {i + 1}:", options, key=f"select_{i}")
            if choice.startswith("Use exact input:"):
                e["ticker"] = e["query"].strip().upper()
                e["company_name"] = e["ticker"]
            else:
                idx = options.index(choice) - 1
                r = e["search_results"][idx]
                e["ticker"] = r["symbol"]
                e["company_name"] = r.get("shortname", r["symbol"])

        # Confirmed ticker badge
        if e["ticker"]:
            st.caption(f"✅ Selected: **{e['ticker']}** ({e['company_name']})")

        val_label = f"Value for {e['company_name'] or 'asset'} ({'₪/$' if mode == '1' else '%'})"
        val = st.number_input(val_label, min_value=0.0, value=float(e["val"]),
                               step=0.01, key=f"val_{i}", format="%.2f")
        e["val"] = val
        st.markdown("---")

    if st.button("Confirm Portfolio & Fetch Data →", type="primary"):
        # Auto-resolve any remaining unresolved queries
        for e in entries_state:
            if not e["ticker"] and e["query"]:
                q = e["query"].strip()
                if q.lower() == "cash":
                    e["ticker"] = "Cash"
                    e["company_name"] = "Cash"
                else:
                    direct, dname = search_ticker_direct(q)
                    if direct:
                        e["ticker"] = direct
                        e["company_name"] = dname
                    else:
                        e["ticker"] = q.upper()
                        e["company_name"] = q.upper()

        incomplete = [i + 1 for i, e in enumerate(entries_state) if not e["ticker"] or e["val"] <= 0]
        if incomplete:
            st.error(f"Assets {incomplete} are missing a ticker or value > 0.")
            return

        assets = [
            AssetEntry(ticker=e["ticker"], company_name=e["company_name"], val=e["val"])
            for e in entries_state
        ]
        config = PortfolioConfig(entries=assets, mode=mode, rf_annual_yield=0.0)
        st.session_state["portfolio_config"] = config
        st.session_state["step"] = 2
        st.rerun()
