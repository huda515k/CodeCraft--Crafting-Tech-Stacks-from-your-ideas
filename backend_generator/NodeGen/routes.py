
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form, Request
from fastapi.responses import StreamingResponse, FileResponse, Response
import io
import os
import shutil
import tempfile
import zipfile
import base64
from typing import Optional
import json
import uuid
import asyncio
from datetime import datetime

from backend_generator.OllamabasedGeneration.module1_core import (
    erd_or_prompt_backend,
    frontend_to_backend,
    extract_files,
    extract_api_map,
    make_zip,
    extract_frontend_code,
)
from ..ERD.models import ERDSchema
from ..ERD.services import ERDProcessingService

router = APIRouter(prefix="/nodegen", tags=["NodeJS Generator"])

# Temporary storage for generated files (in production, use Redis or database)
_generated_projects = {}

def format_sse(data: dict) -> str:
    """Format data as Server-Sent Events."""
    return f"data: {json.dumps(data)}\n\n"

@router.post("/prompt-to-backend-stream", summary="Generate backend from prompt with real-time streaming preview")
async def prompt_to_backend_stream(
    prompt: str = Form(..., description="Describe backend requirements (entities, rules, etc.)"),
    arch_type: str = Form("Monolith", description="Architecture type: Monolith or Microservices")
):
    """
    Generate backend code from a prompt with real-time streaming preview.
    Returns Server-Sent Events (SSE) stream with code chunks and preview.
    Use the returned project_id to download the final ZIP.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            # Send initial message
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "Starting code generation..."
            })
            
            # Stream LLM output and collect (like Streamlit does)
            generator = erd_or_prompt_backend(prompt, arch_type)
            full_output = ""
            
            # Stream every chunk immediately for real-time preview (like Streamlit's stream_display)
            for chunk in generator:
                text = getattr(chunk, "content", None) or str(chunk)
                if text:
                    full_output += text
                    
                    # Send every chunk immediately for real-time display (like Streamlit)
                    yield format_sse({
                        "type": "stream",
                        "content": text,
                        "partial": True
                    })
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.001)  # Reduced delay for smoother streaming
            
            # Extract all files from the generated output
            files = extract_files(full_output)
            
            # If no files were extracted but we have output, create fallback files
            if not files and full_output.strip():
                files.append(("generated_code.txt", full_output))
                files.append(("README.md", f"""# Generated Backend Code

This backend code was generated from your prompt.

## Prompt
{prompt[:500]}

## Architecture
{arch_type}

## Generated Output

See generated_code.txt for the full output.

## Note
The model output may need manual formatting into proper file structure.
"""))
            
            # Always generate at least a README if nothing else (handles model refusal)
            if not files:
                files.append(("README.md", f"""# Generated Backend

## Model Response
The model response was received but no files were extracted.

## Your Prompt
{prompt[:500]}

## Architecture
{arch_type}

## Raw Output
{full_output[:2000] if full_output else "No output received from model"}

## Next Steps
- Check if the model refused the request
- Try simplifying your prompt
- Verify Ollama model is working: ollama list
"""))
            
            api_map = extract_api_map(files)
            if api_map:
                files.append(("api_map.json", json.dumps(api_map, indent=2)))
            
            # Send file previews
            for path, code in files:
                yield format_sse({
                    "type": "file",
                    "filename": path,
                    "preview": code[:1000] + ("..." if len(code) > 1000 else ""),
                    "size": len(code)
                })
            
            # Always generate ZIP - even with just a README
            zip_file = make_zip(files)
            zip_bytes = zip_file.read()
            
            _generated_projects[project_id] = {
                "zip_bytes": zip_bytes,
                "files": files,
                "created_at": datetime.now().isoformat(),
                "arch_type": arch_type,
                "full_output": full_output  # Store raw output for debugging
            }
            
            # Send completion message
            yield format_sse({
                "type": "complete",
                "project_id": project_id,
                "files_count": len(files),
                "download_url": f"/nodegen/download/{project_id}",
                "message": f"Generated {len(files)} file(s). Download ready!"
            })
            
        except Exception as e:
            yield format_sse({
                "type": "error",
                "message": str(e)
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


@router.post("/prompt-to-backend", summary="Generate backend from prompt using Ollama (legacy - returns ZIP directly)")
async def prompt_to_backend(
    prompt: str = Form(..., description="Describe backend requirements (entities, rules, etc.)"),
    arch_type: str = Form("Monolith", description="Architecture type: Monolith or Microservices")
):
    """
    Generate backend code from a natural language prompt using Ollama LLM.
    Returns a ZIP file of the generated backend project.
    For streaming preview, use /prompt-to-backend-stream instead.
    """
    try:
        # Stream LLM output and collect
        generator = erd_or_prompt_backend(prompt, arch_type)
        full_output = ""
        for chunk in generator:
            text = getattr(chunk, "content", None) or str(chunk)
            full_output += text
        files = extract_files(full_output)
        api_map = extract_api_map(files)
        if api_map:
            files.append(("api_map.json", json.dumps(api_map, indent=2)))
        zip_file = make_zip(files)
        return StreamingResponse(zip_file, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=ollama_backend.zip"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama backend generation failed: {str(e)}")


@router.post("/frontend-to-backend-stream", summary="Generate backend from frontend ZIP with real-time streaming preview")
async def frontend_to_backend_stream(
    file: UploadFile = File(..., description="Frontend ZIP file (.zip) containing .js/.jsx/.ts/.tsx/.html files"),
    arch_type: str = Form("Monolith", description="Architecture type: Monolith or Microservices")
):
    """
    Generate backend code from frontend ZIP with real-time streaming preview.
    Returns Server-Sent Events (SSE) stream with code chunks.
    Use the returned project_id to download the final ZIP.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            # Send initial message
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "Analyzing frontend code..."
            })
            
            uploaded_zip = await file.read()
            frontend_code = extract_frontend_code(io.BytesIO(uploaded_zip))
            
            yield format_sse({
                "type": "info",
                "message": f"Extracted {len(frontend_code)} characters of frontend code. Generating backend..."
            })
            
            generator = frontend_to_backend(frontend_code, arch_type)
            full_output = ""
            
            # Stream every chunk immediately for real-time preview (like Streamlit)
            for chunk in generator:
                text = getattr(chunk, "content", None) or str(chunk)
                if text:
                    full_output += text
                    
                    # Send every chunk immediately for real-time display (like Streamlit)
                    yield format_sse({
                        "type": "stream",
                        "content": text,
                        "partial": True
                    })
                
                await asyncio.sleep(0.001)  # Reduced delay for smoother streaming
            
            # Extract all files from the generated output
            files = extract_files(full_output)
            
            # If no files were extracted but we have output, create fallback files
            if not files and full_output.strip():
                files.append(("generated_code.txt", full_output))
                files.append(("README.md", f"""# Generated Backend Code

This backend code was generated from frontend analysis.

## Architecture
{arch_type}

## Generated Output

See generated_code.txt for the full output.
"""))
            
            # Always generate at least a README if nothing else
            if not files:
                files.append(("README.md", f"""# Generated Backend

## Model Response
The model response was received but no files were extracted.

## Architecture
{arch_type}

## Raw Output
{full_output[:2000] if full_output else "No output received from model"}
"""))
            
            api_map = extract_api_map(files)
            if api_map:
                files.append(("api_map.json", json.dumps(api_map, indent=2)))
            
            # Send file previews
            for path, code in files:
                yield format_sse({
                    "type": "file",
                    "filename": path,
                    "preview": code[:1000] + ("..." if len(code) > 1000 else ""),
                    "size": len(code)
                })
            
            # Always generate ZIP - even with just a README
            zip_file = make_zip(files)
            zip_bytes = zip_file.read()
            
            _generated_projects[project_id] = {
                "zip_bytes": zip_bytes,
                "files": files,
                "created_at": datetime.now().isoformat(),
                "arch_type": arch_type,
                "full_output": full_output
            }
            
            # Send completion message
            yield format_sse({
                "type": "complete",
                "project_id": project_id,
                "files_count": len(files),
                "download_url": f"/nodegen/download/{project_id}",
                "message": f"Generated {len(files)} file(s). Download ready!"
            })
            
        except Exception as e:
            yield format_sse({
                "type": "error",
                "message": str(e)
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


@router.post("/frontend-to-backend", summary="Generate backend from frontend ZIP using Ollama (legacy - returns ZIP directly)")
async def frontend_to_backend_endpoint(
    file: UploadFile = File(..., description="Frontend ZIP file (.zip) containing .js/.jsx/.ts/.tsx/.html files"),
    arch_type: str = Form("Monolith", description="Architecture type: Monolith or Microservices")
):
    """
    Generate backend code from a frontend ZIP (React/HTML/JS) using Ollama LLM.
    Returns a ZIP file of the generated backend project.
    For streaming preview, use /frontend-to-backend-stream instead.
    """
    try:
        uploaded_zip = await file.read()
        frontend_code = extract_frontend_code(io.BytesIO(uploaded_zip))
        generator = frontend_to_backend(frontend_code, arch_type)
        full_output = ""
        for chunk in generator:
            text = getattr(chunk, "content", None) or str(chunk)
            full_output += text
        files = extract_files(full_output)
        api_map = extract_api_map(files)
        if api_map:
            files.append(("api_map.json", json.dumps(api_map, indent=2)))
        zip_file = make_zip(files)
        return StreamingResponse(zip_file, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=ollama_backend_from_frontend.zip"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama frontend-to-backend generation failed: {str(e)}")

@router.post("/advanced-upload-erd", summary="🚀 AI-Powered Advanced Generator: Upload ERD Image")
async def advanced_upload_erd_and_generate(
    file: UploadFile = File(..., description="ERD image file (PNG, JPG, JPEG)"),
    additional_context: Optional[str] = Form(None, description="Additional context or requirements for the backend"),
    gemini_model: Optional[str] = Form("gemini-flash-latest", description="Gemini model to use (gemini-flash-latest, gemini-1.5-flash, etc.)")
):
    """
    🚀 AI-Powered Advanced Generator: Upload ERD Image and Generate Professional Backend
    
    This endpoint uses AI (Gemini Flash Latest) to:
    1. Analyze your ERD image with advanced AI processing
    2. Extract comprehensive schema information
    3. Generate professional Node.js backend with complete structure
    4. Include all advanced features (middleware, auth, validation, testing, docs)
    
    Features:
    - 🤖 AI-powered ERD analysis using Gemini Flash Latest
    - 🏗️ Complete directory structure (25+ files)
    - 🔒 Advanced security middleware (helmet, cors, rate limiting)
    - 🔐 JWT authentication & authorization ready
    - ✅ Comprehensive validation with Joi
    - 📊 Advanced logging with Winston
    - 🗄️ Database migrations and seeders
    - 🧪 Complete test suite with Jest
    - 📚 API documentation (OpenAPI/Swagger)
    - 🎯 Role-based access control ready
    - 🚀 Production-ready configuration
    
    The AI will intelligently analyze your ERD and generate a backend that matches 100%!
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image (PNG, JPG, JPEG)")
        
        # Read file content
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Initialize ERD processing service with API key
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable.")
        
        erd_service = ERDProcessingService(gemini_api_key)
        
        # Process ERD image with AI
        print(f"🤖 Processing ERD with {gemini_model}...")
        print(f"📁 File size: {len(content)} bytes")
        print(f"📝 Additional context: {additional_context or 'None'}")
        
        # Encode image data to base64 for ERD parser
        image_data_b64 = base64.b64encode(content).decode('utf-8')
        print(f"🔧 Image encoded to base64: {len(image_data_b64)} characters")
        
        erd_result = await erd_service.process_erd(
            image_data=image_data_b64,
            additional_context=additional_context,
            model_override=gemini_model
        )
        
        if not erd_result.success:
            raise HTTPException(status_code=400, detail=f"ERD processing failed: {erd_result.error_message}")
        
        print(f"✅ ERD processed successfully. Entities: {len(erd_result.erd_schema.entities)}")
        
        # Generate advanced backend using the processed ERD schema
        from .advanced_generator import AdvancedNodeProjectGenerator
        gen = AdvancedNodeProjectGenerator()
        project = gen.generate(erd_result.erd_schema)
        
        # Generate intelligent filename based on project name
        project_name = erd_result.erd_schema.project_name or "AdvancedBackend"
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        # Zip the project
        zip_filename = f"🚀_ai_advanced_{safe_name}_backend.zip"
        zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(project.output_dir):
                for f in files:
                    abs_path = os.path.join(root, f)
                    rel_path = os.path.relpath(abs_path, project.output_dir)
                    zf.write(abs_path, rel_path)
        
        print(f"🎉 Advanced backend generated successfully: {zip_filename}")
        return FileResponse(
            zip_path, 
            filename=zip_filename, 
            media_type="application/zip",
            headers={
                "X-Project-Name": project_name,
                "X-Entities-Count": str(len(erd_result.erd_schema.entities)),
                "X-AI-Model": gemini_model
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Advanced generator error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"🚀 AI Advanced Generator Error: {str(e)}")


@router.get("/download/{project_id}", summary="Download generated backend ZIP file")
async def download_project(project_id: str):
    """
    Download the generated backend ZIP file using the project_id from streaming endpoint.
    """
    if project_id not in _generated_projects:
        raise HTTPException(status_code=404, detail="Project not found or expired")
    
    project = _generated_projects[project_id]
    zip_bytes = project["zip_bytes"]
    arch_type = project["arch_type"]
    
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=backend_{arch_type.lower()}_{project_id[:8]}.zip"
        }
    )


@router.get("/preview/{project_id}", summary="Preview generated files")
async def preview_project(project_id: str):
    """
    Get preview of all generated files for a project.
    """
    if project_id not in _generated_projects:
        raise HTTPException(status_code=404, detail="Project not found or expired")
    
    project = _generated_projects[project_id]
    files_preview = []
    
    for path, code in project["files"]:
        files_preview.append({
            "filename": path,
            "size": len(code),
            "preview": code[:1000] + ("..." if len(code) > 1000 else ""),
            "full_length": len(code)
        })
    
    return {
        "project_id": project_id,
        "created_at": project["created_at"],
        "arch_type": project["arch_type"],
        "files": files_preview,
        "download_url": f"/nodegen/download/{project_id}"
    }


