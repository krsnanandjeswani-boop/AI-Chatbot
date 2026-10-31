import streamlit as st
import json
from ui_styles import (
    page_config, hero, section_header, divider, card_container,
    apply_design_system, metric_card, stat_row, badge, info_card
)
from strategy_generator import generate_strategy, critique_strategy
from backtester import backtest_strategy
from sidebar_style import apply_sidebar_css

apply_sidebar_css()

# ─── Page Config & Design System ────────────────────────────────────────
page_config("Strategy Generator", "🎯")
apply_design_system()

# ─── Hero ────────────────────────────────────────────────────────────────
hero("Strategy Generator", "LLM-powered strategy design with multi-asset flexibility", "🎯")

# ─── Input Section ───────────────────────────────────────────────────────
section_header("Create New Strategy", "Define your universe and objectives")

with card_container():
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

# ─── Display Strategy ────────────────────────────────────────────────────
if "last_strategy" in st.session_state:
    strategy = st.session_state["last_strategy"]

    divider()
    st.markdown(f"## {strategy.get('name', 'Unnamed Strategy')}")

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(metric_card("Type", strategy.get('type', 'N/A').replace('_', ' ').title()), unsafe_allow_html=True)
    with m2:
        st.markdown(metric_card("Universe Size", str(len(strategy.get('universe', [])))), unsafe_allow_html=True)
    with m3:
        st.markdown(metric_card("Entry Rules", str(len(strategy.get('entry', [])))), unsafe_allow_html=True)
    with m4:
        st.markdown(metric_card("Exit Rules", str(len(strategy.get('exit', [])))), unsafe_allow_html=True)

    st.markdown(f"**Universe:** {', '.join(strategy.get('universe', []))}")
    st.info(f"**Thesis:** {strategy.get('rationale', 'No rationale provided.')}")

    # Tabs for details
    tab1, tab2, tab3, tab4 = st.tabs(["Entry Rules", "Exit Rules", "Risk Management", "Full JSON"])

    with tab1:
        with card_container():
            for i, rule in enumerate(strategy.get('entry', []), 1):
                st.markdown(f"**{i}.** `{rule}`")

    with tab2:
        with card_container():
            for i, rule in enumerate(strategy.get('exit', []), 1):
                st.markdown(f"**{i}.** `{rule}`")

    with tab3:
        with card_container():
            rm = strategy.get('risk_management', {})
            c1, c2, c3 = st.columns(3)
            with c1:
                sl = rm.get('stop_loss', 'N/A')
                if isinstance(sl, (int, float)):
                    sl = f"{sl:.1%}"
                st.markdown(metric_card("Stop Loss", str(sl)), unsafe_allow_html=True)
            with c2:
                tp = rm.get('take_profit', 'N/A')
                if isinstance(tp, (int, float)):
                    tp = f"{tp:.1%}"
                st.markdown(metric_card("Take Profit", str(tp)), unsafe_allow_html=True)
            with c3:
                ts = rm.get('trailing_stop', 'N/A')
                if isinstance(ts, (int, float)):
                    ts = f"{ts:.1%}"
                st.markdown(metric_card("Trailing Stop", str(ts)), unsafe_allow_html=True)
            if rm.get('notes'):
                st.markdown(f"**Notes:** {rm['notes']}")

    with tab4:
        with card_container():
            st.json(strategy)

    # Action buttons
    divider()
    section_header("Actions", "Backtest, critique, or save your strategy")

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
                        with m1:
                            st.markdown(metric_card("CAGR", f"{metrics.get('cagr',0):.2%}"), unsafe_allow_html=True)
                        with m2:
                            st.markdown(metric_card("Sharpe", f"{metrics.get('sharpe',0):.2f}"), unsafe_allow_html=True)
                        with m3:
                            st.markdown(metric_card("Max DD", f"{metrics.get('max_drawdown',0):.2%}"), unsafe_allow_html=True)
                        with m4:
                            st.markdown(metric_card("Win Rate", f"{metrics.get('win_rate',0):.2%}"), unsafe_allow_html=True)
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
                    with card_container():
                        st.markdown(critique)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    divider()
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("💾 Save to Database", width="stretch"):
            try:
                from strategy_database import save_strategy
                from final import detect_market_regime
                universe = strategy.get('universe', ['SPY'])
                regime = detect_market_regime(universe[0])
                save_strategy(strategy, {"sharpe": 0, "max_drawdown": 0, "cagr": 0}, regime, "Generated via Strategy Generator")
                st.success("✅ Saved to database!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    with col_d:
        with card_container():
            st.markdown("💡 Go to **Strategy Database** to load and backtest saved strategies")

else:
    # Empty state
    with card_container():
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <h3 style="margin-bottom: 0.5rem;">Ready to Generate</h3>
            <p style="color: var(--color-text-secondary);">Fill in the fields above and click <strong>Generate Strategy</strong> to get started.</p>
            <p style="color: var(--color-text-muted); font-size: 0.875rem; margin-top: 1rem;">Leave the ticker field blank to let the AI choose the optimal universe.</p>
        </div>
        """, unsafe_allow_html=True)