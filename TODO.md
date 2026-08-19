# Implementation TODO

## Goal
Make `/strategy`, `/backtest`, `/optimize`, `/evolve` produce **actionable, portfolio-level results with clear verdicts**, and **fold Monte Carlo + Walk-Forward into `/backtest`** so it answers: *"Would this work with real money?"*

## Steps

- [x] **1. `strategy_generator.py`** — LLM generates richer portfolio-aware strategies (universe can be single symbol OR a dynamic basket chosen by the LLM). Adds `risk_management`, `rationale`, `type`, `universe` fields.
- [x] **2. `backtester.py`** — 
  - Robust generic condition evaluator (SMA/EMA/RSI/MACD/BB/Volume)
  - `backtest_portfolio()` for multi-symbol equal-weight returns
  - Real `walkforward_test()` (true out-of-sample folds)
  - `run_full_backtest()` combining in-sample + walk-forward + Monte Carlo with a hardcoded verdict (`CONFIRMED`/`CONDITIONAL`/`REJECTED`)
- [x] **3. `performance_report.py`** — `format_report()` renders the full validation report (in-sample, OOS walk-forward, Monte Carlo, verdict, interpretation).
- [x] **4. `optimizer.py`** — `grid_optimize()` works on portfolio universe and returns concrete strategy dicts (not bare param lines).
- [x] **5. `genetic_optimizer.py`** — `evolve_strategies()` works on portfolio, returns a full strategy + metrics + verdict (not bare params).
- [x] **6. `strategy_database.py`** — support saving portfolio/universe strategies.
- [x] **7. `chatbot.py`** — merge `/mc` + `/wf` into `/backtest` (typed commands print "merged into /backtest"), update `/strategy`, `/backtest`, `/optimize`, `/evolve` output, update help text.
- [x] **8. Verify** — `py_compile` all modified files; smoke-tested full backtest pipeline, optimizer, genetic optimizer, and DB save. All pass.

