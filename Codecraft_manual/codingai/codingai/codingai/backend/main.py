import os
import json
import asyncio
import uuid

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------------------------------------------------
# 🔐 Load ENV & Configure Gemini
# ------------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found. Add it to your .env file.")

genai.configure(api_key=API_KEY)

# 👇 Latest working model (make sure google-generativeai is updated)
# pip install --upgrade google-generativeai
MODEL_NAME = "gemini-2.5-flash"

# ------------------------------------------------------------
# ⚙️ FastAPI app setup
# ------------------------------------------------------------
app = FastAPI(title="CodeCraft Simple Backend", version="1.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # dev ke liye sab allowed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(BASE_DIR, "previews")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "generated_zips")
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ------------------------------------------------------------
# 🚀 Streaming endpoint (frontend se connect hoga)
# ------------------------------------------------------------
@app.post("/api/codecraft/stream")
async def codecraft_stream(
    specs: str = Form(...),
    mode: str = Form(...),
    arch_type: str = Form(...),
):
    """
    React BuildWorkspace yahi endpoint call kar raha hai.
    """

    # Har request ke liye unique session id
    session_id = uuid.uuid4().hex
    preview_file = os.path.join(PREVIEW_DIR, f"{session_id}.html")

    async def generate_stream():
        # Initial logs
        yield f"Initializing {mode.upper()} build...\n"
        await asyncio.sleep(0.5)

        yield f"Connecting to Gemini model ({MODEL_NAME})...\n"
        await asyncio.sleep(0.5)

        logs_text = ""

        try:
            model = genai.GenerativeModel(MODEL_NAME)

            prompt = f"""
You are an AI code generator.

User request:
{specs}

Mode: {mode}
Architecture: {arch_type}

Task:
- Respond like a build terminal: logs, progress messages, some code snippets.
- Do NOT wrap output in markdown fences.
"""

            # google.generativeai streaming
            response = model.generate_content(
                prompt,
                stream=True,
            )

            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    text = chunk.text
                    logs_text += text
                    yield text + "\n"

        except Exception as e:
            err = f"Error: {str(e)}\n"
            yield err
            return

        await asyncio.sleep(0.5)
        yield "\n✅ Build completed successfully!\n"

        # ----------------------------------------------------
        # 🖥️ Simple preview HTML (local file)
        # ----------------------------------------------------
        # Yahan abhi hum simple HTML bana rahe hain jo user ka prompt
        # aur thoda sa logs show kare. Baad mein chaaho to isko
        # Gemini se aane wale real HTML se replace kar sakte ho.
        preview_html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>CodeCraft Preview</title>
    <style>
      body {{
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: radial-gradient(circle at top, #1f2933, #020617);
        color: #f9fafb;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
      }}
      .card {{
        background: rgba(15, 23, 42, 0.92);
        border-radius: 16px;
        padding: 24px 32px;
        max-width: 720px;
        box-shadow: 0 20px 45px rgba(0,0,0,0.6);
        border: 1px solid rgba(148, 163, 184, 0.35);
      }}
      h1 {{
        font-size: 24px;
        margin-bottom: 12px;
        color: #e5e7eb;
      }}
      h2 {{
        font-size: 16px;
        margin: 0 0 8px;
        color: #a5b4fc;
      }}
      .prompt {{
        font-size: 14px;
        color: #e5e7eb;
        background: rgba(30, 64, 175, 0.35);
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 12px;
        white-space: pre-wrap;
      }}
      .meta {{
        font-size: 12px;
        color: #9ca3af;
        margin-bottom: 4px;
      }}
      .note {{
        font-size: 11px;
        color: #6b7280;
        margin-top: 12px;
      }}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>🚀 CodeCraft Preview</h1>
      <div class="meta">Mode: {mode} — Architecture: {arch_type}</div>

      <h2>Prompt</h2>
      <div class="prompt">{specs}</div>

      <h2>Sample Build Log (first 500 chars)</h2>
      <div class="prompt">{logs_text[:500].replace("<", "&lt;").replace(">", "&gt;")}</div>

      <div class="note">
        This is a simple visual preview generated locally.<br/>
        You can extend the backend to compile and run full React/Vite code here.
      </div>
    </div>
  </body>
</html>
"""

        # HTML file likh do
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(preview_html)

        # Local preview URL
        preview_url = f"http://127.0.0.1:4000/preview/{session_id}"

        # Download link abhi bhi dummy hai (baad mein zip real project)
        download_url = "https://example.com/sample.zip"

        meta = {
            "preview_url": preview_url,
            "download_url": download_url,
        }

        # Tumhara frontend yahi pattern parse kar raha hai:
        yield f"\n__ZIP_LINK__ {json.dumps(meta)}\n"

    return StreamingResponse(generate_stream(), media_type="text/plain")


# ------------------------------------------------------------
# 🌐 Preview endpoint (iframe yahan hit karega)
# ------------------------------------------------------------
@app.get("/preview/{session_id}")
def preview_page(session_id: str):
    path = os.path.join(PREVIEW_DIR, f"{session_id}.html")
    if not os.path.exists(path):
        raise HTTPException(404, "Preview not found")
    return FileResponse(path, media_type="text/html")


# ------------------------------------------------------------
# 🏠 Root endpoint
# ------------------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "✅ CodeCraft Backend is running",
        "model": MODEL_NAME,
        "stream_endpoint": "/api/codecraft/stream",
        "preview_example": "/preview/demo-id",
    }


# ------------------------------------------------------------
# 🏁 Local run
# ------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
