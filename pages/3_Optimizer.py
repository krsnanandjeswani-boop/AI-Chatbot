import streamlit as st
import pandas as pd

from backtester import get_default_universe
from optimizer import grid_optimize

st.set_page_config(page_title="Grid Optimizer", page_icon="🔍", layout="wide")

st.title("🔍 Grid Search Optimizer")
st.caption("Systematically search SMA / EMA / RSI parameter space for the best-performing strategy.")

with st.form(key="opt_form"):
    st.subheader("🔧 Universe & Parameters")

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input(
            "Stock Symbol (optional)",
            placeholder="e.g. AAPL,MSFT  — leave blank for default universe",
        )
        period = st.selectbox("History Period", ["5y", "3y", "2y", "1y"], index=0)
    with col2:
        top_n = st.slider("Top N Results to Show", 3, 20, 5)

    st.markdown("---")
    st.subheader("📐 Parameter Grid")
    row1, row2, row3 = st.columns(3)
    with row1:
        sma_fast_str = st.text_input("SMA Fast", value="10,15,20,25,30", help="Comma-separated values")
    with row2:
        sma_slow_str = st.text_input("SMA Slow", value="30,40,50,60,70", help="Comma-separated values")
    with row3:
        rsi_str = st.text_input("RSI Filter", value="55", help="Comma-separated values")

    submitted = st.form_submit_button("🔍 Run Grid Search", type="primary")

if submitted:
    universe = [s.strip().upper() for s in symbol.split(",")] if symbol else get_default_universe()

    def parse_csv(s):
        return [int(x.strip()) for x in s.split(",") if x.strip().isdigit()]

    param_grid = {
        "SMA": parse_csv(sma_fast_str),
        "SMA2": parse_csv(sma_slow_str),
        "RSI": parse_csv(rsi_str),
    }

    st.info(f"Searching **{len(param_grid['SMA']) * len(param_grid['SMA2']) * len(param_grid['RSI'])}** parameter combinations "
            f"across universe: `{', '.join(universe)}`...")

    with st.spinner("Running grid search..."):
        results = grid_optimize(universe, param_grid, period=period, top_n=top_n)

    if not results or results[0].get("error"):
        st.warning("No valid strategies found. Try different parameters or a different universe.")
    else:
        st.success(f"Found **{len(results)}** top strategies!")

        df = pd.DataFrame(results)
        display_cols = ["name", "sharpe", "cagr", "max_drawdown", "profit_factor", "total_trades"]
        st.dataframe(
            df[display_cols].rename(columns={
                "name": "Strategy",
                "sharpe": "Sharpe",
                "cagr": "CAGR",
                "max_drawdown": "Max DD",
                "profit_factor": "Profit Factor",
                "total_trades": "Trades",
            }),
            width="stretch",
            hide_index=True,
            column_config={
                "Sharpe": st.column_config.NumberColumn("Sharpe", format="%.2f"),
                "CAGR": st.column_config.NumberColumn("CAGR", format="%.2%"),
                "Max DD": st.column_config.ProgressColumn("Max DD", format="%.2f", min_value=-1, max_value=0),
                "Profit Factor": st.column_config.NumberColumn("Profit Factor", format="%.2f"),
            },
        )

        st.markdown("---")
        st.subheader("🏆 Best Strategy Detail")
        best = results[0]
        strat = best.get("strategy", {})

        col1, col2, col3 = st.columns(3)
        col1.metric("Strategy Name", best.get("name", "N/A"))
        col2.metric("Sharpe Ratio", f"{best.get('sharpe', 0):.2f}")
        col3.metric("CAGR", f"{best.get('cagr', 0):.2%}")

        tab1, tab2, tab3 = st.tabs(["📋 Details", "🔑 Entry", "🚪 Exit"])
        with tab1:
            st.json(strat)
        with tab2:
            for i, cond in enumerate(strat.get("entry", []), 1):
                st.write(f"  {i}. `{cond}`")
        with tab3:
            for i, cond in enumerate(strat.get("exit", []), 1):
                st.write(f"  {i}. `{cond}`")

        st.session_state["last_strategy"] = strat

else:
    st.info("📝 Configure the parameter grid and click **Run Grid Search**.")
    st.markdown("**Default universe:** " + ", ".join(get_default_universe()))
