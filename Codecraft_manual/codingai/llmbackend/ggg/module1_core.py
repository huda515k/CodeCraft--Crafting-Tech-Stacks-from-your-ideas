import os, io, re, json, zipfile
from gemini_stream import (
    stream_from_gemini_frontend,
    stream_from_gemini_backend,
    stream_from_gemini_integration,
)
from module1_templates import (
    backend_prompt_template,
    frontend_prompt_template,
    frontend_to_backend_template,
    microservices_planner_prompt,
    microservice_code_prompt,
    microservices_infra_prompt,
)

from qwen_stream import stream_from_qwen

# ============================================================
# 🚀 Prompt Handlers (Frontend, Backend, Integration, Microservices)
# ============================================================

def prompt_to_frontend(specs: str):
    """
    Generates a full React + Tailwind + TypeScript project using Gemini (frontend mode).
    """
    prompt = (
        frontend_prompt_template.format(specs=specs)
        + "\nAlways include all required setup/config files."
    )
    return stream_from_gemini_frontend(prompt)


def prompt_to_backend(specs: str, arch_type: str = "Monolith"):
    """
    Generates backend project (monolith or microservices) via Gemini.
    """
    arch_type_lower = arch_type.lower()

    # Microservices architecture handler
    if arch_type_lower.startswith("micro"):
        return generate_microservices_backend_streaming(specs)

    prompt = backend_prompt_template.format(specs=specs, architectureType="Monolith")
    return stream_from_qwen(prompt)


def frontend_to_backend(frontend_code: str, arch_type: str = "Monolith"):
    """
    Converts frontend UI logic into backend routes/controllers.
    """
    prompt = frontend_to_backend_template.format(
        frontend_code=frontend_code, architectureType=arch_type
    )
    return stream_from_gemini_integration(prompt)

# ============================================================
# 🧠 Microservices Streaming Pipeline
# ============================================================

def generate_microservices_backend_streaming(specs: str):
    """
    Complete streaming pipeline:
    1️⃣ Generate service plan (JSON)
    2️⃣ Generate infra (gateway + shared + docker)
    3️⃣ Generate code for each microservice
    """
    import google.generativeai as genai
    from gemini_stream import safety_settings

    yield "🧩 Starting Microservices Architecture Generation...\n"

    # 1️⃣ Generate service plan
    planner_prompt = microservices_planner_prompt.format(specs=specs)
    plan = ""
    yield "📋 Planning services...\n"
    for chunk in stream_from_qwen(planner_prompt):
        plan += chunk
        yield chunk
    try:
        plan_json = json.loads(plan)
    except Exception:
        yield "\n⚠️ Invalid planner JSON. Aborting.\n"
        return

    # 2️⃣ Generate infra layer
    infra_prompt = microservices_infra_prompt.format(specs=specs)
    yield "\n🏗️ Generating infrastructure layer...\n"
    for chunk in stream_from_qwen(infra_prompt):
        yield chunk

    # 3️⃣ Generate each microservice
    for svc in plan_json.get("services", []):
        svc_name = svc.get("name", "Service")
        yield f"\n⚙️ Generating service: {svc_name}\n"
        svc_prompt = microservice_code_prompt.format(service=json.dumps(svc, indent=2))
        for chunk in stream_from_qwen(svc_prompt):
            yield chunk

    yield "\n✅ Microservices backend generation complete.\n"


# ============================================================
# 🧩 Utility: Extract Files, API Map, ZIP, etc.
# ============================================================

def clean_code_block(code: str) -> str:
    code = code.strip()
    code = re.sub(r"^```[a-zA-Z0-9]*\n?", "", code)
    code = re.sub(r"```$", "", code)
    code = re.sub(r"^~~~[a-zA-Z0-9]*\n?", "", code)
    code = re.sub(r"~~~$", "", code)
    return code.strip()


def extract_files(full_output: str):
    files, seen = [], set()
    output = full_output.strip()

    # JSON object format
    try:
        data = json.loads(output)
        if isinstance(data, dict):
            for path, content in data.items():
                if isinstance(content, (dict, list)):
                    content = json.dumps(content, indent=2)
                path, content = str(path).strip(), str(content).strip()
                if path and content and path not in seen:
                    files.append((path, clean_code_block(content)))
                    seen.add(path)
            if files:
                return files
    except Exception:
        pass

    # Markdown filename fences
    fence_pattern = re.compile(
        r"```[a-zA-Z0-9]*\s*(?:file(?:name)?\s*[=:]\s*|path\s*[=:]\s*)?([\w./\\-]+\.\w+)\s*\n([\s\S]*?)```",
        re.MULTILINE,
    )
    for m in fence_pattern.finditer(output):
        path, code = m.groups()
        if path not in seen:
            files.append((path.strip(), clean_code_block(code)))
            seen.add(path.strip())

    # Comment headers fallback
    comment_pattern = re.compile(
        r"(?:^|\n)[#/<!-]{1,4}\s*(?:file(?:name)?\s*[=:]\s*)?([\w./\\-]+\.\w+)\s*(?:-->)?\s*[\r\n]+([\s\S]*?)(?=(?:\n[#/<!-]{1,4}\s*(?:file(?:name)?\s*[=:]|[\w./\\-]+\.)|$))",
        re.IGNORECASE,
    )
    for m in comment_pattern.finditer(output):
        path, code = m.groups()
        if path not in seen:
            files.append((path.strip(), clean_code_block(code)))
            seen.add(path.strip())

    # Fallback anonymous blocks
    if not files:
        anon_pattern = re.compile(r"```[a-zA-Z0-9]*\n([\s\S]*?)```", re.MULTILINE)
        for i, m in enumerate(anon_pattern.finditer(output), start=1):
            code = clean_code_block(m.group(1))
            path = f"unknown_file_{i}.txt"
            if path not in seen:
                files.append((path, code))
                seen.add(path)

    return files


def extract_api_map(files):
    api_map = []
    for path, code in files:
        matches = re.findall(
            r"(?:router|app)\.(get|post|put|delete|patch)\(['\"](.*?)['\"]",
            code,
        )
        for method, endpoint in matches:
            api_map.append({"method": method.upper(), "endpoint": endpoint, "file": path})
    uniq, seen = [], set()
    for e in api_map:
        key = (e["method"], e["endpoint"])
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    return uniq


def make_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for path, code in files:
            z.writestr(path, code)
    buf.seek(0)
    return buf


def extract_frontend_code(uploaded_zip):
    code = ""
    with zipfile.ZipFile(uploaded_zip, "r") as z:
        for f in z.namelist():
            if f.endswith((".js", ".jsx", ".ts", ".tsx", ".html")):
                try:
                    code += f"\n// File: {f}\n" + z.read(f).decode(errors="ignore")
                except Exception:
                    pass
    return code.strip()


# ============================================================
# 🩺 Debug + Auto-Fix (Frontend)
# ============================================================

def debug_and_fix_frontend(specs: str, files, build_logs: str) -> str:
    files_as_markdown = "\n\n".join(
        [f"```tsx filename:{filename}\n{content}\n```" for filename, content in files]
    )

    prompt = f"""
You are a **frontend architect (React + Tailwind + TypeScript)** inside an AI pipeline.

Your goal: Fix and regenerate the project so it builds successfully.

---
USER REQUEST:
{specs}

CURRENT FILES:
{files_as_markdown}

BUILD LOGS:
```text
{build_logs}
Rules:

Return a pure JSON object where keys are file paths and values are file contents.

Include: package.json, vite.config.ts, tsconfig.json, index.html, tailwind.config.js, postcss.config.js, src/main.tsx, src/App.tsx, etc.

Fix syntax, imports, missing dependencies, configs.

Project must build via npm install → npm run build → npm run preview.

No explanations or markdown fences.
"""

    fixed_output = ""
    for chunk in stream_from_gemini_backend(prompt):
        print(chunk, end="", flush=True)
        fixed_output += chunk
    return fixed_output