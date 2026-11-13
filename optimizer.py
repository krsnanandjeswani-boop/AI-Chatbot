from backtester import backtest_portfolio, get_default_universe, normalize_universe


def grid_optimize(
    symbols=None,
    param_grid=None,
    base_strategy=None,
    period="5y",
    top_n=5,
    progress_callback=None,
):
    """Grid-search SMA/RSI parameters on a universe (or single symbol).

    Returns concrete, actionable strategy dicts (not bare param lines) with
    portfolio-level metrics.
    """
    if symbols is None:
        symbols = get_default_universe()
    try:
        symbols = normalize_universe(symbols)
    except ValueError as error:
        return [{"error": str(error)}]
    if not isinstance(top_n, int) or top_n < 1:
        return [{"error": "Top results must be a positive whole number."}]
    if base_strategy is not None and not isinstance(base_strategy, dict):
        return [{"error": "The loaded strategy must be a JSON object."}]
    if param_grid is not None and not isinstance(param_grid, dict):
        return [{"error": "The parameter grid must be an object."}]

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

    if not sma_values or not sma2_values or not rsi_values:
        return [{"error": "Each parameter list must contain at least one value."}]
    for values in (sma_values, sma2_values, rsi_values):
        if any(not isinstance(value, int) or value < 1 for value in values):
            return [{"error": "Parameter values must be positive whole numbers."}]

    combinations = [
        (sma1, sma2, rsi)
        for sma1 in sma_values
        for sma2 in sma2_values
        if sma1 < sma2
        for rsi in rsi_values
    ]
    if not combinations:
        return [{"error": "At least one SMA Fast value must be lower than an SMA Slow value."}]

    total = len(combinations) + int(base_strategy is not None)
    completed = 0
    results = []

    def report_progress():
        if progress_callback:
            progress_callback(completed, total)

    if base_strategy is not None:
        seed_strategy = dict(base_strategy)
        seed_strategy["universe"] = symbols
        seed_metrics = backtest_portfolio(symbols, seed_strategy, period=period)
        completed += 1
        report_progress()
        if "error" not in seed_metrics:
            seed_name = f"{seed_strategy.get('name', 'Library strategy')} (saved seed)"
            seed_metrics.update(
                {
                    "name": seed_name,
                    "parameters": {"source": "Saved strategy"},
                    "strategy": seed_strategy,
                }
            )
            results.append(seed_metrics)

    for sma1, sma2, rsi in combinations:
        test_strategy = dict(base)
        test_strategy.update(
            {
                "name": f"SMA{sma1}/{sma2} RSI{rsi}",
                "type": "basket" if len(symbols) > 1 else "single_stock",
                "universe": symbols,
                "entry": [f"SMA({sma1}) > SMA({sma2})", f"RSI > {rsi}"],
                "exit": [f"SMA({sma1}) < SMA({sma2})"],
                "position_size": base.get("position_size", 0.05),
                "max_positions": base.get("max_positions", 20),
                "risk_management": base.get(
                    "risk_management",
                    {"stop_loss": 0.08, "take_profit": 0.20},
                ),
                "rationale": f"Grid-searched SMA fast={sma1}, slow={sma2}, RSI filter={rsi}.",
            }
        )

        metrics = backtest_portfolio(symbols, test_strategy, period=period)
        completed += 1
        report_progress()
        if "error" in metrics:
            continue

        metrics["name"] = test_strategy["name"]
        metrics["parameters"] = {"SMA_fast": sma1, "SMA_slow": sma2, "RSI": rsi}
        metrics["strategy"] = test_strategy
        results.append(metrics)

    results.sort(key=lambda x: x.get("sharpe", 0), reverse=True)
    if not results:
        return [{"error": "No valid candidates were found for the selected universe and parameter grid."}]
    return results[:top_n]


def get_robust_parameters(grid_results, sharpe_threshold=1.0, dd_threshold=-0.3):
    robust = []
    for r in grid_results:
        if r.get("sharpe", 0) >= sharpe_threshold and r.get("max_drawdown", 0) >= dd_threshold:
            robust.append(r)

    if not robust:
        return None

    return robust[0]

