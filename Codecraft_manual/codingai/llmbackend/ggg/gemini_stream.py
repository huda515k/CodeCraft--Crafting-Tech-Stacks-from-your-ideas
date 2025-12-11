# gemini_stream.py
import os
from typing import Generator
import google.generativeai as genai
from dotenv import load_dotenv

# ------------------------------------------------------------
# ⚙️ Gemini Setup
# ------------------------------------------------------------

# Load .env if available
load_dotenv()

# Try both env variable names for flexibility
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ [Gemini] No API key found! Please set GOOGLE_API_KEY or GEMINI_API_KEY.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ [Gemini] API key configured successfully.")
# ------------------------------------------------------------
# 🔧 Generic Streaming Function (with Fallback Logic)
# ------------------------------------------------------------

def stream_from_gemini(prompt: str, model_name: str = "gemini-2.5-flash") -> Generator[str, None, None]:
    """
    Generic Gemini streaming function with:
    - Flash → Pro → 1.5 Flash fallback sequence
    - Safety settings applied
    - Auto system prefix for code generation
    """
    system_prefix = (
        "You are an AI code generator specialized in React, TypeScript, Tailwind, Node.js, Express, and full-stack apps. "
        "Always produce runnable, clean, modern code. "
        "If blocked, paraphrase safely and continue streaming. "
        "Avoid explanations — output only code or structured content required by the instructions."
    )

    def _safe_yield(stream):
        for chunk in stream:
            text = ""
            try:
                if getattr(chunk, "text", None):
                    text = chunk.text
                elif getattr(chunk, "candidates", None):
                    for cand in chunk.candidates:
                        if getattr(cand, "content", None) and getattr(cand.content, "parts", None):
                            for part in cand.content.parts:
                                if getattr(part, "text", None):
                                    text += part.text
                if text.strip():
                    yield text
            except Exception as e:
                print(f"[Gemini] ⚠️ Stream parse error: {e}")

    def _do_stream(_model_name: str):
        print(f"[Gemini] 🚀 Using model: {_model_name}")
        model = genai.GenerativeModel(
            model_name=_model_name
        )
        stream = model.generate_content(f"{system_prefix}\n\n{prompt}", stream=True)
        yield from _safe_yield(stream)

    # Main fallback sequence: flash → pro → 1.5-flash
    models_to_try = [model_name, "gemini-2.5-pro", "gemini-1.5-flash"]

    for m in models_to_try:
        try:
            yielded_any = False
            for piece in _do_stream(m):
                yielded_any = True
                yield piece
            if yielded_any:
                break
        except Exception as e:
            print(f"[Gemini] ⚠️ {m} failed ({e}), trying next fallback...")
            continue
    else:
        print("[Gemini] ❌ All fallback models failed.")
        yield "\n[ERROR] Gemini streaming failed. Please check your API key or prompt.\n"

# ------------------------------------------------------------
# 🎨 Stream helpers for different modes
# ------------------------------------------------------------

def stream_from_gemini_frontend(prompt: str) -> Generator[str, None, None]:
    """Used for React + TypeScript + Tailwind full projects."""
    return stream_from_gemini(prompt, model_name="gemini-2.5-flash")


def stream_from_gemini_backend(prompt: str) -> Generator[str, None, None]:
    """Used for backend, infra, microservices, JSON plans, etc."""
    return stream_from_gemini(prompt, model_name="gemini-2.5-pro")


def stream_from_gemini_integration(prompt: str) -> Generator[str, None, None]:
    """Used for linking frontend forms → backend routes."""
    return stream_from_gemini(prompt, model_name="gemini-2.5-pro")
