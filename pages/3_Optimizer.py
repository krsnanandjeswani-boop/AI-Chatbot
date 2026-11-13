import re

import pandas as pd
import streamlit as st

from backtester import (
    get_default_universe,
    normalize_universe,
    validate_strategy_conditions,
)
from optimizer import grid_optimize
from nav import render_sidebar
from ui_styles import QUANTBOT_ICON, apply_design_system, render_page_header


def parse_integer_list(text, label, minimum, maximum):
    tokens = [token.strip() for token in text.split(",")]
    if not tokens or any(not token for token in tokens):
        return None, f"{label} must be a comma-separated list of whole numbers."

    if any(not re.fullmatch(r"[0-9]+", token) for token in tokens):
        return None, f"{label} may contain only whole numbers."

    values = list(dict.fromkeys(int(token) for token in tokens))
    if any(value < minimum or value > maximum for value in values):
        return None, f"{label} values must be between {minimum} and {maximum}."

    return values, None


st.set_page_config(page_title="Grid Optimizer — Quantbot", page_icon=QUANTBOT_ICON, layout="wide")

apply_design_system("grid-optimizer")
render_sidebar()

render_page_header(
    "Parameter research",
    "Grid Optimizer",
    "Compare indicator settings systematically and surface the strongest candidates.",
)

loaded_strategy = st.session_state.get("loaded_strategy_opt")
if loaded_strategy is not None:
    if not isinstance(loaded_strategy, dict):
        st.error("The loaded strategy is invalid. Reload it from the Strategy Library.")
        st.stop()
    st.info(
        f"Loaded seed: **{loaded_strategy.get('name', 'Unnamed strategy')}**. "
        "The exact saved strategy is scored as a baseline; generated candidates use SMA/RSI rules "
        "and retain its universe and risk settings."
    )
    unsupported_rules = validate_strategy_conditions(loaded_strategy)
    if unsupported_rules:
        st.warning(
            "The saved strategy contains rules this backtester cannot evaluate, so it will be "
            "excluded as a baseline. The generated SMA/RSI candidates can still be searched."
        )
    if st.button("Clear loaded strategy", key="clear_loaded_optimizer"):
        st.session_state.pop("loaded_strategy_opt", None)
        st.session_state.pop("grid_results", None)
        st.session_state["opt_symbols"] = ""
        st.rerun()

with st.form(key="opt_form"):
    st.subheader("Universe and parameters")

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input(
            "Stock symbols (optional)",
            placeholder="e.g. AAPL,MSFT — blank uses the loaded strategy or default universe",
            key="opt_symbols",
        )
        period = st.selectbox("History period", ["5y", "3y", "2y", "1y"], index=0)
    with col2:
        top_n = st.slider("Top results to show", 3, 20, 5)

    st.markdown("---")
    st.subheader("SMA / RSI search grid")
    row1, row2, row3 = st.columns(3)
    with row1:
        sma_fast_str = st.text_input("SMA Fast", value="10,15,20,25,30", help="Comma-separated periods")
    with row2:
        sma_slow_str = st.text_input("SMA Slow", value="30,40,50,60,70", help="Comma-separated periods")
    with row3:
        rsi_str = st.text_input("RSI Entry Threshold", value="55", help="Comma-separated thresholds")

    submitted = st.form_submit_button("Run Grid Search", type="primary")

if submitted:
    st.session_state.pop("grid_results", None)
    errors = []
    fast_values, error = parse_integer_list(sma_fast_str, "SMA Fast", 2, 250)
    if error:
        errors.append(error)
    slow_values, error = parse_integer_list(sma_slow_str, "SMA Slow", 3, 300)
    if error:
        errors.append(error)
    rsi_values, error = parse_integer_list(rsi_str, "RSI threshold", 1, 99)
    if error:
        errors.append(error)

    if fast_values and slow_values and not any(
        fast < slow for fast in fast_values for slow in slow_values
    ):
        errors.append("At least one SMA Fast value must be lower than an SMA Slow value.")

    try:
        if symbol.strip():
            universe = normalize_universe(symbol)
        elif loaded_strategy:
            universe = normalize_universe(
                loaded_strategy.get("universe") or get_default_universe()
            )
        else:
            universe = get_default_universe()
    except ValueError as error:
        errors.append(str(error))

    if errors:
        st.error("\n\n".join(errors))
    else:
        param_grid = {
            "SMA": fast_values,
            "SMA2": slow_values,
            "RSI": rsi_values,
        }
        progress = st.progress(0.0, text="Preparing candidates...")

        def update_progress(completed, total):
            progress.progress(
                completed / total,
                text=f"Evaluating candidate {completed} of {total}",
            )

        with st.spinner("Running the grid search..."):
            results = grid_optimize(
                universe,
                param_grid,
                base_strategy=loaded_strategy,
                period=period,
                top_n=top_n,
                progress_callback=update_progress,
            )
        st.session_state["grid_results"] = results
        st.session_state["grid_universe"] = universe

results = st.session_state.get("grid_results", [])
if results:
    if results[0].get("error"):
        st.warning(results[0]["error"])
    else:
        st.success(f"Found {len(results)} candidates.")
        df = pd.DataFrame(results)
        display_cols = ["name", "sharpe", "cagr", "max_drawdown", "profit_factor", "total_trades"]
        st.dataframe(
            df[display_cols].rename(
                columns={
                    "name": "Strategy",
                    "sharpe": "Sharpe",
                    "cagr": "CAGR",
                    "max_drawdown": "Max DD",
                    "profit_factor": "Profit Factor",
                    "total_trades": "Trades",
                }
            ),
            width="stretch",
            hide_index=True,
            column_config={
                "Sharpe": st.column_config.NumberColumn("Sharpe", format="%.2f"),
                "CAGR": st.column_config.NumberColumn("CAGR", format="%.2%"),
                "Max DD": st.column_config.ProgressColumn(
                    "Max DD",
                    format="%.2f",
                    min_value=-1,
                    max_value=0,
                ),
                "Profit Factor": st.column_config.NumberColumn("Profit Factor", format="%.2f"),
            },
        )

        best = results[0]
        strategy = best.get("strategy", {})
        st.subheader("Best candidate")
        col1, col2, col3 = st.columns(3)
        col1.metric("Strategy", best.get("name", "N/A"))
        col2.metric("Sharpe ratio", f"{best.get('sharpe', 0):.2f}")
        col3.metric("CAGR", f"{best.get('cagr', 0):.2%}")

        tab1, tab2, tab3 = st.tabs(["Details", "Entry rules", "Exit rules"])
        with tab1:
            st.json(strategy)
        with tab2:
            for index, condition in enumerate(strategy.get("entry", []), 1):
                st.write(f"{index}. `{condition}`")
        with tab3:
            for index, condition in enumerate(strategy.get("exit", []), 1):
                st.write(f"{index}. `{condition}`")

        st.session_state["last_strategy"] = strategy
        if st.button("Save best candidate to Strategy Library", key="save_best_grid"):
            try:
                from final import detect_market_regime
                from strategy_database import save_strategy

                universe = strategy.get("universe") or st.session_state.get("grid_universe", [])
                if not universe:
                    st.error("The best candidate has no ticker universe to save.")
                else:
                    regime = detect_market_regime(universe[0])
                    save_strategy(strategy, best, regime, "Grid optimization")
                    st.success("Best candidate saved to the Strategy Library.")
            except Exception as error:
                st.error(f"Could not save the candidate: {error}")
else:
    st.info("Configure the parameter grid, then run the search.")
    if not loaded_strategy:
        st.caption("Default universe: " + ", ".join(get_default_universe()))
