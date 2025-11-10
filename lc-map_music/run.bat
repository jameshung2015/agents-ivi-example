@echo off
REM Run Streamlit app from project root
cd /d %~dp0
streamlit run app/frontend/app.py
