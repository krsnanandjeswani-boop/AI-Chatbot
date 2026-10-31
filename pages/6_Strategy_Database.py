from sidebar_style import apply_sidebar_css
apply_sidebar_css()

import streamlit as st
import pandas as pd
import json

from strategy_database import query_strategies, rename_strategy, delete_strategy

st.set_page_config(page_title="Strategy Database — Atlas", page_icon="⚡", layout="wide")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 2rem; max-width: 1100px;}
h1 {font-weight: 700; letter-spacing: -0.02em; background: linear-gradient(135deg, #FFFFFF 0%, #B0B0B0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.stButton > button {background: linear-gradient(135deg, #D97757 0%, #B85D42 100%); color: white; border: none; border-radius: 8px;}
.stMetric {background: linear-gradient(145deg, #1A1A1A 0%, #151515 100%); border: 1px solid #2A2A2A; border-radius: 10px; padding: 1rem;}
</style>
""", unsafe_allow_html=True)

st.title("Strategy Database")
st.caption("Load, backtest, optimize, and evolve saved strategies")

with st.sidebar:
    st.header("Filters")
    sharpe_threshold = st.slider("Min Sharpe", 0.0, 2.0, 0.0, 0.1)
    regime_filter = st.selectbox("Regime", ["all"], index=0)
    if st.button("Refresh"):
        st.rerun()

strategies = query_strategies(sharpe_gt=sharpe_threshold, regime=regime_filter)

if not strategies:
    st.info("No strategies saved yet. Generate one in Strategy Generator and click 'Save to Database'.")
else:
    st.success(f"{len(strategies)} strategies found")
    
    df = pd.DataFrame([
        {
            "ID": s.get("id"),
            "Name": s["name"],
            "Universe": s["symbol"],
            "Sharpe": round(s["metrics"].get("in_sample_metrics", s["metrics"]).get("sharpe", 0) if isinstance(s["metrics"], dict) else 0, 2),
            "CAGR": f"{s['metrics'].get('in_sample_metrics', s['metrics']).get('cagr', 0):.2%}" if isinstance(s["metrics"], dict) else "N/A",
            "Regime": s.get("regime", "N/A"),
        }
        for s in strategies
    ])
    
    st.dataframe(df, width="stretch", hide_index=True)
    
    st.markdown("---")
    selected_idx = st.selectbox("Select Strategy", range(len(strategies)), format_func=lambda i: f"{strategies[i].get('name','Unnamed')} ({strategies[i].get('symbol','')})")
    selected = strategies[selected_idx]
    strat_id = selected.get("id")
    strat_json = selected.get("parameters", {})
    
    st.markdown("### Load Into Tools")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Load for Backtest", width="stretch"):
            st.session_state["loaded_strategy"] = strat_json
            st.success("Loaded. Go to Backtester to run full validation.")
    with col2:
        if st.button("Load for Optimizer", width="stretch"):
            st.session_state["loaded_strategy_opt"] = strat_json
            st.success("Loaded. Go to Optimizer to run grid search.")
    with col3:
        if st.button("Load for Evolution", width="stretch"):
            st.session_state["loaded_strategy_evo"] = strat_json
            st.success("Loaded. Go to Genetic Evolution to run evolution.")
    with col4:
        if st.button("Load for Quick Test", width="stretch"):
            st.session_state["last_strategy"] = strat_json
            st.success("Loaded. Go to Strategy Generator.")
    
    st.markdown("### Manage Strategy")
    m1, m2, m3 = st.columns([3, 1, 1])
    with m1:
        new_name = st.text_input("Rename strategy", value=selected.get("name", "Unnamed"), key="rename_input")
    with m2:
        if st.button("Rename", width="stretch"):
            if strat_id is not None and new_name.strip():
                rename_strategy(strat_id, new_name.strip())
                st.success("Renamed")
                st.rerun()
    with m3:
        if st.button("Delete", width="stretch", type="secondary"):
            if strat_id is not None:
                delete_strategy(strat_id)
                st.warning("Deleted")
                st.rerun()
    
    tab1, tab2 = st.tabs(["Strategy Details", "Metrics"])
    with tab1:
        st.json(strat_json)
    with tab2:
        st.json(selected.get("metrics", {}))
        if selected.get("notes"):
            st.caption(selected["notes"])

