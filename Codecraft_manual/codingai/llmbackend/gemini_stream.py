import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Generator

# -------------------------------------------------------------
# ⚙️ Load Gemini API key from .env file
# -------------------------------------------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("⚠️ GEMINI_API_KEY missing in .env")
else:
    genai.configure(api_key=api_key)

# -------------------------------------------------------------
# 🎯 Model initialization
# -------------------------------------------------------------
model = genai.GenerativeModel("gemini-2.0-flash-exp")


def frontend_qwen_stream(prompt: str) -> Generator[str, None, None]:
    """
    ⚡ Pure Gemini streamer — loads .env key and streams text.
    Just streams whatever prompt text is passed from module1_core.
    """
    try:
        stream = model.generate_content(prompt, stream=True)
        for chunk in stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"\n❌ Gemini streaming error: {e}\n"

    yield "\n✅ Gemini stream complete.\n"
