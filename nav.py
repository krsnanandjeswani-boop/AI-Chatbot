import streamlit as st


_PAGES = (
    ("app.py", "Overview"),
    ("pages/1_Strategy_Generator.py", "Strategy Generator"),
    ("pages/2_Backtester.py", "Backtest Lab"),
    ("pages/3_Optimizer.py", "Grid Optimizer"),
    ("pages/4_Genetic_Evolution.py", "Genetic Evolution"),
    ("pages/5_Charts.py", "Market Charts"),
    ("pages/6_Strategy_Database.py", "Strategy Library"),
    ("pages/7_Chat.py", "AI Research"),
)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="quantbot-sidebar-brand">
                <div class="quantbot-brand-mark">
                    <svg viewBox="0 0 32 32" fill="none" aria-hidden="true">
                        <path d="M24.1 22.8a10.5 10.5 0 1 1 2.4-6.7"
                              stroke="#D6A06C" stroke-width="2.2" stroke-linecap="round"/>
                        <path d="m20.6 20.7 6.1 6.1"
                              stroke="#D6A06C" stroke-width="2.2" stroke-linecap="round"/>
                        <path d="m9.2 18.5 4.1-4.1 3.2 2.4 5.3-6"
                              stroke="#F0F2F1" stroke-width="1.8"
                              stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div>
                    <p class="quantbot-brand-name">Quantbot</p>
                    <p class="quantbot-brand-caption">Research terminal</p>
                </div>
            </div>
            <p class="quantbot-nav-label">Workspace</p>
            """,
            unsafe_allow_html=True,
        )

        for page_path, label in _PAGES:
            st.page_link(page_path, label=label)

        st.markdown(
            """
            <div class="quantbot-sidebar-footer">
                Quantitative research tools<br>
                For educational use
            </div>
            """,
            unsafe_allow_html=True,
        )
