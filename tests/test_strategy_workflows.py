import unittest
from unittest.mock import patch

import pandas as pd

import backtester
import genetic_optimizer
import optimizer
from performance_report import format_report


STRATEGY = {
    "name": "Saved crossover",
    "universe": ["AAPL"],
    "entry": ["SMA(10) > SMA(30)", "RSI > 50"],
    "exit": ["SMA(10) < SMA(30)"],
    "position_size": 0.08,
    "max_positions": 4,
    "risk_management": {"stop_loss": 0.06, "take_profit": 0.18},
}


def fake_metrics():
    return {
        "sharpe": 1.0,
        "max_drawdown": -0.1,
        "cagr": 0.1,
        "profit_factor": 1.5,
        "total_trades": 8,
    }


class StrategyValidationTests(unittest.TestCase):
    def test_normalize_universe_cleans_symbols_and_rejects_invalid_lists(self):
        self.assertEqual(backtester.normalize_universe(" aapl, MSFT "), ["AAPL", "MSFT"])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            backtester.normalize_universe("AAPL,aapl")
        with self.assertRaisesRegex(ValueError, "one or more"):
            backtester.normalize_universe("AAPL, ")

    def test_portfolio_backtest_rejects_unsupported_rules_before_fetching_data(self):
        strategy = dict(STRATEGY, entry=["price is rising"])
        with patch("backtester._load_portfolio_prices") as load_prices:
            result = backtester.backtest_portfolio(["AAPL"], strategy)

        self.assertIn("Unsupported entry rule", result["error"])
        load_prices.assert_not_called()

    def test_evaluate_strategy_does_not_silently_ignore_unknown_rules(self):
        strategy = dict(STRATEGY, entry=["price is rising"])
        with self.assertRaisesRegex(ValueError, "Unsupported entry rule"):
            backtester.evaluate_strategy(pd.DataFrame(), strategy)

    def test_saved_strategy_indicators_are_recognized_by_the_backtester(self):
        strategy = dict(
            STRATEGY,
            entry=[
                "SMA(50) > SMA(200)",
                "RSI(14) < 70",
                "Close > SMA(20)",
                "Volume > Volume_SMA(20)",
            ],
            exit=[
                "SMA(50) < SMA(200)",
                "RSI(14) > 80",
                "Close < SMA(20)",
            ],
        )

        self.assertEqual(backtester.validate_strategy_conditions(strategy), [])


class OptimizerWorkflowTests(unittest.TestCase):
    def test_grid_search_scores_saved_seed_and_reports_real_progress(self):
        progress = []
        with patch(
            "optimizer.backtest_portfolio",
            side_effect=lambda *args, **kwargs: fake_metrics(),
        ) as run_backtest:
            results = optimizer.grid_optimize(
                ["AAPL"],
                {"SMA": [5], "SMA2": [20], "RSI": [50]},
                base_strategy=STRATEGY,
                progress_callback=lambda completed, total: progress.append((completed, total)),
            )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["parameters"]["source"], "Saved strategy")
        self.assertEqual(results[0]["strategy"]["entry"], STRATEGY["entry"])
        self.assertEqual(results[1]["strategy"]["risk_management"], STRATEGY["risk_management"])
        self.assertEqual(progress, [(1, 2), (2, 2)])
        self.assertEqual(run_backtest.call_count, 2)

    def test_grid_search_rejects_empty_or_incompatible_grids(self):
        empty_result = optimizer.grid_optimize(
            ["AAPL"],
            {"SMA": [], "SMA2": [20], "RSI": [50]},
        )
        incompatible_result = optimizer.grid_optimize(
            ["AAPL"],
            {"SMA": [30], "SMA2": [20], "RSI": [50]},
        )

        self.assertIn("at least one value", empty_result[0]["error"])
        self.assertIn("lower than", incompatible_result[0]["error"])

    def test_genetic_search_seeds_from_saved_rules_and_preserves_risk_settings(self):
        progress = []
        evaluated_strategies = []

        def fake_backtest(universe, strategy, period):
            evaluated_strategies.append(strategy)
            return fake_metrics()

        with patch("genetic_optimizer.backtest_portfolio", side_effect=fake_backtest), patch(
            "genetic_optimizer.run_full_backtest",
            return_value={"verdict": "CONDITIONAL"},
        ):
            result = genetic_optimizer.evolve_strategies(
                ["AAPL"],
                generations=1,
                population_size=2,
                base_strategy=STRATEGY,
                progress_callback=lambda generation, total, fitness: progress.append(
                    (generation, total, fitness)
                ),
            )

        self.assertTrue(result["seeded_from_strategy"])
        self.assertEqual(result["strategy"]["risk_management"], STRATEGY["risk_management"])
        self.assertEqual(evaluated_strategies[1]["entry"][0], "SMA(10) > SMA(30)")
        self.assertEqual(progress[0][:2], (1, 1))


class BenchmarkReportTests(unittest.TestCase):
    def test_full_report_includes_equal_weight_benchmark_metrics(self):
        prices = pd.DataFrame(
            {"AAPL": [100.0, 110.0, 100.0, 120.0]},
            index=pd.date_range("2024-01-01", periods=4, freq="D"),
        )
        price_data = pd.DataFrame(
            {
                "Close": prices["AAPL"],
                "Volume": [1000, 1100, 900, 1200],
            },
            index=prices.index,
        )

        def evaluate_with_long_position(frame, strategy):
            result = frame.copy()
            result["position"] = 1
            result["strategy_ret"] = result["Close"].pct_change()
            return result

        with patch("backtester.backtest_portfolio", return_value=fake_metrics()), patch(
            "backtester._load_portfolio_prices",
            return_value=prices,
        ), patch("backtester.fetch_price_data", return_value=price_data), patch(
            "backtester.evaluate_strategy",
            side_effect=evaluate_with_long_position,
        ), patch(
            "backtester._monte_carlo",
            return_value={"expected_cagr": 0.1, "prob_ruin_25pct_dd": 0.1},
        ), patch(
            "backtester.walkforward_test",
            return_value={
                "avg_oos_sharpe": 0.8,
                "worst_oos_max_drawdown": -0.2,
                "fold_count": 2,
            },
        ):
            report = backtester.run_full_backtest(["AAPL"], STRATEGY)

        self.assertIn("cagr", report["benchmark_metrics"])
        formatted = format_report(report)
        self.assertIn("EQUAL-WEIGHT, DAILY-REBALANCED BENCHMARK", formatted)
        self.assertIn("not a forecast or guarantee", formatted)


if __name__ == "__main__":
    unittest.main()
