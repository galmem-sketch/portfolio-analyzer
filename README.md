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

## Deployment

Hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Every push to `main` auto-redeploys within ~60 seconds.

To update the app: open any `.py` file on GitHub, click the pencil icon, make your change, and commit — no terminal needed.
