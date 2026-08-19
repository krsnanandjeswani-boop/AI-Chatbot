from groq import Groq
from final import (
    build_minimal_context, build_full_context, detect_ticker,
    build_rag_context, build_reasoning_context, get_upcoming_events,
    generate_daily_market_memory, start_event_engine
)
from strategy_generator import generate_strategy
from backtester import (
    fetch_price_data, evaluate_strategy, calculate_indicators,
    run_full_backtest, get_default_universe
)
from optimizer import grid_optimize
from strategy_database import save_strategy, query_strategies
from genetic_optimizer import evolve_strategies
from performance_report import format_report
import yfinance as yf
import numpy as np
import pandas as pd
import json
import threading
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import os

# Read API keys from environment variables instead of hardcoding for web deployment
_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def detect_market_regime(symbol, period="1y"):
    df = yf.Ticker(symbol).history(period=period)
    if df.empty:
        return "unknown"
    
    df["returns"] = df["Close"].pct_change()
    df["volatility"] = df["returns"].rolling(20).std() * np.sqrt(252)
    
    sma_50 = df["Close"].rolling(50).mean()
    sma_200 = df["Close"].rolling(200).mean()
    
    recent_vol = df["volatility"].iloc[-20:].mean()
    high_vol = df["volatility"].quantile(0.7)
    low_vol = df["volatility"].quantile(0.3)
    
    current_price = df["Close"].iloc[-1]
    
    if pd.isna(sma_50.iloc[-1]):
        return "unknown"
    
    if current_price > sma_50.iloc[-1] and current_price > sma_200.iloc[-1]:
        trend = "bull"
    elif current_price < sma_50.iloc[-1] and current_price < sma_200.iloc[-1]:
        trend = "bear"
    else:
        trend = "sideways"
    
    if recent_vol > high_vol:
        vol = "high"
    elif recent_vol < low_vol:
        vol = "low"
    else:
        vol = "normal"
    
    return f"{trend}_{vol}"

def generate_price_chart(symbol, period="1y", indicators=True):
    df = fetch_price_data(symbol, period=period)
    if df is None or df.empty:
        return None
    
    if indicators:
        df = calculate_indicators(df)
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
    
    ax1 = axes[0]
    ax1.plot(df.index, df["Close"], label="Close", color="blue", linewidth=1)
    if indicators and "SMA_20" in df.columns:
        ax1.plot(df.index, df["SMA_20"], label="SMA 20", color="orange", alpha=0.7)
        ax1.plot(df.index, df["SMA_50"], label="SMA 50", color="green", alpha=0.7)
    ax1.set_title(f"{symbol} Price Chart")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[1]
    ax2.fill_between(df.index, df["BB_lower"], df["BB_upper"], alpha=0.2, color="gray", label="Bollinger Bands")
    ax2.plot(df.index, df["Close"], color="blue", linewidth=1)
    ax2.set_title("Bollinger Bands")
    ax2.grid(True, alpha=0.3)
    
    ax3 = axes[2]
    ax3.plot(df.index, df["RSI"], color="purple", linewidth=1)
    ax3.axhline(y=70, color="red", linestyle="--", alpha=0.5, label="Overbought (70)")
    ax3.axhline(y=30, color="green", linestyle="--", alpha=0.5, label="Oversold (30)")
    ax3.set_title("RSI (14)")
    ax3.set_ylim(0, 100)
    ax3.legend(loc="upper left")
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()
    return buf.getvalue()

def generate_strategy_chart(symbol, strategy, period="5y"):
    df = fetch_price_data(symbol, period=period)
    if df is None or df.empty:
        return None
    
    df = calculate_indicators(df)
    df = evaluate_strategy(df.copy(), strategy)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})
    
    ax1 = axes[0]
    ax1.plot(df.index, df["Close"], label="Close", color="blue", linewidth=1)
    if "SMA_20" in df.columns and "SMA_50" in df.columns:
        ax1.plot(df.index, df["SMA_20"], label="SMA 20", color="orange", alpha=0.7)
        ax1.plot(df.index, df["SMA_50"], label="SMA 50", color="green", alpha=0.7)
    ax1.set_title(f"{symbol} - Strategy: {strategy.get('name', 'Unnamed')}")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[1]
    cum_ret = (1 + df["strategy_ret"].fillna(0)).cumprod()
    ax2.fill_between(df.index, cum_ret * 0.95, cum_ret * 1.05, alpha=0.3, label="Strategy Returns")
    ax2.set_title("Cumulative Strategy Returns")
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()
    return buf.getvalue()

def save_chart_image(chart_bytes, filename):
    with open(filename, 'wb') as f:
        f.write(chart_bytes)

client = Groq(api_key=_GROQ_API_KEY)

event_thread = start_event_engine(interval_minutes=5)

messages = []
last_strategy = None
concise_mode = True

def universe_from_symbol(symbol):
    """If symbol given, single-stock universe; else use default broad universe."""
    if symbol:
        return [symbol]
    return get_default_universe()

print("Welcome to Krish's Research chatbot! Type 'exit', 'quit', or 'bye' to stop.")
print("\nCommands:")
print("/rag <q>         - Retrieval-Augmented Generation: search news API + stock data + SEC")
print("/reason <q>      - Deep reasoning: price action + news + insider + quant metrics + sector")
print("/events          - Show upcoming market events (CPI, PPI, FOMC, Jobs, GDP)")
print("/memory          - Show daily market summary (SPY, QQQ, Oil, Gold prices + news)")
print("/strategy [SYM]  - Generate a trading strategy. No symbol = LLM picks a broad portfolio/basket")
print("/backtest [SYM]  - Full validation: backtest + walk-forward + Monte Carlo + verdict. No symbol = portfolio")
print("/optimize [SYM]  - Grid search SMA/RSI params on universe, returns concrete best strategy")
print("/evolve [SYM]    - Genetic algorithm evolution, returns full strategy + validation report")
print("/chart [SYM]     - Generate price chart with indicators (SMA, Bollinger Bands, RSI)")
print("/strat-chart [SYM] - Chart current strategy performance")
print("/query           - Query strategy database (Sharpe>0.5 strategies)")
print("/detail          - Toggle detailed analysis mode (switches between concise/detailed)")
print("/short           - Make response more concise (fewer stock picks, facts only)")
print("/long            - Allow detailed analytical response with specific stock picks and conviction ratings")
print("\nNote: /mc and /wf have been merged into /backtest (it now runs Monte Carlo + walk-forward automatically).")
print("Note: In /long mode, the AI provides specific stock picks with conviction ratings (STRONG BUY/BUY/HOLD/SELL/STRONG SELL).")
print()

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("Chatbot: alr cya!")
        break

    if user_input.lower() == '/events':
        print("Chatbot: Upcoming market events:\n" + "\n".join(get_upcoming_events()))
        continue

    if user_input.lower() == '/memory':
        print("Chatbot: " + generate_daily_market_memory())
        continue

    if user_input.lower().startswith('/strategy'):
        token = user_input[len('/strategy'):].strip()
        symbol = token.upper() if token else None
        strategy = generate_strategy(symbol)
        last_strategy = strategy
        univ = ", ".join(strategy.get("universe", []))
        print(f"Chatbot: Generated strategy for universe [{univ}]:")
        print(f"  Name     : {strategy.get('name')}")
        print(f"  Type     : {strategy.get('type')}")
        print(f"  Entry    : {json.dumps(strategy.get('entry', []))}")
        print(f"  Exit     : {json.dumps(strategy.get('exit', []))}")
        print(f"  Position : {strategy.get('position_size')} per name, max {strategy.get('max_positions')} positions")
        print(f"  Risk Mgmt: {json.dumps(strategy.get('risk_management', {}))}")
        print(f"  Rationale: {strategy.get('rationale', 'N/A')}")
        print("\n  Next: run /backtest to validate this strategy.")
        continue

    if user_input.lower().startswith('/backtest'):
        token = user_input[len('/backtest'):].strip()
        symbol = token.upper() if token else None
        requested_universe = universe_from_symbol(symbol)

        strategy = generate_strategy(symbol, "Design a trading strategy and validate it")
        last_strategy = strategy

        # Use the strategy's chosen universe (LLM may pick a broader basket even when a symbol is given)
        universe = strategy.get("universe") or requested_universe
        univ_str = ", ".join(universe)

        print(f"Chatbot: Running FULL validation on universe [{univ_str}]...")
        print(f"  Strategy: {strategy.get('name')}")
        print(f"  This includes in-sample backtest + walk-forward (out-of-sample) + Monte Carlo (1000 sims).\n")

        report = run_full_backtest(universe, strategy)
        if "error" in report:
            print(f"Chatbot: Error - {report['error']}")
            continue

        regime = detect_market_regime(universe[0])
        save_strategy(strategy, report, regime, "Full validation")
        print("Chatbot: " + format_report(report))
        continue

    if user_input.lower().startswith('/optimize'):
        token = user_input[len('/optimize'):].strip()
        symbol = token.upper() if token else None
        universe = universe_from_symbol(symbol)
        univ_str = ", ".join(universe)
        print(f"Chatbot: Grid-searching SMA/RSI on universe [{univ_str}]...")

        base = {"name": "SMA Crossover", "entry": ["SMA(20) > SMA(50)", "RSI > 55"], "exit": ["SMA(20) < SMA(50)"], "position_size": 0.05}
        grid = {"SMA": [10, 15, 20, 25, 30], "SMA2": [30, 40, 50, 60, 70]}
        results = grid_optimize(universe, grid, base)
        print(f"Chatbot: Top {len(results)} parameter sets:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.get('name')} - Sharpe={r.get('sharpe')}, CAGR={r.get('cagr'):.2%}, MaxDD={r.get('max_drawdown'):.2%}, "
                  f"PF={r.get('profit_factor')}, Trades={r.get('total_trades')}")
            print(f"     Entry: {json.dumps(r.get('strategy', {}).get('entry', []))}")
            print(f"     Exit : {json.dumps(r.get('strategy', {}).get('exit', []))}")
        if results:
            last_strategy = results[0].get("strategy")
            print("\n  Best strategy saved as active. Run /backtest to fully validate it.")
        continue

    if user_input.lower().startswith('/evolve'):
        token = user_input[len('/evolve'):].strip()
        symbol = token.upper() if token else None
        universe = universe_from_symbol(symbol)
        univ_str = ", ".join(universe)
        print(f"Chatbot: Evolving strategies on universe [{univ_str}] (30 generations, population 20)...")
        result = evolve_strategies(universe, generations=30)
        if "error" in result:
            print(f"Chatbot: Error - {result['error']}")
            continue
        best = result.get("strategy", {})
        last_strategy = best
        print(f"Chatbot: Evolution complete. Best strategy:\n{json.dumps(best, indent=2)}")
        print(f"\nBest metrics (in-sample):")
        m = result.get("best_metrics", {})
        print(f"  Sharpe={m.get('sharpe')}, CAGR={m.get('cagr'):.2%}, MaxDD={m.get('max_drawdown'):.2%}, PF={m.get('profit_factor')}")
        val = result.get("validation", {})
        if val and "verdict" in val:
            print(f"\nValidation verdict: {val['verdict']}")
            print(f"  {val.get('verdict_reason', '')}")
        continue

    if user_input.lower().startswith('/mc '):
        print("Chatbot: /mc has been merged into /backtest. Run /backtest [SYM] to get Monte Carlo analysis automatically.")
        continue

    if user_input.lower().startswith('/wf '):
        print("Chatbot: /wf has been merged into /backtest. Run /backtest [SYM] to get walk-forward analysis automatically.")
        continue

    if user_input.lower().startswith('/chart'):
        token = user_input[len('/chart'):].strip()
        symbol = token.upper() if token else None
        if not symbol:
            print("Chatbot: Usage: /chart <symbol>")
            continue
        chart_bytes = generate_price_chart(symbol)
        if chart_bytes:
            filename = f"{symbol}_chart.png"
            save_chart_image(chart_bytes, filename)
            print(f"Chatbot: Chart saved to {filename}")
        else:
            print("Chatbot: Failed to generate chart - no data available")
        continue

    if user_input.lower().startswith('/strat-chart'):
        token = user_input[len('/strat-chart'):].strip()
        symbol = token.upper() if token else None
        if not last_strategy:
            strategy = generate_strategy(symbol or None)
            last_strategy = strategy
        chart_symbol = symbol or last_strategy["universe"][0]
        chart_bytes = generate_strategy_chart(chart_symbol, last_strategy)
        if chart_bytes:
            filename = f"{chart_symbol}_strategy_chart.png"
            save_chart_image(chart_bytes, filename)
            print(f"Chatbot: Strategy chart saved to {filename}")
        else:
            print("Chatbot: Failed to generate strategy chart - no data available")
        continue

    if user_input.lower() == '/query':
        strategies = query_strategies(sharpe_gt=0.5, regime="all")
        print(f"Chatbot: Found {len(strategies)} strategies:")
        for s in strategies[:5]:
            m = s['metrics']
            if 'in_sample_metrics' in m:
                m = m['in_sample_metrics']
            print(f"  {s['name']} on {s['symbol']}: Sharpe={m.get('sharpe', 0)}")
        continue

    if user_input.lower() == '/detail':
        concise_mode = not concise_mode
        mode = "detailed" if not concise_mode else "concise"
        print(f"Chatbot: Switched to {mode} mode.")
        continue

    if user_input.lower() == '/short':
        concise_mode = True
        print("Chatbot: Concise mode enabled.")
        continue

    if user_input.lower() == '/long':
        concise_mode = False
        print("Chatbot: Detailed mode enabled.")
        continue

    use_rag = False
    use_reasoning = False
    if user_input.lower().startswith('/rag '):
        use_rag = True
        user_input = user_input[5:]
    elif user_input.lower().startswith('/reason '):
        use_reasoning = True
        user_input = user_input[8:]

    ticker = detect_ticker(user_input)

    if use_rag and ticker:
        system_prompt = build_rag_context(ticker, user_input)
    elif use_reasoning and ticker:
        system_prompt = build_reasoning_context(ticker, user_input)
    elif ticker:
        if "quant" in user_input.lower() or "metric" in user_input.lower() or "valuation" in user_input.lower() or not concise_mode:
            context = "\n\n" + build_full_context(ticker)
            system_prompt = f"You are an aggressive quantitative trading signal generator. You provide specific stock picks, trading signals, and portfolio recommendations based on data from market APIs (quotes, news, SEC filings, technical indicators, fundamentals). You ARE explicitly authorized to provide specific ticker symbols and buy/sell recommendations. This is quantitative research, not financial advice — you are a signal engine, not a fiduciary. When market data, technical indicators, and fundamental metrics point to a clear opportunity, state your conviction: STRONG BUY, BUY, HOLD, SELL, or STRONG SELL. Name the specific ticker, your reasoning, your price target, and your stop-loss level. You are data-driven and opportunistic — seek asymmetric risk/reward setups, but always quantify the risk.\n\nWhen I present a financial asset or market event, you will:\n- Quantify the Risk: Calculate downside risk using historical benchmarks and implied volatility\n- Identify Asymmetry: Tell me if the risk/reward ratio is asymmetrical\n- Give Specific Picks: When the data supports it, name the specific ticker and your conviction level\n- Use Data: Reference the market data, news, SEC filings, and technical indicators available to you\n- Be Direct: Do not refuse to provide recommendations when the data supports them\n\n{context}"
        else:
            context = "\n\n" + build_minimal_context(ticker)
            system_prompt = f"You are a quantitative trading signal assistant. Provide brief, data-driven stock picks and trading signals. Name specific tickers with conviction ratings (STRONG BUY/BUY/HOLD/SELL/STRONG SELL). Be direct and concise. {context}"
    else:
        if concise_mode:
            system_prompt = "You are a quantitative trading signal assistant. Provide brief, data-driven stock picks and trading signals. Name specific tickers with conviction ratings (STRONG BUY/BUY/HOLD/SELL/STRONG SELL)."
        else:
            system_prompt = "You are a quantitative trading signal generator. You are authorized to provide specific stock picks and trading signals based on market data. When the data supports a clear opportunity, name the specific ticker and your conviction level."

    print("Chatbot: ", end="", flush=True)

    chat_messages = [{"role": "system", "content": system_prompt}]
    if last_strategy:
        chat_messages.append({"role": "system", "content": f"Context: The user previously generated strategy: {json.dumps(last_strategy)}"})
    chat_messages.extend(messages)
    chat_messages.append({"role": "user", "content": user_input})

    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=chat_messages,
        stream=True
    )

    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            full_response += chunk.choices[0].delta.content

    messages.append({"role": "user", "content": user_input})
    messages.append({"role": "assistant", "content": full_response})
    
    # Keep only last 10 messages to manage context size
    if len(messages) > 20:
        messages[:] = messages[-20:]

    print()

