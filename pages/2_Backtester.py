import streamlit as st

from backtester import run_full_backtest, get_default_universe
from performance_report import format_report
from strategy_generator import generate_strategy
from strategy_database import save_strategy
from final import detect_market_regime
from nav import render_sidebar
from ui_styles import QUANTBOT_ICON, apply_design_system, render_page_header

st.set_page_config(page_title="Backtest Lab — Quantbot", page_icon=QUANTBOT_ICON, layout="wide")

apply_design_system()
render_sidebar()

render_page_header(
    "Strategy lab",
    "Backtest Lab",
    "Validate strategy behavior across historical, out-of-sample, and simulated market conditions.",
)

col1, col2 = st.columns([2, 1])
with col1:
    symbol = st.text_input("Ticker / Universe", placeholder="e.g., SPY or AAPL,MSFT,NVDA (blank = AI chooses)")
with col2:
    period = st.selectbox("Period", ["5y", "3y", "2y"], index=0)

if st.button("Run Full Validation", type="primary", width="stretch"):
    with st.spinner("Generating strategy and running full validation... This may take 60-90 seconds"):
        try:
            if symbol.strip():
                syms = [s.strip().upper() for s in symbol.split(",")]
                strategy = generate_strategy(syms, question="Design a robust strategy for full validation")
            else:
                strategy = generate_strategy(None, question="Design a robust portfolio strategy for full validation")
            
            st.session_state["bt_strategy"] = strategy
            universe = strategy.get("universe", syms if symbol.strip() else get_default_universe())
            
            report = run_full_backtest(universe, strategy, period=period, mc_sims=1000)
            
            if report and "error" not in report:
                st.session_state["bt_report"] = report
                st.success("Validation complete")
                st.rerun()
            else:
                st.error(f"Validation failed: {report.get('error', 'Unknown error') if report else 'No result'}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

if "bt_report" in st.session_state:
    report = st.session_state["bt_report"]
    strategy = st.session_state.get("bt_strategy", report.get("strategy", {}))
    
    st.markdown("---")
    verdict = report.get("verdict", "UNKNOWN")
    reason = report.get("verdict_reason", "")
    
    if verdict == "CONFIRMED":
        st.success(f"**{verdict}** — {reason}")
    elif verdict == "CONDITIONAL":
        st.warning(f"**{verdict}** — {reason}")
    else:
        st.error(f"**{verdict}** — {reason}")
    
    is_m = report.get("in_sample_metrics", {})
    wf = report.get("walk_forward", {})
    mc = report.get("monte_carlo", {})
    
    tab1, tab2, tab3, tab4 = st.tabs(["In-Sample", "Walk-Forward", "Monte Carlo", "Report"])
    
    with tab1:
        if "error" not in is_m:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("CAGR", f"{is_m.get('cagr',0):.2%}")
            c2.metric("Sharpe", f"{is_m.get('sharpe',0):.2f}")
            c3.metric("Max DD", f"{is_m.get('max_drawdown',0):.2%}")
            c4.metric("Profit Factor", f"{is_m.get('profit_factor',0):.2f}")
        else:
            st.warning(is_m["error"])
    
    with tab2:
        if "error" not in wf:
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg OOS Sharpe", f"{wf.get('avg_oos_sharpe',0):.2f}")
            c2.metric("Avg OOS CAGR", f"{wf.get('avg_oos_cagr',0):.2%}")
            c3.metric("Worst OOS Max DD", f"{wf.get('worst_oos_max_drawdown',0):.2%}")
        else:
            st.warning(wf["error"])
    
    with tab3:
        if "error" not in mc:
            c1, c2 = st.columns(2)
            c1.metric("Expected CAGR", f"{mc.get('expected_cagr',0):.2%}")
            c2.metric("P(25% DD)", f"{mc.get('prob_ruin_25pct_dd',0):.2%}")
        else:
            st.warning(mc["error"])
    
    with tab4:
        st.code(format_report(report), language="text")
    
    if st.button("Save to Strategy Library", width="stretch"):
        try:
            regime = detect_market_regime(report.get("universe", ["SPY"])[0])
            save_strategy(strategy, report, regime, "Web validation")
            st.success("Saved successfully")
        except Exception as e:
            st.error(f"Error: {str(e)}")
