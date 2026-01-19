# app.py
import streamlit as st
from ui.sidebar import render_sidebar
from ui.input import render_input
from core.gemini_client import call_gemini
from core import prompts

st.set_page_config(
    page_title="LLM Data Labeling & Quality Assistant",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 LLM Data Labeling & Quality Assistant")

mode = render_sidebar()
user_text, label_input_mode = render_input(mode)

if st.button("🚀 Run"):
    if not user_text.strip():
        st.warning("Please enter or upload some input first.")
        st.stop()

    with st.spinner("Processing with Gemini..."):

        if mode == "Label Suggestion":
            system_prompt = (
                prompts.LABEL_SINGLE
                if label_input_mode == "Single Text Input"
                else prompts.LABEL_BATCH
            )
            temperature = 0.0

        elif mode == "QA Consistency Check":
            system_prompt = prompts.QA_CHECK
            temperature = 0.0

        elif mode == "Explain Labeling Guideline":
            system_prompt = prompts.EXPLAIN_GUIDELINE
            temperature = 0.2

        else:
            system_prompt = prompts.PYTHON_ASSISTANT
            temperature = 0.1

        if mode == "QA Consistency Check":
            output = call_gemini(system_prompt, user_text, temperature=temperature, max_output_tokens=6144)
        else:
            output = call_gemini(system_prompt, user_text, temperature=temperature)

    st.subheader("Output")
    st.write(output)
    st.success("Done! You may copy the output.")
