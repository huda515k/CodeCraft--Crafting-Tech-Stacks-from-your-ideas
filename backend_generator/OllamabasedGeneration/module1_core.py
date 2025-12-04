
import re
import io
import zipfile
import json
from langchain_ollama import OllamaLLM
from backend_generator.OllamabasedGeneration.module1_templates import backend_prompt_template, frontend_to_backend_template


def stream_from_llm(prompt_text: str, model: str = None):
    """Generic LLM streamer using Ollama."""
    # Try qwen2.5-coder:7b first, fallback to codellama:13b
    if model is None:
        model = "qwen2.5-coder:7b"
    
    llm = OllamaLLM(model=model, base_url="http://localhost:11434")
    return llm.stream(prompt_text)


def erd_or_prompt_backend(specs: str, arch_type: str = "Monolith"):
    """
    Generate backend code (ERD or prompt-based) with architecture type.
    """
    prompt = backend_prompt_template.format(
        specs=specs,
        architectureType=arch_type
    )
    return stream_from_llm(prompt)


def frontend_to_backend(frontend_code: str, arch_type: str = "Monolith"):
    """Generate backend from uploaded frontend ZIP."""
    prompt = frontend_to_backend_template.format(
        frontend_code=frontend_code,
        architectureType=arch_type
    )
    return stream_from_llm(prompt)


def extract_files(full_output: str):
    """Extracts code blocks in format: ```js filename: path/to/file.js```"""
    files = []
    pattern = r"```[a-zA-Z0-9]*\s*filename:\s*(.*?)\n([\s\S]*?)```"
    for match in re.finditer(pattern, full_output):
        path, code = match.groups()
        files.append((path.strip(), code.strip()))
    return files


def extract_api_map(files):
    """Creates a small API map by scanning express routes."""
    api_map = []
    for path, code in files:
        for m in re.findall(r"(?:router|app)\.(get|post|put|delete)\(['\"](.*?)['\"]", code):
            api_map.append({
                "method": m[0].upper(),
                "endpoint": m[1],
                "file": path
            })
    seen, uniq = set(), []
    for e in api_map:
        key = (e["method"], e["endpoint"])
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    return uniq


def make_zip(files):
    """Bundle files into a downloadable ZIP."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for path, code in files:
            z.writestr(path, code)
    buf.seek(0)
    return buf


def extract_frontend_code(uploaded_zip):
    """Extract .js/.jsx/.ts/.tsx/.html files from uploaded frontend ZIP."""
    code = ""
    with zipfile.ZipFile(uploaded_zip, "r") as z:
        for f in z.namelist():
            if f.endswith((".js", ".jsx", ".ts", ".tsx", ".html")):
                try:
                    code += f"\n// File: {f}\n" + z.read(f).decode(errors="ignore")
                except Exception:
                    pass
    return code.strip()


def image_to_prompt(uploaded_file):
    """Converts ERD image into textual DBML-like format."""
    llm = OllamaLLM(model="llava", base_url="http://localhost:11434")
    result = llm.invoke("Describe this ERD image in DBML-like format.")
    return result
