# app.py
import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# =========================
# Streamlit config
# =========================
st.set_page_config(
    page_title="LLM Data Labeling & Quality Assistant",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 LLM Data Labeling & Quality Assistant")
st.markdown(
    """
This LLM-powered assistant helps **data scientists** with:
- Automatic **label suggestions** for text data  
- **Quality assurance** (QA) and label consistency checks  
- Explaining **labeling guidelines**  
- Generating Python **data processing**
"""
)

# =========================
# API key from backend only (secrets/env)
# =========================
def _get_secret(name: str):
    # Streamlit secrets first
    try:
        return st.secrets.get(name, None)
    except Exception:
        return None

api_key = _get_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "Server is not configured with GEMINI_API_KEY.\n\n"
        "Set it in Streamlit Secrets (recommended) or as an environment variable."
    )
    st.stop()

genai.configure(api_key=api_key)

# =========================
# Model setup (primary + fallback)
# =========================
PRIMARY_MODEL_NAME = (
    _get_secret("GEMINI_MODEL_PRIMARY")
    or os.getenv("GEMINI_MODEL_PRIMARY")
    or "gemini-2.5-pro"
)
FALLBACK_MODEL_NAME = (
    _get_secret("GEMINI_MODEL_FALLBACK")
    or os.getenv("GEMINI_MODEL_FALLBACK")
    or "gemini-2.5-flash"
)

primary_model = genai.GenerativeModel(PRIMARY_MODEL_NAME)
fallback_model = genai.GenerativeModel(FALLBACK_MODEL_NAME)

st.sidebar.caption("Backend model config")
st.sidebar.write(f"Primary: `{PRIMARY_MODEL_NAME}`")
st.sidebar.write(f"Fallback: `{FALLBACK_MODEL_NAME}`")

# =========================
# Helper function
# =========================
def call_gemini(
        system_prompt: str, 
        user_input: str, 
        temperature: float = 0.2,
        max_output_tokens: int = 4096
) -> str:
    """Wrapper to call Gemini API with system prompt + user input (with fallback on 429/quota)."""
    full_prompt = system_prompt + "\n\nUser Input:\n" + user_input

    generation_cfg = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    def _extract_text(response) -> str:
        if not getattr(response, "candidates", None):
            fb = getattr(response, "prompt_feedback", None)
            if fb and getattr(fb, "block_reason", None):
                return f"Request was blocked by safety filters. Block reason: {fb.block_reason}"
            return "Gemini did not return any content for this request."

        cand = response.candidates[0]
        fr = getattr(cand, "finish_reason", None)

        text_parts = []
        if cand.content and getattr(cand.content, "parts", None):
            for part in cand.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)

        text = "".join(text_parts).strip()

        if not text:
            extra = ""
            fb = getattr(response, "prompt_feedback", None)
            if fb and getattr(fb, "block_reason", None):
                extra = f" (safety: {fb.block_reason})"
            return f"Model returned an empty response. finish_reason={fr}{extra}"

        # Notes for finish reasons
        if fr == 2:  # MaxTokens
            text += "\n\n---\n_NOTE: Output may be truncated (max token limit)._"
        elif fr == 3:  # Safety
            text += "\n\n---\n⚠️ SAFETY FILTER TRIGGERED — The model removed or blocked some content."
        elif fr == 4:  # Recitation
            text += "\n\n---\n⚠️ RECITATION FILTER TRIGGERED — Model detected long verbatim text."
        elif fr not in (None, 0, 1, 2, 3, 4):
            text += f"\n\n---\n(Finish reason: {fr})"

        return text

    # Try primary first
    try:
        response = primary_model.generate_content(
            full_prompt,
            generation_config=generation_cfg,
        )
        return _extract_text(response)

    except Exception as e:
        msg = str(e).lower()

        # Fallback on quota / 429 / rate-limit style errors
        if ("429" in msg) or ("quota" in msg) or ("rate" in msg) or ("too many requests" in msg):
            try:
                response = fallback_model.generate_content(
                    full_prompt,
                    generation_config=generation_cfg,
                )
                out = _extract_text(response)
                return out + "\n\n---\n_Used fallback model due to quota/rate limit on primary._"
            except Exception as e2:
                return f"Error calling Gemini API:\nPrimary failed (quota/rate): {e}\nFallback failed: {e2}"

        return f"Error calling Gemini API:\n{e}"

# =========================
# Sidebar
# =========================
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
- Text data labeling  
- Label quality validation  
- Label guideline documentation  
- Preparing training datasets with Python 
"""
)

# =========================
# Input area
# =========================
st.subheader("Input")

uploaded_file = None
label_input_mode = None
user_text = ""

if mode == "Label Suggestion":
    label_input_mode = st.radio(
        "Label Suggestion Input Mode:",
        [
            "Single Text Input",
            "Multiple Text",
            "Upload CSV",
        ],
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

elif mode in ["QA Consistency Check"]:
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

elif mode in ["Explain Labeling Guideline"]:
    user_text = st.text_area(
        "Enter text or instruction:",
        height=200,
        placeholder=(
            "Example :\n"
            "Explain the labeling guideline for our fintech customer support dataset.\n\n"
        ),
    )
else:  # Python Data Processing Assistant
    user_text = st.text_area(
        "Enter your data processing request:",
        height=200,
        placeholder=(
            "Example:\n"
            "Generate Python code to read a CSV file, clean missing values, "
            "and create a summary report of label distributions using pandas.\n\n"
        ),
    )
    

# =========================
# Processing
# =========================
if st.button("🚀 Run"):
    if not user_text or user_text.strip() == "":
        st.warning("Please enter or upload some input first.")
    else:
        with st.spinner("Processing with Gemini..."):

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

RULES (must follow):
- If the message mentions balance discrepancy keywords such as:
"balance looks wrong", "incorrect balance", "wrong balance", "missing money",
"unexpected balance", "balance decreased/increased", "saldo tidak sesuai",
then label MUST be: Transaction Issue.
- Do NOT use Account_Management for balance discrepancies.
- Account_Management is ONLY for: profile changes, settings, or account details.
- Transaction Inquiry is ONLY when the user asks about transaction status/history WITHOUT reporting an error (no failed/deducted/missing/wrong/charged).

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

The user will provide raw data (free-form or CSV-like) containing at least:
- text
- label
TASK:
- Detect **potentially incorrect or inconsistent labels**.
- For each problematic entry, recommend the correct label.

CRITICAL OUTPUT RULES (must follow):
1) FIRST output a Markdown table with ALL problematic rows (no intro text before the table).
2) AFTER the table, provide a short summary (max 2 sentences).
3) Keep explanations concise (max 1 sentence).
4) If there are no issues, output: "No obvious label issues found." (and no table).

TABLE FORMAT (exact):
| row_index | text | current_label | recommended_label | explanation |
|---|---|---|---|---|

- row_index starts at 1 based on the provided order.
- Truncate long text to ~120 characters.

Answer in English. Follow the CRITICAL OUTPUT RULES strictly.
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

            else:  # Python Data Processing Assistant
                system_prompt = """
You are a data science assistant.

The user will request Python code for data processing tasks (pandas, scikit-learn, etc.).

TASK:
- Generate **Python code only** (no long explanations).
- Use clean, readable practices.
- Add short comments where needed.

Respond in English inside a Python markdown code block.
"""

            if mode == "Label Suggestion":
                temperature = 0.0
            elif mode == "QA Consistency Check":
                temperature = 0.0
            elif mode == "Explain Labeling Guideline":
                temperature = 0.2
            else: # Python Data Processing Assistant
                temperature = 0.1
            
            # single gemini call
            if mode == "QA Consistency Check":
                output = call_gemini(system_prompt, user_text, temperature=temperature, max_output_tokens=6144)
            else:
                output = call_gemini(system_prompt, user_text, temperature=temperature)

        st.subheader("Output")
        st.write(output)
        st.success("Done! You may copy the output for documentation or evaluation.")
