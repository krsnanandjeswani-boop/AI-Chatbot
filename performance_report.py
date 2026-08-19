import numpy as np
import pandas as pd
import json


def monte_carlo_analysis(df, n_sims=1000):
    strat_ret = df["strategy_ret"].dropna()
    if len(strat_ret) == 0:
        return {"error": "No trades to simulate"}

    results = []
    for _ in range(n_sims):
        shuffled = strat_ret.sample(frac=1, replace=True)
        cagr = (1 + shuffled.mean()) ** 252 - 1
        dd = ((1 + shuffled).cumprod() - (1 + shuffled).cumprod().cummax()).min() / (1 + shuffled).cumprod().max()
        results.append({"cagr": cagr, "max_dd": dd})

    car_list = [r["cagr"] for r in results]
    dd_list = [r["max_dd"] for r in results]

    return {
        "expected_cagr": float(np.mean(car_list)),
        "cagr_5th_percentile": float(np.percentile(car_list, 5)),
        "cagr_95th_percentile": float(np.percentile(car_list, 95)),
        "prob_ruin_25pct_dd": float(len([d for d in dd_list if d < -0.25]) / n_sims),
        "worst_drawdown": float(min(dd_list))
    }


def _pct(x, default="N/A"):
    try:
        return f"{float(x):.2%}"
    except (TypeError, ValueError):
        return default


def _fmt_metrics(metrics, indent=""):
    if not metrics or "error" in metrics:
        return f"{indent}N/A ({metrics.get('error', 'no data')})"
    lines = [
        f"CAGR: {_pct(metrics.get('cagr'))}",
        f"Sharpe Ratio: {metrics.get('sharpe', 'N/A')}",
        f"Sortino Ratio: {metrics.get('sortino', 'N/A')}",
        f"Max Drawdown: {_pct(metrics.get('max_drawdown'))}",
        f"Calmar Ratio: {metrics.get('calmar', 'N/A')}",
        f"Profit Factor: {metrics.get('profit_factor', 'N/A')}",
        f"Win Rate: {metrics.get('win_rate', 'N/A')}",
        f"Total Trades: {metrics.get('total_trades', 'N/A')}",
        f"Total Return: {_pct(metrics.get('total_return'))}",
    ]
    return "\n".join(f"{indent}{l}" for l in lines)


def _fmt_mc(mc):
    if not mc or "error" in mc:
        return "Monte Carlo: N/A"
    return (
        f"Monte Carlo ({'1000' if mc.get('samples') is None else mc.get('samples')} sims):\n"
        f"  Expected CAGR: {_pct(mc.get('expected_cagr'))}\n"
        f"  5th-95th CAGR: {_pct(mc.get('cagr_5th_percentile'))} - {_pct(mc.get('cagr_95th_percentile'))}\n"
        f"  P(25%+ Drawdown): {_pct(mc.get('prob_ruin_25pct_dd'))}\n"
        f"  Worst Drawdown: {_pct(mc.get('worst_drawdown'))}"
    )


def _fmt_wf(wf):
    if not wf or "error" in wf:
        return "Walk-Forward: N/A"
    lines = [
        "Walk-Forward (out-of-sample):",
        f"  Avg OOS Sharpe: {wf.get('avg_oos_sharpe', 'N/A')}",
        f"  Worst OOS Sharpe: {wf.get('worst_oos_sharpe', 'N/A')}",
        f"  Avg OOS CAGR: {_pct(wf.get('avg_oos_cagr'))}",
        f"  Avg OOS Max DD: {_pct(wf.get('avg_oos_max_drawdown'))}",
        f"  Worst OOS Max DD: {_pct(wf.get('worst_oos_max_drawdown'))}",
        f"  Folds: {wf.get('fold_count', 'N/A')}",
    ]
    for f in wf.get("folds", [])[:4]:
        lines.append(f"    Fold {f.get('fold')}: Sharpe={f.get('sharpe', 'N/A')}, "
                     f"CAGR={_pct(f.get('cagr'))}, MaxDD={_pct(f.get('max_drawdown'))} ({f.get('period', '')})")
    return "\n".join(lines)


def format_report(report):
    """Render a full validation report from run_full_backtest()."""
    strategy = report.get("strategy", {})
    universe = report.get("universe", [])
    is_metrics = report.get("in_sample_metrics", {})
    wf = report.get("walk_forward", {})
    mc = report.get("monte_carlo", {})
    verdict = report.get("verdict", "N/A")
    verdict_reason = report.get("verdict_reason", "")

    univ_str = ", ".join(universe) if universe else "N/A"
    name = strategy.get("name", "Unnamed")

    header = f"""
==========================================================
 VALIDATION REPORT
==========================================================
 Strategy : {name}
 Type     : {strategy.get('type', 'N/A')}
 Universe : {univ_str}
 Rationale: {strategy.get('rationale', 'N/A')}
 Entry    : {json.dumps(strategy.get('entry', []))}
 Exit     : {json.dumps(strategy.get('exit', []))}
 Risk Mgmt: {json.dumps(strategy.get('risk_management', {}))}

 VERDICT  : {verdict}
 Reason   : {verdict_reason}
==========================================================
"""

    sections = f"""
[1] IN-SAMPLE BACKTEST
{_fmt_metrics(is_metrics, indent='    ')}

[2] WALK-FORWARD (OUT-OF-SAMPLE)
{_fmt_wf(wf)}

[3] MONTE CARLO RISK ANALYSIS
{_fmt_mc(mc)}

[4] INTERPRETATION
    Verdict {verdict} means:
    - CONFIRMED   : Strategy passes in-sample + walk-forward + risk checks. Strong candidate for real-money.
    - CONDITIONAL : Mixed evidence. Paper-trade / use smaller size before deploying real capital.
    - REJECTED    : Fails validation. Do not deploy without major changes.

    Next steps:
      - /optimize {universe[0] if universe else 'SYM'} to refine parameters (grid search)
      - /evolve {universe[0] if universe else 'SYM'}  to evolve a family of strategies
      - /query        to compare against previously saved strategies
"""
    return header + sections


def format_report_old(metrics, mc_results=None):
    report = f"""
Strategy Performance Report
==========================

CAGR: {metrics.get('cagr', 'N/A')}%
Sharpe Ratio: {metrics.get('sharpe', 'N/A')}
Sortino Ratio: {metrics.get('sortino', 'N/A')}
Max Drawdown: {metrics.get('max_drawdown', 'N/A')}%
Calmar Ratio: {metrics.get('calmar', 'N/A')}
Profit Factor: {metrics.get('profit_factor', 'N/A')}
Win Rate: {metrics.get('win_rate', 'N/A')}
Total Trades: {metrics.get('total_trades', 'N/A')}

Monte Carlo Analysis (1000 simulations):
{json.dumps(mc_results, indent=2) if mc_results else "Run /mc <symbol> for Monte Carlo analysis"}
"""
    return report

