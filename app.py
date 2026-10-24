import streamlit as st

st.set_page_config(
    page_title="Atlas — AI Trading Research",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean, professional CSS (Claude-inspired)
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }
    
    /* Headers */
    h1 {
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #FFFFFF;
    }
    h2 {
        font-weight: 600;
        letter-spacing: -0.01em;
        color: #FFFFFF;
        margin-top: 2rem;
    }
    h3 {
        font-weight: 600;
        color: #FFFFFF;
    }
    
    /* Cards */
    .stMetric {
        background: #1A1A1A;
        border: 1px solid #2A2A2A;
        padding: 1rem;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #D97757 0%, #B85D42 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #E88A6B 0%, #D97757 100%);
        box-shadow: 0 4px 12px rgba(217, 119, 87, 0.3);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-radius: 6px;
        color: #E8E8E8;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D97757;
        border-color: #D97757;
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 1px solid #2A2A2A;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
# Atlas

**AI-Powered Quantitative Research & Trading Signal Platform**

A clean, data-driven research terminal for generating, validating, and deploying systematic trading strategies with LLM-assisted signal generation.

---

## Capabilities

| Feature | Description |
|---|---|
| **Strategy Generator** | Generate custom strategies with LLM reasoning, optimized for specific market conditions |
| **Backtester** | Rigorous validation: in-sample, walk-forward out-of-sample, and Monte Carlo simulation |
| **Optimizer** | Grid search parameter optimization across your universe |
| **Genetic Evolution** | Evolutionary algorithm to discover robust, high-Sharpe strategies |
| **Charts** | Interactive technical analysis with indicators and strategy overlays |
| **Strategy Database** | Query and compare historically validated strategies |
| **AI Chat** | Direct access to quantitative signals with conviction ratings (STRONG BUY/BUY/HOLD/SELL/STRONG SELL) |

---

## Quick Start

1. Navigate to **Strategy Generator** or **AI Chat** from the sidebar
2. Use **AI Chat** with Signal Mode enabled for specific ticker recommendations
3. Run strategies through **Backtester** for full validation
4. Refine with **Optimizer** or **Genetic Evolution**
5. Save validated strategies to the **Database**

---

*Research & educational purposes only. Not financial advice. Past performance is not indicative of future results.*
""")
