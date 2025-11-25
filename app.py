# app.py
import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# config streamlit 
st.set_page_config(
    page_title="LLM Data Labeling & Quality Assistant",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 LLM Data Labeling & Quality Assistant")
st.markdown(
     """
This LLM-powered assistant helps **data scientists** and **data labelers** with:
- Automatic **label suggestions** for text data  
- **Quality assurance** (QA) and label consistency checks  
- Explaining **labeling guidelines**  
- Generating Python **data processing snippets**

"""
)

# API Key input
api_key = st.text_input(
    "Enter your Google Generative AI API Key:",
    type="password")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.info("Please enter your Gemini API key to start using the assistant.")
    st.stop()

# initialize model
model = genai.GenerativeModel("gemini-2.5-pro")

# helper function 
def call_gemini(system_prompt: str, user_input: str) -> str:
    """Wrapper to call Gemini API with system prompt + user input"""
    full_prompt = system_prompt + "\n\nUser Input:\n" + user_input
    
    try:
        response = model.generate_content(
        full_prompt,
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=4096,
        ),
    )
    except Exception as e:
        return f"Error calling Gemini API:\n{e}"
    
    if not getattr(response, "candidates", None):
        fb = getattr(response, "prompt_feedback", None)
        if fb and getattr(fb, "block_reason", None):
            return f"Reqest was blocked by safety filters. Block reason: {fb.block_reason} "
        return f"Gemini did not return any content for this request"
    
    cand = response.candidates[0]
    fr = getattr(cand, "finish_reason", None)
    text_parts = []
    if cand.content and getattr(cand.content, "parts", None):
            for part in cand.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)
    text = "".join(text_parts).strip()

    # Kalau benar-benar kosong
    if not text:
        extra = ""
        fb = getattr(response, "prompt_feedback", None)
        if fb and getattr(fb, "block_reason", None):
            extra = f" (safety: {fb.block_reason})"
        return f"Model returned an empty response. finish_reason={fr}{extra}"
    
    # Kalau kena MAX_TOKENS, kasih note tapi tetap balikin teksnya
    if fr == 2:  # MaxTokens
        text += "\n\n---\n_NOTE: Output may be truncated (max token limit)._"

    # Kalau kena SAFETY, kasih info tapi tetap balikin apa yang ada
    elif fr == 3:  # Safety
        text += "\n\n---\n⚠️ SAFETY FILTER TRIGGERED — The model removed or blocked some content."

    # Recitation (4) bisa kamu treat mirip safety atau cukup diinformasikan
    elif fr == 4:  # Recitation
        text += "\n\n---\n⚠️ RECITATION FILTER TRIGGERED — Model detected long verbatim text."

    # Finish reason lain (Other, Blocklist, dsb)
    elif fr not in (None, 0, 1, 2, 3, 4):
        text += f"\n\n---\n(Finish reason: {fr})"


    return text

# sidebar
st.sidebar.header("Assistant Mode")
mode = st.sidebar.radio(
    "Choose a mode:",
    [
        "Label Suggestion",
        "QA Consistency Check",
        "Explain Labeling Guideline",
        "Python Helper",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Use Case Overview")
st.sidebar.write(
    """
This chatbot is designed as an internal tool that can support  
**Data Scientist** in a fintech company by assisting with:

- Text data labeling  
- Label quality validation  
- Label guideline documentation  
- Preparing datasets for LLM training  
"""
)

# input area
st.subheader("Input")
st.write("Provide input according to the selected mode")

uploaded_file = None
label_input_mode = None
user_text = ""

if mode == "Label Suggestion":
    label_input_mode = st.radio(
        "Label Suggestion Input Mode:",
        [
            "Single Text Input",
            "Multiple Text",
            "Upload CSV"
        ]
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
            df_multi = pd.DataFrame({"text": texts})
            user_text = df_multi.to_csv(index=False)
        else:
            user_text = ""

    elif label_input_mode == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV with 'text' column:", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:")
            st.dataframe(df.head())
            user_text = df.to_csv(index=False)
        else:
            user_text = ""

elif mode in ["Explain Labeling Guideline", "Python Helper"]:
    user_text = st.text_area(
        "Enter text or instruction:",
        height=200,
        placeholder=(
            "Example (Explain Labeling Guideline):\n"
            "Explain the labeling guideline for our fintech customer support dataset.\n\n"
            "Example (Python Helper):\n"
            "Generate Python code to split a dataset 80/20 with stratified sampling."
        ),
    )

else:
    tab1, tab2 = st.tabs(["Direct Text", "Upload CSV"])
    with tab1:
        user_text = st.text_area(
             "Enter multiple rows of text + labels (any simple format, e.g., CSV):",
            height=200,
            placeholder=(
                "Example:\n"
                "text,label\n"
                "Transfer failed,complaint\n"
                "I only want to check my balance,informational\n"
            ),
        )
        uploaded_file = None
    with tab2:
        uploaded_file = st.file_uploader(
            "Upload a CSV file with 'text' and 'label' columns:",
            type=["csv"],
        )
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:")
            st.dataframe(df.head())
            user_text = df.to_csv(index=False)

# processing
if st.button("🚀 Run"):
    if not user_text or user_text.strip() == "":
        st.warning("Please enter or upload some input first.")
    else:
        with st.spinner("Processing with Gemini..."):

            # label suggestion
            if mode == "Label Suggestion":
                if label_input_mode == "Single Text Input":
                    system_prompt = """
You are an assistant supporting text data labeling for a fintech company developing an in-house LLM.

The user will send ONE customer message (in English or Indonesian).
Your job is to assign a single best-fit label.

TASK:
- Provide **one primary label** that best matches the text.
- Briefly explain **why** the label was chosen.
- Provide an estimated **confidence score** (0–100%).

RESPONSE FORMAT (English):
**Label:** <label_name>


**Confidence:** <number>%


**Explanation:** <clear, short reasoning>


**Important text span:** "<quote the key text span influencing your decision>"
"""
                else:
                    system_prompt = """
You are an assistant supporting **batch text data labeling** for a fintech company
developing an in-house LLM.

The user will send a small CSV snippet as plain text.  
It will have at least a `text` column, and may include other columns
(e.g. `current_label`) for context.

TASK:
- For **each row**, read the `text` column.
- Assign exactly **one primary label** for that text.
- Provide:
  - label
  - confidence (0–100%)
  - short explanation

OUTPUT FORMAT (English):
Return a **Markdown table** with columns:

| row_index | text | label | confidence | explanation |

- `row_index` is the row number starting from 1.
- Keep `text` reasonably short (truncate if very long).
- Explanations should be 1–2 short sentences.

You can understand both English and Indonesian text,
but always answer in English.
"""
            elif mode == "QA Consistency Check":
                system_prompt = """
You are a QA assistant for a labeled text dataset.

The user will provide raw data (free-form or CSV-like).
TASK:
- Detect **potentially incorrect or inconsistent labels**.
- For each problematic entry, provide:
  - the text
  - the current label
  - your recommended label
  - a short explanation
- If most labels are correct, include a positive summary.
Answer in English and, when helpful, use bullet points or Markdown tables.
"""
            elif mode == "Explain Labeling Guideline":
                system_prompt = """
You are a trainer explaining labeling guidelines to new data labelers.

TASK:
- Explain the labeling guidelines clearly and simply.
- Provide **example sentences** for each label category.
- Include **counter-examples** (common labeling mistakes).

Respond in English with clean structure: headings + bullet points.
"""
            else:  # Python Helper
                system_prompt = """
You are a data science assistant.

The user will request Python code for data processing tasks (pandas, scikit-learn, etc.).

TASK:
- Generate **Python code only** (no long explanations).
- Use clean, readable practices.
- Add short comments where needed.

Respond in English inside a Python markdown code block.
"""
            output = call_gemini(system_prompt, user_text)
        
        st.subheader("Output")
        st.write(output)
        st.success("Done! You may copy the output for documentation or evaluation.")