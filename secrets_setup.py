"""
Bridges Streamlit Cloud secrets into os.environ so all modules using
os.getenv() work identically both locally (via .env) and on Streamlit Cloud.
"""
import os
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

def sync_secrets():
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for key in st.secrets:
                try:
                    val = st.secrets[key]
                    if isinstance(val, str):
                        os.environ.setdefault(key, val)
                except Exception:
                    pass
    except Exception:
        pass

sync_secrets()
