# ui/sidebar.py
import streamlit as st

def render_sidebar():
    st.sidebar.header("Assistant Mode")
    mode = st.sidebar.radio(
        "Choose a mode:",
        [
            "Label Suggestion",
            "QA Consistency Check",
            "Explain Labeling Guideline",
            "Python Data Processing Assistant",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Use Case Overview")
    st.sidebar.write(
        """
This chatbot is designed as an internal tool that can support **Data Scientist** in a fintech company by assisting with:
- Text labeling
- QA checks
- Label guidelines
- Python data processing
"""
    )
    return mode
