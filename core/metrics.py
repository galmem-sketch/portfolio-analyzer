import pandas as pd
import numpy as np
from .portfolio import PortfolioConfig


def calculate_portfolio_metrics(config: PortfolioConfig, all_returns: pd.DataFrame):
    """
    Compute annualized mean, std, Sharpe, and the aligned calc_df.
    Returns dict with keys: port_mean, port_std, sharpe, c_years, calc_df, aligned_weights.
    On error, port_mean/port_std are np.nan.
    """
    weights = config.weights()
    rf = config.rf_annual_yield

    # Build calc_df: stock columns from all_returns, CASH_INTERNAL as constant
    calc_df = pd.DataFrame(index=all_returns.index)
    for ticker, w in weights.items():
        if ticker.upper() == 'CASH':
            calc_df['CASH_INTERNAL'] = rf / 252
        elif ticker in all_returns.columns:
            calc_df[ticker] = all_returns[ticker]

    # Align on common stock history
    stock_cols = [c for c in calc_df.columns if c != 'CASH_INTERNAL']
    if stock_cols:
        temp = calc_df[stock_cols].dropna()
        if 'CASH_INTERNAL' in calc_df.columns:
            cash_aligned = pd.Series(rf / 252, index=temp.index, name='CASH_INTERNAL')
            calc_df = pd.concat([temp, cash_aligned], axis=1)
        else:
            calc_df = temp
    elif 'CASH_INTERNAL' in calc_df.columns:
        calc_df = calc_df[['CASH_INTERNAL']].dropna()

    if calc_df.empty:
        return {
            'port_mean': np.nan, 'port_std': np.nan, 'sharpe': np.nan,
            'c_years': 0.0, 'calc_df': calc_df, 'aligned_weights': np.array([])
        }

    c_years = len(calc_df) / 252
    mu_annual = calc_df.mean() * 252
    cov_matrix = calc_df.cov() * 252

    # Build aligned_weights array matching calc_df column order
    aligned_w = []
    for col in calc_df.columns:
        if col == 'CASH_INTERNAL':
            aligned_w.append(weights.get('Cash', weights.get('CASH', 0)))
        else:
            aligned_w.append(weights.get(col, 0))
    aligned_w = np.array(aligned_w)

    if aligned_w.sum() == 0:
        return {
            'port_mean': np.nan, 'port_std': np.nan, 'sharpe': np.nan,
            'c_years': c_years, 'calc_df': calc_df, 'aligned_weights': aligned_w
        }

    aligned_w = aligned_w / aligned_w.sum()
    port_mean = float(np.dot(aligned_w, mu_annual))
    port_std = float(np.sqrt(aligned_w.T @ cov_matrix @ aligned_w))
    sharpe = (port_mean - rf) / port_std if port_std > 0 else np.nan

    return {
        'port_mean': port_mean,
        'port_std': port_std,
        'sharpe': sharpe,
        'c_years': c_years,
        'calc_df': calc_df,
        'aligned_weights': aligned_w,
    }


def align_benchmark(bench_returns: pd.DataFrame, window_index: pd.Index):
    """
    Align benchmark returns to the given window. Returns (b_mu, b_std) annualized.
    """
    aligned = bench_returns.reindex(window_index).dropna()
    if aligned.empty:
        return np.nan, np.nan
    b_mu = float(aligned.mean().iloc[0] * 252)
    b_std = float(aligned.std().iloc[0] * np.sqrt(252))
    return b_mu, b_std


def calculate_hypo_metrics(
    all_returns: pd.DataFrame,
    new_assets_data: list[dict],
    config: PortfolioConfig,
    total_sum: float,
):
    """
    Compute hypothetical portfolio metrics after adding new_assets_data.
    new_assets_data: list of {ticker, mode ('1'=%, '2'=cash), amt, history_df, company_name}
    Returns dict: hypo_mu, hypo_sig, h_years, hypo_df, w_new, final_total_val, combined_details
    """
    new_ret_map = {item['ticker']: item['history_df'].pct_change() for item in new_assets_data}
    hypo_df = pd.concat(
        [all_returns] + [ser.rename(tk) for tk, ser in new_ret_map.items()], axis=1
    ).dropna()
    h_years = len(hypo_df) / 252

    total_target_pct = sum(item['amt'] / 100 for item in new_assets_data if item['mode'] == '1')
    total_fixed_cash = sum(item['amt'] for item in new_assets_data if item['mode'] == '2')
    final_total_val = (total_sum + total_fixed_cash) / (1 - total_target_pct)

    weights = config.weights()
    w_new = np.zeros(len(hypo_df.columns))
    for idx, ticker in enumerate(hypo_df.columns):
        orig = weights.get(ticker)
        if orig is not None:
            w_new[idx] = (orig * total_sum) / final_total_val
        new = next((it for it in new_assets_data if it['ticker'] == ticker), None)
        if new is not None:
            w_new[idx] = (new['amt'] / 100) if new['mode'] == '1' else (new['amt'] / final_total_val)

    h_mu = hypo_df.mean() * 252
    h_cov = hypo_df.cov() * 252
    hypo_mu = float(h_mu.dot(w_new))
    hypo_sig = float(np.sqrt(w_new.T @ h_cov @ w_new))

    # Build combined portfolio details for the table
    orig_ticker_map = {}
    orig_tickers = set()
    for entry in config.entries:
        key = 'CASH_INTERNAL' if entry.ticker.upper() == 'CASH' else entry.ticker
        orig_ticker_map[key] = entry.company_name
        orig_tickers.add(key)

    new_ticker_map = {item['ticker']: item['company_name'] for item in new_assets_data}

    combined_details = []
    for i, ticker in enumerate(hypo_df.columns):
        is_new = ticker not in orig_tickers
        company = new_ticker_map.get(ticker, ticker) if is_new else orig_ticker_map.get(ticker, ticker)
        combined_details.append({
            'ticker': ticker,
            'weight': w_new[i],
            'company_name': company,
            'is_new': is_new,
        })

    # Append Cash rows for display (Cash excluded from hypo_df math — correct per MPT)
    for entry in config.entries:
        if entry.ticker.upper() == 'CASH':
            cash_weight = weights.get('Cash', weights.get('CASH', 0))
            cash_display_weight = (cash_weight * total_sum) / final_total_val
            combined_details.append({
                'ticker': 'Cash',
                'weight': cash_display_weight,
                'company_name': entry.company_name,
                'is_new': False,
            })

    return {
        'hypo_mu': hypo_mu,
        'hypo_sig': hypo_sig,
        'h_years': h_years,
        'hypo_df': hypo_df,
        'w_new': w_new,
        'final_total_val': final_total_val,
        'combined_details': combined_details,
    }
