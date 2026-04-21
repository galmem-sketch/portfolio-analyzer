import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.patheffects as pe
import scipy.stats as stats
from utils import to_float


def plot_efficiency(
    port_mean, port_std, bench_ticker, b_mu, b_std, rf,
    c_years, hypo_mu=None, hypo_sig=None
):
    """
    Returns a matplotlib Figure for the Capital Allocation Line / efficiency plot.
    If hypo_mu/hypo_sig are provided, shows both current and new portfolio points.
    """
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='white')
    ax.set_axisbelow(True)

    orig_std = to_float(port_std)
    orig_mu = to_float(port_mean)
    b_mu_f = to_float(b_mu)
    b_std_f = to_float(b_std)

    if hypo_mu is not None:
        c_mean = to_float(hypo_mu)
        c_std = to_float(hypo_sig)
    else:
        c_mean = orig_mu
        c_std = orig_std

    x_max = max(b_std_f, c_std, orig_std, 0.15) * 1.2
    extra_y = orig_mu if hypo_mu is not None else 0.0
    y_max = max(b_mu_f, c_mean, extra_y, rf) * 1.2

    x_cal = np.linspace(0, x_max, 100)
    safe_b_std = max(b_std_f, 0.0001)
    slope = (b_mu_f - rf) / safe_b_std
    ax.plot(x_cal, rf + slope * x_cal, color='#e74c3c', lw=2, label=f'CAL ({bench_ticker})', alpha=0.8)

    ax.scatter(0, rf, color='#7f8c8d', s=250, label='CASH (Rf)', zorder=6)
    ax.scatter(b_std_f, b_mu_f, color='#2980b9', s=250, label=f'100% {bench_ticker}', zorder=5)

    if hypo_mu is not None:
        ax.scatter(orig_std, orig_mu, color='#e67e22', s=600, marker='*', label='Current Portfolio', zorder=10)
        ax.scatter(c_std, c_mean, color='#8e44ad', s=600, marker='*', label='New Portfolio', zorder=10)
    else:
        ax.scatter(c_std, c_mean, color='#e67e22', s=700, marker='*', label='My Portfolio', zorder=10)

    ax.set_xlim(left=0, right=x_max)
    ax.set_ylim(bottom=0, top=y_max)
    ax.set_title(f"Efficiency Analysis ({c_years:.1f} Yrs Shared Period)", fontsize=15, fontweight='bold', pad=20)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(alpha=0.2)

    plt.tight_layout()
    return fig


def plot_bell_curve(
    port_mean, port_std, bench_ticker, b_mu, b_std, rf,
    title_years, hypo_mu=None, hypo_sig=None
):
    """
    Returns a matplotlib Figure for the normal distribution / bell curve plot.
    """
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='#FDFDFD')

    COL_CURR = '#457b9d'
    COL_HYPO = '#e76f51'
    ALPHA_FILL = 0.12

    pm = to_float(port_mean)
    ps = to_float(port_std)
    b_mu_f = to_float(b_mu)
    b_std_f = to_float(b_std)

    all_mu = [pm]
    all_sig = [ps]
    if hypo_mu is not None:
        all_mu.append(to_float(hypo_mu))
        all_sig.append(to_float(hypo_sig))

    sigma_mult = 2.8
    x_min = min(m - sigma_mult * s for m, s in zip(all_mu, all_sig))
    x_max = max(m + sigma_mult * s for m, s in zip(all_mu, all_sig))
    x = np.linspace(x_min, x_max, 1000)

    text_style = dict(fontweight='bold', ha='center', fontsize=10,
                      bbox=dict(facecolor='white', alpha=0.9, edgecolor='none', pad=1))

    y_curr = stats.norm.pdf(x, pm, ps)
    ax.plot(x, y_curr, color=COL_CURR, lw=3.5, label='Current Portfolio', zorder=3,
            path_effects=[pe.Stroke(linewidth=6, foreground='white'), pe.Normal()])
    ax.fill_between(x, y_curr, color=COL_CURR, alpha=ALPHA_FILL)
    ax.text(pm, max(y_curr) * 1.05, f'{pm:.1%}', color=COL_CURR, **text_style)

    if hypo_mu is not None:
        hm = to_float(hypo_mu)
        hs = to_float(hypo_sig)
        y_hypo = stats.norm.pdf(x, hm, hs)
        ax.plot(x, y_hypo, color=COL_HYPO, lw=3.5, label='New Portfolio', zorder=4,
                path_effects=[pe.Stroke(linewidth=6, foreground='white'), pe.Normal()])
        ax.fill_between(x, y_hypo, color=COL_HYPO, alpha=ALPHA_FILL)
        ax.text(hm, max(y_hypo) * 0.90, f'{hm:.1%}', color=COL_HYPO, **text_style)

    # Stat boxes
    box_props = dict(facecolor='white', alpha=0.7, edgecolor='white',
                     boxstyle='round,pad=1.2', linewidth=0.5)
    b_sharpe = (b_mu_f - rf) / b_std_f if b_std_f > 0 else 0
    sharpe_curr = (pm - rf) / ps if ps > 0 else 0
    p_loss_curr = stats.norm.cdf(0, pm, ps)

    bench_label = bench_ticker[:6] if len(bench_ticker) > 6 else bench_ticker
    ax.text(0.02, 0.95,
            f"  BENCHMARK ({bench_label})\n  Sharpe: {b_sharpe:>8.2f}",
            transform=ax.transAxes, va='top', fontsize=11, fontfamily='monospace',
            color='#2c3e50', bbox=box_props)

    ax.text(0.02, 0.82,
            f"  CURRENT PORTFOLIO\n"
            f"  Exp. Yield:    {pm:>8.2%}\n"
            f"  Volatility:    {ps:>8.2%}\n"
            f"  Sharpe Ratio:  {sharpe_curr:>8.2f}\n"
            f"  Prob. of Loss: {p_loss_curr:>8.1%}",
            transform=ax.transAxes, va='top', fontsize=11, fontfamily='monospace',
            color=COL_CURR, bbox=box_props)

    if hypo_mu is not None:
        hm = to_float(hypo_mu)
        hs = to_float(hypo_sig)
        sharpe_hypo = (hm - rf) / hs if hs > 0 else 0
        p_loss_hypo = stats.norm.cdf(0, hm, hs)
        ax.text(0.02, 0.63,
                f"  NEW PORTFOLIO\n"
                f"  Exp. Yield:    {hm:>8.2%}\n"
                f"  Volatility:    {hs:>8.2%}\n"
                f"  Sharpe Ratio:  {sharpe_hypo:>8.2f}\n"
                f"  Prob. of Loss: {p_loss_hypo:>8.1%}",
                transform=ax.transAxes, va='top', fontsize=11, fontfamily='monospace',
                color=COL_HYPO, bbox=box_props)

    plt.title(f"Annual Portfolio Performance Projection\n(Based on {title_years:.1f}-Year Historical Data)",
              fontsize=16, fontweight='bold', pad=40, color='#1a2b3c')
    ax.set_xlabel("Annual Total Return", fontsize=12, labelpad=10, fontweight='bold')
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(axis='x', linestyle='--', alpha=0.3, color='gray')
    ax.legend(frameon=False, loc='upper right', fontsize=11)

    plt.tight_layout()
    return fig
