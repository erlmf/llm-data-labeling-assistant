import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("***REMOVED*** "))

MODELS_TO_TEST = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

def can_use(model_name: str) -> bool:
    try:
        model = genai.GenerativeModel(model_name)
        model.generate_content(
            "ping",
            generation_config=genai.types.GenerationConfig(max_output_tokens=1)
        )
        return True
    except Exception as e:
        msg = str(e).lower()
        if "quota" in msg or "429" in msg:
            return False
        return False

usable = []
blocked = []

for m in MODELS_TO_TEST:
    if can_use(m):
        usable.append(m)
    else:
        blocked.append(m)

print("✅ Usable models:")
for m in usable:
    print("-", m)

print("\n❌ Blocked models:")
for m in blocked:
    print("-", m)
