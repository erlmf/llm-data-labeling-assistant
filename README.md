# 🧠 LLM Data Labeling & Quality Assistant

An **LLM-powered Streamlit application** designed to support **data scientists and data labeling teams** in building high-quality NLP datasets for fintech and customer support use cases.

This tool helps with:
- Automatic **label suggestions**
- **Label quality assurance (QA)** and consistency checks
- Clear **labeling guideline explanations**
- Lightweight **Python data processing assistance**

---

## ✨ Key Features

### 1️⃣ Label Suggestion
- Single text labeling
- Batch labeling from multiple inputs
- CSV upload support
- Outputs:
  - Primary label
  - Top-3 label candidates with confidence scores
  - Short explanation and key text span

### 2️⃣ QA Consistency Check
- Detects incorrect or inconsistent labels
- Works with:
  - Direct text input
  - CSV uploads (`text`, `label`)
- Produces:
  - Structured Markdown table
  - Clear recommended labels
  - Short summary

### 3️⃣ Explain Labeling Guidelines
- Beginner-friendly explanations
- Examples and counter-examples
- Consistent label taxonomy

### 4️⃣ Python Data Processing Assistant
- Generates clean Python code
- Focused on pandas / ML preprocessing tasks
- Code-only output (ready to run)

---

## 🏗️ Project Structure
```text
llm-data-labeling-assistant/
│
├── app.py # Streamlit app entry point
├── requirements.txt
├── README.md
│
├── core/
│ ├── gemini_client.py # Gemini API wrapper (primary + fallback)
│ ├── prompts.py # All system prompts
│ └── config.py # Environment & secrets handling
│
├── ui/
│ └── sidebar.py # Sidebar UI logic
│
└── .gitignore
```

---

## 🔐 API Key & Security

This project uses **Google Gemini API**.

### ✅ API keys are **never hardcoded**
They are loaded from:
- Streamlit Secrets (`.streamlit/secrets.toml`)
- or environment variables

Example (`.streamlit/secrets.toml` – NOT committed):

```toml
GEMINI_API_KEY = "your_api_key_here"
GEMINI_MODEL_PRIMARY = "gemini-2.5-pro"
GEMINI_MODEL_FALLBACK = "gemini-2.5-flash"
