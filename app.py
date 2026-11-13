import streamlit as st

from nav import render_sidebar
from ui_styles import QUANTBOT_ICON, apply_design_system


st.set_page_config(
    page_title="Quantbot — Quantitative Research",
    page_icon=QUANTBOT_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_design_system("overview")
render_sidebar()

st.markdown(
    """
    <section class="home-hero">
        <div class="home-hero-copy">
            <p class="page-eyebrow">Quantitative research platform</p>
            <h1>Research with<br>more conviction.</h1>
            <p class="page-description">
                Design, test, and refine systematic strategies in one focused workspace.
                Turn market ideas into measurable evidence.
            </p>
        </div>
        <div class="home-hero-mark" aria-hidden="true">
            <svg viewBox="0 0 64 64" fill="none">
                <path d="M47 29.5a15.5 15.5 0 1 1-4.5-11"
                      stroke="#D6A06C" stroke-width="3.2" stroke-linecap="round"/>
                <path d="m39 39 10.5 10.5"
                      stroke="#D6A06C" stroke-width="3.2" stroke-linecap="round"/>
                <path d="m20 37 6.3-6.3 5.2 3.9 8.5-9.6"
                      stroke="#F0F2F1" stroke-width="2.4"
                      stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h2 class="section-heading">A disciplined research workflow</h2>', unsafe_allow_html=True)

features = (
    (
        "01",
        "Signal research",
        "Explore data-backed market ideas with clear reasoning, conviction, and risk context.",
    ),
    (
        "02",
        "Strategy validation",
        "Evaluate performance with backtests, walk-forward analysis, and Monte Carlo risk checks.",
    ),
    (
        "03",
        "Parameter discovery",
        "Compare grid-search and evolutionary approaches to find robust strategy settings.",
    ),
)

for column, (index, title, description) in zip(st.columns(3), features):
    with column:
        st.markdown(
            f"""
            <article class="feature-card">
                <span class="feature-index">{index} / 03</span>
                <h3>{title}</h3>
                <p>{description}</p>
            </article>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<h2 class="section-heading">Tools in this workspace</h2>', unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    st.markdown(
        """
        - **Strategy Generator** — Build systematic rules for a ticker or basket.
        - **Backtest Lab** — Review in-sample, out-of-sample, and simulated risk.
        - **Grid Optimizer** — Compare parameter combinations methodically.
        - **Genetic Evolution** — Search a strategy population over generations.
        """
    )
with right:
    st.markdown(
        """
        - **Market Charts** — Inspect price action and technical indicators.
        - **Strategy Library** — Save, review, and reuse research.
        - **AI Research** — Explore tickers, hypotheses, and market context.
        """
    )

st.markdown('<h2 class="section-heading">A simple path from idea to evidence</h2>', unsafe_allow_html=True)
st.markdown(
    """
    1. Explore a market question in **AI Research**.
    2. Turn the thesis into rules with **Strategy Generator**.
    3. Test robustness in **Backtest Lab** and **Market Charts**.
    4. Refine the parameters with **Grid Optimizer** or **Genetic Evolution**.
    5. Save promising work in **Strategy Library**.
    """
)

st.divider()
st.caption(
    "For research and educational purposes only. Not financial advice. "
    "Past performance does not guarantee future results."
)
