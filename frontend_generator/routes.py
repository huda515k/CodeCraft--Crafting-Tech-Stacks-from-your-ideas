# frontend_generator/routes.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
import os
import base64
from datetime import datetime
import io

from .models import UIProcessingRequest, UIProcessingResponse
from .services import FrontendGenerationService

router = APIRouter(prefix="/frontend", tags=["Frontend Generation"])

# Dependency injection for frontend service
def get_frontend_service():
    """Service that requires GEMINI_API_KEY (for image parsing endpoints)."""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    return FrontendGenerationService(gemini_api_key)

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

@router.post("/generate-react")
async def generate_react_from_ui(
    file: UploadFile = File(..., description="UI design image file"),
    additional_context: Optional[str] = Form(None, description="Additional context or instructions"),
    framework: str = Form("react", description="Target framework"),
    styling_approach: str = Form("css-modules", description="Styling approach"),
    include_typescript: bool = Form(True, description="Include TypeScript"),
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
            include_typescript=include_typescript
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
            "Tailwind CSS support"
        ]
    }

