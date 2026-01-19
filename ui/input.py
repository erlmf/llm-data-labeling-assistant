# ui/input.py
import streamlit as st
import pandas as pd


def render_input(mode: str):
    st.subheader("Input")
    st.markdown("Provide input according to the selected mode")

    uploaded_file = None
    label_input_mode = None
    user_text = ""

    if mode == "Label Suggestion":
        label_input_mode = st.radio(
            "Label Suggestion Input Mode:",
            ["Single Text Input", "Multiple Text", "Upload CSV"],
        )

        if label_input_mode == "Single Text Input":
            user_text = st.text_area(
                "Enter a single customer message:",
                height=200,
                placeholder=(
                    "Example:\n"
                    "\"My transfer to another bank failed but the balance was deducted.\""
                ),
            )

        elif label_input_mode == "Multiple Text":
            raw_multiple = st.text_area(
                "Enter multiple customer messages (one per line):",
                height=240,
                placeholder=(
                    "Example:\n"
                    "My transfer to another bank failed but the balance was deducted.\n"
                    "I want to check my account balance.\n"
                    "How do I reset my password?\n"
                ),
            )
            texts = [t.strip() for t in raw_multiple.split("\n") if t.strip()]
            if texts:
                df = pd.DataFrame({"text": texts})
                user_text = df.to_csv(index=False)

        elif label_input_mode == "Upload CSV":
            uploaded_file = st.file_uploader(
                "Upload CSV with 'text' column:", type=["csv"]
            )
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                st.write("Preview:")
                st.dataframe(df.head())
                user_text = df.to_csv(index=False)

    elif mode == "QA Consistency Check":
        tab1, tab2 = st.tabs(["Direct Text", "Upload CSV"])

        with tab1:
            user_text = st.text_area(
                "Enter multiple rows of text + labels:",
                height=200,
                placeholder=(
                    "Example:\n"
                    "text,label\n"
                    "Transfer failed,complaint\n"
                    "I only want to check my balance,informational\n"
                ),
            )

        with tab2:
            uploaded_file = st.file_uploader(
                "Upload a CSV file with 'text' and 'label' columns:",
                type=["csv"],
            )
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                st.write("Preview:")
                st.dataframe(df.head())
                user_text = df.to_csv(index=False)

    elif mode == "Explain Labeling Guideline":
        user_text = st.text_area(
            "Enter text or instruction:",
            height=200,
            placeholder=(
                "Example:\n"
                "Explain the labeling guideline for our fintech customer support dataset.\n"
            ),
        )

    else:  # Python Data Processing Assistant
        user_text = st.text_area(
            "Enter your data processing request:",
            height=200,
            placeholder=(
                "Example:\n"
                "Generate Python code to read a CSV file, clean missing values, "
                "and create a summary report of label distributions using pandas.\n"
            ),
        )

    return user_text, label_input_mode
