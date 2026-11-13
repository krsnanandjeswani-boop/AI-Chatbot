import streamlit as st
import pandas as pd
import json

from strategy_database import query_strategies, rename_strategy, delete_strategy
from nav import render_sidebar
from ui_styles import QUANTBOT_ICON, apply_design_system, render_page_header

st.set_page_config(page_title="Strategy Library — Quantbot", page_icon=QUANTBOT_ICON, layout="wide")

apply_design_system("strategy-library")
render_sidebar()

render_page_header(
    "Research library",
    "Strategy Library",
    "Keep validated strategies organized and ready to reuse across research tools.",
)

with st.sidebar:
    st.header("Filters")
    sharpe_threshold = st.slider("Min Sharpe", 0.0, 2.0, 0.0, 0.1)
    regime_filter = st.selectbox("Regime", ["all"], index=0)
    if st.button("Refresh library"):
        st.rerun()

strategies = query_strategies(sharpe_gt=sharpe_threshold, regime=regime_filter)

if not strategies:
    st.info("No strategies saved yet. Generate one and save it to the Strategy Library.")
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
    if not isinstance(strat_json, dict):
        st.error("This saved strategy is not a valid JSON object and cannot be loaded.")
        st.stop()
    strategy_universe = strat_json.get("universe")
    if not isinstance(strategy_universe, list) or not strategy_universe:
        strategy_universe = selected.get("symbol", "").split("+")
    symbols_text = ",".join(str(symbol) for symbol in strategy_universe if str(symbol).strip())
    
    st.markdown("### Use this strategy")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Load for Backtest", width="stretch"):
            st.session_state["loaded_strategy"] = strat_json
            st.session_state["bt_symbols"] = symbols_text
            st.session_state.pop("bt_strategy", None)
            st.session_state.pop("bt_report", None)
            st.switch_page("pages/2_Backtester.py")
    with col2:
        if st.button("Load for Optimizer", width="stretch"):
            st.session_state["loaded_strategy_opt"] = strat_json
            st.session_state["opt_symbols"] = symbols_text
            st.session_state.pop("grid_results", None)
            st.switch_page("pages/3_Optimizer.py")
    with col3:
        if st.button("Load for Evolution", width="stretch"):
            st.session_state["loaded_strategy_evo"] = strat_json
            st.session_state["evo_symbols"] = symbols_text
            st.session_state.pop("evolution_result", None)
            st.switch_page("pages/4_Genetic_Evolution.py")
    with col4:
        if st.button("Load for Quick Test", width="stretch"):
            st.session_state["last_strategy"] = strat_json
            st.session_state.pop("last_metrics", None)
            st.switch_page("pages/1_Strategy_Generator.py")
    
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
    
    tab1, tab2 = st.tabs(["Strategy details", "Metrics"])
    with tab1:
        st.json(strat_json)
    with tab2:
        st.json(selected.get("metrics", {}))
        if selected.get("notes"):
            st.caption(selected["notes"])

