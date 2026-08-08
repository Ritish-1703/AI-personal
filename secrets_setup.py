"""
Bridges Streamlit Cloud secrets into os.environ so all modules using
os.getenv() work identically both locally (via .env) and on Streamlit Cloud.
Import this at the very top of app.py, before any other project imports.
"""
import os
from dotenv import load_dotenv

# Load .env first (works locally; no-op if file doesn't exist on cloud)
load_dotenv()

# On Streamlit Cloud, secrets are in st.secrets.
# Copy them into os.environ so os.getenv() calls work everywhere.
try:
    import streamlit as st
    for key, value in st.secrets.items():
        if isinstance(value, str):
            os.environ.setdefault(key, value)
except Exception:
    # Not running under Streamlit (e.g., during testing) — skip silently
    pass
