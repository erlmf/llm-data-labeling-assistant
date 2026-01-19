# core/gemini_client.py
import google.generativeai as genai
from core.config import GEMINI_API_KEY, PRIMARY_MODEL_NAME, FALLBACK_MODEL_NAME

# ✅ CONFIGURE SEKALI, PAKAI KEY YANG BENAR
genai.configure(api_key=GEMINI_API_KEY)

_primary = genai.GenerativeModel(PRIMARY_MODEL_NAME)
_fallback = genai.GenerativeModel(FALLBACK_MODEL_NAME)

def _extract_text(response) -> str:
    if not getattr(response, "candidates", None):
        fb = getattr(response, "prompt_feedback", None)
        if fb and getattr(fb, "block_reason", None):
            return f"Request blocked by safety filters: {fb.block_reason}"
        return "No content returned."

    cand = response.candidates[0]
    fr = getattr(cand, "finish_reason", None)

    parts = []
    if cand.content and getattr(cand.content, "parts", None):
        for part in cand.content.parts:
            if hasattr(part, "text") and part.text:
                parts.append(part.text)

    text = "".join(parts).strip()
    if not text:
        return f"Empty response (finish_reason={fr})"

    if fr == 2:
        text += "\n\n---\n_NOTE: Output may be truncated._"

    return text


def call_gemini(
    system_prompt: str,
    user_input: str,
    temperature: float = 0.2,
    max_output_tokens: int = 4096,
) -> str:
    prompt = f"{system_prompt}\n\nUser Input:\n{user_input}"

    cfg = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    try:
        resp = _primary.generate_content(prompt, generation_config=cfg)
        return _extract_text(resp)

    except Exception as e:
        msg = str(e).lower()
        if any(k in msg for k in ["429", "quota", "rate", "too many requests"]):
            try:
                resp = _fallback.generate_content(prompt, generation_config=cfg)
                return _extract_text(resp) + "\n\n---\n_Used fallback model._"
            except Exception as e2:
                return f"Primary failed: {e}\nFallback failed: {e2}"

        return f"Error calling Gemini API: {e}"

