# this extra algorithm lists available Google Generative AI models that support content generation configured with a specific API key.
# I wrote this code to check which models are available for use with my API key because I was encountering quota exceeded errors and I was done with it :)
import google.generativeai as genai


API_KEY = "AIzaSyAHWRVD-JmqPTyeG9_C8aQAkvEmMiiF-Pg"
genai.configure(api_key=API_KEY)

print("Kullanılabilir modeller (LÜTFEN ARTIK KOTA AŞILMASIN)")

try:
    for m in genai.list_models():
       
        if 'generateContent' in m.supported_generation_methods:
            print(f"{m.name}")
except Exception as e:
    print(f"Hata: {e}")


''' Model listesi (Kodun çıktısı)
models/gemini-2.5-flash
models/gemini-2.5-pro
models/gemini-2.0-flash-exp
models/gemini-2.0-flash
models/gemini-2.0-flash-001
models/gemini-2.0-flash-exp-image-generation
models/gemini-2.0-flash-lite-001
models/gemini-2.0-flash-lite
models/gemini-2.0-flash-lite-preview-02-05
models/gemini-2.0-flash-lite-preview
models/gemini-2.0-pro-exp
models/gemini-2.0-pro-exp-02-05
models/gemini-exp-1206
models/gemini-2.5-flash-preview-tts
models/gemini-2.5-pro-preview-tts
models/gemma-3-1b-it
models/gemma-3-4b-it
models/gemma-3-12b-it
models/gemma-3-27b-it
models/gemma-3n-e4b-it
models/gemma-3n-e2b-it
models/gemini-flash-latest
models/gemini-flash-lite-latest
models/gemini-pro-latest
models/gemini-2.5-flash-lite
models/gemini-2.5-flash-image-preview
models/gemini-2.5-flash-image
models/gemini-2.5-flash-preview-09-2025
models/gemini-2.5-flash-lite-preview-09-2025
models/gemini-3-pro-preview
models/gemini-3-pro-image-preview
models/nano-banana-pro-preview
models/gemini-robotics-er-1.5-preview
models/gemini-2.5-computer-use-preview-10-2025'''