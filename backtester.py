import re
import time
import yfinance as yf
import pandas as pd
import numpy as np

_price_cache = {}

def fetch_price_data(symbol, period="5y", interval="1d"):
    key = (symbol, period, interval)
    now = time.time()
    if key in _price_cache and now - _price_cache[key]["ts"] < 1800:
        return _price_cache[key]["data"]
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval)
    if hist.empty:
        return None
    _price_cache[key] = {"data": hist, "ts": now}
    return hist

# Supported condition patterns (uppercased, spaces stripped before matching)
SUPPORTED_CONDITION_PATTERNS = [
    r"SMA\(\d+\)>SMA\(\d+\)",
    r"SMA\(\d+\)<SMA\(\d+\)",
    r"CLOSE>SMA\(\d+\)",
    r"CLOSE<SMA\(\d+\)",
    r"EMA\(\d+\)>EMA\(\d+\)",
    r"EMA\(\d+\)<EMA\(\d+\)",
    r"RSI>\d+",
    r"RSI<\d+",
    r"RSI\(\d+\)>\d+",
    r"RSI\(\d+\)<\d+",
    r"MACD>MACD_SIGNAL",
    r"MACD<MACD_SIGNAL",
    r"CLOSE>BB_UPPER",
    r"CLOSE<BB_LOWER",
    r"VOLUME>VOLUME_SMA\(\d+\)",
]

DEFAULT_UNIVERSE = ["SPY", "QQQ", "IWM", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM", "XOM"]


def get_default_universe():
    return list(DEFAULT_UNIVERSE)


def calculate_indicators(df):
    df = df.copy()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()
    df["SMA_200"] = df["Close"].rolling(200).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    exp1 = df["Close"].ewm(span=12).mean()
    exp2 = df["Close"].ewm(span=26).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_signal"] = df["MACD"].ewm(span=9).mean()

    df["BB_middle"] = df["Close"].rolling(20).mean()
    df["BB_std"] = df["Close"].rolling(20).std()
    df["BB_upper"] = df["BB_middle"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_middle"] - 2 * df["BB_std"]

    df["Volume_SMA_20"] = df["Volume"].rolling(20).mean()

    return df


def evaluate_condition(df, cond):
    """Evaluate a single entry/exit condition string against a prepared df."""
    c = str(cond).strip()

    # SMA(n1) > SMA(n2) or SMA(n1) < SMA(n2)
    m = re.search(r"SMA\((\d+)\)\s*([<>])\s*SMA\((\d+)\)", c)
    if m:
        n1, op, n2 = int(m.group(1)), m.group(2), int(m.group(3))
        col1, col2 = f"SMA_{n1}", f"SMA_{n2}"
        if col1 not in df.columns:
            df[col1] = df["Close"].rolling(n1).mean()
        if col2 not in df.columns:
            df[col2] = df["Close"].rolling(n2).mean()
        s1, s2 = df[col1], df[col2]
        return (s1 > s2) if op == ">" else (s1 < s2)

    # Close > SMA(n) or Close < SMA(n)
    m = re.search(r"Close\s*([<>])\s*SMA\((\d+)\)", c)
    if m:
        op, n = m.group(1), int(m.group(2))
        col = f"SMA_{n}"
        if col not in df.columns:
            df[col] = df["Close"].rolling(n).mean()
        return (df["Close"] > df[col]) if op == ">" else (df["Close"] < df[col])

    # EMA(n1) > EMA(n2) or EMA(n1) < EMA(n2)
    m = re.search(r"EMA\((\d+)\)\s*([<>])\s*EMA\((\d+)\)", c)
    if m:
        n1, op, n2 = int(m.group(1)), m.group(2), int(m.group(3))
        col1, col2 = f"EMA_{n1}", f"EMA_{n2}"
        if col1 not in df.columns:
            df[col1] = df["Close"].ewm(span=n1, adjust=False).mean()
        if col2 not in df.columns:
            df[col2] = df["Close"].ewm(span=n2, adjust=False).mean()
        s1, s2 = df[col1], df[col2]
        return (s1 > s2) if op == ">" else (s1 < s2)

    # RSI > x / RSI < x  / RSI(n) > x / RSI(n) < x
    m = re.search(r"RSI(?:\((\d+)\))?\s*([<>])\s*(\d+)", c)
    if m:
        n = int(m.group(1)) if m.group(1) else 14
        op, val = m.group(2), int(m.group(3))
        col = f"RSI"
        if f"RSI_{n}" in df.columns:
            col = f"RSI_{n}"
        elif f"RSI_{n}" not in df.columns:
            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(n).mean()
            avg_loss = loss.rolling(n).mean()
            rs_series = avg_gain / avg_loss
            df[f"RSI_{n}"] = 100 - (100 / (1 + rs_series))
            col = f"RSI_{n}"
        rsi = df[col]
        return (rsi > val) if op == ">" else (rsi < val)

    # MACD > MACD_signal / MACD < MACD_signal
    m = re.search(r"MACD\s*([<>])\s*MACD_signal", c)
    if m:
        op = m.group(1)
        if "MACD" not in df.columns:
            exp1 = df["Close"].ewm(span=12).mean()
            exp2 = df["Close"].ewm(span=26).mean()
            df["MACD"] = exp1 - exp2
            df["MACD_signal"] = df["MACD"].ewm(span=9).mean()
        return (df["MACD"] > df["MACD_signal"]) if op == ">" else (df["MACD"] < df["MACD_signal"])

    # Close > BB_upper / Close < BB_lower
    m = re.search(r"Close\s*([<>])\s*BB_(upper|lower)", c)
    if m:
        op, band = m.group(1), m.group(2)
        if "BB_upper" not in df.columns:
            df["BB_middle"] = df["Close"].rolling(20).mean()
            df["BB_std"] = df["Close"].rolling(20).std()
            df["BB_upper"] = df["BB_middle"] + 2 * df["BB_std"]
            df["BB_lower"] = df["BB_middle"] - 2 * df["BB_std"]
        if band == "upper":
            return (df["Close"] > df["BB_upper"]) if op == ">" else (df["Close"] < df["BB_upper"])
        else:
            return (df["Close"] > df["BB_lower"]) if op == ">" else (df["Close"] < df["BB_lower"])

    # Volume > Volume_SMA(n)
    m = re.search(r"Volume\s*>\s*Volume_SMA\((\d+)\)", c)
    if m:
        n = int(m.group(1))
        col = f"Volume_SMA_{n}"
        if col not in df.columns:
            df[col] = df["Volume"].rolling(n).mean()
        return df["Volume"] > df[col]

    return None


def evaluate_strategy(df, strategy, inplace=False):
    """Evaluate a strategy on a single-symbol df. Returns df with position + strategy_ret."""
    if not inplace:
        df = df.copy()
    df = calculate_indicators(df)

    entry_signal = pd.Series(True, index=df.index)
    for cond in strategy.get("entry", []):
        signal = evaluate_condition(df, cond)
        if signal is not None:
            entry_signal &= signal.fillna(False)

    exit_signal = pd.Series(False, index=df.index)
    for cond in strategy.get("exit", []):
        signal = evaluate_condition(df, cond)
        if signal is not None:
            exit_signal |= signal.fillna(False)

    df["position"] = 0
    in_pos = False
    for i in range(len(df)):
        if in_pos:
            if exit_signal.iloc[i]:
                in_pos = False
        else:
            if entry_signal.iloc[i]:
                in_pos = True
        df.loc[df.index[i], "position"] = int(in_pos)

    df["returns"] = df["Close"].pct_change()
    df["strategy_ret"] = df["returns"] * df["position"].shift(1).fillna(0)
    return df


def compute_metrics(df):
    strat_ret = df["strategy_ret"].dropna()
    if len(strat_ret) == 0:
        return {"error": "No trades generated"}

    total_ret = (1 + strat_ret).prod() - 1
    years = len(strat_ret) / 252
    cagr = (1 + total_ret) ** (1 / years) - 1 if years > 0 else 0
    sharpe = strat_ret.mean() / strat_ret.std() * np.sqrt(252) if strat_ret.std() > 0 else 0
    downside = strat_ret[strat_ret < 0]
    sortino = strat_ret.mean() / downside.std() * np.sqrt(252) if len(downside) > 0 and downside.std() > 0 else 0

    cum = (1 + strat_ret).cumprod()
    max_dd = (cum - cum.cummax()) / cum.cummax()
    max_drawdown = max_dd.min()

    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0

    wins = strat_ret[strat_ret > 0]
    losses = strat_ret[strat_ret < 0]
    profit_factor = wins.sum() / abs(losses.sum()) if len(losses) > 0 else float("inf")

    position = df["position"]
    trades = position.diff().abs().sum() / 2

    return {
        "cagr": round(cagr, 4),
        "sharpe": round(sharpe, 4),
        "sortino": round(sortino, 4),
        "max_drawdown": round(max_drawdown, 4),
        "calmar": round(calmar, 4),
        "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else 999.9,
        "win_rate": round(len(wins) / len(strat_ret), 4) if len(strat_ret) > 0 else 0,
        "total_trades": int(trades),
        "total_return": round(total_ret, 4)
    }


def backtest_strategy(symbol, strategy, period="5y"):
    df = fetch_price_data(symbol, period=period)
    if df is None or df.empty:
        return {"error": f"No data for {symbol}"}

    df = evaluate_strategy(df, strategy)
    metrics = compute_metrics(df)
    metrics["symbol"] = symbol
    metrics["strategy_name"] = strategy.get("name", "Unnamed")
    return metrics


def _load_portfolio_prices(universe, period="5y"):
    prices = {}
    for sym in universe:
        df = fetch_price_data(sym, period=period)
        if df is None or df.empty:
            continue
        prices[sym] = df["Close"]
    if not prices:
        return None
    frame = pd.DataFrame(prices).dropna()
    return frame


def backtest_portfolio(universe, strategy, period="5y"):
    """Equal-weight, rebalanced-daily portfolio backtest across the universe."""
    frame = _load_portfolio_prices(universe, period=period)
    if frame is None or frame.empty:
        return {"error": "No data for universe"}

    rets = frame.pct_change()
    signals = {}
    for sym in frame.columns:
        df = fetch_price_data(sym, period=period)
        if df is None or df.empty:
            continue
        df_eval = evaluate_strategy(df, strategy)
        signals[sym] = df_eval["position"]
    sig_frame = pd.DataFrame(signals).reindex(frame.index).ffill().fillna(0)

    n = len(frame.columns)
    portfolio_ret = (rets * sig_frame).sum(axis=1) / n
    df = pd.DataFrame({"strategy_ret": portfolio_ret, "position": sig_frame.mean(axis=1)})
    metrics = compute_metrics(df)
    metrics["symbol"] = "+".join(frame.columns) if len(frame.columns) <= 5 else f"{len(frame.columns)}-symbol portfolio"
    metrics["universe"] = list(frame.columns)
    metrics["strategy_name"] = strategy.get("name", "Unnamed")
    return metrics


def walkforward_test(symbols, strategy, folds=4, period="6y"):
    """True out-of-sample walk-forward test.

    Splits the full timeline into `folds` contiguous windows. For each window,
    optimizes nothing (uses the given strategy as-is) and evaluates on the
    out-of-sample next window. Aggregates OOS metrics.
    """
    if isinstance(symbols, str):
        symbols = [symbols]

    frame = _load_portfolio_prices(symbols, period=period)
    if frame is None or frame.empty:
        return {"error": "No data for walk-forward"}

    rets = frame.pct_change()
    n = len(frame)
    fold_size = n // folds
    if fold_size < 30:
        folds = max(2, n // 30)
        fold_size = n // folds

    fold_results = []
    # gather position per symbol
    positions = {}
    for sym in frame.columns:
        df = fetch_price_data(sym, period=period)
        if df is None or df.empty:
            continue
        positions[sym] = evaluate_strategy(df, strategy)["position"]
    pos_frame = pd.DataFrame(positions).reindex(frame.index).ffill().fillna(0)

    for i in range(folds - 1):
        start = i * fold_size
        end = (i + 1) * fold_size
        oos_end = min((i + 2) * fold_size, n)
        if end >= oos_end or (oos_end - end) < 20:
            continue

        oos_ret = rets.iloc[end:oos_end]
        oos_pos = pos_frame.iloc[end:oos_end]
        n_syms = len(frame.columns)
        oos_strat = (oos_ret * oos_pos).sum(axis=1) / n_syms
        fold_df = pd.DataFrame({"strategy_ret": oos_strat, "position": oos_pos.mean(axis=1)})
        metrics = compute_metrics(fold_df)
        if "error" in metrics:
            continue
        metrics["fold"] = i + 1
        metrics["period"] = f"{frame.index[end].date()} -> {frame.index[oos_end - 1].date()}"
        fold_results.append(metrics)

    if not fold_results:
        return {"error": "Walk-forward produced no valid folds", "folds": folds}

    sharpe_list = [r["sharpe"] for r in fold_results]
    dd_list = [r["max_drawdown"] for r in fold_results]
    cagr_list = [r["cagr"] for r in fold_results]

    summary = {
        "fold_count": len(fold_results),
        "avg_oos_sharpe": round(float(np.mean(sharpe_list)), 4),
        "worst_oos_sharpe": round(float(np.min(sharpe_list)), 4),
        "best_oos_sharpe": round(float(np.max(sharpe_list)), 4),
        "avg_oos_cagr": round(float(np.mean(cagr_list)), 4),
        "avg_oos_max_drawdown": round(float(np.mean(dd_list)), 4),
        "worst_oos_max_drawdown": round(float(np.min(dd_list)), 4),
        "folds": fold_results
    }
    return summary


def _monte_carlo(df, n_sims=1000):
    from performance_report import monte_carlo_analysis
    return monte_carlo_analysis(df, n_sims=n_sims)


def run_full_backtest(universe, strategy, period="5y", mc_sims=1000):
    """Full validation pipeline: in-sample backtest + walk-forward OOS + Monte Carlo + verdict."""
    if isinstance(universe, str):
        universe = [universe]

    in_sample = backtest_portfolio(universe, strategy, period=period)
    if "error" in in_sample:
        return {"error": in_sample["error"]}

    # Monte Carlo on the in-sample portfolio series
    frame = _load_portfolio_prices(universe, period=period)
    mc = {"error": "No MC data"}
    if frame is not None and not frame.empty:
        rets = frame.pct_change()
        signals = {}
        for sym in frame.columns:
            df = fetch_price_data(sym, period=period)
            if df is None or df.empty:
                continue
            signals[sym] = evaluate_strategy(df, strategy)["position"]
        sig_frame = pd.DataFrame(signals).reindex(frame.index).ffill().fillna(0)
        port_ret = (rets * sig_frame).sum(axis=1) / len(frame.columns)
        mc = _monte_carlo(pd.DataFrame({"strategy_ret": port_ret, "position": sig_frame.mean(axis=1)}), n_sims=mc_sims)

    wf = walkforward_test(universe, strategy, period=period)

    verdict, verdict_reason = _verdict(in_sample, wf, mc)
    report = {
        "strategy": strategy,
        "universe": universe,
        "in_sample_metrics": in_sample,
        "walk_forward": wf,
        "monte_carlo": mc,
        "verdict": verdict,
        "verdict_reason": verdict_reason
    }
    return report


def _verdict(in_sample, wf, mc):
    """Hardcoded sensible defaults for CONFIRMED / CONDITIONAL / REJECTED."""
    reasons = []

    is_sharpe = in_sample.get("sharpe", 0)
    is_dd = in_sample.get("max_drawdown", 0)

    wf_ok = "error" not in wf
    avg_oos_sharpe = wf.get("avg_oos_sharpe", 0) if wf_ok else 0
    worst_oos_dd = wf.get("worst_oos_max_drawdown", 0) if wf_ok else 0

    mc_ok = "error" not in mc
    ruin = mc.get("prob_ruin_25pct_dd", 1) if mc_ok else 1
    expected_cagr = mc.get("expected_cagr", 0) if mc_ok else 0

    reasons.append(f"In-sample Sharpe={is_sharpe:.2f}, MaxDD={is_dd:.2%}")
    reasons.append(f"Walk-forward avg OOS Sharpe={avg_oos_sharpe:.2f}" if wf_ok else "Walk-forward: no valid folds")
    reasons.append(f"Monte Carlo P(25% DD)={ruin:.2%}" if mc_ok else "Monte Carlo: insufficient data")

    score = 0
    if is_sharpe >= 1.0 and is_dd > -0.25:
        score += 1
    if wf_ok and avg_oos_sharpe >= 0.5 and worst_oos_dd > -0.30:
        score += 1
    if mc_ok and ruin < 0.20 and expected_cagr > 0:
        score += 1

    if score >= 2 and is_sharpe >= 1.0:
        verdict = "CONFIRMED"
        reason = "Passes in-sample, walk-forward, and risk checks. Strong candidate for real-money deployment (subject to further due diligence)."
    elif score >= 1 and is_sharpe >= 0.5:
        verdict = "CONDITIONAL"
        reason = "Mixed evidence. Use smaller size / paper trade before deploying real capital."
    else:
        verdict = "REJECTED"
        reason = "Fails validation. Does not pass the bar for real-money deployment without major changes."

    return verdict, f"{reason} | {'; '.join(reasons)}"

