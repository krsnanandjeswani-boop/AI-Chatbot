import streamlit as st
from ui_styles import page_config, hero, section_header, divider, feature_grid, apply_design_system

# ─── Page Config & Design System ────────────────────────────────────────
page_config("Atlas", "⚡", "wide", "expanded")
apply_design_system()

# ─── Hero Section ────────────────────────────────────────────────────────
hero(
    "Atlas",
    "AI-Powered Quantitative Research & Trading Intelligence",
    "⚡"
)

st.markdown("""
<div style="text-align: center; max-width: 720px; margin: 0 auto 4rem auto; color: var(--color-text-secondary); font-size: 1.125rem; line-height: 1.6;">
    A precision-built research terminal combining LLMs with real-time market data to generate, validate, and optimize systematic trading strategies with conviction-based signal generation.
</div>
""", unsafe_allow_html=True)

# ─── Features Grid ───────────────────────────────────────────────────────
section_header(
    "Core Capabilities",
    "Four integrated modules for end-to-end quantitative research"
)

features = [
    {
        "icon": "🎯",
        "title": "Signal Generation",
        "description": "Get specific ticker picks with conviction ratings, price targets, and risk management levels."
    },
    {
        "icon": "⚡",
        "title": "Strategy Validation",
        "description": "Rigorous backtesting with walk-forward analysis, Monte Carlo simulation, and data-driven verdicts."
    },
    {
        "icon": "🧬",
        "title": "AI Optimization",
        "description": "Grid search and genetic evolution to discover robust, high-Sharpe parameter combinations."
    },
    {
        "icon": "📊",
        "title": "Interactive Charts",
        "description": "Technical analysis with SMA, Bollinger Bands, RSI, and strategy performance overlays."
    },
    {
        "icon": "💾",
        "title": "Strategy Database",
        "description": "Save, query, and compare validated strategies across market regimes."
    },
    {
        "icon": "💬",
        "title": "AI Chat",
        "description": "Real-time quantitative signals with reasoning — powered by GPT-OSS models."
    },
]

feature_grid(features, cols=3)

# ─── Quick Start ─────────────────────────────────────────────────────────
section_header(
    "Quick Start",
    "Go from idea to validated strategy in minutes"
)

st.markdown("""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
    <div class="card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <div style="width: 32px; height: 32px; border-radius: var(--radius-lg); background: var(--color-accent-light); color: var(--color-accent); display: flex; align-items: center; justify-content: center; font-weight: 600;">1</div>
            <strong>Explore Signals</strong>
        </div>
        <p style="margin: 0; color: var(--color-text-secondary);">Go to <strong>AI Chat</strong> and enable <strong>Signal Mode</strong> for specific picks with conviction ratings.</p>
    </div>
    <div class="card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <div style="width: 32px; height: 32px; border-radius: var(--radius-lg); background: var(--color-accent-light); color: var(--color-accent); display: flex; align-items: center; justify-content: center; font-weight: 600;">2</div>
            <strong>Build Strategy</strong>
        </div>
        <p style="margin: 0; color: var(--color-text-secondary);">Use <strong>Strategy Generator</strong> to create systematic rules tailored to market conditions.</p>
    </div>
    <div class="card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <div style="width: 32px; height: 32px; border-radius: var(--radius-lg); background: var(--color-accent-light); color: var(--color-accent); display: flex; align-items: center; justify-content: center; font-weight: 600;">3</div>
            <strong>Validate</strong>
        </div>
        <p style="margin: 0; color: var(--color-text-secondary);">Run through <strong>Backtester</strong> for full performance analysis: in-sample, walk-forward, Monte Carlo.</p>
    </div>
    <div class="card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <div style="width: 32px; height: 32px; border-radius: var(--radius-lg); background: var(--color-accent-light); color: var(--color-accent); display: flex; align-items: center; justify-content: center; font-weight: 600;">4</div>
            <strong>Optimize</strong>
        </div>
        <p style="margin: 0; color: var(--color-text-secondary);">Refine with <strong>Grid Optimizer</strong> or <strong>Genetic Evolution</strong> for robust parameters.</p>
    </div>
    <div class="card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <div style="width: 32px; height: 32px; border-radius: var(--radius-lg); background: var(--color-accent-light); color: var(--color-accent); display: flex; align-items: center; justify-content: center; font-weight: 600;">5</div>
            <strong>Track</strong>
        </div>
        <p style="margin: 0; color: var(--color-text-secondary);">Save results to <strong>Strategy Database</strong> for future comparison and deployment.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────
divider()
st.markdown("""
<div style="text-align: center; color: var(--color-text-muted); font-size: 0.875rem; padding: 2rem 0;">
    <p>Research & educational purposes only &bull; Not financial advice &bull; Past performance is not indicative of future results</p>
    <p style="margin-top: 0.5rem;">Built with Streamlit & Groq &bull; Powered by GPT-OSS models</p>
</div>
""", unsafe_allow_html=True)
