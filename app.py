import streamlit as st

st.set_page_config(
    page_title="AI Trading Research Assistant",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
# :robot_face: AI Trading Research Assistant

A portfolio-grade quantitative research platform powered by LLM-driven strategy generation,
backtesting, optimization, and genetic evolution.

---

## :sparkles: What It Does

This AI combines a **Llama-3.3-70B LLM** (via Groq) with real-time market data from:
- :chart_with_upwards_trend: **Yahoo Finance** — price history, dividends, splits
- :newspaper: **Finnhub** — real-time quotes, company news
- :bank: **Alpha Vantage** — company overviews, fundamentals
- :mag_right: **SEC EDGAR** — 10-K / 10-Q filings
- :globe_with_meridians: **NewsAPI** — market-wide headlines

---

## :gear: Core Capabilities

| Capability | Description | Status |
|---|---|---|
| **Strategy Generator** | LLM designs custom trading strategies across single stocks, baskets, or sector rotation | :white_check_mark: |
| **Backtester** | Full validation pipeline: in-sample backtest + walk-forward OOS + Monte Carlo (1000 sims) | :white_check_mark: |
| **Grid Optimizer** | Systematic parameter search over SMA / EMA / RSI configurations | :white_check_mark: |
| **Genetic Evolution** | Evolutionary algorithm (30 generations, population 20) to discover robust strategies | :white_check_mark: |
| **Strategy Database** | SQLite-backed storage and querying of tested strategies by Sharpe ratio | :white_check_mark: |
| **Price Charts** | Interactive charts with SMA, Bollinger Bands, RSI, MACD indicators | :white_check_mark: |
| **Market Memory** | Daily market summary (SPY, QQQ, Oil, Gold, BTC) + top news | :white_check_mark: |
| **LLM Chat** | Direct Q&A with the AI research assistant | :white_check_mark: |

---

## :clipboard: How It Works

1. **Generate** — The LLM designs a strategy (entry/exit rules, universe, risk management) based on your prompt and market data context.
2. **Backtest** — The strategy is validated across multiple dimensions: in-sample performance, walk-forward out-of-sample testing, and Monte Carlo risk simulation.
3. **Verdict** — Each strategy receives a verdict: `CONFIRMED`, `CONDITIONAL`, or `REJECTED` based on Sharpe ratio, drawdown, and walk-forward consistency.
4. **Optimize / Evolve** — Refine parameters via grid search or genetic algorithm to maximize robustness.
5. **Save & Query** — Persisted strategies can be compared and queried from the database.

---

## :warning: Risk Disclosure

> This platform is for **research and educational purposes only**. It is not financial advice.
> Past performance is not indicative of future results. Cryptocurrency and stock trading
> carry substantial risk of loss. Always perform your own due diligence and consider
> consulting a qualified financial advisor before making any investment decisions.

---

### :arrow_left_click: Use the sidebar to navigate between tools.
""")
