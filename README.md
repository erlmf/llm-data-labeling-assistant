# 🧠 LLM Data Labeling & Quality Assistant

An internal **LLM-powered Streamlit application** designed to support **data scientists** and **data labelers** in fintech or enterprise environments.

This tool helps streamline:
- Text data labeling
- Label quality assurance (QA)
- Labeling guideline documentation
- Dataset preparation for LLM training

Built with **Google Gemini API** and designed for **safe deployment** using backend-only secrets.

---

## ✨ Features

### 🔹 Label Suggestion
Automatically suggest labels for:
- Single customer message
- Multiple messages (batch input)
- Uploaded CSV files

Each suggestion includes:
- Primary label
- Confidence score
- Short explanation
- Important text span

---

### 🔹 QA Consistency Check
Detects **potentially incorrect or inconsistent labels** in labeled datasets.

Capabilities:
- Accepts raw text or CSV (`text`, `label`)
- Flags problematic rows only
- Recommends corrected labels
- Outputs a **clean Markdown table**
- Provides a concise summary

Ideal for:
- Label audit
- Dataset validation
- Human-in-the-loop review

---

### 🔹 Explain Labeling Guideline
Helps onboard new labelers by:
- Explaining label definitions
- Giving positive examples
- Highlighting common labeling mistakes

---

### 🔹 Python Helper
Generates **ready-to-use Python code** for:
- Data preprocessing
- Train/validation split
- Stratified sampling
- Pandas / scikit-learn workflows

Output is **code-only** inside Python markdown blocks.

---

## 🏗️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Google Gemini API
- **Language**: Python 3.9+
- **Deployment**: Streamlit Cloud
- **Secrets Management**: Streamlit Secrets / Environment Variables

---

## 📁 Project Structure
```text
.
├── app.py                 # Streamlit UI & LLM orchestration
├── check_models.py        # Gemini model availability checker
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── .gitignore             # Ignore rules
└── .streamlit/
    └── secrets.toml       # API keys & model config (local only)
```
---

## 🔐 Secrets Configuration (IMPORTANT)

This app **does NOT** accept API keys from the UI.

You must configure secrets via **Streamlit Secrets** or environment variables.

### Streamlit Cloud → Secrets
```toml
GEMINI_API_KEY = your_api_key_here
GEMINI_MODEL_PRIMARY = gemini-2.5-flash
GEMINI_MODEL_FALLBACK = gemini-flash-latest
