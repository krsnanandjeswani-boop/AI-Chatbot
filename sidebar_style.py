import streamlit as st

def apply_sidebar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0a0a 0%, #050505 100%) !important;
            border-right: 1px solid #1f1f1f !important;
        }
        
        [data-testid="stSidebarNav"] {
            padding-top: 1rem !important;
        }
        
        [data-testid="stSidebarNav"] a {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            color: #a1a1aa !important;
            padding: 0.5rem 0.875rem !important;
            margin: 0.125rem 0.5rem !important;
            border-radius: 6px !important;
            transition: all 0.15s ease-in-out !important;
            letter-spacing: -0.01em !important;
        }
        
        [data-testid="stSidebarNav"] a:hover {
            background-color: #141414 !important;
            color: #ffffff !important;
            transform: translateX(4px) !important;
            box-shadow: inset 2px 0 0 #d97757 !important;
        }
        
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #141414 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: inset 2px 0 0 #d97757 !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            font-family: 'Inter', sans-serif !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em !important;
            padding: 0 0.5rem !important;
        }
        
        [data-testid="stSidebar"] hr {
            border-color: #1f1f1f !important;
            margin: 1rem 0.5rem !important;
        }
        
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        [data-testid="stSidebarUserContent"] {
            padding-top: 1.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
