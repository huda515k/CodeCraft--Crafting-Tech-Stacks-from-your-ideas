# gemini_routes.py - Routes for Gemini-powered CodeCraft modules
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional, List
import os
import sys
import io
import json
import uuid
import zipfile
import base64
from pathlib import Path
from datetime import datetime

# Add CODECRAFT llmbackend to path
project_root = Path(__file__).parent
codecraft_llmbackend_path = project_root / "CODECRAFT" / "codingai" / "llmbackend"
if str(codecraft_llmbackend_path) not in sys.path:
    sys.path.insert(0, str(codecraft_llmbackend_path))

# Import CODECRAFT modules
from module1_core import (
    prompt_to_backend,
    prompt_to_frontend,
    frontend_to_backend,
    backend_to_frontend,
    extract_files,
    make_zip,
    extract_frontend_code,
    extract_backend_code,
)

# Import frontend_generator modules for UI to Frontend
frontend_generator_path = project_root / "frontend_generator"
if str(frontend_generator_path) not in sys.path:
    sys.path.insert(0, str(frontend_generator_path))

# Import frontend_generator modules (will be imported in routes when needed)
# from multi_ui_reactgenerator import EnhancedMultiScreenGenerator

router = APIRouter(prefix="/gemini", tags=["Gemini Code Generation"])

# Temporary storage for generated projects
_generated_projects = {}

def format_sse(data: dict) -> str:
    """Format data as Server-Sent Events."""
    return f"data: {json.dumps(data)}\n\n"

# ============================================================
# Prompt to Backend
# ============================================================
@router.post("/prompt-to-backend-stream")
async def prompt_to_backend_stream(
    prompt: str = Form(...),
    arch_type: str = Form("Monolith")
):
    """
    Generate Express.js backend from natural language prompt using Gemini.
    Returns Server-Sent Events (SSE) stream with code chunks.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "🚀 Starting backend generation with Gemini..."
            })
            
            full_output = ""
            stream = prompt_to_backend(prompt, arch_type)
            
            for chunk in stream:
                if chunk:
                    full_output += chunk
                    yield format_sse({
                        "type": "chunk",
                        "content": chunk
                    })
            
            # Extract files
            yield format_sse({
                "type": "info",
                "message": "📦 Extracting files from generated code..."
            })
            
            files = extract_files(full_output)
            if not files:
                yield format_sse({
                    "type": "error",
                    "message": "❌ No valid files found in generated code"
                })
                return
            
            # Create ZIP
            zip_bytes = make_zip(files)
            _generated_projects[project_id] = {
                "zip_bytes": zip_bytes.getvalue(),
                "created_at": datetime.now().isoformat(),
                "arch_type": arch_type,
            }
            
            yield format_sse({
                "type": "complete",
                "project_id": project_id,
                "files_count": len(files),
                "download_url": f"/gemini/download/{project_id}",
                "message": f"✅ Backend generation complete! {len(files)} files generated."
            })
            
        except Exception as e:
            yield format_sse({
                "type": "error",
                "message": f"❌ Error: {str(e)}"
            })
    
    return StreamingResponse(
        generate_and_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================
# Prompt to Frontend
# ============================================================
@router.post("/prompt-to-frontend-stream")
async def prompt_to_frontend_stream(
    prompt: str = Form(...)
):
    """
    Generate React frontend from natural language prompt using Gemini.
    Returns Server-Sent Events (SSE) stream with code chunks.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "✨ Starting frontend generation with Gemini..."
            })
            
            full_output = ""
            stream = prompt_to_frontend(prompt)
            
            for chunk in stream:
                if chunk:
                    full_output += chunk
                    yield format_sse({
                        "type": "chunk",
                        "content": chunk
                    })
            
            # Extract files
            yield format_sse({
                "type": "info",
                "message": "📦 Extracting files from generated code..."
            })
            
            files = extract_files(full_output)
            if not files:
                yield format_sse({
                    "type": "error",
                    "message": "❌ No valid files found in generated code"
                })
                return
            
            # Create ZIP
            zip_bytes = make_zip(files)
            _generated_projects[project_id] = {
                "zip_bytes": zip_bytes.getvalue(),
                "created_at": datetime.now().isoformat(),
                "arch_type": "Frontend",
            }
            
            yield format_sse({
                "type": "complete",
                "project_id": project_id,
                "files_count": len(files),
                "download_url": f"/gemini/download/{project_id}",
                "message": f"✅ Frontend generation complete! {len(files)} files generated."
            })
            
        except Exception as e:
            yield format_sse({
                "type": "error",
                "message": f"❌ Error: {str(e)}"
            })
    
    return StreamingResponse(
        generate_and_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================
# Frontend to Backend
# ============================================================
@router.post("/frontend-to-backend-stream")
async def frontend_to_backend_stream(
    file: UploadFile = File(...),
    arch_type: str = Form("Monolith")
):
    """
    Generate Express.js backend from React frontend code using Gemini.
    Returns Server-Sent Events (SSE) stream with code chunks.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "🔄 Analyzing frontend code and generating backend..."
            })
            
            # Read and extract frontend code
            uploaded_zip = await file.read()
            if len(uploaded_zip) == 0:
                yield format_sse({
                    "type": "error",
                    "message": "❌ Uploaded file is empty"
                })
                return
            
            try:
                frontend_code = extract_frontend_code(io.BytesIO(uploaded_zip))
            except Exception as e:
                yield format_sse({
                    "type": "error",
                    "message": f"❌ Failed to extract frontend code: {str(e)}"
                })
                return
            
            if not frontend_code or len(frontend_code.strip()) == 0:
                yield format_sse({
                    "type": "error",
                    "message": "❌ No frontend code found in ZIP file"
                })
                return
            
            # Generate backend
            full_output = ""
            stream = frontend_to_backend(frontend_code, arch_type)
            
            for chunk in stream:
                if chunk:
                    full_output += chunk
                    yield format_sse({
                        "type": "chunk",
                        "content": chunk
                    })
            
            # Extract files
            yield format_sse({
                "type": "info",
                "message": "📦 Extracting files from generated code..."
            })
            
            files = extract_files(full_output)
            if not files:
                yield format_sse({
                    "type": "error",
                    "message": "❌ No valid files found in generated code"
                })
                return
            
            # Create ZIP
            zip_bytes = make_zip(files)
            _generated_projects[project_id] = {
                "zip_bytes": zip_bytes.getvalue(),
                "created_at": datetime.now().isoformat(),
                "arch_type": arch_type,
            }
            
            yield format_sse({
                "type": "complete",
                "project_id": project_id,
                "files_count": len(files),
                "download_url": f"/gemini/download/{project_id}",
                "message": f"✅ Backend generation complete! {len(files)} files generated."
            })
            
        except Exception as e:
            yield format_sse({
                "type": "error",
                "message": f"❌ Error: {str(e)}"
            })
    
    return StreamingResponse(
        generate_and_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================
# Backend to Frontend
# ============================================================
@router.post("/backend-to-frontend-stream")
async def backend_to_frontend_stream(
    file: UploadFile = File(...)
):
    """
    Generate React frontend from Express.js backend code using Gemini.
    Returns Server-Sent Events (SSE) stream with code chunks.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "🎨 Analyzing backend code and generating frontend..."
            })
            
            # Read and extract backend code
            uploaded_zip = await file.read()
            if len(uploaded_zip) == 0:
                yield format_sse({
                    "type": "error",
                    "message": "❌ Uploaded file is empty"
                })
                return
            
            try:
                backend_code = extract_backend_code(io.BytesIO(uploaded_zip))
            except Exception as e:
                yield format_sse({
                    "type": "error",
                    "message": f"❌ Failed to extract backend code: {str(e)}"
                })
                return
            
            if not backend_code or len(backend_code.strip()) == 0:
                yield format_sse({
                    "type": "error",
                    "message": "❌ No backend code found in ZIP file"
                })
                return
            
            # Generate frontend
            full_output = ""
            stream = backend_to_frontend(backend_code)
            
            for chunk in stream:
                if chunk:
                    full_output += chunk
                    yield format_sse({
                        "type": "chunk",
                        "content": chunk
                    })
            
            # Extract files
            yield format_sse({
                "type": "info",
                "message": "📦 Extracting files from generated code..."
            })
            
            files = extract_files(full_output)
            if not files:
                yield format_sse({
                    "type": "error",
                    "message": "❌ No valid files found in generated code"
                })
                return
            
            # Create ZIP
            zip_bytes = make_zip(files)
            _generated_projects[project_id] = {
                "zip_bytes": zip_bytes.getvalue(),
                "created_at": datetime.now().isoformat(),
                "arch_type": "Frontend",
            }
            
            yield format_sse({
                "type": "complete",
                "project_id": project_id,
                "files_count": len(files),
                "download_url": f"/gemini/download/{project_id}",
                "message": f"✅ Frontend generation complete! {len(files)} files generated."
            })
            
        except Exception as e:
            yield format_sse({
                "type": "error",
                "message": f"❌ Error: {str(e)}"
            })
    
    return StreamingResponse(
        generate_and_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================
# UI to Frontend (using frontend_generator)
# ============================================================
@router.post("/ui-to-frontend-stream")
async def ui_to_frontend_stream(
    file: UploadFile = File(...),
    additional_context: Optional[str] = Form(None),
    styling_approach: str = Form("tailwind"),
    include_typescript: bool = Form(True)
):
    """
    Convert UI designs/screenshots to React components using Gemini.
    Returns Server-Sent Events (SSE) stream with code chunks.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "🖼️ Analyzing UI image and generating React code..."
            })
            
            # Read file
            file_content = await file.read()
            image_data = base64.b64encode(file_content).decode('utf-8')
            
            # Get Gemini API key
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                yield format_sse({
                    "type": "error",
                    "message": "❌ GEMINI_API_KEY not configured"
                })
                return
            
            yield format_sse({
                "type": "info",
                "message": "📤 Processing UI image with Gemini..."
            })
            
            # Use FrontendGenerationService
            from services import FrontendGenerationService
            from models import UIProcessingRequest
            
            service = FrontendGenerationService(gemini_api_key=api_key, use_ai_generator=True)
            
            request = UIProcessingRequest(
                image_data=image_data,
                additional_context=additional_context or "",
                framework="react",
                styling_approach=styling_approach
            )
            
            # Process UI
            result = await service.process_ui(request)
            
            if not result.success:
                yield format_sse({
                    "type": "error",
                    "message": f"❌ UI processing failed: {result.error_message}"
                })
                return
            
            yield format_sse({
                "type": "info",
                "message": "⚛️ Generating React project with AI..."
            })
            
            # Generate project using AI generator
            project_result = await service.process_and_generate(
                image_data=image_data,
                additional_context=additional_context,
                framework="react",
                styling_approach=styling_approach,
                include_typescript=include_typescript,
                use_ai=True
            )
            
            if not project_result.get("success"):
                yield format_sse({
                    "type": "error",
                    "message": f"❌ Generation failed: {project_result.get('error_message', 'Unknown error')}"
                })
                return
            
            project = project_result.get("project")
            if not project or not project.files:
                yield format_sse({
                    "type": "error",
                    "message": "❌ Failed to generate project files"
                })
                return
            
            # Create ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_name, file_content in project.files.items():
                    zf.writestr(file_name, file_content)
            
            zip_bytes = zip_buffer.getvalue()
            _generated_projects[project_id] = {
                "zip_bytes": zip_bytes,
                "created_at": datetime.now().isoformat(),
                "arch_type": "Frontend",
            }
            
            yield format_sse({
                "type": "complete",
                "project_id": project_id,
                "files_count": len(project.files),
                "download_url": f"/gemini/download/{project_id}",
                "message": f"✅ Frontend generation complete! {len(project.files)} files generated."
            })
            
        except Exception as e:
            import traceback
            yield format_sse({
                "type": "error",
                "message": f"❌ Error: {str(e)}\n{traceback.format_exc()}"
            })
    
    return StreamingResponse(
        generate_and_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================
# Multi-UI to Frontend (using multi_ui_reactgenerator)
# ============================================================
@router.post("/ui-to-frontend-multi-stream")
async def ui_to_frontend_multi_stream(
    files: List[UploadFile] = File(...),
    additional_context: Optional[str] = Form(None),
    styling_approach: str = Form("tailwind"),
    include_typescript: bool = Form(True)
):
    """
    Convert multiple UI designs/screenshots to complete React application using Gemini.
    Returns Server-Sent Events (SSE) stream with code chunks.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": f"🖼️ Analyzing {len(files)} UI images and generating React application..."
            })
            
            # Get Gemini API key
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                yield format_sse({
                    "type": "error",
                    "message": "❌ GEMINI_API_KEY not configured"
                })
                return
            
            # Use multi-screen generator
            from multi_ui_reactgenerator import EnhancedMultiScreenGenerator
            generator = EnhancedMultiScreenGenerator(api_key=api_key)
            
            # Save images temporarily
            import tempfile
            temp_dir = tempfile.mkdtemp()
            image_paths = []
            
            try:
                for idx, file in enumerate(files):
                    file_content = await file.read()
                    image_path = os.path.join(temp_dir, f"screen_{idx}.png")
                    with open(image_path, "wb") as f:
                        f.write(file_content)
                    image_paths.append(image_path)
                
                yield format_sse({
                    "type": "info",
                    "message": "📤 Processing UI images with Gemini..."
                })
                
                # Prepare screen images for generator
                screen_images = [
                    {"path": path, "name": f"Screen{i+1}"}
                    for i, path in enumerate(image_paths)
                ]
                
                # Generate multi-screen application
                project_files = await generator.generate_complete_app(
                    screen_images=screen_images,
                    project_name="react-app",
                    include_typescript=include_typescript,
                    styling_approach=styling_approach,
                    output_format="dict"
                )
                
                # If additional_context provided, we could pass it through but the method doesn't support it directly
                # For now, we'll just use the generated files
                
                if not project_files:
                    yield format_sse({
                        "type": "error",
                        "message": "❌ Failed to generate project files"
                    })
                    return
                
                # Create ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file_name, file_content in project_files.items():
                        zf.writestr(file_name, file_content)
                
                zip_bytes = zip_buffer.getvalue()
                _generated_projects[project_id] = {
                    "zip_bytes": zip_bytes,
                    "created_at": datetime.now().isoformat(),
                    "arch_type": "Frontend",
                }
                
                yield format_sse({
                    "type": "complete",
                    "project_id": project_id,
                    "files_count": len(project_files),
                    "download_url": f"/gemini/download/{project_id}",
                    "message": f"✅ Multi-screen frontend generation complete! {len(project_files)} files generated."
                })
                
            finally:
                # Cleanup temp files
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            import traceback
            yield format_sse({
                "type": "error",
                "message": f"❌ Error: {str(e)}\n{traceback.format_exc()}"
            })
    
    return StreamingResponse(
        generate_and_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================
# Download endpoint
# ============================================================
@router.get("/download/{project_id}")
async def download_project(project_id: str):
    """Download generated project ZIP file."""
    if project_id not in _generated_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = _generated_projects[project_id]
    zip_bytes = project_data["zip_bytes"]
    
    return FileResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        filename=f"codecraft-project-{project_id}.zip"
    )
