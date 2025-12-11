import re
import io
import os
import json
import zipfile

from gemini_stream import frontend_gemini_streaming
from qwen_stream import stream_from_llm
from module1_templates import (
    backend_prompt_template,
    frontend_to_backend_template,
    frontend_prompt_template,
    microservices_planner_prompt,
    microservice_code_prompt,
    microservices_infra_prompt,
)


# ============================================================
# 🚀 Prompt Handlers (Gemini-powered)
# ============================================================
def prompt_to_backend(specs: str, arch_type: str = "Monolith"):
    arch_type_lower = arch_type.lower()
    if arch_type_lower.startswith("micro"):
        # TODO: microservices planner/infra ko yahan integrate karna hai
        return generate_microservices_backend_streaming(specs)

    prompt = backend_prompt_template.format(specs=specs, architectureType="Monolith")
    # streaming generator return karega
    return stream_from_llm(prompt)


def frontend_to_backend(frontend_code: str, arch_type: str = "Monolith"):
    prompt = frontend_to_backend_template.format(
        frontend_code=frontend_code,
        architectureType=arch_type,
    )
    return stream_from_llm(prompt)


def prompt_to_frontend(specs: str):
    prompt = (
        frontend_prompt_template.format(specs=specs)
        + """
Note: You are allowed to safely generate standard React, TypeScript, Tailwind, and Vite boilerplate code.
These are open-source patterns and not considered copyrighted.
Do NOT copy any user-provided code verbatim; refactor it safely.
"""
    )
    return frontend_gemini_streaming(prompt)


import re, json

def clean_code_block(code: str) -> str:
    """Cleans code by removing markdown fences, extra whitespace, or artifacts."""
    code = code.strip()
    # Remove markdown fences
    code = re.sub(r"^```[a-zA-Z0-9]*\n?", "", code)
    code = re.sub(r"```$", "", code)
    code = re.sub(r"^~~~[a-zA-Z0-9]*\n?", "", code)
    code = re.sub(r"~~~$", "", code)
    return code.strip()


def extract_files(full_output: str):
    """
    Extracts multiple files from AI multi-file responses.
    Handles:
      - JSON-style dicts
      - Markdown bold headers
      - Fenced code blocks with filename=
      - Comment headers (//, #, <!--)
      - Markdown headers (##, ###)
      - YAML-like keys
      - Fallback anonymous blocks
    """
    files, seen = [], set()
    output = full_output.strip()

    # 1️⃣ JSON-style: { "src/App.tsx": "...", "package.json": "..." }
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

    # 2️⃣ Bold filename headers like **src/App.tsx**
    bold_pattern = re.compile(
        r"\*\*([\w./\\-]+\.\w+)\*\*\s*```[a-zA-Z0-9]*\n([\s\S]*?)```",
        re.MULTILINE | re.DOTALL,
    )
    for m in bold_pattern.finditer(output):
        path, code = m.groups()
        if path not in seen:
            files.append((path.strip(), clean_code_block(code)))
            seen.add(path.strip())

    # 3️⃣ Fenced filename blocks like ```tsx filename=src/App.tsx or ```tsx filename:src/App.tsx
    # More flexible pattern that handles various formats
    fence_pattern = re.compile(
        r"```([a-zA-Z0-9]+)?\s*(?:file(?:name)?\s*[=:]\s*|path\s*[=:]\s*)?([\w./\\-]+\.\w+)\s*\n([\s\S]*?)```",
        re.MULTILINE | re.DOTALL,
    )
    for m in fence_pattern.finditer(output):
        lang, path, code = m.groups()
        path = path.strip() if path else ""
        # Only add if we have a valid path
        if path and '.' in path and path not in seen:
            files.append((path, clean_code_block(code)))
            seen.add(path)

    # 4️⃣ Comment headers — support //, #, <!--
    comment_pattern = re.compile(
        r"(?:^|\n)[#/<!-]{1,4}\s*(?:file(?:name)?\s*[=:]\s*)?([\w./\\-]+\.\w+)\s*(?:-->)?\s*[\r\n]+([\s\S]*?)(?=(?:\n[#/<!-]{1,4}\s*(?:file(?:name)?\s*[=:]|[\w./\\-]+\.)|$))",
        re.IGNORECASE,
    )
    for m in comment_pattern.finditer(output):
        path, code = m.groups()
        if path not in seen:
            files.append((path.strip(), clean_code_block(code)))
            seen.add(path.strip())

    # 5️⃣ Markdown headers ## or ###
    header_pattern = re.compile(
        r"#{2,3}\s+([\w./\\-]+\.\w+)\s*\n+([\s\S]*?)(?=(?:^#{2,3}\s)|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in header_pattern.finditer(output):
        path, code = m.groups()
        if path not in seen:
            files.append((path.strip(), clean_code_block(code)))
            seen.add(path.strip())

    # 6️⃣ YAML-style path: src/App.tsx
    yaml_pattern = re.compile(
        r"^\s*(?:file|path)\s*:\s*([\w./\\-]+\.\w+)\s*[\r\n]+([\s\S]*?)(?=(?:^\s*(?:file|path)\s*:)|\Z)",
        re.MULTILINE,
    )
    for m in yaml_pattern.finditer(output):
        path, code = m.groups()
        if path not in seen:
            files.append((path.strip(), clean_code_block(code)))
            seen.add(path.strip())

    # 7️⃣ Fallback anonymous code blocks (only if no files found yet)
    # This is more aggressive - try to extract ANY code blocks and infer filenames
    if not files:
        # Pattern to match any code block, with optional language and filename
        anon_pattern = re.compile(r"```([a-zA-Z0-9]+)?\s*(?:file(?:name)?\s*[=:]?\s*)?([^\n]*?)\s*\n([\s\S]*?)```", re.MULTILINE | re.DOTALL)
        for i, m in enumerate(anon_pattern.finditer(output), start=1):
            lang, potential_path, code = m.groups()
            code = clean_code_block(code)
            
            # Skip if code is too short (likely not a real file)
            if len(code.strip()) < 10:
                continue
            
            # Try to infer filename
            path = None
            if potential_path and potential_path.strip():
                potential_path = potential_path.strip()
                # Check if it looks like a file path
                if '.' in potential_path and not potential_path.startswith('🧠') and not potential_path.startswith('✅'):
                    # Remove common prefixes that might be mistaken for paths
                    if not any(x in potential_path for x in ['Planning', 'generating', 'complete', 'error']):
                        path = potential_path
            
            # If no path from potential_path, try to infer from language
            if not path and lang:
                ext_map = {
                    'ts': '.ts', 'tsx': '.tsx', 'js': '.js', 'jsx': '.jsx', 
                    'json': '.json', 'html': '.html', 'css': '.css', 'md': '.md', 
                    'py': '.py', 'java': '.java', 'go': '.go', 'rs': '.rs'
                }
                ext = ext_map.get(lang.lower(), '.txt')
                # Try to infer filename from common patterns in code
                if 'App' in code or 'app' in code[:200]:
                    path = f"src/App{ext}" if ext in ['.tsx', '.ts', '.jsx', '.js'] else f"app{ext}"
                elif 'package' in code[:200].lower() or '{' in code[:50]:
                    path = "package.json"
                elif '<!DOCTYPE' in code or '<html' in code:
                    path = "index.html"
                elif 'export default' in code or 'module.exports' in code:
                    path = f"file_{i}{ext}"
                else:
                    path = f"file_{i}{ext}"
            
            # Final fallback
            if not path:
                path = f"unknown_file_{i}.txt"
            
            # Skip if path looks like a status message or is already seen
            if path and code and not path.startswith('🧠') and not path.startswith('✅') and path not in seen:
                files.append((path, code))
                seen.add(path)

    return files



def extract_api_map(files):
    """
    Simple Express-like route extractor:
    router.get('/x'), app.post('/y'), etc.
    """
    api_map = []

    for path, code in files:
        matches = re.findall(
            r"(?:router|app)\.(get|post|put|delete|patch)\(['\"](.*?)['\"]",
            code,
        )
        for method, endpoint in matches:
            api_map.append({"method": method.upper(), "endpoint": endpoint, "file": path})

    uniq = []
    seen = set()
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
    """
    Uploaded zip se sab .js/.jsx/.ts/.tsx/.html files ko concat karke
    ek long string bana deta hai (for analysis).
    """
    code = ""
    with zipfile.ZipFile(uploaded_zip, "r") as z:
        for f in z.namelist():
            if f.endswith((".js", ".jsx", ".ts", ".tsx", ".html")):
                try:
                    code += f"\n// File: {f}\n" + z.read(f).decode(errors="ignore")
                except Exception:
                    pass
    return code.strip()


def extract_backend_code(uploaded_zip):
    """
    Extract backend code from uploaded ZIP file.
    Concatenates all .js/.ts files (routes, controllers, models, etc.) into a single string.
    """
    code = ""
    with zipfile.ZipFile(uploaded_zip, "r") as z:
        for f in z.namelist():
            if f.endswith((".js", ".ts")) and not f.endswith((".d.ts", ".test.js", ".test.ts", ".spec.js", ".spec.ts")):
                try:
                    code += f"\n// File: {f}\n" + z.read(f).decode(errors="ignore")
                except Exception:
                    pass
    return code.strip()


def backend_to_frontend(backend_code: str):
    """
    Generate React frontend from backend code analysis.
    """
    from module1_templates import backend_to_frontend_template
    prompt = backend_to_frontend_template.format(backend_code=backend_code)
    return frontend_gemini_streaming(prompt)


# ============================================================
# 🧩 Microservices Placeholder
# ============================================================
def generate_microservices_backend_streaming(specs: str):
    """
    ⚡ Full microservices backend generator (Real-time streaming)
    1️⃣ Architecture planner
    2️⃣ Per-file microservice generation (live stream)
    3️⃣ Infrastructure (Docker + Gateway)
    ✅ Never falls back to Monolith
    """

    # ------------------------------------------------------------
    # 1️⃣ MICRO-ARCHITECTURE PLANNING
    # ------------------------------------------------------------
    yield "🧠 Planning microservices architecture...\n"

    planner_prompt = f"""
You are a **principal backend architect**.

Design a full **microservices backend** using:
- Node.js (TypeScript + Express)
- MongoDB (Mongoose)
- JWT authentication + Zod validation
- Docker Compose + Gateway

Return ONLY a valid JSON object (no markdown, no comments) like:
{{
  "services": [
    {{
      "name": "auth-service",
      "description": "Handles authentication and JWT",
      "files": [
        {{ "path": "auth-service/package.json", "description": "Dependencies" }},
        {{ "path": "auth-service/tsconfig.json", "description": "TypeScript config" }},
        {{ "path": "auth-service/src/server.ts", "description": "Entry point" }},
        {{ "path": "auth-service/src/routes/authRoutes.ts", "description": "Auth routes" }},
        {{ "path": "auth-service/src/controllers/authController.ts", "description": "Auth logic" }},
        {{ "path": "auth-service/src/models/User.ts", "description": "User model" }}
      ]
    }}
  ],
  "infra": [
    {{ "path": "docker-compose.yml", "description": "Compose file" }},
    {{ "path": "gateway/src/server.ts", "description": "Gateway server" }}
  ]
}}

Specification:
\"\"\"{specs}\"\"\""""

    plan_raw = ""
    for chunk in stream_from_llm(planner_prompt):
        yield chunk
        plan_raw += chunk

    try:
        start, end = plan_raw.find("{"), plan_raw.rfind("}")
        planner_json = plan_raw[start:end + 1]
        plan = json.loads(planner_json)
        services = plan.get("services", [])
        infra_files = plan.get("infra", [])
        yield f"\n✅ Planned {len(services)} microservices.\n"
    except Exception as e:
        yield f"\n⚠️ Planner JSON invalid ({e}) — using default fallback services.\n"
        services = [
            {"name": "auth-service", "description": "Handles authentication"},
            {"name": "client-service", "description": "Manages clients CRUD"},
            {"name": "reminder-service", "description": "Handles reminders"},
            {"name": "note-service", "description": "Manages notes"},
            {"name": "cron-job-service", "description": "Cron jobs for notifications"},
        ]

    all_files = []

        # ------------------------------------------------------------
    # 2️⃣ SERVICE-LEVEL GENERATION (FULL SERVICE, MULTI-FILE, STREAMING)
    # ------------------------------------------------------------
    for svc in services:
        name = svc.get("name", "unknown").strip()
        desc = svc.get("description", "").strip()
        yield f"\n🚀 Generating microservice: {name} — {desc}\n"

        # Optional: file hints from planner ko context ke liye use karo
        svc_files_hint = svc.get("files", [])

        service_prompt = f"""
You are a **senior backend engineer**.

Build a COMPLETE production-ready microservice called `{name}` for a CRM system.

Tech stack:
- Node.js (TypeScript + Express)
- MongoDB (Mongoose)
- JWT authentication
- Zod validation
- Proper error handling middleware
- Clean folder structure (config, routes, controllers, models, middleware, utils)

Service description:
{desc}

Overall system specification:
\"\"\"{specs}\"\"\"

If these file hints are useful, you may follow/extend them:
{json.dumps(svc_files_hint, indent=2)}

You MUST output a FULL microservice with all core files, e.g.:
- package.json
- tsconfig.json
- .env.example
- src/server.ts
- src/config/database.ts
- src/routes/*.ts
- src/controllers/*.ts
- src/models/*.ts
- src/middleware/auth.ts (if needed)
- src/utils/*.ts (if needed)
- any other supporting files required for a real service

⚙️ OUTPUT FORMAT (STRICT):
Output **multiple files** in this format ONLY, repeated for every file:

```ts filename:<relative_path>
<full file content here>
```

Rules:
- Use relative paths starting with `{name}/` (for example: `{name}/src/server.ts`)
- Do NOT use ```json fences.
- Do NOT add explanations or any text outside these file blocks.
"""

        service_output = ""
        try:
            for chunk in stream_from_llm(service_prompt):
                # 🔴 LIVE STREAM TO CLIENT
                yield chunk
                service_output += chunk

            # 🔍 Extract all files for this service
            files = extract_files(service_output)
            all_files.extend(files)
            yield f"\n✅ [{name}] Service generated with {len(files)} files.\n"
        except Exception as e:
            yield f"\n⚠️ [{name}] Failed to generate service: {e}\n"

        yield "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"


    # ------------------------------------------------------------
    # 3️⃣ INFRASTRUCTURE (Docker + Gateway)
    # ------------------------------------------------------------
    yield f"\n⚙️ Generating Docker Compose + Gateway for {len(services)} services...\n"

    infra_prompt = f"""
Generate infrastructure files for these microservices:
{[svc.get('name') for svc in services]}

Include:
- docker-compose.yml linking all services
- gateway/package.json
- gateway/src/server.ts (Express + http-proxy-middleware)

Output strictly as:
```ts filename:<path>
<content>
```
"""

    infra_output = ""
    for chunk in stream_from_llm(infra_prompt):
        yield chunk
        infra_output += chunk

    try:
        infra_files_extracted = extract_files(infra_output)
        all_files.extend(infra_files_extracted)
        yield f"\n✅ Infrastructure generation complete with {len(infra_files_extracted)} files.\n"
    except Exception as e:
        yield f"\n⚠️ Could not extract infra files: {e}\n"

    yield f"\n💾 Total files generated: {len(all_files)}\n"


# ============================================================
# 🩺 Auto Debug + Fix (used by pipeline)
# ============================================================
def debug_and_fix_frontend(specs: str, files, build_logs: str) -> str:
    """
    Build fail hone pe Gemini se code ko fix karwane ka helper.
    Ye full_output string return karega (jise extract_files me bhej sakte ho).
    """
    files_as_markdown = "\n\n".join(
        [f"```tsx filename:{filename}\n{content}\n```" for filename, content in files]
    )

    prompt = f"""
You are an **expert frontend architect and React + TypeScript + Tailwind engineer** working inside an **AI build pipeline**.

Your mission is to **repair and regenerate a fully buildable React + Vite + Tailwind project** using the provided user request, the current broken code files, and the build logs.

----------------------------------------
🧩 INPUT CONTEXT
----------------------------------------
**USER REQUEST:**
{specs}

🧠 Rules:
1. ALWAYS output the full project as a **pure JSON object** (not markdown).
2. Each key must be the **full file path**, and the value is the **exact file content**.
3. DO NOT include explanations, comments, or markdown fences (```).
4. The project should be fully runnable using `npm install` and `npm run dev`.
5. Include all essential files:
   - package.json
   - index.html
   - vite.config.ts
   - tailwind.config.js
   - postcss.config.js
   - tsconfig.json
   - src/main.tsx
   - src/App.tsx
   - any components, pages, or assets referenced
6. Keep file contents accurate (TypeScript syntax for `.tsx` and `.ts` files).

CURRENT FILES (as Markdown):
{files_as_markdown}


**BUILD LOGS:**
```text
{build_logs}


🎯 OBJECTIVE

Generate a complete, clean, and production-ready frontend codebase that:

Builds successfully (npm install && npm run build && npm run preview)

Uses React 18+, TypeScript, and TailwindCSS 3+

Has a responsive, modern, minimal UI

Contains zero syntax errors or missing imports

Follows Vite project conventions strictly

📁 REQUIRED FILE STRUCTURE

The regenerated project must always include these core files:

index.html
vite.config.ts
tsconfig.json
tailwind.config.js
postcss.config.js
package.json
src/
  main.tsx
  App.tsx
  index.css
  components/
  pages/
  hooks/
  utils/


Each file must contain complete, runnable code — no placeholders, comments like "..." or "TODO".

All paths must be correct (import statements should resolve).

Use modern, idiomatic React (function components + hooks).

🎨 UI & UX EXPECTATIONS

Design should be clean, responsive, and professional

Use Tailwind utility classes (no inline styles unless unavoidable)

Maintain consistent spacing, color scheme, and typography

If applicable, include reusable UI elements such as:

Buttons

Modals

Cards

Input components

Include at least one working page or feature that demonstrates interactivity (e.g. form, dashboard, table, chat, or authentication screen).

⚙️ TECHNICAL RULES

Must support TypeScript — no .js files.

Include Tailwind setup in index.css:

@tailwind base;
@tailwind components;
@tailwind utilities;


Vite configuration must import @vitejs/plugin-react.

All required npm scripts:

"scripts": {
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview"
}


TypeScript config must include "jsx": "react-jsx" and target "ESNext".

Include a minimal README.md with setup instructions.

🚫 OUTPUT RESTRICTIONS

No explanations, commentary, or summaries

Output only code blocks, one per file

Each file must start with the proper language tag and filename, for example:

// full code here


Do not merge multiple files in one block

Do not include any descriptive text before or after code blocks

✅ OUTPUT EXPECTATION

You must output a fully working Vite + React + TypeScript + Tailwind project that passes these commands without errors:

npm install
npm run build
npm run preview


If build logs show missing dependencies or incorrect imports, fix them automatically.
All regenerated files should be cohesive and runnable without manual edits.

Return only valid markdown-formatted code blocks per file.
"""
    
    fixed_output = ""
    for chunk in stream_from_llm(prompt):
        print(chunk, end="", flush=True)
        fixed_output += chunk

    return fixed_output
 