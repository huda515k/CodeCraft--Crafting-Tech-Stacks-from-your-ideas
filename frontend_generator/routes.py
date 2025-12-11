# frontend_generator/routes.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, List
import os
import base64
from datetime import datetime
import io
import json
import uuid
import zipfile
import sys
from pathlib import Path

from .models import UIProcessingRequest, UIProcessingResponse
from .services import FrontendGenerationService
from .langgraph_agent import LangGraphFrontendAgent
from .multi_ui_reactgenerator import EnhancedMultiScreenGenerator
import tempfile
import shutil
import asyncio
import concurrent.futures
import queue

# Import from Codecraft_manual (Ollama-based UI to Frontend)
project_root = Path(__file__).parent.parent.parent
codecraft_llmbackend_path = project_root / "Codecraft_manual" / "codingai" / "llmbackend"
if str(codecraft_llmbackend_path) not in sys.path:
    sys.path.insert(0, str(codecraft_llmbackend_path))

router = APIRouter(prefix="/frontend", tags=["Frontend Generation"])

# Temporary storage for generated files (in production, use Redis or database)
_generated_projects = {}

def format_sse(data: dict) -> str:
    """Format data as Server-Sent Events."""
    return f"data: {json.dumps(data)}\n\n"

# Dependency injection for frontend service
def get_frontend_service():
    """Service that requires GEMINI_API_KEY (for image parsing endpoints)."""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    return FrontendGenerationService(gemini_api_key)

# Dependency injection for LangGraph frontend agent
def get_langgraph_frontend_agent():
    """Get LangGraph frontend agent instance - creates fresh instance each time"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    # Import fresh each time to avoid caching issues
    import importlib
    import sys
    
    # Clear module cache
    modules_to_clear = [k for k in list(sys.modules.keys()) if 'frontend_generator.langgraph_agent' in k]
    for mod_key in modules_to_clear:
        del sys.modules[mod_key]
    
    # Import fresh
    from frontend_generator.langgraph_agent import LangGraphFrontendAgent
    
    # Verify methods exist on class before creating instance
    required_methods = ['process_ui_to_react', 'process_multi_ui_to_react']
    missing_methods = [m for m in required_methods if not hasattr(LangGraphFrontendAgent, m)]
    if missing_methods:
        class_methods = [m for m in dir(LangGraphFrontendAgent) if not m.startswith('_')]
        raise HTTPException(
            status_code=500, 
            detail=f"LangGraphFrontendAgent class missing methods: {missing_methods}. Available class methods: {class_methods}"
        )
    
    # Create instance
    agent = LangGraphFrontendAgent(gemini_api_key)
    
    # Verify methods exist on instance
    missing_instance_methods = [m for m in required_methods if not hasattr(agent, m)]
    if missing_instance_methods:
        instance_methods = [m for m in dir(agent) if not m.startswith('_')]
        raise HTTPException(
            status_code=500,
            detail=f"LangGraphFrontendAgent instance missing methods: {missing_instance_methods}. Instance type: {type(agent)}, Available instance methods: {instance_methods}"
        )
    
    return agent

@router.post("/upload-ui", response_model=UIProcessingResponse)
async def upload_ui_image(
    file: UploadFile = File(..., description="UI design image file (Figma, Canva, or screenshot)"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions"),
    framework: str = Form("react", description="Target framework"),
    styling_approach: str = Form("css-modules", description="Styling approach (css-modules, tailwind)"),
    service: FrontendGenerationService = Depends(get_frontend_service)
):
    """
    🤖 AI Agent: Upload and process a UI design image
    
    Supported formats: PNG, JPG, JPEG, GIF, BMP
    The AI agent will intelligently analyze your UI design and extract:
    - Components and their hierarchy
    - Layout structure
    - Colors and typography
    - Spacing and styling details
    
    Returns structured UI analysis ready for code generation.
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 10MB"
        )
    
    try:
        # Convert to base64
        image_data = base64.b64encode(file_content).decode('utf-8')
        
        # Process UI
        request = UIProcessingRequest(
            image_data=image_data,
            additional_context=additional_context,
            framework=framework,
            styling_approach=styling_approach
        )
        
        result = await service.process_ui(request)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.post("/agent/generate-react-stream", summary="🤖 Generate React from UI with live streaming")
async def generate_react_from_ui_stream(
    file: UploadFile = File(..., description="UI design image file"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions"),
    framework: str = Form("react", description="Target framework"),
    styling_approach: str = Form("css-modules", description="Styling approach"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
    agent: LangGraphFrontendAgent = Depends(get_langgraph_frontend_agent)
):
    """
    🤖 AI Agent: Generate React code from UI design image with live streaming!
    
    This endpoint provides real-time progress updates:
    1. Analyzes your UI design image using AI (streamed)
    2. Extracts components, styles, and layout (streamed)
    3. Generates complete React project with all files (streamed)
    4. Returns downloadable ZIP file
    
    Returns Server-Sent Events (SSE) stream with live code generation.
    """
    # Read file content BEFORE creating the generator to avoid "I/O operation on closed file" error
    # Validate file type first
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check file size and read content
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 10MB"
        )
    
    # Convert to base64 immediately
    image_data = base64.b64encode(file_content).decode('utf-8')
    
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            # Send initial message
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "🎨 Starting UI analysis and React code generation..."
            })
            
            yield format_sse({
                "type": "info",
                "message": "📤 UI image uploaded. Analyzing with AI..."
            })
            
            # Process with LangGraph agent
            result = await agent.process_ui_to_react(
                image_data=image_data,
                additional_context=additional_context,
                project_name="react-app",
                include_typescript=include_typescript,
                styling_approach=styling_approach
            )
            
            if result.get("success") and result.get("project_files"):
                yield format_sse({
                    "type": "info",
                    "message": "✅ UI analyzed successfully! Generating React code..."
                })
                
                project_files = result["project_files"]
                file_count = len(project_files)
                
                yield format_sse({
                    "type": "info",
                    "message": f"📦 Generated {file_count} files in React project"
                })
                
                # Stream file previews
                for file_name, file_content in list(project_files.items())[:15]:
                    preview = file_content[:1000] + ("..." if len(file_content) > 1000 else "")
                    yield format_sse({
                        "type": "file",
                        "filename": file_name,
                        "preview": preview,
                        "size": len(file_content)
                    })
                
                if file_count > 15:
                    yield format_sse({
                        "type": "info",
                        "message": f"... and {file_count - 15} more files"
                    })
                
                # Create ZIP file
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
                    "files_count": file_count,
                    "download_url": f"/frontend/download/{project_id}",
                    "message": f"🎉 Frontend generation complete! {file_count} files generated."
                })
            else:
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


@router.post("/generate-react", summary="🤖 Generate React from UI (Legacy - returns ZIP directly)")
async def generate_react_from_ui(
    file: UploadFile = File(..., description="UI design image file"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions"),
    framework: str = Form("react", description="Target framework"),
    styling_approach: str = Form("css-modules", description="Styling approach"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
    use_ai: bool = Form(False, description="Use AI-powered code generator (LangGraph agent) for better UI matching"),
    service: FrontendGenerationService = Depends(get_frontend_service)
):
    """
    🤖 AI Agent: Generate React code from UI design image
    
    This endpoint:
    1. Analyzes your UI design image using AI
    2. Extracts components, styles, and layout
    3. Generates complete React project with all files
    4. Returns downloadable ZIP file
    
    Features:
    - 🎨 Pixel-perfect component extraction
    - 🎯 Accurate color and typography extraction
    - 📦 Complete React project structure
    - 💅 CSS modules or Tailwind support
    - 📘 TypeScript support
    - 🔧 Ready-to-run code
    
    For streaming preview, use /agent/generate-react-stream instead.
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check file size
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 10MB"
        )
    
    try:
        # Convert to base64
        image_data = base64.b64encode(file_content).decode('utf-8')
        
        # Process and generate
        result = await service.process_and_generate(
            image_data=image_data,
            additional_context=additional_context,
            framework=framework,
            styling_approach=styling_approach,
            include_typescript=include_typescript,
            use_ai=use_ai
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error_message", "Generation failed")
            )
        
        # Create ZIP file
        project = result["project"]
        zip_buffer = service.create_zip_from_project(project)
        
        # Generate filename
        project_name = project.project_name or "react-app"
        filename = f"{project_name.replace(' ', '_')}_frontend.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating React code: {str(e)}")

@router.post("/analyze-ui-only")
async def analyze_ui_only(
    file: UploadFile = File(..., description="UI design image file"),
    additional_context: Optional[str] = Form(None, description="Additional context"),
    service: FrontendGenerationService = Depends(get_frontend_service)
):
    """
    🤖 AI Agent: Analyze UI design without generating code
    
    Use this endpoint to get detailed UI analysis including:
    - Component structure
    - Color palette
    - Typography
    - Layout information
    
    Perfect for reviewing the analysis before generating code.
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check file size
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 10MB"
        )
    
    try:
        # Convert to base64
        image_data = base64.b64encode(file_content).decode('utf-8')
        
        # Process UI
        request = UIProcessingRequest(
            image_data=image_data,
            additional_context=additional_context
        )
        
        result = await service.process_ui(request)
        
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=result.error_message or "UI analysis failed"
            )
        
        # Return detailed analysis
        return {
            "success": True,
            "ui_analysis": result.ui_analysis.dict(),
            "processing_metadata": result.processing_metadata,
            "components_count": len(result.ui_analysis.components) if result.ui_analysis else 0,
            "message": "🤖 AI Agent: UI analyzed successfully! Ready for code generation."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing UI: {str(e)}")

@router.post("/generate-multi-screen")
async def generate_multi_screen_app(
    files: List[UploadFile] = File(..., description="Multiple UI design image files for different screens"),
    screen_names: Optional[str] = Form(None, description="Comma-separated screen names (e.g., 'Home,Profile,Settings')"),
    screen_routes: Optional[str] = Form(None, description="Comma-separated routes (e.g., '/,/profile,/settings')"),
    project_name: str = Form("multi-screen-app", description="Project name"),
    additional_context: Optional[str] = Form(None, description="Additional context for all screens"),
    framework: str = Form("react", description="Target framework"),
    styling_approach: str = Form("css-modules", description="Styling approach"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
    use_ai: bool = Form(False, description="Use AI-powered code generator (LangGraph agent) for better UI matching"),
    service: FrontendGenerationService = Depends(get_frontend_service)
):
    """
    🤖 AI Agent: Generate React app with multiple screens connected via React Router
    
    This endpoint:
    1. Accepts multiple UI design images (one per screen)
    2. Analyzes each screen using AI
    3. Generates React components for each screen
    4. Connects all screens with React Router
    5. Returns a complete multi-screen React application
    
    Features:
    - 🎨 Multiple screen support
    - 🔗 React Router integration
    - 📱 Navigation between screens
    - 🎯 Shared component library
    - 💅 Consistent styling across screens
    - 📦 Complete project structure
    
    Example:
    - Upload 3 images: Home.png, Profile.png, Settings.png
    - Get a complete app with navigation between all 3 screens
    """
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one image file is required"
        )
    
    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 screens allowed per project"
        )
    
    # Validate all files
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    max_size = 10 * 1024 * 1024  # 10MB per file
    
    screen_images = []
    parsed_screen_names = None
    parsed_screen_routes = None
    
    # Parse screen names and routes
    if screen_names:
        parsed_screen_names = [name.strip() for name in screen_names.split(',')]
    if screen_routes:
        parsed_screen_routes = [route.strip() for route in screen_routes.split(',')]
    
    try:
        # Process all files
        for idx, file in enumerate(files):
            # Validate file type
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename}: Unsupported file type. Allowed types: {', '.join(allowed_types)}"
                )
            
            # Check file size
            file_content = await file.read()
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename}: File size too large. Maximum size is 10MB"
                )
            
            # Convert to base64
            image_data = base64.b64encode(file_content).decode('utf-8')
            screen_images.append(image_data)
        
        # Auto-generate or truncate screen names and routes to match file count
        if not parsed_screen_names:
            parsed_screen_names = [f"Screen{i+1}" for i in range(len(screen_images))]
        elif len(parsed_screen_names) < len(screen_images):
            # If some names provided, use them and auto-generate the rest
            for i in range(len(parsed_screen_names), len(screen_images)):
                parsed_screen_names.append(f"Screen{i+1}")
        elif len(parsed_screen_names) > len(screen_images):
            # If more names provided than files, truncate to match file count
            parsed_screen_names = parsed_screen_names[:len(screen_images)]
        
        if not parsed_screen_routes:
            # Default routes: first is "/", rest are "/screen2", "/screen3", etc.
            parsed_screen_routes = ["/"] if len(screen_images) == 1 else ["/"] + [f"/screen{i+1}" for i in range(1, len(screen_images))]
        elif len(parsed_screen_routes) < len(screen_images):
            # If some routes provided, use them and auto-generate the rest
            for i in range(len(parsed_screen_routes), len(screen_images)):
                parsed_screen_routes.append(f"/screen{i+1}")
        elif len(parsed_screen_routes) > len(screen_images):
            # If more routes provided than files, truncate to match file count
            parsed_screen_routes = parsed_screen_routes[:len(screen_images)]
        
        # Generate multi-screen project
        result = await service.generate_multi_screen_project(
            screen_images=screen_images,
            screen_names=parsed_screen_names,
            screen_routes=parsed_screen_routes,
            project_name=project_name,
            additional_context=additional_context,
            framework=framework,
            styling_approach=styling_approach,
            include_typescript=include_typescript,
            use_ai=use_ai
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error_message", "Multi-screen generation failed")
            )
        
        # Create ZIP file
        project = result["project"]
        zip_buffer = service.create_zip_from_project(project)
        
        # Generate filename
        filename = f"{project_name.replace(' ', '_')}_multi_screen.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Screens-Count": str(result.get("screens_count", len(screen_images)))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating multi-screen app: {str(e)}")

@router.post("/agent/generate-multi-screen", summary="🤖 AI Agent: Upload Multiple UI Screens and Generate Complete Multi-Screen React App")
async def agent_generate_multi_screen_react(
    files: List[UploadFile] = File(..., description="Multiple UI design image files for different screens"),
    screen_names: Optional[str] = Form(None, description="Comma-separated screen names (e.g., 'Home,Profile,Settings')"),
    screen_routes: Optional[str] = Form(None, description="Comma-separated routes (e.g., '/,/profile,/settings')"),
    project_name: str = Form("multi-screen-app", description="Project name"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions for all screens"),
    framework: str = Form("react", description="Target framework"),
    styling_approach: str = Form("css-modules", description="Styling approach"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
    agent_instance: LangGraphFrontendAgent = Depends(get_langgraph_frontend_agent)
):
    """
    🤖 LangGraph AI Agent: Upload Multiple UI Screens and Get Complete Multi-Screen React App!
    
    This endpoint uses the LangGraph AI agent for intelligent multi-screen code generation:
    1. Upload multiple UI design images (one per screen)
    2. AI analyzes each screen and extracts component structure
    3. AI generates structured React code for each screen
    4. AI connects all screens with React Router
    5. Downloads complete multi-screen project as ZIP
    
    Features:
    - 🎨 AI-powered component generation for each screen
    - 🔗 Automatic React Router integration
    - 📱 Navigation between all screens
    - 🎯 Better UI matching with structured code
    - 📦 Complete React project structure
    - 💅 CSS modules or Tailwind support
    - 📘 TypeScript support
    - 🔧 Production-ready code
    
    Example:
    - Upload 3 images: Home.png, Profile.png, Settings.png
    - Screen names: "Home,Profile,Settings"
    - Routes: "/,/profile,/settings"
    - Get a complete app with navigation between all 3 screens!
    
    No manual steps required - the AI agent handles everything!
    """
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one image file is required"
        )
    
    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 screens allowed per project"
        )
    
    # Validate all files
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    max_size = 10 * 1024 * 1024  # 10MB per file
    
    screen_images = []
    parsed_screen_names = None
    parsed_screen_routes = None
    
    try:
        # Process all files FIRST - we need to know how many files we have
        for idx, file in enumerate(files):
            # Validate file type
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for file {idx + 1}: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
                )
            
            # Check file size
            file_content = await file.read()
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {idx + 1} is too large. Maximum size is 10MB per file"
                )
            
            # Convert to base64
            image_data = base64.b64encode(file_content).decode('utf-8')
            screen_images.append(image_data)
        
        # NOW parse and auto-generate screen names and routes AFTER processing files
        # This ensures we know the exact number of files
        # Handle empty strings, "string" placeholder from Swagger, and None
        if screen_names and screen_names.strip() and screen_names.strip().lower() not in ['string', '']:
            parsed_screen_names = [name.strip() for name in screen_names.split(',') if name.strip()]
        else:
            parsed_screen_names = []  # Empty list - will be auto-generated
        
        if screen_routes and screen_routes.strip() and screen_routes.strip().lower() not in ['string', '']:
            parsed_screen_routes = [route.strip() for route in screen_routes.split(',') if route.strip()]
        else:
            parsed_screen_routes = []  # Empty list - will be auto-generated
            
        # Auto-generate or truncate screen names to match file count
        if len(parsed_screen_names) == 0:
            parsed_screen_names = [f"Screen{i+1}" for i in range(len(screen_images))]
            print(f"🔧 Auto-generated {len(parsed_screen_names)} screen names: {parsed_screen_names}")
        elif len(parsed_screen_names) < len(screen_images):
            # If some names provided, use them and auto-generate the rest
            print(f"🔧 Auto-generating {len(screen_images) - len(parsed_screen_names)} missing screen names...")
            for i in range(len(parsed_screen_names), len(screen_images)):
                parsed_screen_names.append(f"Screen{i+1}")
            print(f"   Final screen names: {parsed_screen_names}")
        elif len(parsed_screen_names) > len(screen_images):
            # If more names provided than files, truncate to match file count
            print(f"🔧 Truncating {len(parsed_screen_names)} screen names to match {len(screen_images)} files...")
            parsed_screen_names = parsed_screen_names[:len(screen_images)]
            print(f"   Final screen names: {parsed_screen_names}")
        
        if not parsed_screen_routes or len(parsed_screen_routes) == 0:
            # Default routes: first is "/", rest are "/screen2", "/screen3", etc.
            parsed_screen_routes = ["/"] if len(screen_images) == 1 else ["/"] + [f"/screen{i+1}" for i in range(1, len(screen_images))]
            print(f"🔧 Auto-generated {len(parsed_screen_routes)} screen routes: {parsed_screen_routes}")
        elif len(parsed_screen_routes) < len(screen_images):
            # If some routes provided, use them and auto-generate the rest
            print(f"🔧 Auto-generating {len(screen_images) - len(parsed_screen_routes)} missing screen routes...")
            for i in range(len(parsed_screen_routes), len(screen_images)):
                parsed_screen_routes.append(f"/screen{i+1}")
            print(f"   Final screen routes: {parsed_screen_routes}")
        elif len(parsed_screen_routes) > len(screen_images):
            # If more routes provided than files, truncate to match file count
            print(f"🔧 Truncating {len(parsed_screen_routes)} screen routes to match {len(screen_images)} files...")
            parsed_screen_routes = parsed_screen_routes[:len(screen_images)]
            print(f"   Final screen routes: {parsed_screen_routes}")
        
        # Final validation - ensure counts match (they should after auto-generation)
        if len(parsed_screen_names) != len(screen_images):
            raise HTTPException(
                status_code=500,
                detail=f"Internal error: Screen names count ({len(parsed_screen_names)}) doesn't match files count ({len(screen_images)}) after auto-generation"
            )
        if len(parsed_screen_routes) != len(screen_images):
            raise HTTPException(
                status_code=500,
                detail=f"Internal error: Screen routes count ({len(parsed_screen_routes)}) doesn't match files count ({len(screen_images)}) after auto-generation"
            )
        
        # Process with LangGraph agent
        # Verify method exists and get it safely
        if not hasattr(agent_instance, 'process_multi_ui_to_react'):
            available_methods = [m for m in dir(agent_instance) if not m.startswith('_') and callable(getattr(agent_instance, m, None))]
            raise HTTPException(
                status_code=500,
                detail=f"LangGraphFrontendAgent instance missing process_multi_ui_to_react method. Instance type: {type(agent_instance).__name__}, Available methods: {available_methods}"
            )
        
        # Get the method safely
        try:
            method = getattr(agent_instance, 'process_multi_ui_to_react')
            if not callable(method):
                raise HTTPException(
                    status_code=500,
                    detail=f"process_multi_ui_to_react exists but is not callable. Type: {type(method)}"
                )
        except AttributeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Could not get process_multi_ui_to_react method: {str(e)}"
            )
        
        # Call the method
        result = await method(
            screen_images=screen_images,
            screen_names=parsed_screen_names,
            screen_routes=parsed_screen_routes,
            project_name=project_name,
            additional_context=additional_context,
            include_typescript=include_typescript,
            styling_approach=styling_approach
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error_message", "AI agent multi-screen generation failed")
            )
        
        # Create ZIP file from project files
        from .models import GeneratedProject
        from .services import FrontendGenerationService
        
        project = GeneratedProject(
            project_name=result.get("project_name", project_name),
            files=result["project_files"],
            metadata={
                "framework": framework,
                "styling_approach": styling_approach,
                "typescript": include_typescript,
                "generation_method": "ai_langgraph_agent",
                "screens_count": result.get("screens_count", len(screen_images))
            }
        )
        
        # Create service instance just for ZIP creation
        service = FrontendGenerationService(os.getenv("GEMINI_API_KEY"))
        zip_buffer = service.create_zip_from_project(project)
        
        # Generate filename
        filename = f"{project_name.replace(' ', '_')}_multi_screen_frontend.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🤖 AI Agent Multi-Screen Error: {str(e)}")

@router.post("/agent/generate-react")
async def agent_generate_react_from_ui(
    file: UploadFile = File(..., description="UI design image file"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions"),
    project_name: str = Form("react-app", description="Project name"),
    framework: str = Form("react", description="Target framework"),
    styling_approach: str = Form("css-modules", description="Styling approach"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
    agent_instance: LangGraphFrontendAgent = Depends(get_langgraph_frontend_agent)
):
    """
    🤖 LangGraph AI Agent: Upload UI and get complete React app automatically!
    
    This endpoint uses the LangGraph AI agent for intelligent code generation:
    1. Upload your UI design image
    2. AI analyzes and extracts component structure
    3. AI generates structured React code that matches the UI
    4. Downloads complete project as ZIP
    
    Features:
    - 🎨 AI-powered component generation
    - 🎯 Better UI matching with structured code
    - 📦 Complete React project structure
    - 💅 CSS modules or Tailwind support
    - 📘 TypeScript support
    - 🔧 Production-ready code
    
    No manual steps required - the AI agent handles everything!
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    if not file.content_type or file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type or 'unknown'}. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check file size
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty. Please upload a valid image file."
        )
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 10MB"
        )
    
    try:
        # Convert to base64
        image_data = base64.b64encode(file_content).decode('utf-8')
        
        # Verify agent has the required method
        if not hasattr(agent_instance, 'process_ui_to_react'):
            raise HTTPException(
                status_code=500,
                detail=f"Agent instance missing process_ui_to_react method. Available methods: {[m for m in dir(agent_instance) if not m.startswith('_')]}"
            )
        
        # Process with LangGraph agent
        print(f"🚀 Processing UI with LangGraph agent...")
        print(f"   Project name: {project_name}")
        print(f"   Image data length: {len(image_data)}")
        print(f"   Include TypeScript: {include_typescript}")
        print(f"   Styling approach: {styling_approach}")
        
        result = await agent_instance.process_ui_to_react(
            image_data=image_data,
            project_name=project_name,
            additional_context=additional_context,
            include_typescript=include_typescript,
            styling_approach=styling_approach
        )
        
        print(f"📊 Agent result: success={result.get('success')}, error={result.get('error_message', 'None')}")
        
        if not result.get("success"):
            error_msg = result.get("error_message", "AI agent generation failed")
            print(f"❌ Agent generation failed: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"AI agent generation failed: {error_msg}"
            )
        
        # Create ZIP file from project files
        from .models import GeneratedProject
        from .services import FrontendGenerationService
        
        project = GeneratedProject(
            project_name=result.get("project_name", project_name),
            files=result["project_files"],
            metadata={
                "framework": framework,
                "styling_approach": styling_approach,
                "typescript": include_typescript,
                "generation_method": "ai_langgraph_agent"
            }
        )
        
        # Create service instance just for ZIP creation
        service = FrontendGenerationService(os.getenv("GEMINI_API_KEY"))
        zip_buffer = service.create_zip_from_project(project)
        
        # Generate filename
        filename = f"{project_name.replace(' ', '_')}_ai_frontend.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ AI Agent Error: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"🤖 AI Agent Error: {str(e)}")

@router.post("/claudeAgent/Multiple_ui_to_React", summary="🤖 Claude Agent: Generate Multi-Screen React App from Multiple UI Images")
async def claude_agent_multiple_ui_to_react(
    files: List[UploadFile] = File(..., description="Multiple UI design image files for different screens"),
    screen_names: Optional[str] = Form(None, description="Comma-separated screen names (e.g., 'Home,Profile,Settings')"),
    project_name: str = Form("multi-screen-app", description="Project name"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions for all screens"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
    styling_approach: str = Form("css-modules", description="Styling approach (css-modules or tailwind)")
):
    """
    🤖 Claude Agent: Upload Multiple UI Screens and Generate Complete Multi-Screen React App
    
    This endpoint uses the EnhancedMultiScreenGenerator to:
    1. Analyze multiple UI design images (one per screen)
    2. Detect navigation flow between screens
    3. Generate complete React application with React Router
    4. Return downloadable ZIP file
    
    Features:
    - 🎨 AI-powered screen analysis
    - 🔗 Automatic React Router integration
    - 📱 Navigation flow detection
    - 🎯 Pixel-perfect UI matching
    - 📦 Complete React project structure
    - 💅 CSS modules or Tailwind support
    - 📘 TypeScript support
    
    Example:
    - Upload 3 images: Home.png, Profile.png, Settings.png
    - Screen names: "Home,Profile,Settings"
    - Get a complete app with navigation between all 3 screens!
    """
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one image file is required"
        )
    
    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 screens allowed per project"
        )
    
    # Validate all files
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    max_size = 10 * 1024 * 1024  # 10MB per file
    
    # Parse screen names
    if screen_names and screen_names.strip() and screen_names.strip().lower() not in ['string', '']:
        parsed_screen_names = [name.strip() for name in screen_names.split(',') if name.strip()]
    else:
        parsed_screen_names = []
    
    # Auto-generate or truncate screen names to match file count
    if len(parsed_screen_names) == 0:
        parsed_screen_names = [f"Screen{i+1}" for i in range(len(files))]
    elif len(parsed_screen_names) < len(files):
        for i in range(len(parsed_screen_names), len(files)):
            parsed_screen_names.append(f"Screen{i+1}")
    elif len(parsed_screen_names) > len(files):
        parsed_screen_names = parsed_screen_names[:len(files)]
    
    # Create temporary directory for uploaded files
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="claude_agent_ui_")
        
        screen_images = []
        
        # Process all files
        for idx, file in enumerate(files):
            # Validate file type
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for file {idx + 1}: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
                )
            
            # Check file size
            file_content = await file.read()
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {idx + 1} is too large. Maximum size is 10MB per file"
                )
            
            # Save to temporary file
            # Handle case where filename might be None
            filename = file.filename or f"screen_{idx+1}"
            file_ext = filename.split('.')[-1] if '.' in filename else 'png'
            temp_file_path = os.path.join(temp_dir, f"screen_{idx}_{parsed_screen_names[idx]}.{file_ext}")
            
            with open(temp_file_path, 'wb') as f:
                f.write(file_content)
            
            screen_images.append({
                "path": temp_file_path,
                "name": parsed_screen_names[idx]
            })
        
        # Get Gemini API key
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Initialize generator
        generator = EnhancedMultiScreenGenerator(api_key=gemini_api_key)
        
        # Generate complete app
        print(f"🚀 Starting Claude Agent multi-screen generation...")
        print(f"   Screens: {len(screen_images)}")
        print(f"   Project: {project_name}")
        
        zip_bytes = await generator.generate_complete_app(
            screen_images=screen_images,
            project_name=project_name,
            include_typescript=include_typescript,
            styling_approach=styling_approach,
            output_format="zip"
        )
        
        # Generate filename
        filename = f"{project_name.replace(' ', '_')}_claude_agent_multi_screen_frontend.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error in claude_agent_multiple_ui_to_react: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"🤖 Claude Agent Multi-Screen Error: {str(e)}")
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"🧹 Cleaned up temporary directory: {temp_dir}")
            except Exception as cleanup_error:
                print(f"⚠️  Warning: Could not clean up temp directory {temp_dir}: {cleanup_error}")

@router.get("/download/{project_id}", summary="Download generated frontend ZIP file")
async def download_project(project_id: str):
    """
    Download the generated frontend ZIP file using the project_id from streaming endpoint.
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
            "Content-Disposition": f"attachment; filename=frontend_{project_id[:8]}.zip"
        }
    )

@router.post("/ollama/generate-react-stream", summary="🎨 Generate React from UI using Ollama local models (streaming)")
async def generate_react_from_ui_ollama_stream(
    file: UploadFile = File(..., description="UI design image file"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
    styling_approach: str = Form("tailwind", description="Styling approach (tailwind or css-modules)")
):
    """
    🎨 Ollama-based: Generate React code from UI design image with live streaming!
    
    This endpoint uses Ollama local models:
    - Vision model (llama3.2-vision/llava) for UI analysis
    - Qwen2.5-Coder for React code generation
    
    Returns Server-Sent Events (SSE) stream with live code generation.
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check file size and read content
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum size is 10MB"
        )
    
    project_id = str(uuid.uuid4())
    
    async def generate_and_stream():
        try:
            # Import Ollama-based UI to frontend
            from ui_to_frontend_ollama import ui_to_react_pipeline_streaming, extract_react_files, create_project_zip
            
            # Send initial message
            yield format_sse({
                "type": "start",
                "project_id": project_id,
                "message": "🎨 Starting UI analysis with Ollama local models..."
            })
            
            # Run the pipeline in non-blocking way
            import concurrent.futures
            import queue
            
            chunk_queue = queue.Queue()
            full_output = ""
            files = []
            
            def run_pipeline():
                """Run blocking pipeline in separate thread"""
                try:
                    for chunk in ui_to_react_pipeline_streaming(
                        [file_content],
                        additional_context or "",
                        include_typescript,
                        styling_approach
                    ):
                        chunk_queue.put(chunk)
                    chunk_queue.put(None)  # Signal completion
                except Exception as e:
                    chunk_queue.put(("error", str(e)))
            
            # Start pipeline in thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_pipeline)
                
                # Stream chunks as they arrive
                pipeline_done = False
                while not pipeline_done:
                    try:
                        # Get chunk with timeout
                        chunk = chunk_queue.get(timeout=1.0)
                        
                        if chunk is None:  # Completion signal
                            pipeline_done = True
                            break
                        if isinstance(chunk, tuple) and chunk[0] == "error":
                            raise Exception(chunk[1])
                        
                        # Stream all chunks including progress messages
                        if chunk:
                            yield format_sse({
                                "type": "stream",
                                "content": chunk,
                                "partial": True
                            })
                            full_output += chunk
                    except queue.Empty:
                        # Check if pipeline thread is still running
                        if future.done():
                            # Pipeline finished, check for remaining chunks
                            try:
                                while True:
                                    chunk = chunk_queue.get_nowait()
                                    if chunk is None:
                                        pipeline_done = True
                                        break
                                    if isinstance(chunk, tuple) and chunk[0] == "error":
                                        raise Exception(chunk[1])
                                    if chunk:
                                        yield format_sse({
                                            "type": "stream",
                                            "content": chunk,
                                            "partial": True
                                        })
                                        full_output += chunk
                            except queue.Empty:
                                pipeline_done = True
                                break
                        else:
                            # No chunk yet, yield control briefly
                            await asyncio.sleep(0.001)
                            continue
            
            # Extract files from the generated output
            files = extract_react_files(full_output)
            
            if not files:
                yield format_sse({
                    "type": "error",
                    "message": "⚠️ No files extracted from generated code. Please try again."
                })
                return
            
            # Send file previews
            for filepath, content in files[:15]:
                preview = content[:1000] + ("..." if len(content) > 1000 else "")
                yield format_sse({
                    "type": "file",
                    "filename": filepath,
                    "preview": preview,
                    "size": len(content)
                })
            
            if len(files) > 15:
                yield format_sse({
                    "type": "info",
                    "message": f"... and {len(files) - 15} more files"
                })
            
            # Create ZIP file
            zip_buffer = create_project_zip(files)
            zip_bytes = zip_buffer.getvalue()
            
            _generated_projects[project_id] = {
                "zip_bytes": zip_bytes,
                "created_at": datetime.now().isoformat(),
                "arch_type": "Frontend",
            }
            
            yield format_sse({
                "type": "complete",
                "project_id": project_id,
                "files_count": len(files),
                "download_url": f"/frontend/download/{project_id}",
                "message": f"🎉 Frontend generation complete! {len(files)} files generated using Ollama."
            })
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            yield format_sse({
                "type": "error",
                "message": f"❌ Ollama UI to Frontend Error: {str(e)}"
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


@router.post("/ollama/generate-react-multi-stream", summary="🎨 Generate Multi-Screen React App from UI images using Ollama (streaming)")
async def generate_multi_screen_react_ollama_stream(
    files: List[UploadFile] = File(..., description="Multiple UI design image files"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
    styling_approach: str = Form("tailwind", description="Styling approach (tailwind or css-modules)")
):
    """
    🎨 Ollama-based: Generate multi-screen React app from multiple UI images with live streaming!
    
    Uses Ollama local models for both UI analysis and code generation.
    """
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one image file is required"
        )
    
    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 screens allowed per project"
        )
    
    # Validate all files
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp"]
    max_size = 10 * 1024 * 1024  # 10MB per file
    
    image_data_list = []
    
    try:
        for idx, file in enumerate(files):
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for file {idx + 1}: {file.content_type}"
                )
            
            file_content = await file.read()
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {idx + 1} is too large. Maximum size is 10MB per file"
                )
            
            image_data_list.append(file_content)
        
        project_id = str(uuid.uuid4())
        
        async def generate_and_stream():
            try:
                from ui_to_frontend_ollama import ui_to_react_pipeline_streaming, extract_react_files, create_project_zip
                
                yield format_sse({
                    "type": "start",
                    "project_id": project_id,
                    "message": f"🎨 Starting multi-screen analysis with Ollama ({len(image_data_list)} screens)..."
                })
                
                # Run pipeline in non-blocking way
                chunk_queue = queue.Queue()
                full_output = ""
                
                def run_pipeline():
                    """Run blocking pipeline in separate thread"""
                    try:
                        for chunk in ui_to_react_pipeline_streaming(
                            image_data_list,
                            additional_context or "",
                            include_typescript,
                            styling_approach
                        ):
                            chunk_queue.put(chunk)
                        chunk_queue.put(None)  # Signal completion
                    except Exception as e:
                        chunk_queue.put(("error", str(e)))
                
                # Start pipeline in thread
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_pipeline)
                    
                    # Stream chunks as they arrive
                    pipeline_done = False
                    while not pipeline_done:
                        try:
                            # Get chunk with timeout
                            chunk = chunk_queue.get(timeout=1.0)
                            
                            if chunk is None:  # Completion signal
                                pipeline_done = True
                                break
                            if isinstance(chunk, tuple) and chunk[0] == "error":
                                raise Exception(chunk[1])
                            
                            # Stream ALL chunks including progress messages
                            if chunk:
                                yield format_sse({
                                    "type": "stream",
                                    "content": chunk,
                                    "partial": True
                                })
                                full_output += chunk
                        except queue.Empty:
                            # Check if pipeline thread is still running
                            if future.done():
                                # Pipeline finished, check for remaining chunks
                                try:
                                    while True:
                                        chunk = chunk_queue.get_nowait()
                                        if chunk is None:
                                            pipeline_done = True
                                            break
                                        if isinstance(chunk, tuple) and chunk[0] == "error":
                                            raise Exception(chunk[1])
                                        if chunk:
                                            yield format_sse({
                                                "type": "stream",
                                                "content": chunk,
                                                "partial": True
                                            })
                                            full_output += chunk
                                except queue.Empty:
                                    pipeline_done = True
                                    break
                            else:
                                # No chunk yet, yield control briefly
                                await asyncio.sleep(0.001)
                                continue
                
                # Extract files
                files_extracted = extract_react_files(full_output)
                
                if not files_extracted:
                    yield format_sse({
                        "type": "error",
                        "message": "⚠️ No files extracted from generated code."
                    })
                    return
                
                # Send file previews
                for filepath, content in files_extracted[:15]:
                    preview = content[:1000] + ("..." if len(content) > 1000 else "")
                    yield format_sse({
                        "type": "file",
                        "filename": filepath,
                        "preview": preview,
                        "size": len(content)
                    })
                
                if len(files_extracted) > 15:
                    yield format_sse({
                        "type": "info",
                        "message": f"... and {len(files_extracted) - 15} more files"
                    })
                
                # Create ZIP
                zip_buffer = create_project_zip(files_extracted)
                zip_bytes = zip_buffer.getvalue()
                
                _generated_projects[project_id] = {
                    "zip_bytes": zip_bytes,
                    "created_at": datetime.now().isoformat(),
                    "arch_type": "Frontend",
                }
                
                yield format_sse({
                    "type": "complete",
                    "project_id": project_id,
                    "files_count": len(files_extracted),
                    "download_url": f"/frontend/download/{project_id}",
                    "message": f"🎉 Multi-screen React app generated! {len(files_extracted)} files created using Ollama."
                })
                
            except Exception as e:
                yield format_sse({
                    "type": "error",
                    "message": f"❌ Ollama Multi-Screen Error: {str(e)}"
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Frontend Generation Service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "UI image analysis",
            "Component extraction",
            "React code generation",
            "TypeScript support",
            "CSS modules support",
            "Tailwind CSS support",
            "Multi-screen app generation",
            "React Router integration",
            "AI-powered code generation (LangGraph agent)",
            "Ollama local models support"
        ],
        "endpoints": {
            "regular": [
                "/frontend/upload-ui",
                "/frontend/generate-react",
                "/frontend/analyze-ui-only",
                "/frontend/generate-multi-screen"
            ],
            "ai_agent": [
                "/frontend/agent/generate-react"
            ],
            "ollama": [
                "/frontend/ollama/generate-react-stream",
                "/frontend/ollama/generate-react-multi-stream"
            ]
        }
    }

