"""
Build a self-contained HTML report for browser-based PDF export (File → Print → Save as PDF).
No server-side PDF library required.
"""
from __future__ import annotations
import io
import base64

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from utils.styles import TABLE_CSS
from ui.tables import render_portfolio_table, render_hypo_table
from ui.charts import plot_efficiency, plot_bell_curve


def _fig_to_data_uri(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{b64}"


def _metrics_block(label: str, rows: list[tuple[str, str]]) -> str:
    cells = ''.join(
        f'<div class="metric"><div class="metric-label">{k}</div>'
        f'<div class="metric-value">{v}</div></div>'
        for k, v in rows
    )
    return f'<div class="section-title">{label}</div><div class="metrics-row">{cells}</div>'


_HTML_CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: Arial, sans-serif; font-size: 11pt; color: #1a1a2e; margin: 0; padding: 24px 32px; }
h1   { font-size: 22pt; color: #009879; margin-bottom: 4px; }
h2   { font-size: 14pt; color: #009879; margin-top: 24px; margin-bottom: 6px;
       border-bottom: 2px solid #009879; padding-bottom: 4px; }
.subtitle { color: #666; margin-top: 0; font-size: 10pt; }
.section-title { font-size: 12pt; font-weight: bold; color: #333; margin: 16px 0 8px; }
.metrics-row { display: flex; gap: 16px; margin-bottom: 14px; }
.metric { flex: 1; background: #f4f9f7; border: 1px solid #c9e8df; border-radius: 6px; padding: 10px 14px; }
.metric-label { font-size: 9pt; color: #555; }
.metric-value { font-size: 16pt; font-weight: bold; color: #009879; margin-top: 2px; }
.chart-img { width: 100%; margin: 10px 0 20px; }
.page-break { page-break-before: always; }
@media print {
    .no-print { display: none !important; }
    body { padding: 0; }
}
"""


def build_report_html(
    config,
    metrics: dict,
    bench_ticker: str,
    b_mu_plot: float,
    b_std_plot: float,
    c_years_plot: float,
    years: float,
    hypo_result: dict | None,
) -> bytes:
    port_mean = metrics["port_mean"]
    port_std  = metrics["port_std"]
    sharpe    = metrics["sharpe"]
    rf        = config.rf_annual_yield

    hypo_mu  = hypo_result["hypo_mu"]  if hypo_result else None
    hypo_sig = hypo_result["hypo_sig"] if hypo_result else None

    # ── Charts ────────────────────────────────────────────────────────────────
    fig_eff = plot_efficiency(
        port_mean=port_mean, port_std=port_std,
        bench_ticker=bench_ticker, b_mu=b_mu_plot, b_std=b_std_plot,
        rf=rf, c_years=c_years_plot,
        hypo_mu=hypo_mu, hypo_sig=hypo_sig,
    )
    eff_uri = _fig_to_data_uri(fig_eff)
    plt.close(fig_eff)

    title_years = hypo_result["h_years"] if hypo_result else years
    fig_bell = plot_bell_curve(
        port_mean=port_mean, port_std=port_std,
        bench_ticker=bench_ticker, b_mu=b_mu_plot, b_std=b_std_plot,
        rf=rf, title_years=title_years,
        hypo_mu=hypo_mu, hypo_sig=hypo_sig,
    )
    bell_uri = _fig_to_data_uri(fig_bell)
    plt.close(fig_bell)

    # ── Tables ────────────────────────────────────────────────────────────────
    curr_table = render_portfolio_table(config.entries, config.mode).replace(TABLE_CSS, '')

    hypo_table_html = ''
    hypo_metrics_html = ''
    if hypo_result:
        hypo_table_html = render_hypo_table(
            hypo_result["combined_details"], config.mode, hypo_result["final_total_val"]
        ).replace(TABLE_CSS, '')
        hypo_sharpe = (hypo_mu - rf) / hypo_sig if hypo_sig and hypo_sig > 0 else float('nan')
        hypo_metrics_html = _metrics_block("Hypothetical Portfolio Metrics", [
            ("New Expected Yield (μ)", f"{hypo_mu:.2%}"),
            ("New Volatility (σ)", f"{hypo_sig:.2%}"),
            ("New Sharpe Ratio", f"{hypo_sharpe:.2f}" if not np.isnan(hypo_sharpe) else "N/A"),
        ])

    curr_metrics_html = _metrics_block("Current Portfolio Metrics", [
        ("Expected Annual Yield (μ)", f"{port_mean:.2%}" if not np.isnan(port_mean) else "N/A"),
        ("Annualized Volatility (σ)", f"{port_std:.2%}"  if not np.isnan(port_std)  else "N/A"),
        ("Sharpe Ratio",              f"{sharpe:.2f}"    if not np.isnan(sharpe)    else "N/A"),
    ])

    table_css_clean = TABLE_CSS.replace('<style>', '').replace('</style>', '')

    hypo_section = ''
    if hypo_result:
        hypo_section = f"""
<div class="section-title" style="margin-top:20px;">Hypothetical Portfolio Summary</div>
{hypo_table_html}
{hypo_metrics_html}
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Portfolio Analysis Report</title>
<style>
{_HTML_CSS}
{table_css_clean}
</style>
</head>
<body>

<div class="no-print" style="background:#009879;color:white;padding:12px 20px;margin:-24px -32px 24px;
     display:flex;align-items:center;justify-content:space-between;">
  <span style="font-size:14pt;font-weight:bold;">Portfolio Analysis Report</span>
  <button onclick="window.print()"
    style="background:white;color:#009879;border:none;padding:8px 20px;border-radius:4px;
           font-size:11pt;font-weight:bold;cursor:pointer;">
    ⬇ Save as PDF
  </button>
</div>

<h1>Portfolio Analysis Report</h1>
<p class="subtitle">Benchmark: {bench_ticker} &nbsp;·&nbsp; Analysis window: {c_years_plot:.1f} years</p>

<h2>Portfolio Efficiency Analysis</h2>
<img class="chart-img" src="{eff_uri}">

<h2>Annual Performance Projection</h2>
<img class="chart-img" src="{bell_uri}">

<div class="page-break"></div>

<h2>Full Report</h2>

<div class="section-title">Current Portfolio Summary</div>
{curr_table}
{curr_metrics_html}
{hypo_section}

</body>
</html>"""

    return html.encode('utf-8')
