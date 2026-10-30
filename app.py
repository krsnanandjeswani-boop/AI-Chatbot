import streamlit as st

st.set_page_config(page_title="Atlas", layout="wide", initial_sidebar_state="collapsed")

# Custom left navigation
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .nav-container {
        position: fixed;
        left: 0;
        top: 0;
        height: 100vh;
        width: 250px;
        background: linear-gradient(180deg, #0F0F0F 0%, #0A0A0B 100%);
        border-right: 1px solid #2A2A2A;
        padding: 2rem 1rem;
        overflow-y: auto;
        z-index: 999;
    }
    
    .nav-logo {
        color: #FFFFFF;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 2rem;
        padding-left: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .nav-link {
        display: block;
        color: #A1A1AA;
        text-decoration: none;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.25rem;
        border-radius: 6px;
        transition: all 0.2s ease;
        font-size: 0.9rem;
    }
    
    .nav-link:hover {
        background: #1A1A1B;
        color: #FFFFFF;
        text-decoration: none;
    }
    
    .main-content {
        margin-left: 250px;
        padding: 2rem 3rem;
    }
</style>

<div class="nav-container">
    <div class="nav-logo">Atlas</div>
    <a href="/" class="nav-link">Home</a>
    <a href="/?page=chat" class="nav-link">AI Chat</a>
    <a href="/?page=generator" class="nav-link">Strategy Generator</a>
    <a href="/?page=backtester" class="nav-link">Backtester</a>
    <a href="/?page=optimizer" class="nav-link">Optimizer</a>
    <a href="/?page=evolution" class="nav-link">Genetic Evolution</a>
    <a href="/?page=charts" class="nav-link">Charts</a>
    <a href="/?page=database" class="nav-link">Strategy Database</a>
</div>
""", unsafe_allow_html=True)

query_params = st.query_params
page = query_params.get("page", "home")

if page == "home":
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("Atlas")
    st.caption("Quantitative Research Terminal")
    st.markdown("Use the navigation menu on the left to access all tools.")
    st.markdown('</div>', unsafe_allow_html=True)
elif page == "chat":
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.switch_page("pages/7_Chat.py")
elif page == "generator":
    st.switch_page("pages/1_Strategy_Generator.py")
elif page == "backtester":
    st.switch_page("pages/2_Backtester.py")
elif page == "optimizer":
    st.switch_page("pages/3_Optimizer.py")
elif page == "evolution":
    st.switch_page("pages/4_Genetic_Evolution.py")
elif page == "charts":
    st.switch_page("pages/5_Charts.py")
elif page == "database":
    st.switch_page("pages/6_Strategy_Database.py")
else:
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("Atlas")
    st.markdown('</div>', unsafe_allow_html=True)
