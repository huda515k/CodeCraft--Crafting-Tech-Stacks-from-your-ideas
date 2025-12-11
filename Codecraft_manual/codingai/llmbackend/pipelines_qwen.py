import json
import time
from typing import Generator
from qwen_stream import stream_from_llm


def extract_json(text: str) -> str:
    """Extracts the first valid JSON object from possibly noisy output."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        return text[start:end + 1]
    return text


def backend_qwen_stream(specs: str, arch_type: str = "Monolith") -> Generator[str, None, None]:
    """
    Qwen-based backend generator.
    Prevents early JSON parsing, duplicate triggers, and removes fallback.
    """
    import os
    print(f"[DEBUG] PID={os.getpid()} — new generation triggered")
    if getattr(backend_qwen_stream, "_is_running", False):
        yield "⚠️ Generation already in progress — skipping duplicate run.\n"
        return
    backend_qwen_stream._is_running = True

    try:
        arch_clean = arch_type.strip() or "Monolith"
        yield f"🔧 Starting backend generation | Arch: {arch_clean}\n"

        plan_prompt = f"""
You are a **principal backend architect**.
Design a complete {arch_clean} backend using:
- Node.js 20+
- Express.js 5+
- MongoDB (Mongoose)
- TypeScript (ESM imports)
- JWT auth, RBAC, env, error middleware, zod validation

Specification:\n{specs}\n
Return ONLY valid JSON in format:\n{{\n  \"files\": [{{\"path\":..., \"description\":...}}]\n}}\n"""

        plan_raw = ""
        json_parsed = False
        for chunk in stream_from_llm(plan_prompt):
            if "{" in chunk or plan_raw:
                plan_raw += chunk
            # Wait until enough closing braces appear to safely parse
            if plan_raw.count("{") > 0 and plan_raw.count("}") >= plan_raw.count("{") and not json_parsed:
                time.sleep(0.3)
                extracted = extract_json(plan_raw)
                try:
                    plan = json.loads(extracted)
                    files_meta = plan.get("files", [])
                    if not isinstance(files_meta, list) or not files_meta:
                        raise ValueError("invalid files array")
                    yield f"🔧 Planned {len(files_meta)} backend files.\n"
                    json_parsed = True
                    break
                except Exception:
                    continue

        if not json_parsed:
            yield "❌ Plan parse failed — stopping generation. No valid architecture plan detected.\n"
            return

        total_files = len(files_meta)

        for idx, meta in enumerate(files_meta, start=1):
            path = (meta.get("path") or "").strip()
            desc = (meta.get("description") or "").strip()
            if not path:
                continue

            yield f"\n📄 Generating production-ready file {idx}/{total_files}: {path}\n"

            file_prompt = f"""
Generate a **production-ready TypeScript file** for this backend.
Tech stack: Node.js, Express.js, Mongoose, TypeScript, JWT, RBAC, zod.
Path: {path}\nDescription: {desc}\nBased on: {specs}\n
Output ONLY this format:\n```ts filename:{path}\n// full runnable TypeScript code here\n```\n"""

            yield f"```ts filename:{path}\n"
            try:
                for chunk in stream_from_llm(file_prompt):
                    yield chunk
            except Exception as e:
                yield f"// ⚠️ Error while streaming this file: {e}\n"
            yield "\n```\n"

        yield f"\n✅ Backend generation complete. Files: {total_files}\n"

    finally:
        backend_qwen_stream._is_running = False
# 🟣 INTEGRATION PIPELINE (Frontend → Backend)
# ------------------------------------------------------------
def integration_qwen_stream(frontend_code: str) -> Generator[str, None, None]:
    """
    Dynamic, streaming integration pipeline — builds backend based on any React frontend.
    """

    yield "🧠 Analyzing frontend to infer backend endpoints, entities, and data flow...\n"

    frontend_snippet = frontend_code[:15000]

    # ------------------------------------------------------------
    # 1️⃣ Dynamic backend architecture planning
    # ------------------------------------------------------------
    plan_prompt = f"""
You are a **senior full-stack architect**.

Analyze the following React frontend code and design a **complete backend architecture** using:
- Node.js + Express.js
- TypeScript (ESM)
- MongoDB (Mongoose)
- JWT authentication (if login/register forms exist)
- Zod validation (for input forms)
- Proper modular architecture: routes, controllers, models, middleware, utils, config

FRONTEND CODE (truncated):
{frontend_snippet}

Return ONLY valid JSON like this (no markdown, no comments):
{{
  "files": [
    {{ "path": "src/server.ts", "description": "App entry point" }},
    {{ "path": "src/config/database.ts", "description": "Database connection" }},
    {{ "path": "src/routes/*.ts", "description": "API routes based on frontend calls" }},
    {{ "path": "src/controllers/*.ts", "description": "Controller logic matching frontend pages" }},
    {{ "path": "src/models/*.ts", "description": "Mongoose models inferred from frontend data" }},
    {{ "path": "src/middleware/*.ts", "description": "JWT auth and validation middleware" }},
    {{ "path": "src/utils/*.ts", "description": "Helper functions" }}
  ]
}}
"""

    plan_raw = ""
    for chunk in stream_from_llm(plan_prompt):
        yield chunk
        plan_raw += chunk

    try:
        start, end = plan_raw.find("{"), plan_raw.rfind("}")
        planner_json = plan_raw[start:end + 1]
        plan = json.loads(planner_json)
        files_meta = plan.get("files", [])
        yield f"\n✅ Planned {len(files_meta)} integration backend files dynamically.\n"
    except Exception as e:
        yield f"\n⚠️ Plan parsing failed ({e}), using default fallback plan.\n"
        files_meta = [
            {"path": "src/server.ts", "description": "Express server entry point"},
            {"path": "src/config/database.ts", "description": "MongoDB config"},
            {"path": "src/routes/apiRoutes.ts", "description": "API routes"},
            {"path": "src/controllers/apiController.ts", "description": "Controller logic"},
            {"path": "src/models/User.ts", "description": "Mongoose model"}
        ]

    # ------------------------------------------------------------
    # 2️⃣ Dynamic file-by-file generation (Streaming)
    # ------------------------------------------------------------
    total_files = len(files_meta)
    for idx, meta in enumerate(files_meta, start=1):
        path = meta.get("path", "").strip()
        desc = meta.get("description", "").strip()
        if not path:
            continue

        yield f"\n📄 Generating file {idx}/{total_files}: {path}\n"

        file_prompt = f"""
You are a **senior TypeScript backend engineer** integrating a React frontend.

Generate the full, production-ready backend file `{path}` matching the following:
- Description: {desc}
- Must handle actual frontend API endpoints and logic.
- Implement JWT auth, CRUD operations, and input validation if needed.
- Use proper Express async/await error handling.
- Connect to MongoDB using Mongoose.
- Code should be real, runnable, and modular.

FRONTEND SNIPPET (context):
{frontend_snippet[:5000]}

Output format:
```ts filename:{path}
<complete code>
```
Do NOT add markdown or explanations.
"""

        file_output = ""
        try:
            for chunk in stream_from_llm(file_prompt):
                yield chunk  # 🔴 Live streaming
                file_output += chunk

        except Exception as e:
            yield f"// ⚠️ Error while streaming {path}: {e}\n"

        yield f"\n✅ Completed {path}\n"

    yield f"\n🎯 Integration backend generation complete. Total files: {total_files}\n"