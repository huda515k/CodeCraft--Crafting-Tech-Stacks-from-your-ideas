import streamlit as st
import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend_generator.OllamabasedGeneration.module1_core import (
    erd_or_prompt_backend,
    frontend_to_backend,
    extract_files,
    extract_api_map,
    make_zip,
    extract_frontend_code,
    image_to_prompt,
)


def stream_display(generator):
    """Display streaming text output from LLM."""
    stream_box = st.empty()
    full_output = ""
    for chunk in generator:
        text = getattr(chunk, "content", None) or str(chunk)
        full_output += text
        stream_box.markdown(
            f"<div style='background:#0d1117;color:#d6f7ff;padding:10px;"
            f"border-radius:6px;font-family:monospace;white-space:pre-wrap;"
            f"max-height:70vh;overflow-y:auto;'>{full_output}</div>",
            unsafe_allow_html=True,
        )
    return full_output


def finalize_output(files, zipname):
    """Display code preview and allow ZIP download."""
    if not files:
        st.warning("No files were produced.")
        return

    st.subheader("Generated Files (preview)")
    for path, code in files:
        with st.expander(path):
            st.code(code[:30000] + ("..." if len(code) > 30000 else ""), language="javascript")

    zip_file = make_zip(files)
    st.success("Generation complete!")
    st.download_button("Download Project ZIP", zip_file, zipname)


def main():
    st.set_page_config(page_title="CodeCraft Module 1 – Backend Generation", layout="centered")
    st.title(" CodeCraft – Module 1: Backend Generation")
    st.markdown("Automated backend creation from ERDs, prompts, images, or frontends — with architecture selection.")

    arch_type = st.selectbox("Select Architecture Type:", ["Monolith", "Microservices"])
    rules = st.text_area("Business Rules (optional):", placeholder="e.g., Only admins can delete users.")
    mode = st.selectbox("Select Mode:", ["ERD → Backend", "Prompt → Backend", "Image → Backend", "Frontend → Backend"])

    if mode == "ERD → Backend":
        upload = st.file_uploader("Upload ERD (.dbml / .txt)", type=["dbml", "txt"])
        text = st.text_area("Extra description (optional):", height=100)
        if st.button("Generate Backend"):
            specs = ""
            if upload:
                specs += upload.read().decode(errors="ignore")
            specs += "\n" + text + "\n" + rules
            if specs.strip():
                st.info(f"Generating {arch_type} backend from ERD ...")
                backend_output = stream_display(erd_or_prompt_backend(specs, arch_type))
                files = extract_files(backend_output)
                api_map = extract_api_map(files)
                if api_map:
                    files.append(("api_map.json", json.dumps(api_map, indent=2)))
                finalize_output(files, f"{arch_type.lower()}_erd_backend.zip")
            else:
                st.error("Please upload ERD or enter prompt text.")

    elif mode == "Prompt → Backend":
        prompt_text = st.text_area("Describe backend requirements:", height=150)
        if st.button("Generate Backend"):
            if not prompt_text.strip():
                st.error("Please describe what backend you need.")
                return
            specs = prompt_text + "\n" + rules
            st.info(f"Generating {arch_type} backend from natural language prompt ...")
            backend_output = stream_display(erd_or_prompt_backend(specs, arch_type))
            files = extract_files(backend_output)
            api_map = extract_api_map(files)
            if api_map:
                files.append(("api_map.json", json.dumps(api_map, indent=2)))
            finalize_output(files, f"{arch_type.lower()}_prompt_backend.zip")

    elif mode == "Image → Backend":
        upload = st.file_uploader("Upload ERD image (.png/.jpg)", type=["png", "jpg", "jpeg"])
        text = st.text_area("Extra description (optional):", height=100)
        if upload and st.button("Generate Backend from ERD Image"):
            st.info("Converting ERD image to schema...")
            erd_text = image_to_prompt(upload)
            specs = erd_text + "\n" + text + "\n" + rules
            st.info(f"Generating {arch_type} backend from image-derived ERD ...")
            backend_output = stream_display(erd_or_prompt_backend(specs, arch_type))
            files = extract_files(backend_output)
            api_map = extract_api_map(files)
            if api_map:
                files.append(("api_map.json", json.dumps(api_map, indent=2)))
            finalize_output(files, f"{arch_type.lower()}_image_backend.zip")

    elif mode == "Frontend → Backend":
        upload = st.file_uploader("Upload frontend ZIP (React app):", type=["zip"])
        if upload and st.button("Generate Backend from Frontend"):
            st.info(f"Analyzing frontend code to generate {arch_type} backend ...")
            code = extract_frontend_code(upload)
            backend_output = stream_display(frontend_to_backend(code, arch_type))
            files = extract_files(backend_output)
            api_map = extract_api_map(files)
            if api_map:
                files.append(("api_map.json", json.dumps(api_map, indent=2)))
            finalize_output(files, f"{arch_type.lower()}_frontend_backend.zip")


if __name__ == "__main__":
    main()
