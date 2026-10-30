import streamlit as st

st.set_page_config(
    page_title="Atlas — AI Trading Research",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: block !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    button[kind="header"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] button {
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
