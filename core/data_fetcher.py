import yfinance as yf
import pandas as pd
import numpy as np
import requests
import re
from bs4 import BeautifulSoup


def get_boi_interest_rate():
    """Scrapes the Bank of Israel website for the current interest rate. Returns float or None."""
    url = "https://www.boi.org.il/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup.find_all(string=re.compile(r'ריבית בנק ישראל')):
            parent = element.parent
            match = re.search(r'(\d+\.?\d*)%', parent.get_text())
            if not match:
                match = re.search(r'(\d+\.?\d*)%', parent.parent.get_text())
            if match:
                rate = float(match.group(1)) / 100
                if 0 < rate < 0.15:
                    return rate
    except Exception:
        pass
    return None


def search_ticker_direct(query: str):
    """
    Try query and query+'.TA' as direct ticker lookups.
    Returns (ticker_symbol, short_name) or (None, None).
    """
    original = query.strip().upper()
    attempts = [original]
    if not original.endswith('.TA'):
        attempts.append(original + '.TA')

    for attempt in attempts:
        try:
            t = yf.Ticker(attempt)
            info = t.info
            if not t.history(period="1d").empty and 'shortName' in info:
                return attempt, info['shortName']
        except Exception:
            pass
    return None, None


def search_ticker_query(query: str):
    """
    Run yfinance Search for query. Returns list of result dicts (filtered, prioritized).
    Each dict has keys: symbol, shortname, exchDisp.
    """
    original = query.strip().upper()
    try:
        s = yf.Search(original, max_results=10)
        results = s.quotes
    except Exception:
        return []

    otc_ids = {'OTC', 'OTCMKTS', 'PNK', 'PK', 'NMS', 'XOTC', 'PINK', 'OB', 'GREY'}
    filtered = [
        r for r in results
        if not any(oid in r.get('exchDisp', '').upper() or oid in r.get('market', '').upper()
                   for oid in otc_ids)
    ]

    priority_exchanges = {'TA', 'TLV', 'NYSE', 'NASDAQ', 'NMS', 'NYQ'}
    priority, other = [], []
    for r in filtered:
        if any(p in r.get('exchDisp', '').upper() for p in priority_exchanges):
            priority.append(r)
        else:
            other.append(r)
    return priority + other


def download_portfolio_data(tickers: list[str]):
    """
    Download max-period Adj Close for the given tickers.
    Returns (data_df, problematic_tickers, history_report).
    data_df columns = tickers, NaN where download failed.
    history_report: {ticker: years_of_data}
    """
    if not tickers:
        return pd.DataFrame(), [], {}

    raw = yf.download(tickers, period="max", auto_adjust=False, progress=False)
    data = pd.DataFrame(index=raw.index if not raw.empty else pd.to_datetime([]))

    for ticker in tickers:
        if len(tickers) > 1:
            if 'Adj Close' in raw and ticker in raw['Adj Close'].columns:
                data[ticker] = raw['Adj Close'][ticker]
            else:
                data[ticker] = np.nan
        else:
            if 'Adj Close' in raw.columns:
                data[ticker] = raw['Adj Close']
            else:
                data[ticker] = np.nan

    problematic = [t for t in tickers if data[t].dropna().empty]
    valid = [t for t in tickers if not data[t].dropna().empty]
    history_report = {t: len(data[t].dropna()) / 252 for t in valid}

    return data, problematic, history_report


def download_benchmark(ticker: str):
    """
    Download benchmark returns for the given ticker.
    Tries adding/removing '^' if the first attempt fails.
    Returns (actual_ticker, bench_returns_df) or raises ValueError.
    """
    for attempt in [ticker, (ticker[1:] if ticker.startswith('^') else '^' + ticker)]:
        test = yf.download(attempt, period="5d", progress=False)
        if not test.empty:
            raw = yf.download(attempt, period="max", auto_adjust=True, progress=False)['Close']
            returns = raw.pct_change().dropna()
            if hasattr(returns.index, 'tz_localize'):
                returns.index = returns.index.tz_localize(None)
            if isinstance(returns, pd.Series):
                returns = returns.to_frame(name=attempt)
            return attempt, returns

    raise ValueError(f"No price data found for '{ticker}'")
