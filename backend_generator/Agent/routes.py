from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import os
import base64
import json
import uuid
import asyncio
import zipfile
import tempfile
from datetime import datetime
from .langgraph_agent import LangGraphCodeCraftAgent

router = APIRouter(prefix="/agent", tags=["🤖 LangGraph AI Agent"])

# Temporary storage for generated files (in production, use Redis or database)
_generated_projects = {}

def format_sse(data: dict) -> str:
    """Format data as Server-Sent Events."""
    return f"data: {json.dumps(data)}\n\n"

# Initialize the LangGraph agent
agent = None

def get_langgraph_agent():
    """Get or create the LangGraph CodeCraft agent"""
    global agent
    if agent is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        agent = LangGraphCodeCraftAgent(gemini_api_key)
    return agent

@router.post("/upload-erd-stream", summary="🤖 Upload ERD and Generate Complete Backend (Streaming)")
async def upload_erd_and_generate_backend_stream(
    file: UploadFile = File(..., description="ERD image file"),
    additional_context: Optional[str] = Form(None, description="Additional context or requirements"),
    agent_instance: LangGraphCodeCraftAgent = Depends(get_langgraph_agent)
):
    """
    🤖 LangGraph AI Agent: Upload ERD and get complete Node.js backend with live streaming!
    
    This endpoint provides a seamless workflow with real-time progress updates:
    1. Upload your ERD image
    2. AI analyzes and extracts schema (streamed)
    3. Automatically generates Node.js backend (streamed)
    4. Downloads complete project as ZIP
    
    Returns Server-Sent Events (SSE) stream with live code generation.
    """
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            # Send initial message
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "🤖 Starting ERD analysis and backend generation..."
            })
            
            # Read and encode the image
            content = await file.read()
            image_data = base64.b64encode(content).decode('utf-8')
            
            yield format_sse({
                "type": "info",
                "message": "📤 ERD image uploaded. Analyzing with AI..."
            })
            
            # Process with LangGraph agent
            result = await agent_instance.process_erd_to_backend(
                image_data=image_data,
                additional_context=additional_context
            )
            
            if result["success"]:
                yield format_sse({
                    "type": "info",
                    "message": "✅ ERD analyzed successfully! Generating backend code..."
                })
                
                # Stream backend generation progress
                if result.get("backend_zip_path") and os.path.exists(result["backend_zip_path"]):
                    zip_path = result["backend_zip_path"]
                    filename = os.path.basename(zip_path)
                    
                    # Read the zip file and extract files for preview
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as z:
                            file_list = z.namelist()
                            yield format_sse({
                                "type": "info",
                                "message": f"📦 Generated {len(file_list)} files in backend project"
                            })
                            
                            # Stream file previews (first 10 files)
                            for i, file_name in enumerate(file_list[:10]):
                                try:
                                    file_content = z.read(file_name).decode('utf-8', errors='ignore')
                                    preview = file_content[:1000] + ("..." if len(file_content) > 1000 else "")
                                    yield format_sse({
                                        "type": "file",
                                        "filename": file_name,
                                        "preview": preview,
                                        "size": len(file_content)
                                    })
                                except:
                                    pass
                            
                            if len(file_list) > 10:
                                yield format_sse({
                                    "type": "info",
                                    "message": f"... and {len(file_list) - 10} more files"
                                })
                    except Exception as e:
                        yield format_sse({
                            "type": "info",
                            "message": f"📦 Backend project generated successfully"
                        })
                    
                    # Read zip file bytes
                    with open(zip_path, 'rb') as f:
                        zip_bytes = f.read()
                    
                    _generated_projects[project_id] = {
                        "zip_bytes": zip_bytes,
                        "created_at": datetime.now().isoformat(),
                        "arch_type": "Backend",
                    }
                    
                    yield format_sse({
                        "type": "complete",
                        "project_id": project_id,
                        "files_count": len(file_list) if 'file_list' in locals() else 0,
                        "download_url": f"/agent/download/{project_id}",
                        "message": f"🎉 Backend generation complete! {len(file_list) if 'file_list' in locals() else 0} files generated."
                    })
                else:
                    yield format_sse({
                        "type": "error",
                        "message": "🤖 AI Agent: Backend generation completed but file not found"
                    })
            else:
                # Provide more helpful error messages
                error_msg = result.get('error_message', 'Unknown error')
                yield format_sse({
                    "type": "error",
                    "message": f"❌ {error_msg}"
                })
            
        except Exception as e:
            yield format_sse({
                "type": "error",
                "message": f"🤖 AI Agent Error: {str(e)}"
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


@router.post("/upload-erd", summary="🤖 Upload ERD and Generate Complete Backend (Legacy - returns ZIP directly)")
async def upload_erd_and_generate_backend(
    file: UploadFile = File(..., description="ERD image file"),
    additional_context: Optional[str] = Form(None, description="Additional context or requirements"),
    agent_instance: LangGraphCodeCraftAgent = Depends(get_langgraph_agent)
):
    """
    🤖 LangGraph AI Agent: Upload ERD and get complete Node.js backend automatically!
    
    This endpoint provides a seamless workflow:
    1. Upload your ERD image
    2. AI analyzes and extracts schema
    3. Automatically generates Node.js backend
    4. Downloads complete project as ZIP
    
    No manual steps required - the AI agent handles everything!
    For streaming preview, use /upload-erd-stream instead.
    """
    try:
        # Read and encode the image
        content = await file.read()
        image_data = base64.b64encode(content).decode('utf-8')
        
        # Process with LangGraph agent
        result = await agent_instance.process_erd_to_backend(
            image_data=image_data,
            additional_context=additional_context
        )
        
        if result["success"]:
            # Return the backend zip file with intelligent naming
            if result.get("backend_zip_path") and os.path.exists(result["backend_zip_path"]):
                # Extract filename from path for better naming
                zip_path = result["backend_zip_path"]
                filename = os.path.basename(zip_path)
                
                return FileResponse(
                    zip_path,
                    filename=f"🤖_{filename}",
                    media_type="application/zip"
                )
            else:
                raise HTTPException(status_code=500, detail="🤖 AI Agent: Backend generation completed but file not found")
        else:
            # Provide more helpful error messages
            error_msg = result.get('error_message', 'Unknown error')
            if "Invalid JSON" in error_msg:
                raise HTTPException(
                    status_code=400, 
                    detail="🤖 AI Agent: The ERD image could not be processed properly. Please ensure the image is clear and contains a valid ERD diagram."
                )
            elif "ERD processing failed" in error_msg:
                raise HTTPException(
                    status_code=400, 
                    detail=f"🤖 AI Agent: {error_msg}"
                )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"🤖 AI Agent Error: {error_msg}"
                )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🤖 AI Agent Error: {str(e)}")

@router.post("/process-schema", summary="🤖 Process ERD Schema and Generate Backend")
async def process_schema_and_generate_backend(
    erd_schema: dict,
    agent_instance: LangGraphCodeCraftAgent = Depends(get_langgraph_agent)
):
    """
    🤖 LangGraph AI Agent: Process ERD schema and generate backend
    
    Provide an ERD schema and the AI agent will:
    1. Validate and optimize the schema
    2. Generate complete Node.js backend
    3. Return download link
    """
    try:
        # Convert dict to ERDSchema object
        from ..ERD.models import ERDSchema
        schema_obj = ERDSchema(**erd_schema)
        
        # Generate intelligent project name
        project_name = agent_instance._generate_project_name(schema_obj, None)
        safe_name = agent_instance._sanitize_filename(project_name)
        
        # Generate backend directly from schema
        project = agent_instance.nodegen_service.generate(schema_obj)
        
        # Create zip file with intelligent naming
        import tempfile
        import zipfile
        zip_path = os.path.join(tempfile.gettempdir(), f"{safe_name}_backend.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(project.output_dir):
                for f in files:
                    abs_path = os.path.join(root, f)
                    rel_path = os.path.relpath(abs_path, project.output_dir)
                    zf.write(abs_path, rel_path)
        
        return FileResponse(
            zip_path,
            filename=f"🤖_{safe_name}_backend.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🤖 AI Agent Error: {str(e)}")

@router.get("/capabilities", summary="🤖 Get AI Agent Capabilities")
async def get_agent_capabilities():
    """
    🤖 Get information about the LangGraph AI Agent capabilities.
    """
    return {
        "agent_name": "CodeCraft LangGraph AI Agent",
        "framework": "LangGraph + LangChain",
        "ai_model": "Gemini Flash Latest",
        "workflow_type": "Seamless ERD to Backend",
        "capabilities": [
            "🧠 Intelligent ERD image analysis",
            "⚡ Automatic schema extraction and validation", 
            "🚀 Smart Node.js backend generation",
            "🔄 Multi-step reasoning and error recovery",
            "📦 Complete project packaging",
            "🎯 Context-aware processing",
            "💬 Conversational AI responses"
        ],
        "workflow": [
            "1. 📤 Upload ERD image",
            "2. 🔍 AI analyzes and extracts schema", 
            "3. ✅ Validates and optimizes schema",
            "4. 🏗️ Generates complete Node.js backend",
            "5. 📦 Packages and delivers project"
        ],
        "tools": [
            "🔧 ERD Analysis Tool",
            "📋 Schema Validation Tool", 
            "🏗️ Backend Generation Tool",
            "🛠️ Error Handling Tool",
            "📦 Project Packaging Tool"
        ],
        "benefits": [
            "No manual steps required",
            "Intelligent error handling",
            "Complete automation",
            "Best practices included",
            "Production-ready code"
        ]
    }

@router.get("/download/{project_id}", summary="Download generated backend ZIP file")
async def download_project(project_id: str):
    """
    Download the generated backend ZIP file using the project_id from streaming endpoint.
    """
    if project_id not in _generated_projects:
        raise HTTPException(status_code=404, detail="Project not found or expired")
    
    project = _generated_projects[project_id]
    zip_bytes = project["zip_bytes"]
    
    from fastapi.responses import Response
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=backend_{project_id[:8]}.zip"
        }
    )


@router.get("/status", summary="🤖 Get AI Agent Status")
async def get_agent_status():
    """
    🤖 Check the status of the LangGraph AI Agent.
    """
    try:
        agent = get_langgraph_agent()
        return {
            "status": "active",
            "agent_type": "LangGraph AI Agent",
            "model": "Gemini Flash Latest",
            "capabilities": "Full ERD to Backend automation",
            "ready": True
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "ready": False
        }