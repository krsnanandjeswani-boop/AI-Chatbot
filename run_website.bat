@echo off
cd /d "%~dp0"
echo Starting AI Trading Research Assistant website...
echo.
echo If this is your first time, you may need to install dependencies:
echo   pip install streamlit plotly
echo.
echo Opening in your browser...
streamlit run app.py
