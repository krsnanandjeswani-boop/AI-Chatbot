import random
import re

from backtester import (
    backtest_portfolio,
    get_default_universe,
    normalize_universe,
    run_full_backtest,
)


def _build_strategy(dna, universe, base_strategy=None):
    strategy = dict(base_strategy) if isinstance(base_strategy, dict) else {}
    strategy.update(
        {
            "name": f"Genetic SMA{dna['sma_fast']}/{dna['sma_slow']} RSI{dna['rsi']}",
            "type": "basket" if len(universe) > 1 else "single_stock",
            "universe": list(universe),
            "entry": [f"SMA({dna['sma_fast']}) > SMA({dna['sma_slow']})", f"RSI > {dna['rsi']}"],
            "exit": [f"SMA({dna['sma_fast']}) < SMA({dna['sma_slow']})"],
            "position_size": strategy.get("position_size", 0.05),
            "max_positions": strategy.get("max_positions", 20),
            "risk_management": strategy.get(
                "risk_management",
                {"stop_loss": 0.08, "take_profit": 0.20},
            ),
            "rationale": "Genetic-algorithm evolved trend-following crossover.",
        }
    )
    return strategy


def create_random_strategy(universe, base_strategy=None):
    sma_fast = random.randint(5, 30)
    sma_slow = random.randint(sma_fast + 10, 100)
    rsi_entry = random.randint(30, 70)
    return _build_strategy(
        {"sma_fast": sma_fast, "sma_slow": sma_slow, "rsi": rsi_entry},
        universe,
        base_strategy,
    )


def extract_seed_dna(strategy):
    """Extract the SMA/RSI genes the evolution algorithm can actually mutate."""
    if not isinstance(strategy, dict):
        return None

    entry_rules = strategy.get("entry", [])
    if not isinstance(entry_rules, (list, tuple)):
        return None

    sma_values = None
    rsi_value = None
    for rule in entry_rules:
        sma_match = re.search(
            r"SMA\((\d+)\)\s*>\s*SMA\((\d+)\)",
            str(rule),
            re.IGNORECASE,
        )
        if sma_match:
            sma_values = (int(sma_match.group(1)), int(sma_match.group(2)))

        rsi_match = re.search(
            r"RSI(?:\(\d+\))?\s*>\s*(\d+)",
            str(rule),
            re.IGNORECASE,
        )
        if rsi_match:
            rsi_value = int(rsi_match.group(1))

    if sma_values is None or rsi_value is None:
        return None

    sma_fast, sma_slow = sma_values
    if (
        not 5 <= sma_fast <= 100
        or sma_fast >= sma_slow
        or sma_slow > 250
        or not 20 <= rsi_value <= 80
    ):
        return None

    return {"sma_fast": sma_fast, "sma_slow": sma_slow, "rsi": rsi_value}


def evaluate_dna(dna, universe, period="3y", base_strategy=None):
    strategy = _build_strategy(dna, universe, base_strategy)
    metrics = backtest_portfolio(universe, strategy, period=period)
    if "error" in metrics:
        return -999, strategy, metrics

    sharpe = metrics.get("sharpe", 0)
    max_dd = metrics.get("max_drawdown", 0)
    fitness = sharpe - 0.5 * abs(max_dd)
    return fitness, strategy, metrics


def evolve_strategies(
    symbols=None,
    generations=30,
    population_size=20,
    period="3y",
    base_strategy=None,
    progress_callback=None,
):
    try:
        universe = normalize_universe(
            symbols if symbols is not None else get_default_universe()
        )
    except ValueError as error:
        return {"error": str(error)}
    if not isinstance(generations, int) or generations < 1:
        return {"error": "Generations must be a positive whole number."}
    if not isinstance(population_size, int) or population_size < 2:
        return {"error": "Population size must be at least 2."}
    if base_strategy is not None and not isinstance(base_strategy, dict):
        return {"error": "The loaded strategy must be a JSON object."}

    population = []
    for _ in range(population_size):
        sma_fast = random.randint(5, 50)
        population.append(
            {
                "sma_fast": sma_fast,
                "sma_slow": random.randint(max(sma_fast + 10, 35), 200),
                "rsi": random.randint(30, 70),
            }
        )

    seed_dna = extract_seed_dna(base_strategy)
    if seed_dna:
        population[0] = seed_dna

    best_strategy = None
    best_metrics = None
    best_fitness = -999
    best_dna = None

    if base_strategy is not None:
        baseline_strategy = dict(base_strategy)
        baseline_strategy["universe"] = universe
        baseline_strategy["type"] = "basket" if len(universe) > 1 else "single_stock"
        baseline_metrics = backtest_portfolio(universe, baseline_strategy, period=period)
        if "error" not in baseline_metrics:
            best_strategy = baseline_strategy
            best_metrics = baseline_metrics
            best_fitness = baseline_metrics.get("sharpe", 0) - 0.5 * abs(
                baseline_metrics.get("max_drawdown", 0)
            )

    for generation in range(generations):
        scored = []
        for dna in population:
            fitness, strategy, metrics = evaluate_dna(
                dna,
                universe,
                period=period,
                base_strategy=base_strategy,
            )
            scored.append((dna, fitness, strategy, metrics))
        scored.sort(key=lambda result: result[1], reverse=True)

        if scored[0][1] > best_fitness:
            best_dna, best_fitness, best_strategy, best_metrics = scored[0]

        if progress_callback:
            progress_callback(generation + 1, generations, best_fitness)

        elites = [result[0] for result in scored[: min(5, len(scored))]]
        next_population = elites.copy()
        while len(next_population) < population_size:
            parent1, parent2 = random.sample(elites, 2)
            child = {
                "sma_fast": (
                    parent1["sma_fast"] + random.randint(-5, 5)
                    if random.random() > 0.5
                    else parent2["sma_fast"]
                ),
                "sma_slow": (
                    parent1["sma_slow"] + random.randint(-10, 10)
                    if random.random() > 0.5
                    else parent2["sma_slow"]
                ),
                "rsi": (
                    parent1["rsi"] + random.randint(-5, 5)
                    if random.random() > 0.5
                    else parent2["rsi"]
                ),
            }
            child["sma_fast"] = max(5, min(100, child["sma_fast"]))
            child["sma_slow"] = max(child["sma_fast"] + 10, min(250, child["sma_slow"]))
            child["rsi"] = max(20, min(80, child["rsi"]))
            next_population.append(child)
        population = next_population

    if best_strategy is None:
        return {"error": "No viable strategy evolved"}

    full = run_full_backtest(universe, best_strategy, period=period)
    return {
        "best_params": best_dna,
        "strategy": best_strategy,
        "best_metrics": best_metrics,
        "validation": full,
        "generations": generations,
        "population_size": population_size,
        "seeded_from_strategy": seed_dna is not None,
    }
