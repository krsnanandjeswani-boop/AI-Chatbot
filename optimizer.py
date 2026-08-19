import itertools
import pandas as pd
import numpy as np
from backtester import (
    fetch_price_data, calculate_indicators, evaluate_strategy, compute_metrics,
    backtest_portfolio, get_default_universe
)


def grid_optimize(symbols=None, param_grid=None, base_strategy=None, period="5y", top_n=5):
    """Grid-search SMA/RSI parameters on a universe (or single symbol).

    Returns concrete, actionable strategy dicts (not bare param lines) with
    portfolio-level metrics.
    """
    if isinstance(symbols, str):
        symbols = [symbols]
    if symbols is None:
        symbols = get_default_universe()

    base = base_strategy or {
        "name": "SMA Crossover",
        "entry": ["SMA(20) > SMA(50)", "RSI > 55"],
        "exit": ["SMA(20) < SMA(50)"],
        "position_size": 0.05,
        "max_positions": 20,
    }

    sma_values = param_grid.get("SMA", [10, 15, 20, 25, 30]) if param_grid else [10, 15, 20, 25, 30]
    sma2_values = param_grid.get("SMA2", [30, 40, 50, 60, 70]) if param_grid else [30, 40, 50, 60, 70]
    rsi_values = param_grid.get("RSI", [55]) if param_grid else [55]

    results = []
    for sma1 in sma_values:
        for sma2 in sma2_values:
            if sma1 >= sma2:
                continue
            for rsi in rsi_values:
                test_strategy = {
                    "name": f"SMA{sma1}/{sma2} RSI{rsi}",
                    "type": "basket" if len(symbols) > 1 else "single_stock",
                    "universe": symbols,
                    "entry": [f"SMA({sma1}) > SMA({sma2})", f"RSI > {rsi}"],
                    "exit": [f"SMA({sma1}) < SMA({sma2})"],
                    "position_size": base.get("position_size", 0.05),
                    "max_positions": base.get("max_positions", 20),
                    "risk_management": base.get("risk_management", {"stop_loss": 0.08, "take_profit": 0.20}),
                    "rationale": f"Grid-searched SMA fast={sma1}, slow={sma2}, RSI filter={rsi}."
                }

                metrics = backtest_portfolio(symbols, test_strategy, period=period)
                if "error" in metrics:
                    continue

                metrics["name"] = test_strategy["name"]
                metrics["parameters"] = {"SMA_fast": sma1, "SMA_slow": sma2, "RSI": rsi}
                metrics["strategy"] = test_strategy
                results.append(metrics)

    results.sort(key=lambda x: x.get("sharpe", 0), reverse=True)
    return results[:top_n]


def get_robust_parameters(grid_results, sharpe_threshold=1.0, dd_threshold=-0.3):
    robust = []
    for r in grid_results:
        if r.get("sharpe", 0) >= sharpe_threshold and r.get("max_drawdown", 0) >= dd_threshold:
            robust.append(r)

    if not robust:
        return None

    return robust[0]

