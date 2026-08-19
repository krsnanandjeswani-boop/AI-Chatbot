import streamlit as st
import pandas as pd
import json

from strategy_database import query_strategies

st.set_page_config(page_title="Strategy Database", page_icon="💾", layout="wide")

st.title("💾 Strategy Database")
st.caption("Query and browse previously saved trading strategies by performance metrics.")

with st.sidebar:
    st.header("🔍 Query Filters")
    sharpe_threshold = st.slider("Minimum Sharpe Ratio", 0.0, 2.0, 0.5, 0.1)
    regime_filter = st.selectbox(
        "Market Regime",
        ["all", "bull_high", "bear_high", "sideways_normal", "bull_normal", "bear_normal"],
        index=0,
        format_func=lambda x: "All Regimes" if x == "all" else x,
    )

strategies = query_strategies(sharpe_gt=sharpe_threshold, regime=regime_filter)

if not strategies:
    st.info(f"No strategies found with Sharpe >= {sharpe_threshold} and regime = '{regime_filter}'.")
    st.markdown("Run the **Backtester** or **Genetic Evolution** page and click 'Save to Database' to add strategies.")
else:
    st.success(f"Found **{len(strategies)}** strategies.")

    df = pd.DataFrame([
        {
            "name": s["name"],
            "symbol": s["symbol"],
            "sharpe": round(s["metrics"].get("in_sample_metrics", s["metrics"]).get("sharpe", 0), 2)
            if isinstance(s["metrics"], dict) else 0,
            "cagr": round(s["metrics"].get("in_sample_metrics", s["metrics"]).get("cagr", 0), 2)
            if isinstance(s["metrics"], dict) else 0,
            "max_dd": s["metrics"].get("in_sample_metrics", s["metrics"]).get("max_drawdown", 0)
            if isinstance(s["metrics"], dict) else 0,
            "regime": s.get("regime", "N/A"),
        }
        for s in strategies
    ])

    st.dataframe(df, width="stretch", hide_index=True)

    st.markdown("---")
    selected_name = st.selectbox("Select a strategy to inspect", options=df["name"].tolist(), index=0)
    selected_strategy = next(s for s in strategies if s["name"] == selected_name)

    strat_json = selected_strategy.get("parameters", {})
    metrics = selected_strategy.get("metrics", {})

    tab1, tab2, tab3 = st.tabs(["📋 Strategy", "📊 Metrics", "🏷️ Metadata"])

    with tab1:
        st.json(strat_json)

    with tab2:
        if isinstance(metrics, dict):
            if "in_sample_metrics" in metrics:
                st.json(metrics["in_sample_metrics"])
            else:
                st.json(metrics)

    with tab3:
        st.markdown(f"**Regime:** {selected_strategy.get('regime', 'N/A')}")
        st.markdown(f"**Notes:** {selected_strategy.get('notes', 'N/A')}")
