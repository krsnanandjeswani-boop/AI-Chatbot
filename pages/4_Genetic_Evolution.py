import streamlit as st

from backtester import (
    get_default_universe,
    normalize_universe,
    validate_strategy_conditions,
)
from genetic_optimizer import evolve_strategies, extract_seed_dna
from nav import render_sidebar
from ui_styles import QUANTBOT_ICON, apply_design_system, render_page_header


st.set_page_config(page_title="Genetic Evolution — Quantbot", page_icon=QUANTBOT_ICON, layout="wide")

apply_design_system()
render_sidebar()

render_page_header(
    "Parameter research",
    "Genetic Evolution",
    "Evolve a population of candidate strategies and compare the strongest configurations.",
)

loaded_strategy = st.session_state.get("loaded_strategy_evo")
if loaded_strategy is not None:
    if not isinstance(loaded_strategy, dict):
        st.error("The loaded strategy is invalid. Reload it from the Strategy Library.")
        st.stop()
    st.info(
        f"Loaded seed: **{loaded_strategy.get('name', 'Unnamed strategy')}**. "
        "The exact saved strategy is scored as a baseline when its rules are supported. "
        "Generated candidates retain its universe and risk settings."
    )
    if extract_seed_dna(loaded_strategy) is None:
        st.warning(
            "The saved entry rules do not match the genetic search's SMA/RSI genes. "
            "The saved strategy will still be tested as a baseline when supported, but evolution "
            "will start with generated SMA/RSI candidates."
        )
    if validate_strategy_conditions(loaded_strategy):
        st.warning(
            "The saved strategy contains rules this backtester cannot evaluate, so it cannot be "
            "scored as a baseline."
        )
    if st.button("Clear loaded strategy", key="clear_loaded_evolution"):
        st.session_state.pop("loaded_strategy_evo", None)
        st.session_state.pop("evolution_result", None)
        st.session_state["evo_symbols"] = ""
        st.rerun()

with st.form(key="evo_form"):
    st.subheader("Evolution settings")

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input(
            "Stock symbols / basket (optional)",
            placeholder="e.g. AAPL,MSFT — blank uses the loaded strategy or default universe",
            key="evo_symbols",
        )
        period = st.selectbox("Backtest period", ["3y", "5y", "2y", "1y"], index=0)
    with col2:
        generations = st.slider("Generations", 5, 50, 30)
        population_size = st.slider("Population size", 10, 50, 20)

    submitted = st.form_submit_button("Start Evolution", type="primary")

if submitted:
    st.session_state.pop("evolution_result", None)
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
        st.error(str(error))
    else:
        progress = st.progress(0.0, text="Preparing the population...")
        status_text = st.empty()

        def update_progress(generation, total, best_fitness):
            progress.progress(
                generation / total,
                text=f"Generation {generation} of {total}",
            )
            status_text.caption(f"Best fitness so far: {best_fitness:.3f}")

        with st.spinner(f"Evaluating {population_size} candidates across {generations} generations..."):
            result = evolve_strategies(
                universe,
                generations=generations,
                population_size=population_size,
                period=period,
                base_strategy=loaded_strategy,
                progress_callback=update_progress,
            )
        st.session_state["evolution_result"] = result
        st.session_state["evolution_universe"] = universe

result = st.session_state.get("evolution_result")
if result:
    if "error" in result:
        st.error(result["error"])
    else:
        best_strategy = result["strategy"]
        best_metrics = result["best_metrics"]
        validation = result.get("validation", {})
        best_params = result.get("best_params") or {}

        st.success("Evolution complete.")
        if result.get("seeded_from_strategy"):
            st.caption("The population included genes extracted from the loaded strategy.")

        st.subheader("Best candidate")
        if best_params:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("SMA Fast", best_params.get("sma_fast", "N/A"))
            col2.metric("SMA Slow", best_params.get("sma_slow", "N/A"))
            col3.metric("RSI Entry", best_params.get("rsi", "N/A"))
            col4.metric("Sharpe", f"{best_metrics.get('sharpe', 0):.2f}")
        else:
            st.caption("The saved strategy baseline was the strongest candidate.")

        st.subheader("Candidate metrics")
        cols = st.columns(4)
        cols[0].metric("CAGR", f"{best_metrics.get('cagr', 0):.2%}")
        cols[1].metric("Sharpe", f"{best_metrics.get('sharpe', 0):.2f}")
        cols[2].metric("Max drawdown", f"{best_metrics.get('max_drawdown', 0):.2%}")
        cols[3].metric("Profit factor", f"{best_metrics.get('profit_factor', 0):.2f}")

        if validation and "error" not in validation:
            benchmark = validation.get("benchmark_metrics", {})
            if "error" not in benchmark:
                st.caption("Same-universe equal-weight benchmark")
                b1, b2 = st.columns(2)
                b1.metric(
                    "CAGR vs benchmark",
                    f"{best_metrics.get('cagr', 0):.2%}",
                    delta=f"{best_metrics.get('cagr', 0) - benchmark.get('cagr', 0):+.2%}",
                )
                b2.metric(
                    "Sharpe vs benchmark",
                    f"{best_metrics.get('sharpe', 0):.2f}",
                    delta=f"{best_metrics.get('sharpe', 0) - benchmark.get('sharpe', 0):+.2f}",
                )

            verdict = validation.get("verdict", "UNKNOWN")
            verdict_reason = validation.get("verdict_reason", "")
            if verdict == "CONFIRMED":
                st.success(f"Historical validation: {verdict}. {verdict_reason}")
            elif verdict == "CONDITIONAL":
                st.warning(f"Historical validation: {verdict}. {verdict_reason}")
            else:
                st.error(f"Historical validation: {verdict}. {verdict_reason}")
        elif isinstance(validation, dict) and validation.get("error"):
            st.warning(f"Full validation could not be completed: {validation['error']}")

        with st.expander("Full strategy JSON"):
            st.json(best_strategy)

        if st.button("Save best strategy to Strategy Library", key="save_best_evolution"):
            try:
                from final import detect_market_regime
                from strategy_database import save_strategy

                universe = best_strategy.get("universe") or st.session_state.get(
                    "evolution_universe",
                    [],
                )
                if not universe:
                    st.error("The best strategy has no ticker universe to save.")
                else:
                    regime = detect_market_regime(universe[0])
                    strategy_metrics = (
                        validation
                        if isinstance(validation, dict) and "error" not in validation
                        else best_metrics
                    )
                    save_strategy(
                        best_strategy,
                        strategy_metrics,
                        regime,
                        "Genetic evolution",
                    )
                    st.success("Best strategy saved to the Strategy Library.")
            except Exception as error:
                st.error(f"Could not save the strategy: {error}")
else:
    st.info("Configure evolution parameters, then start the run.")
    if not loaded_strategy:
        st.caption("Default universe: " + ", ".join(get_default_universe()))
