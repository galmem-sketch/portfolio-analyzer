import pandas as pd
from bs4 import BeautifulSoup
from utils.styles import TABLE_CSS


def _inject_row_classes(html: str, row_flags: list[tuple[int, str]]) -> str:
    """
    row_flags: list of (row_index_in_tbody, css_class) to apply.
    row_index is 0-based (excluding header row).
    """
    soup = BeautifulSoup(html, 'html.parser')
    all_trs = soup.find_all('tr')
    # all_trs[0] is header; data rows start at index 1
    for row_idx, css_class in row_flags:
        tr = all_trs[row_idx + 1]
        tr['class'] = tr.get('class', []) + [css_class]
    return str(soup)


def render_portfolio_table(entries, mode: str) -> str:
    """
    Build the portfolio summary HTML table.
    entries: list of AssetEntry (ticker, company_name, val).
    Returns full HTML string (CSS + table).
    """
    total = sum(e.val for e in entries)
    rows = []
    for e in entries:
        pct = (e.val / total) * 100
        display_ticker = '' if e.ticker == 'Cash' else e.ticker
        if mode == '1':
            rows.append([e.company_name, display_ticker, e.val, pct])
        else:
            rows.append([e.company_name, display_ticker, pct])

    total_pct = sum(r[-1] for r in rows)
    if mode == '1':
        rows.append(['Total', '', total, total_pct])
        cols = ['Security', 'Ticker', 'Value', '% of Total Portfolio']
        df = pd.DataFrame(rows, columns=cols)
        df['Value'] = df['Value'].apply(lambda x: f'${x:,.2f}' if isinstance(x, (int, float)) else x)
    else:
        rows.append(['Total', '', total_pct])
        cols = ['Security', 'Ticker', '% of Total Portfolio']
        df = pd.DataFrame(rows, columns=cols)

    df['% of Total Portfolio'] = df['% of Total Portfolio'].apply(
        lambda x: f'{x:.2f}%' if isinstance(x, (int, float)) else x
    )

    html = df.to_html(index=False, classes='styled-table')
    # Mark last row as summary
    flags = [(len(df) - 1, 'summary-row')]
    html = _inject_row_classes(html, flags)
    return TABLE_CSS + html


def render_hypo_table(combined_details: list[dict], mode: str, final_total_val: float) -> str:
    """
    Build the hypothetical portfolio summary HTML table.
    combined_details: list of {ticker, weight, company_name, is_new}.
    Returns full HTML string (CSS + table).
    """
    rows = []
    is_new_flags = []
    for d in combined_details:
        ticker = d['ticker']
        weight = d['weight']
        display_ticker = '' if ticker == 'CASH_INTERNAL' else ticker
        pct = weight * 100
        if mode == '1':
            val = weight * final_total_val
            rows.append([d['company_name'], display_ticker, val, pct, d['is_new']])
        else:
            rows.append([d['company_name'], display_ticker, pct, d['is_new']])

    total_pct = sum(r[-2] for r in rows)  # second-to-last is pct (before is_new)
    if mode == '1':
        total_val = sum(r[2] for r in rows)
        rows.append(['Total', '', total_val, total_pct, False])
        cols = ['Security', 'Ticker', 'Value', '% of Total Portfolio', 'is_new']
    else:
        rows.append(['Total', '', total_pct, False])
        cols = ['Security', 'Ticker', '% of Total Portfolio', 'is_new']

    df = pd.DataFrame(rows, columns=cols)
    is_new_col = df['is_new'].tolist()

    if mode == '1':
        df['Value'] = df['Value'].apply(lambda x: f'${x:,.2f}' if isinstance(x, (int, float)) else x)
    df['% of Total Portfolio'] = df['% of Total Portfolio'].apply(
        lambda x: f'{x:.2f}%' if isinstance(x, (int, float)) else x
    )

    html = df.drop(columns=['is_new']).to_html(index=False, classes='styled-table')

    flags = []
    for i, is_new in enumerate(is_new_col[:-1]):  # exclude total row
        if is_new:
            flags.append((i, 'new-asset-row'))
    flags.append((len(df) - 1, 'summary-row'))

    html = _inject_row_classes(html, flags)
    return TABLE_CSS + html
