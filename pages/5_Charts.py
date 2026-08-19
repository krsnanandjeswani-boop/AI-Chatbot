import streamlit as st
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backtester import fetch_price_data, calculate_indicators, evaluate_strategy

st.set_page_config(page_title="Charts", page_icon="📈", layout="wide")

st.title("📈 Charts & Visualizations")
st.caption("Price charts with technical indicators, and strategy performance overlays.")


def plotly_price_chart(symbol, period="1y", show_indicators=True):
    """Render an interactive price chart with indicators using Plotly."""
    df = fetch_price_data(symbol, period=period)
    if df is None or df.empty:
        return None

    if show_indicators:
        df = calculate_indicators(df)

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.25, 0.25],
    )

    # Price + SMAs
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close", line=dict(color="blue")), row=1, col=1)
    if show_indicators and "SMA_20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20", line=dict(color="orange", width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="SMA 50", line=dict(color="green", width=1)), row=1, col=1)
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)

    # Bollinger Bands
    if show_indicators and "BB_upper" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], name="BB Upper", line=dict(color="gray", width=1, dash="dot")), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], name="BB Lower", line=dict(color="gray", width=1, dash="dot")), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price", line=dict(color="blue", width=1)), row=2, col=1)

    # RSI
    if show_indicators and "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="purple")), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        fig.update_yaxes(range=[0, 100], row=3, col=1)

    fig.update_layout(
        title=f"{symbol} Price Chart",
        height=600,
        template="plotly_dark",
        hovermode="x unified",
    )
    return fig


def plotly_strategy_chart(symbol, strategy, period="5y"):
    """Render an interactive strategy performance chart."""
    df = fetch_price_data(symbol, period=period)
    if df is None or df.empty:
        return None

    df = calculate_indicators(df)
    df = evaluate_strategy(df, strategy)

    if "strategy_ret" not in df.columns:
        return None

    cum_ret = (1 + df["strategy_ret"].fillna(0)).cumprod()

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.4],
    )
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close", line=dict(color="blue")), row=1, col=1)
    if "SMA_20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20", line=dict(color="orange", width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="SMA 50", line=dict(color="green", width=1)), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=cum_ret, name="Cumulative Strategy Return",
                             line=dict(color="lime"), fill="tonexty"), row=2, col=1)

    fig.update_layout(
        title=f"{symbol} - Strategy: {strategy.get('name', 'Unnamed')}",
        height=600,
        template="plotly_dark",
        hovermode="x unified",
    )
    return fig


tab1, tab2 = st.tabs(["📉 Price Chart with Indicators", "📊 Strategy Performance Chart"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        symbol = st.text_input("Symbol", value="AAPL", key="price_symbol")
    with col2:
        period = st.selectbox("Period", ["1y", "2y", "5y", "max"], index=0, key="price_period")
        show_indicators = st.checkbox("Show Indicators (SMA/Bollinger/RSI)", value=True, key="show_ind")

    if st.button("Generate Price Chart"):
        if symbol:
            with st.spinner(f"Fetching {symbol} data..."):
                fig = plotly_price_chart(symbol.upper(), period, show_indicators)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"No data available for {symbol.upper()}")
        else:
            st.warning("Please enter a symbol.")

with tab2:
    col1, col2 = st.columns([2, 1])
    with col1:
        strat_symbol = st.text_input("Symbol", value="AAPL", key="strat_symbol")
    with col2:
        strat_period = st.selectbox("Period", ["3y", "5y"], index=1, key="strat_period")

    st.markdown("---")
    if "last_strategy" in st.session_state:
        st.info(f"Using strategy from session: **{st.session_state['last_strategy'].get('name', 'Unknown')}**")
        use_session = st.checkbox("Use this session strategy", value=True, key="use_session_strat")
    else:
        use_session = False

    if st.button("Generate Strategy Chart"):
        if not strat_symbol:
            st.warning("Please enter a symbol.")
        else:
            strategy = st.session_state["last_strategy"] if use_session else None
            if not strategy:
                from strategy_generator import generate_strategy
                with st.spinner("Generating strategy via LLM..."):
                    strategy = generate_strategy(strat_symbol.upper())
            with st.spinner(f"Backtesting strategy on {strat_symbol.upper()}..."):
                fig = plotly_strategy_chart(strat_symbol.upper(), strategy, strat_period)
            if fig:
                st.session_state["last_strategy"] = strategy
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to generate strategy chart.")
