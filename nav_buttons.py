import streamlit as st

PAGES = [
    ("app.py", "Home"),
    ("pages/1_Strategy_Generator.py", "Strategy Generator"),
    ("pages/2_Backtester.py", "Backtester"),
    ("pages/3_Optimizer.py", "Optimizer"),
    ("pages/4_Genetic_Evolution.py", "Genetic Evolution"),
    ("pages/5_Charts.py", "Charts"),
    ("pages/6_Strategy_Database.py", "Strategy Database"),
    ("pages/7_Chat.py", "AI Chat"),
]

def page_navigation(current_page):
    try:
        idx = next(i for i, (p, _) in enumerate(PAGES) if p == current_page)
    except StopIteration:
        return
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if idx > 0:
            if st.button(f"← {PAGES[idx-1][1]}", use_container_width=True):
                st.switch_page(PAGES[idx-1][0])
    with col2:
        st.markdown(f"<center style='padding-top: 0.5rem; color: #888;'>Page {idx+1} of {len(PAGES)}</center>", unsafe_allow_html=True)
    with col3:
        if idx < len(PAGES)-1:
            if st.button(f"{PAGES[idx+1][1]} →", use_container_width=True):
                st.switch_page(PAGES[idx+1][0])
