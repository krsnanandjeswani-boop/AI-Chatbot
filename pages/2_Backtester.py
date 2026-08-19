import streamlit as st
import json

from strategy_generator import generate_strategy
from backtester import run_full_backtest, get_default_universe
from performance_report import format_report

st.set_page_config(page_title="Backtester", page_icon="📊", layout="wide")

st.title("📊 Full Backtest & Validation Pipeline")
st.caption("In-sample backtest + walk-forward out-of-sample + Monte Carlo (1000 sims) + verdict.")

with st.form(key="bt_form"):
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input(
            "Stock Symbol (optional)",
            placeholder="e.g. AAPL  — leave blank for AI-picked universe",
        )
    with col2:
        question = st.text_input(
            "Design prompt",
            value="Design a trading strategy and validate it",
        )
    submitted = st.form_submit_button("🏃 Run Full Validation", type="primary")

if submitted:
    sym_list = [symbol.upper()] if symbol else None
    with st.spinner("🧠 Generating strategy via LLM..."):
        strategy = generate_strategy(sym_list, question=question)

    st.session_state["last_strategy"] = strategy
    st.session_state["last_report"] = None

    st.success(f"Generated strategy: **{strategy.get('name')}**")
    st.markdown(f"Universe: `{', '.join(strategy.get('universe', ['SPY']))}`")

    with st.expander("📋 Strategy Details", expanded=False):
        st.json(strategy)

    universe = strategy.get("universe") or (sym_list or get_default_universe())

    with st.spinner("⏳ Running full validation pipeline (in-sample + walk-forward + Monte Carlo)..."):
        report = run_full_backtest(universe, strategy, mc_sims=1000)

    st.session_state["last_report"] = report
    st.session_state["last_strategy"] = strategy

    if "error" in report:
        st.error(f"Validation failed: {report['error']}")
    else:
        # --- Verdict banner ---
        verdict = report.get("verdict", "UNKNOWN")
        verdict_reason = report.get("verdict_reason", "")

        color_map = {
            "CONFIRMED": "green",
            "CONDITIONAL": "orange",
            "REJECTED": "red",
        }
        color = color_map.get(verdict, "gray")
        st.markdown(
            f"""
            <div style="background-color: {color}20; border-left: 6px solid {color};
                        padding: 16px; border-radius: 8px; margin: 20px 0;">
                <h2 style="color: {color}; margin: 0;">VERDICT: {verdict}</h2>
                <p style="color: {color}; margin: 4px 0 0 0;">{verdict_reason}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- Metrics tabs ---
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📈 In-Sample", "🚶 Walk-Forward", "🎲 Monte Carlo", "📄 Full Report"]
        )

        is_metrics = report.get("in_sample_metrics", {})
        wf = report.get("walk_forward", {})
        mc = report.get("monte_carlo", {})

        with tab1:
            if "error" in is_metrics:
                st.warning(is_metrics["error"])
            else:
                cols = st.columns(4)
                cols[0].metric("CAGR", f"{is_metrics.get('cagr', 0):.2%}")
                cols[1].metric("Sharpe Ratio", f"{is_metrics.get('sharpe', 0):.2f}")
                cols[2].metric("Max Drawdown", f"{is_metrics.get('max_drawdown', 0):.2%}")
                cols[3].metric("Profit Factor", f"{is_metrics.get('profit_factor', 0):.2f}")
                st.markdown("---")
                cols2 = st.columns(4)
                cols2[0].metric("Sortino", f"{is_metrics.get('sortino', 0):.2f}")
                cols2[1].metric("Calmar", f"{is_metrics.get('calmar', 0):.2f}")
                cols2[2].metric("Win Rate", f"{is_metrics.get('win_rate', 0):.2%}")
                cols2[3].metric("Total Trades", f"{is_metrics.get('total_trades', 0)}")

        with tab2:
            if "error" in wf:
                st.warning(wf["error"])
            else:
                cols = st.columns(3)
                cols[0].metric("Avg OOS Sharpe", f"{wf.get('avg_oos_sharpe', 0):.2f}")
                cols[1].metric("Avg OOS CAGR", f"{wf.get('avg_oos_cagr', 0):.2%}")
                cols[2].metric("Worst OOS Max DD", f"{wf.get('worst_oos_max_drawdown', 0):.2%}")
                st.markdown(f"Folds run: **{wf.get('fold_count', 'N/A')}**")
                if "folds" in wf:
                    import pandas as pd
                    fold_df = pd.DataFrame(wf["folds"])
                    st.dataframe(fold_df, width="stretch")

        with tab3:
            if "error" in mc:
                st.warning(mc["error"])
            else:
                cols = st.columns(2)
                cols[0].metric("Expected CAGR", f"{mc.get('expected_cagr', 0):.2%}")
                cols[1].metric("P(25% Drawdown)", f"{mc.get('prob_ruin_25pct_dd', 0):.2%}")
                st.markdown(f"90% CAGR range: **{mc.get('cagr_5th_percentile', 0):.2%} - {mc.get('cagr_95th_percentile', 0):.2%}**")
                st.markdown(f"Worst drawdown across 1000 sims: **{mc.get('worst_drawdown', 0):.2%}**")

        with tab4:
            st.code(format_report(report), language="text")

        # --- Save to DB ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Strategy to Database", width="stretch", key="save_btn"):
                from strategy_database import save_strategy
                from final import detect_market_regime
                regime = detect_market_regime(universe[0])
                save_strategy(strategy, report, regime, "Full validation via web")
                st.success("✅ Strategy saved to database!")
        with col2:
            if st.button("📋 Copy Full Report", width="stretch", key="copy_btn"):
                st.code(format_report(report), language="text")

else:
    st.info("📝 Enter a symbol or leave blank, then click **Run Full Validation**.")
    st.markdown("**Default universe:** " + ", ".join(get_default_universe()))
