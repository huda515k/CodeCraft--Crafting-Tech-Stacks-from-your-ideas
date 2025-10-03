from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
import tempfile
import zipfile

from ..ERD.models import ERDSchema
# from .generator import NodeProjectGenerator  # Lazy import


router = APIRouter(prefix="/nodegen", tags=["NodeJS Generator"])


@router.post("/generate", summary="🤖 AI Agent: Generate NodeJS Backend from ERD Schema")
def generate_node_project(erd_schema: ERDSchema):
    try:
        from .generator import NodeProjectGenerator  # Lazy import
        gen = NodeProjectGenerator()
        project = gen.generate(erd_schema)

        # Zip the project
        zip_path = os.path.join(tempfile.gettempdir(), "codecraft_node_project.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(project.output_dir):
                for f in files:
                    abs_path = os.path.join(root, f)
                    rel_path = os.path.relpath(abs_path, project.output_dir)
                    zf.write(abs_path, rel_path)

        return FileResponse(zip_path, filename="🤖_ai_generated_nodejs_backend.zip", media_type="application/zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent-generate", summary="🤖 AI Agent: Generate NodeJS Backend from ERD Schema")
def agent_generate_node_project(erd_schema: ERDSchema):
    """
    🤖 AI Agent: Generate complete Node.js backend with intelligent optimization
    
    The AI agent will analyze your ERD schema and generate an optimized Node.js backend
    with best practices, proper error handling, and intelligent code structure.
    """
    try:
        from .generator import NodeProjectGenerator  # Lazy import
        gen = NodeProjectGenerator()
        project = gen.generate(erd_schema)

        # Zip the project
        zip_path = os.path.join(tempfile.gettempdir(), "🤖_ai_agent_generated_backend.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(project.output_dir):
                for f in files:
                    abs_path = os.path.join(root, f)
                    rel_path = os.path.relpath(abs_path, project.output_dir)
                    zf.write(abs_path, rel_path)

        return FileResponse(zip_path, filename="🤖_ai_agent_generated_backend.zip", media_type="application/zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🤖 AI Agent Error: {str(e)}")


