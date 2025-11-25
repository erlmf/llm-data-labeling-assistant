import google.generativeai as genai

# 1) Ask API key from user (same key as in Streamlit)
api_key = input("Enter your Gemini API key: ").strip()
if not api_key:
    print("No API key provided. Exiting.")
    exit()

# 2) Configure client
genai.configure(api_key=api_key)

# 3) List models
print("Listing available models that support generateContent:\n")
models = genai.list_models()

found_any = False
for m in models:
    if hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
        print("-", m.name)
        found_any = True

if not found_any:
    print("No models with generateContent found. Check your API key / permissions.")
