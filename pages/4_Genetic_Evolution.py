import streamlit as st
import json
import pandas as pd

from backtester import get_default_universe
from genetic_optimizer import evolve_strategies

st.set_page_config(page_title="Genetic Evolution", page_icon="🧬", layout="wide")

st.title("🧬 Genetic Algorithm Strategy Evolution")
st.caption("Evolve a population of SMA/RSI strategies across multiple generations to discover robust, high-Sharpe configurations.")

with st.form(key="evo_form"):
    st.subheader("🧬 Evolution Settings")

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input(
            "Stock Symbol / Basket (optional)",
            placeholder="e.g. AAPL,MSFT  — leave blank for default universe",
        )
        period = st.selectbox("Backtest Period", ["3y", "5y", "2y", "1y"], index=0)
    with col2:
        generations = st.slider("Generations", 5, 50, 30, help="Number of evolution generations")
        population_size = st.slider("Population Size", 10, 50, 20, help="Strategies per generation")

    submitted = st.form_submit_button("🧪 Start Evolution", type="primary")

if submitted:
    universe = [s.strip().upper() for s in symbol.split(",")] if symbol else get_default_universe()

    st.info(f"Evolving strategies across **{generations} generations** (pop={population_size}) on universe: `{', '.join(universe)}`")

    progress = st.progress(0)
    status_text = st.empty()

    # evolve_strategies doesn't support streaming progress, so we use a callback wrapper
    total_gens = generations

    def evolve_with_progress():
        results = evolve_strategies(universe, generations=generations, population_size=population_size, period=period)
        return results

    with st.spinner(f"Running evolution ({generations} generations)..."):
        result = evolve_strategies(universe, generations=generations, population_size=population_size, period=period)

    progress.progress(1.0)
    status_text.success("Evolution complete!")

    if "error" in result:
        st.error(result["error"])
    else:
        best_strategy = result.get("strategy", {})
        best_metrics = result.get("best_metrics", {})
        validation = result.get("validation", {})
        best_params = result.get("best_params", {})

        st.session_state["last_strategy"] = best_strategy

        # --- Best parameters ---
        st.subheader("🏆 Best Evolved Strategy")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("SMA Fast", best_params.get("sma_fast", "N/A"))
        col2.metric("SMA Slow", best_params.get("sma_slow", "N/A"))
        col3.metric("RSI Entry", best_params.get("rsi", "N/A"))
        col4.metric("Sharpe", f"{best_metrics.get('sharpe', 0):.2f}")

        # --- Best metrics ---
        st.markdown("---")
        st.subheader("📊 Best Strategy Metrics (In-Sample)")
        cols = st.columns(4)
        cols[0].metric("CAGR", f"{best_metrics.get('cagr', 0):.2%}")
        cols[1].metric("Sharpe", f"{best_metrics.get('sharpe', 0):.2f}")
        cols[2].metric("Max Drawdown", f"{best_metrics.get('max_drawdown', 0):.2%}")
        cols[3].metric("Profit Factor", f"{best_metrics.get('profit_factor', 0):.2f}")

        # --- Validation ---
        if validation and "error" not in validation:
            verdict = validation.get("verdict", "UNKNOWN")
            verdict_color = {"CONFIRMED": "green", "CONDITIONAL": "orange", "REJECTED": "red"}.get(verdict, "gray")
            st.markdown(
                f"<div style='background-color: {verdict_color}20; border-left: 4px solid {verdict_color}; "
                f"padding: 12px; border-radius: 6px;'><h3 style='color: {verdict_color}; margin: 0;'>"
                f"Full Validation Verdict: {verdict}</h3></div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<small>{validation.get('verdict_reason', '')}</small>", unsafe_allow_html=True)

            # Walk-forward and MC summary
            wf = validation.get("walk_forward", {})
            mc = validation.get("monte_carlo", {})
            if "error" not in wf:
                st.markdown(f"**Walk-Forward:** Avg OOS Sharpe = {wf.get('avg_oos_sharpe', 0):.2f}, "
                            f"Folds = {wf.get('fold_count', 'N/A')}")
            if "error" not in mc:
                st.markdown(f"**Monte Carlo:** Expected CAGR = {mc.get('expected_cagr', 0):.2%}, "
                            f"P(25% DD) = {mc.get('prob_ruin_25pct_dd', 0):.2%}")

        # --- Strategy JSON ---
        with st.expander("📋 Full Strategy JSON"):
            st.json(best_strategy)

        # --- Save to DB ---
        if st.button("💾 Save to Strategy Database"):
            from strategy_database import save_strategy
            from final import detect_market_regime
            regime = detect_market_regime(universe[0])
            save_strategy(best_strategy, validation, regime, "Genetic evolution")
            st.success("✅ Saved to database!")

else:
    st.info("📝 Configure evolution parameters and click **Start Evolution**.")
    st.markdown("**Default universe:** " + ", ".join(get_default_universe()))
