# Portfolio Analyzer

A personal investment portfolio analysis tool built with Streamlit.

Enter your holdings, pull live market data, and get a full picture of your portfolio's risk, return, and efficiency — compared against a benchmark of your choice.

## Features

- **Portfolio entry** — input stocks by ticker or name, with amounts in ILS or USD
- **Live data** — prices fetched automatically via Yahoo Finance
- **Data audit** — flags tickers with insufficient history, lets you replace or remove them
- **Benchmark comparison** — compare against S&P 500, Nasdaq, or any custom ticker
- **Metrics dashboard** — annualized return (μ), volatility (σ), Sharpe ratio, correlation heatmap
- **What-If engine** — simulate adding or swapping assets and see the impact instantly
- **Charts** — efficiency plot (risk/return scatter) and bell curve (annual return distribution)
- **Report export** — download a full HTML report, printable as PDF

## How to Use

The app is a 6-step wizard:

1. **Portfolio Entry** — enter your holdings
2. **Data Retrieval & Audit** — review data quality, fix any bad tickers
3. **Benchmark Selection** — pick what to compare against
4. **Metrics Dashboard** — view return, volatility, Sharpe, and correlations
5. **What-If Engine** — experiment with hypothetical changes
6. **Charts & Report** — view final charts and download the report

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Tech Stack

| Library | Purpose |
|---------|---------|
| Streamlit | UI framework |
| yfinance | Market data |
| pandas / numpy | Data processing |
| matplotlib / seaborn | Charts |
| scipy | Statistical distributions |
| requests / beautifulsoup4 | Bank of Israel rate scraping |

## Project Structure

```
portfolio-analyzer/
├── app.py                        # Main entry point — page config, sidebar nav, step dispatcher
│
├── core/                         # Business logic (no UI)
│   ├── portfolio.py              # Data classes: AssetEntry, PortfolioConfig
│   ├── data_fetcher.py           # Yahoo Finance downloads, ticker search, BOI rate scraping
│   ├── metrics.py                # Portfolio & hypothetical metrics (μ, σ, Sharpe, weights)
│   └── benchmark.py             # Benchmark preset definitions (SPY, TA-125, etc.)
│
├── ui/                           # Streamlit UI components (one per wizard step)
│   ├── portfolio_form.py         # Step 1 — ticker search and holdings entry
│   ├── benchmark_selector.py     # Step 3 — benchmark picker (preset or custom)
│   ├── what_if.py                # Step 5 — hypothetical portfolio simulator
│   ├── charts.py                 # Step 6 — efficiency plot and bell curve charts
│   ├── tables.py                 # Styled HTML tables for portfolio and hypothetical summaries
│   └── report_pdf.py             # Step 6 — builds self-contained HTML report for PDF export
│
├── utils/
│   ├── __init__.py               # to_float() helper (handles pandas scalars safely)
│   └── styles.py                 # Shared CSS for styled tables
│
├── .github/workflows/
│   └── ci.yml                    # CI — installs deps and syntax-checks all .py files on push
│
├── requirements.txt              # Python dependencies
└── .gitignore                    # Excludes .venv, __pycache__, secrets.toml
```

## Deployment

Hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Every push to `main` auto-redeploys within ~60 seconds.

To update the app: open any `.py` file on GitHub, click the pencil icon, make your change, and commit — no terminal needed.
