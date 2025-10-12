from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import FileResponse
import os
import shutil
import tempfile
import zipfile
import base64
from typing import Optional

from ..ERD.models import ERDSchema
from ..ERD.services import ERDProcessingService


router = APIRouter(prefix="/nodegen", tags=["NodeJS Generator"])

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


