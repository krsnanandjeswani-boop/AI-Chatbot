import streamlit as st
import json

from strategy_generator import generate_strategy, critique_strategy
from backtester import backtest_strategy

st.set_page_config(page_title="Strategy Generator", page_icon="🤖", layout="wide")

st.title("🤖 Strategy Generator")
st.caption("LLM designs custom trading strategies for single stocks, baskets, or sector rotation.")

with st.form(key="gen_form"):
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input(
            "Stock Symbol (optional)",
            placeholder="e.g. AAPL  — leave blank for AI-picked universe",
            help="If blank, the LLM intelligently picks a single stock OR a broader basket.",
        )
    with col2:
        question = st.text_input(
            "Design prompt (optional)",
            value="Design a trading strategy and validate it",
            help="Custom instruction for the LLM.",
        )
    submitted = st.form_submit_button("🎯 Generate Strategy", type="primary")

if submitted:
    with st.spinner("🧠 The LLM is designing a strategy... This may take 15-30 seconds."):
        strategy = generate_strategy(
            symbol if not symbol else symbol.upper(),
            question=question,
        )

    st.session_state["last_strategy"] = strategy

    # --- Display strategy ---
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader(strategy.get("name", "Unnamed Strategy"))
        st.caption(f"Type: ``{strategy.get('type', 'N/A')}``")

    with col_right:
        verdict_color = "gray"
        st.markdown(f"**Verdict:** :{verdict_color}[Not yet tested]")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 Summary", "🔑 Entry", "🚪 Exit", "🎯 Risk Mgmt", "💭 Rationale"]
    )

    with tab1:
        st.json(strategy)

    with tab2:
        st.write("**Entry Conditions** (all must be true to enter a position):")
        for i, cond in enumerate(strategy.get("entry", []), 1):
            st.write(f"  {i}. `{cond}`")

    with tab3:
        st.write("**Exit Conditions** (any true triggers exit):")
        for i, cond in enumerate(strategy.get("exit", []), 1):
            st.write(f"  {i}. `{cond}`")

    with tab4:
        st.json(strategy.get("risk_management", {}))
        st.info(f"Position size: **{strategy.get('position_size', 'N/A')}** per name, "
                f"max **{strategy.get('max_positions', 'N/A')}** positions.")

    with tab5:
        st.write(strategy.get("rationale", "No rationale provided."))

    st.markdown("---")

    # --- Quick backtest ---
    if st.button("🚀 Run Quick Backtest on This Strategy", use_container_width=True):
        universe = strategy.get("universe", ["SPY"])
        sym = universe[0] if universe else "SPY"
        with st.spinner(f"Backtesting {strategy.get('name')} on {sym}..."):
            metrics = backtest_strategy(sym, strategy)
        from backtester import compute_metrics
        if "error" in metrics:
            st.error(metrics["error"])
        else:
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("CAGR", f"{metrics.get('cagr', 0):.2%}")
            kpi2.metric("Sharpe", f"{metrics.get('sharpe', 0):.2f}")
            kpi3.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0):.2%}")
            kpi4.metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")

    # --- Critique ---
    if st.button("🔍 Get LLM Critique", use_container_width=True):
        with st.spinner("Analyzing strategy performance..."):
            critique = critique_strategy(strategy, {
                "cagr": 0, "sharpe": 0, "max_drawdown": 0,
                "total_return": 0, "total_trades": 0
            })
        st.markdown(critique)

else:
    st.info("📝 Enter a symbol or leave blank and click **Generate Strategy** to get started.")
