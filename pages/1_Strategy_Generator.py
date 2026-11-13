import streamlit as st
import json

from strategy_generator import generate_strategy, critique_strategy
from backtester import backtest_strategy
from nav import render_sidebar
from ui_styles import QUANTBOT_ICON, apply_design_system, render_page_header

st.set_page_config(page_title="Strategy Generator — Quantbot", page_icon=QUANTBOT_ICON, layout="wide")

apply_design_system("strategy-generator")
render_sidebar()

render_page_header(
    "Strategy lab",
    "Strategy Generator",
    "Turn a market thesis into systematic entry, exit, and risk-management rules.",
)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input(
            "Ticker / Universe (optional)",
            placeholder="e.g., AAPL or AAPL,MSFT,NVDA — leave blank for AI to pick optimally",
            help="Leave blank to let the AI choose the best universe for the strategy"
        )
    with col2:
        question = st.text_input(
            "Strategy Goal (optional)",
            value="Design a robust, high-Sharpe trading strategy",
            help="Guide the AI's strategy design"
        )
    
    if st.button("Generate Strategy", type="primary", width="stretch"):
        with st.spinner("Designing strategy with AI... This may take 15-30 seconds"):
            try:
                syms = [s.strip().upper() for s in symbol.split(",")] if symbol and "," in symbol else (symbol.upper() if symbol.strip() else None)
                strategy = generate_strategy(syms, question=question)
                if strategy:
                    st.session_state["last_strategy"] = strategy
                    st.success("Strategy generated successfully")
                    st.rerun()
                else:
                    st.error("Failed to generate strategy. Please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if "last_strategy" in st.session_state:
    strategy = st.session_state["last_strategy"]
    
    st.markdown("---")
    st.markdown(f"## {strategy.get('name', 'Unnamed Strategy')}")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Type", strategy.get('type', 'N/A').replace('_', ' ').title())
    m2.metric("Universe Size", len(strategy.get('universe', [])))
    m3.metric("Entry Rules", len(strategy.get('entry', [])))
    m4.metric("Exit Rules", len(strategy.get('exit', [])))
    
    st.markdown(f"**Universe:** {', '.join(strategy.get('universe', []))}")
    st.info(f"**Thesis:** {strategy.get('rationale', 'No rationale provided.')}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Entry Rules", "Exit Rules", "Risk Management", "Full JSON"])
    
    with tab1:
        for i, rule in enumerate(strategy.get('entry', []), 1):
            st.markdown(f"**{i}.** `{rule}`")
    
    with tab2:
        for i, rule in enumerate(strategy.get('exit', []), 1):
            st.markdown(f"**{i}.** `{rule}`")
    
    with tab3:
        rm = strategy.get('risk_management', {})
        c1, c2, c3 = st.columns(3)
        c1.metric("Stop Loss", f"{rm.get('stop_loss', 0):.1%}" if isinstance(rm.get('stop_loss'), (int,float)) else rm.get('stop_loss', 'N/A'))
        c2.metric("Take Profit", f"{rm.get('take_profit', 0):.1%}" if isinstance(rm.get('take_profit'), (int,float)) else rm.get('take_profit', 'N/A'))
        c3.metric("Trailing Stop", f"{rm.get('trailing_stop', 0):.1%}" if isinstance(rm.get('trailing_stop'), (int,float)) else rm.get('trailing_stop', 'N/A'))
        if rm.get('notes'):
            st.markdown(f"**Notes:** {rm['notes']}")
    
    with tab4:
        st.json(strategy)
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Run Quick Backtest", width="stretch", type="primary"):
            with st.spinner("Backtesting..."):
                try:
                    universe = strategy.get('universe', ['SPY'])
                    sym = universe[0] if universe else 'SPY'
                    metrics = backtest_strategy(sym, strategy)
                    if metrics and 'error' not in metrics:
                        st.success("Backtest Complete")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("CAGR", f"{metrics.get('cagr',0):.2%}")
                        m2.metric("Sharpe", f"{metrics.get('sharpe',0):.2f}")
                        m3.metric("Max DD", f"{metrics.get('max_drawdown',0):.2%}")
                        m4.metric("Win Rate", f"{metrics.get('win_rate',0):.2%}")
                        st.session_state['last_metrics'] = metrics
                    else:
                        st.error(f"Backtest failed: {metrics.get('error', 'Unknown error') if metrics else 'No result'}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col_b:
        if st.button("Get AI Critique", width="stretch"):
            with st.spinner("Analyzing strategy..."):
                try:
                    critique = critique_strategy(strategy, st.session_state.get('last_metrics', {}))
                    st.markdown("### AI Critique")
                    st.markdown(critique)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("Save to Strategy Library", width="stretch"):
            try:
                from strategy_database import save_strategy
                from final import detect_market_regime
                universe = strategy.get('universe', ['SPY'])
                regime = detect_market_regime(universe[0])
                save_strategy(strategy, {"sharpe": 0, "max_drawdown": 0, "cagr": 0}, regime, "Generated via Strategy Generator")
                st.success("Saved to the Strategy Library.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    with col_d:
        st.info("Open Strategy Library to review and reuse saved strategies.")
else:
    st.info("Generate a strategy to get started. Leave the ticker field blank to let the AI choose the optimal universe.")
