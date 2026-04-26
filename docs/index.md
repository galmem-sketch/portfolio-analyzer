# Portfolio Analyzer

## What is Portfolio Analyzer?

**Portfolio Analyzer** is a smart, interactive tool for understanding your long-term investment portfolio. Enter your holdings, and get instant insights into risk, return, and efficiency — all backed by live market data.

Whether you're building wealth steadily or optimizing an existing portfolio, Portfolio Analyzer helps you:
- **See the bigger picture** — how your assets work together
- **Make informed decisions** — understand risk vs. return trade-offs for long-term growth
- **Plan for the future** — test portfolio adjustments before committing to changes
- **Compare fairly** — benchmark your performance against the market

---

## How It Works

Portfolio Analyzer is a **6-step wizard** that guides you through analysis:

### 1. **Portfolio Entry**
Enter your holdings by ticker symbol or company name. Add amounts in either ILS (Israeli Shekel) or USD — the app converts automatically using live Bank of Israel rates.

### 2. **Data Retrieval & Audit**
The app fetches 5 years of historical price data via Yahoo Finance. If any tickers have issues, you'll see exactly what went wrong and can fix or replace them.

### 3. **Benchmark Selection**
Choose a benchmark to compare against:
- **S&P 500** (US market)
- **Nasdaq-100** (Tech-heavy)
- **TA-125** (Israeli market)
- **Custom ticker** (your choice)

### 4. **Metrics Dashboard**
View your portfolio's key metrics:
- **Annualized Return (μ)** — expected yearly gain
- **Volatility (σ)** — how much your returns fluctuate
- **Sharpe Ratio** — return per unit of risk
- **Correlation Heatmap** — how your assets move together

### 5. **What-If Engine**
Plan strategic changes:
- Add a new asset to your portfolio
- Increase/decrease positions
- Swap out holdings
See how each change affects your portfolio's risk and return **instantly**.

### 6. **Charts & Report**
Visualize your portfolio:
- **Efficiency Plot** — scatter of risk vs. return
- **Bell Curve** — distribution of potential annual returns
- **Export as PDF** — download a professional report

---

## Key Features

✅ **Live Market Data** — Real-time prices via Yahoo Finance  
✅ **Multi-Currency** — Work in ILS or USD (auto-converted)  
✅ **Data Validation** — Flags bad tickers before analysis  
✅ **Long-Term Metrics** — Return, volatility, Sharpe, correlation  
✅ **Strategic Planning** — Test portfolio changes before implementing  
✅ **Beautiful Charts** — Risk/return scatter + return distribution  
✅ **PDF Reports** — Download a full analysis report  
✅ **No Sign-Up** — Just open and start analyzing  

---

## Who Is This For?

- **Long-Term Investors** — build and optimize wealth over years
- **Retirement Planners** — understand your asset allocation risk
- **Individual Portfolio Managers** — analyze and rebalance holdings
- **Financial Learners** — explore portfolio theory interactively
- **Anyone with investments** — get clarity and confidence in your holdings

---

## Get Started

### Online (No Installation)
Visit the live app hosted on [Streamlit Community Cloud](https://streamlit.io/cloud) — just open it in your browser.

### Local Setup
```bash
git clone https://github.com/galmem-sketch/portfolio-analyzer.git
cd portfolio-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| **Streamlit** | Interactive web UI |
| **yfinance** | Market data & prices |
| **pandas / numpy** | Data processing & analysis |
| **matplotlib / seaborn** | Charts & visualizations |
| **scipy** | Statistical calculations |
| **requests / BeautifulSoup** | Bank of Israel rate scraping |

---

## Learn More

- 📖 [Full README](https://github.com/galmem-sketch/portfolio-analyzer)
- 💻 [Source Code](https://github.com/galmem-sketch/portfolio-analyzer)
- 🐛 [Report an Issue](https://github.com/galmem-sketch/portfolio-analyzer/issues)

---

**Made with ❤️ for smart, long-term investing.**
