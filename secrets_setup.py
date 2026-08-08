"""
Bridges Streamlit Cloud secrets into os.environ so all modules using
os.getenv() work identically both locally (via .env) and on Streamlit Cloud.
"""
import os
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

# Copy Streamlit secrets into os.environ
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        for key in st.secrets:
            try:
                val = st.secrets[key]
                if isinstance(val, str):
                    os.environ[key] = val
            except Exception:
                pass
except Exception:
    pass
