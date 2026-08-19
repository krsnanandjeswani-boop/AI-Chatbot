import random
import numpy as np
from backtester import (
    fetch_price_data, backtest_portfolio, run_full_backtest, get_default_universe
)


def create_random_strategy(universe):
    sma_fast = random.randint(5, 30)
    sma_slow = random.randint(sma_fast + 10, 100)
    rsi_entry = random.randint(30, 70)
    return {
        "name": f"Genetic SMA{sma_fast}/{sma_slow} RSI{rsi_entry}",
        "type": "basket" if len(universe) > 1 else "single_stock",
        "universe": list(universe),
        "entry": [f"SMA({sma_fast}) > SMA({sma_slow})", f"RSI > {rsi_entry}"],
        "exit": [f"SMA({sma_fast}) < SMA({sma_slow})"],
        "position_size": 0.05,
        "max_positions": 20,
        "risk_management": {"stop_loss": 0.08, "take_profit": 0.20},
        "rationale": "Genetic-algorithm evolved trend-following crossover."
    }


def evaluate_dna(dna, universe, period="3y"):
    strategy = {
        "name": f"Genetic SMA{dna['sma_fast']}/{dna['sma_slow']} RSI{dna['rsi']}",
        "type": "basket" if len(universe) > 1 else "single_stock",
        "universe": list(universe),
        "entry": [f"SMA({dna['sma_fast']}) > SMA({dna['sma_slow']})", f"RSI > {dna['rsi']}"],
        "exit": [f"SMA({dna['sma_fast']}) < SMA({dna['sma_slow']})"],
        "position_size": 0.05,
        "max_positions": 20,
        "risk_management": {"stop_loss": 0.08, "take_profit": 0.20},
        "rationale": "Genetic-algorithm evolved trend-following crossover."
    }
    metrics = backtest_portfolio(universe, strategy, period=period)
    if "error" in metrics:
        return -999, strategy, metrics

    sharpe = metrics.get("sharpe", 0)
    max_dd = metrics.get("max_drawdown", 0)
    fitness = sharpe - 0.5 * abs(max_dd)
    return fitness, strategy, metrics


def evolve_strategies(symbols=None, generations=30, population_size=20, period="3y"):
    if isinstance(symbols, str):
        symbols = [symbols]
    if symbols is None:
        symbols = get_default_universe()

    population = [
        {"sma_fast": random.randint(5, 30), "sma_slow": random.randint(35, 100), "rsi": random.randint(30, 70)}
        for _ in range(population_size)
    ]

    best_strategy = None
    best_metrics = None
    best_fitness = -999

    for gen in range(generations):
        scored = []
        for dna in population:
            fitness, strat, metrics = evaluate_dna(dna, symbols, period=period)
            scored.append((dna, fitness, strat, metrics))
        scored.sort(key=lambda x: x[1], reverse=True)

        if scored[0][1] > best_fitness:
            best_dna, best_fitness, best_strategy, best_metrics = scored[0]

        elites = [s[0] for s in scored[:5]]
        new_pop = elites.copy()
        while len(new_pop) < population_size:
            parent1, parent2 = random.sample(elites, 2)
            child = {
                "sma_fast": parent1["sma_fast"] + random.randint(-5, 5) if random.random() > 0.5 else parent2["sma_fast"],
                "sma_slow": parent1["sma_slow"] + random.randint(-10, 10) if random.random() > 0.5 else parent2["sma_slow"],
                "rsi": parent1["rsi"] + random.randint(-5, 5) if random.random() > 0.5 else parent2["rsi"],
            }
            child["sma_fast"] = max(5, min(50, child["sma_fast"]))
            child["sma_slow"] = max(30, min(150, child["sma_slow"]))
            child["rsi"] = max(20, min(80, child["rsi"]))
            if child["sma_fast"] >= child["sma_slow"]:
                child["sma_slow"] = child["sma_fast"] + 10
            new_pop.append(child)
        population = new_pop

    if best_strategy is None:
        return {"error": "No viable strategy evolved"}

    # Full validation on the best strategy
    full = run_full_backtest(symbols, best_strategy, period=period)
    return {
        "best_params": best_dna,
        "strategy": best_strategy,
        "best_metrics": best_metrics,
        "validation": full,
        "generations": generations,
        "population_size": population_size,
    }

