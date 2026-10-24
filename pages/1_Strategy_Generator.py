import streamlit as st
import json

from strategy_generator import generate_strategy, critique_strategy
from backtester import backtest_strategy

st.set_page_config(page_title="Strategy Generator — Atlas", page_icon="⚡", layout="wide")

# Premium styling
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 2rem; max-width: 1100px;}
h1 {font-weight: 700; letter-spacing: -0.02em; background: linear-gradient(135deg, #FFFFFF 0%, #B0B0B0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
h2 {font-weight: 600; color: #FFFFFF;}
.stButton > button {background: linear-gradient(135deg, #D97757 0%, #B85D42 100%); color: white; border: none; border-radius: 8px; transition: all 0.3s ease;}
.stButton > button:hover {background: linear-gradient(135deg, #E88A6B 0%, #D97757 100%); box-shadow: 0 6px 20px rgba(217, 119, 87, 0.4); transform: translateY(-2px);}
.stTextInput > div > div > input, .stTextArea > div > div > textarea {background-color: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 8px;}
.stTabs [data-baseweb="tab-list"] {gap: 6px;}
.stTabs [data-baseweb="tab"] {background-color: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 8px;}
.stTabs [aria-selected="true"] {background: linear-gradient(135deg, #D97757 0%, #B85D42 100%); border-color: #D97757;}
</style>
""", unsafe_allow_html=True)

st.title("Strategy Generator")
st.caption("LLM-powered strategy design with multi-asset flexibility")

with st.container():
    col1, col2 = st.columns([2, 1])
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
else:
    st.info("Generate a strategy to get started. Leave the ticker field blank to let the AI choose the optimal universe.")
