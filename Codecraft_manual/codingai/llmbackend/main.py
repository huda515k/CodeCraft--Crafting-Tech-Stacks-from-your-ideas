import os
import io
import json
import uuid
import shutil
import traceback
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
import subprocess
import socket
import sys

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

import google.generativeai as genai
from module1_core import (
    prompt_to_frontend,
    extract_files,
    make_zip,
    generate_microservices_backend_streaming,
)
from pipelines_qwen import backend_qwen_stream, integration_qwen_stream


# ============================================================
# ⚙️ SETUP
# ============================================================
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

DOWNLOAD_DIR = "generated_zips"
TEMP_DIR = "temp_previews"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI(title="CodeCraft AI Builder (Windows Optimized)", version="24.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️ GEMINI_API_KEY missing in .env")


# ============================================================
# 🚀 MAIN STREAMING ENDPOINT
# ============================================================
@app.post("/api/generate/stream")
async def generate_stream(
    specs: str = Form(...),
    mode: str = Form("frontend"),  # frontend | backend | integration
    arch_type: str = Form("Monolith"),  # Monolith | Microservices
):
    async def event_stream():
        try:
            session_id = uuid.uuid4().hex
            session_dir = os.path.join(TEMP_DIR, session_id)
            os.makedirs(session_dir, exist_ok=True)

            mode_clean = (mode or "frontend").lower().strip()
            arch_clean = (arch_type or "Monolith").strip()
            arch_lower = arch_clean.lower()

            full_output = ""

            yield f"🔧 Starting {mode_clean} generation | Arch: {arch_clean}\n"

            # ---------------- AI GENERATION ----------------
            if mode_clean == "frontend":
                stream = prompt_to_frontend(specs)

            elif mode_clean == "backend":
                if arch_lower == "monolith":
                    stream = backend_qwen_stream(specs, arch_clean)
                elif arch_lower == "microservices":
                    stream = generate_microservices_backend_streaming(specs)
                else:
                    yield f"❌ Invalid arch_type: {arch_type}\n"
                    yield "__STREAM_END__\n"
                    return

            elif mode_clean == "integration":
                stream = integration_qwen_stream(specs)

            else:
                yield f"❌ Invalid mode: {mode}\n"
                yield "__STREAM_END__\n"
                return

            # ✅ Stream live logs
            for chunk in stream:
                if chunk:
                    full_output += chunk
                    yield chunk

            # 🧩 Ensure full flush
            time.sleep(0.6)
            yield "\n📦 Finalizing generation...\n"
            time.sleep(0.4)
            yield "\n✅ Generation complete. Extracting files...\n"

            # ---------------- EXTRACT FILES ----------------
            files = extract_files(full_output)
            if not files:
                yield "\n❌ No valid files found.\n"
                yield "__STREAM_END__\n"
                return

            for filename, content in files:
                filepath = os.path.join(session_dir, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

            yield f"\n📁 Project files written to: {session_dir}\n"

            # =====================================================
            # 🧱 FRONTEND ONLY → npm install + run dev
            # =====================================================
            if mode_clean == "frontend":
                npm_path = shutil.which("npm.cmd" if os.name == "nt" else "npm")
                if not npm_path:
                    yield "❌ npm not found. Please install Node.js.\n"
                    yield "__STREAM_END__\n"
                    return

                yield "\n📦 Installing dependencies (blocking mode)...\n"

                install_success = False
                attempts = 0
                max_attempts = 3

                while not install_success and attempts < max_attempts:
                    attempts += 1
                    yield f"🔁 Attempt {attempts}: npm install --force\n"

                    try:
                        result = subprocess.run(
                            [npm_path, "install", "--force", "--no-audit", "--no-fund"],
                            cwd=session_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            timeout=1200,
                        )
                        yield result.stdout

                        if result.returncode == 0:
                            install_success = True
                            yield "✅ npm install completed successfully.\n"
                        else:
                            yield f"⚠️ npm install failed (exit {result.returncode}), retrying...\n"
                            time.sleep(5)

                    except subprocess.TimeoutExpired:
                        yield "⏰ npm install timed out — retrying...\n"
                        subprocess.run([npm_path, "install", "--legacy-peer-deps", "--force"], cwd=session_dir)

                if not install_success:
                    yield "❌ npm install failed after 3 attempts. Aborting preview.\n"
                    yield "__STREAM_END__\n"
                    return

                # -------------------------------------------------
                # 🚀 Launch CMD with npm run dev
                # -------------------------------------------------
                yield "\n🚀 Launching Vite dev server in new CMD window...\n"

                if os.name == "nt":
                    subprocess.Popen(
                        ["start", "cmd", "/K", f"cd /d {session_dir} && npm run dev -- --port 5174"],
                        shell=True,
                    )

                else:
                    subprocess.Popen(
                        ["gnome-terminal", "--", "bash", "-c", f"cd {session_dir} && npm run dev; exec bash"]
                    )

                # Wait a bit for server start
                time.sleep(6)
                preview_url = "http://localhost:5174"
                yield f"\n🌐 Live Preview: {preview_url}\n"
                yield f"💡 Manual: cd {session_dir} && npm run dev\n"

            # =====================================================
            # 📦 ZIP CREATION (ALL MODES)
            # =====================================================
            yield "\n📦 Creating ZIP package...\n"
            zip_bytes = make_zip(files)
            zip_name = f"{uuid.uuid4().hex}.zip"
            zip_path = os.path.join(DOWNLOAD_DIR, zip_name)
            with open(zip_path, "wb") as f:
                f.write(zip_bytes.getvalue())

            base_url = "http://127.0.0.1:4002"
            dl = f"{base_url}/api/download/{zip_name}"

            # ✅ JSON link for React frontend
            zip_meta = {
                "download_url": dl,
                "preview_url": "http://localhost:5173" if mode_clean == "frontend" else None,
            }
            yield f"\n⬇ Download ZIP: {dl}\n"
            yield f"\n__ZIP_LINK__ {json.dumps(zip_meta)}\n"
            yield "\n__STREAM_END__\n"

        except Exception as e:
            logging.error(traceback.format_exc())
            yield f"\n❌ ERROR: {e}\n"
            yield "__STREAM_END__\n"

    return StreamingResponse(event_stream(), media_type="text/plain")



# ============================================================
# 📦 ZIP DOWNLOAD ENDPOINT
# ============================================================
@app.get("/api/download/{filename}")
def download_file(filename: str):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")
    return FileResponse(path, media_type="application/zip", filename=filename)


# ============================================================
# 🏠 ROOT
# ============================================================
@app.get("/")
def home():
    return {
        "message": "✅ CodeCraft AI Builder Running (Windows Optimized)",
        "modes": ["frontend (build + preview)", "backend", "integration"],
        "docs": "/docs",
    }
