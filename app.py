import streamlit as st

st.set_page_config(
    page_title="Atlas — AI Trading Research",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium CSS with animations
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Smooth scroll */
    html {
        scroll-behavior: smooth;
    }
    
    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
        animation: fadeIn 0.6s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(217, 119, 87, 0.3); }
        50% { box-shadow: 0 0 30px rgba(217, 119, 87, 0.5); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Headers with gradient */
    h1 {
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 0%, #B0B0B0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeIn 0.8s ease-in;
    }
    
    h2 {
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #FFFFFF;
        margin-top: 2.5rem;
        position: relative;
        padding-bottom: 0.5rem;
    }
    
    h2::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, #D97757 0%, transparent 100%);
    }
    
    h3 {
        font-weight: 600;
        color: #FFFFFF;
    }
    
    /* Hero section */
    .hero {
        text-align: center;
        padding: 2rem 0 3rem 0;
        animation: fadeIn 1s ease-in;
    }
    
    .hero-subtitle {
        color: #A0A0A0;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Feature cards with hover effect */
    .feature-card {
        background: linear-gradient(145deg, #1A1A1A 0%, #151515 100%);
        border: 1px solid #2A2A2A;
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #D97757 50%, transparent 100%);
    }
    
    .feature-card:hover {
        border-color: #D97757;
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(217, 119, 87, 0.2);
    }
    
    .feature-card:hover::before {
        background: linear-gradient(90deg, transparent 0%, #E88A6B 50%, transparent 100%);
    }
    
    /* Metrics */
    .stMetric {
        background: linear-gradient(145deg, #1A1A1A 0%, #151515 100%);
        border: 1px solid #2A2A2A;
        padding: 1.25rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        border-color: #3A3A3A;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #D97757 0%, #B85D42 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #E88A6B 0%, #D97757 100%);
        box-shadow: 0 6px 20px rgba(217, 119, 87, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-radius: 8px;
        color: #E8E8E8;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #D97757;
        box-shadow: 0 0 0 1px rgba(217, 119, 87, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: transparent;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #252525;
        border-color: #3A3A3A;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D97757 0%, #B85D42 100%);
        border-color: #D97757;
        color: white;
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 1px solid #2A2A2A;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #1A1A1A 0%, #151515 100%);
        border: 1px solid #2A2A2A;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #3A3A3A;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F0F0F 0%, #151515 100%);
        border-right: 1px solid #2A2A2A;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: linear-gradient(145deg, #1A1A1A 0%, #151515 100%);
        border: 1px solid #2A2A2A;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.4s ease-in;
    }
    
    /* Links */
    a {
        color: #D97757;
        text-decoration: none;
        transition: color 0.2s ease;
    }
    
    a:hover {
        color: #E88A6B;
        text-decoration: underline;
    }
    
    /* Divider */
    hr {
        border-color: #2A2A2A;
        margin: 2rem 0;
    }
    
    /* Pulse animation for live elements */
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">Atlas</h1>
    <p class="hero-subtitle">AI-Powered Quantitative Research & Trading Intelligence</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## What It Does")
st.markdown("A precision-built research terminal combining GPT-OSS with real-time market data to generate, validate, and optimize systematic trading strategies with conviction-based signal generation.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 Signal Generation</h3>
        <p style="color: #A0A0A0; margin-top: 0.5rem;">Get specific ticker picks with conviction ratings, price targets, and risk management levels.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>⚡ Strategy Validation</h3>
        <p style="color: #A0A0A0; margin-top: 0.5rem;">Rigorous backtesting with walk-forward analysis, Monte Carlo simulation, and data-driven verdicts.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🧬 AI Optimization</h3>
        <p style="color: #A0A0A0; margin-top: 0.5rem;">Grid search and genetic evolution to discover robust, high-Sharpe parameter combinations.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## Core Features")

feat_col1, feat_col2 = st.columns(2)

with feat_col1:
    st.markdown("""
    - **Strategy Generator** — LLM-designed strategies tailored to market conditions
    - **Backtester** — In-sample, walk-forward OOS, Monte Carlo (1000 sims)
    - **Grid Optimizer** — Systematic parameter search
    - **Genetic Evolution** — Evolutionary strategy discovery
    """)

with feat_col2:
    st.markdown("""
    - **Interactive Charts** — Technical analysis with SMA, Bollinger Bands, RSI
    - **Strategy Database** — Query and compare validated strategies
    - **AI Chat** — Real-time quantitative signals with reasoning
    - **Market Intelligence** — Live data from multiple sources
    """)

st.markdown("## Quick Start")
st.markdown("""
1. **Explore Signals** → Go to *AI Chat* and enable *Signal Mode* for specific picks
2. **Build Strategy** → Use *Strategy Generator* to create systematic rules
3. **Validate** → Run through *Backtester* for full performance analysis
4. **Optimize** → Refine with *Optimizer* or *Genetic Evolution*
5. **Track** → Save results to *Strategy Database*
""")

st.divider()
st.markdown("<p style='text-align: center; color: #666;'>Research & educational purposes only • Not financial advice • Past performance is not indicative of future results</p>", unsafe_allow_html=True)
