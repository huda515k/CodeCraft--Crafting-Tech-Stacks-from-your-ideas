import google.generativeai as genai
from typing import Generator
import json

# ============================================================
# ⚙️ Safe Gemini Wrapper (Flash → Pro Fallback)
# ============================================================

def stream_from_gemini(prompt: str, model_name: str = "gemini-2.5-flash") -> Generator[str, None, None]:
    """
    Streams text chunks safely from Gemini models.
    Falls back to gemini-2.5-pro if flash fails or yields nothing.
    """
    system_prefix = (
        "You are an AI code generator specialized in React, TypeScript, Tailwind, and backend code. "
        "Always output clean, runnable code. "
        "If blocked or interrupted, paraphrase safely and continue. "
        "Avoid explanations — only output code or structured text."
    )

    def _safe_yield(stream):
        for chunk in stream:
            text = ""
            try:
                if hasattr(chunk, "text") and chunk.text:
                    text = chunk.text
                elif getattr(chunk, "candidates", None):
                    for cand in chunk.candidates:
                        if hasattr(cand, "content") and cand.content.parts:
                            for part in cand.content.parts:
                                if hasattr(part, "text"):
                                    text += part.text
                if text.strip():
                    yield text
            except Exception as inner_e:
                print(f"[Gemini] ⚠️ Stream parse error: {inner_e}")

    def _do_stream(_model_name: str):
        model = genai.GenerativeModel(model_name=_model_name)
        stream = model.generate_content(f"{system_prefix}\n\n{prompt}", stream=True)
        yield from _safe_yield(stream)

    try:
        yielded_any = False
        for piece in _do_stream(model_name):
            yielded_any = True
            yield piece
        if not yielded_any:
            raise ValueError("Empty output from flash")
    except Exception as e:
        print(f"[Gemini] ⚠️ Flash failed ({e}), retrying with gemini-2.5-pro...")
        try:
            for piece in _do_stream("gemini-2.5-pro"):
                yield piece
        except Exception as e2:
            print(f"[Gemini] ❌ Pro failed: {e2}")


# ============================================================
# 🎨 One-Time Full Frontend Generator
# ============================================================

def frontend_gemini_streaming(specs: str) -> Generator[str, None, None]:
    """
    One-time full frontend generation.
    Generates all files in one go (like monolith backend style).
    Returns multiple code blocks (one per file) inside one stream.
    """
    yield "🧠 Planning + generating full React + TypeScript + Vite + Tailwind project (Gemini)...\n"

    full_prompt = f"""
You are a **senior full-stack engineer**.

Generate a complete, production-ready React + TypeScript + Vite + Tailwind project for a CRM Dashboard.

Specification:
\"\"\"{specs}\"\"\"

✅ Rules:
- Output ALL project files in one response (index.html, vite.config.ts, tailwind.config.js, postcss.config.cjs, tsconfig.json, package.json, src/main.tsx, src/App.tsx, src/pages/*, src/styles/globals.css, etc.).
- No backend calls or axios imports.
- No favicon.ico or <link rel="icon"> in index.html.
- Import Tailwind from './styles/globals.css' or './index.css' (never '/tailwind.css').
- Each file must start and end with code fences like:
```ts filename:src/App.tsx
<file content>
```
end with ```end
- Use `.tsx` for all React/JSX files.
- Must compile in Vite + TypeScript with Tailwind 3+.
- Include minimal working UI: header, sidebar, dashboard cards, etc.
- Include all essential config and setup files (vite, tailwind, postcss, tsconfig, package.json).

🎯 Objective:
Generate a cohesive, buildable project ready to run with:
npm install && npm run dev
"""

    try:
        for chunk in stream_from_gemini(full_prompt):
            yield chunk
    except Exception as e:
        yield f"\n❌ Gemini one-shot generation error: {e}\n"

    yield "\n✅ One-shot frontend generation complete.\n"