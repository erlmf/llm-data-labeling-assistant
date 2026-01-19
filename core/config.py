# core/config.py
import os
import streamlit as st

def get_secret(name: str, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.getenv(name, default)

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Configure it in Streamlit secrets or environment variables."
    )

PRIMARY_MODEL_NAME = get_secret("GEMINI_MODEL_PRIMARY", "gemini-2.5-flash")
FALLBACK_MODEL_NAME = get_secret("GEMINI_MODEL_FALLBACK", "gemini-flash-latest")
