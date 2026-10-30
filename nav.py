import streamlit as st

st.set_page_config(page_title="Atlas", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.markdown("## Atlas")
    st.page_link("app.py", label="Home")
    st.page_link("pages/1_Strategy_Generator.py", label="Strategy Generator")
    st.page_link("pages/2_Backtester.py", label="Backtester")
    st.page_link("pages/3_Optimizer.py", label="Optimizer")
    st.page_link("pages/4_Genetic_Evolution.py", label="Genetic Evolution")
    st.page_link("pages/5_Charts.py", label="Charts")
    st.page_link("pages/6_Strategy_Database.py", label="Strategy Database")
    st.page_link("pages/7_Chat.py", label="AI Chat")

# Also add to all pages by importing this
