import streamlit as st
from ui_styles import apply_design_system

# Apply design system to sidebar
apply_design_system()

with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1.5rem 0; border-bottom: 1px solid var(--color-border-subtle); margin-bottom: 1rem;">
        <h1 style="margin: 0; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em;
                   background: linear-gradient(135deg, var(--color-text-primary) 0%, var(--color-text-secondary) 100%);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            ⚡ Atlas
        </h1>
        <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: var(--color-text-muted); font-weight: 500;">
            Quantitative Research Terminal
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.page_link("app.py", label="Home", icon="🏠")
    st.page_link("pages/1_Strategy_Generator.py", label="Strategy Generator", icon="🎯")
    st.page_link("pages/2_Backtester.py", label="Backtester", icon="⚡")
    st.page_link("pages/3_Optimizer.py", label="Optimizer", icon="🔍")
    st.page_link("pages/4_Genetic_Evolution.py", label="Genetic Evolution", icon="🧬")
    st.page_link("pages/5_Charts.py", label="Charts", icon="📈")
    st.page_link("pages/6_Strategy_Database.py", label="Strategy Database", icon="💾")
    st.page_link("pages/7_Chat.py", label="AI Chat", icon="💬")

    st.markdown("""
    <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--color-border-subtle);">
        <p style="font-size: 0.75rem; color: var(--color-text-muted); margin: 0;">
            Research & educational purposes only
        </p>
    </div>
    """, unsafe_allow_html=True)