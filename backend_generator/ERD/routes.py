# backend_generator/erd/routes.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import base64
import json
from typing import Optional
import os
from datetime import datetime

from .models import ERDProcessingRequest, ERDProcessingResponse, ERDSchema
# Lazy imports to speed up startup
# from .services import ERDProcessingService
from .validators import JSONValidator

router = APIRouter(prefix="/erd", tags=["ERD Processing"])

# Dependency injection for ERD service
def get_required_erd_service():
    """Service that requires GEMINI_API_KEY (for image parsing endpoints)."""
    from .services import ERDProcessingService  # Lazy import
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    return ERDProcessingService(gemini_api_key)

def get_optional_erd_service():
    """Service that does not require GEMINI_API_KEY (for conversion endpoints)."""
    from .services import ERDProcessingService  # Lazy import
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    return ERDProcessingService(gemini_api_key)

@router.post("/upload-image", response_model=ERDProcessingResponse)
async def upload_erd_image(
    file: UploadFile = File(..., description="ERD image file"),
    additional_context: Optional[str] = None,
    service = Depends(get_required_erd_service)
):
    """
    🤖 AI Agent: Upload and process an ERD image file
    
    Supported formats: PNG, JPG, JPEG, GIF, BMP
    The AI agent will intelligently analyze your ERD and extract the schema.
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
        
        # Process ERD
        request = ERDProcessingRequest(
            image_data=image_data,
            additional_context=additional_context
        )
        
        result = await service.process_erd(request)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.post("/process-base64", response_model=ERDProcessingResponse, include_in_schema=False)
async def process_base64_image(
    request: ERDProcessingRequest,
    service = Depends(get_required_erd_service)
):
    """
    Process ERD from base64 encoded image data
    """
    if not request.image_data and not request.image_url:
        raise HTTPException(
            status_code=400,
            detail="Either image_data or image_url must be provided"
        )
    
    try:
        result = await service.process_erd(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing ERD: {str(e)}")

@router.post("/validate-schema", include_in_schema=False)
async def validate_erd_schema(schema_data: dict):
    """
    Validate ERD schema structure
    """
    try:
        validator = JSONValidator()
        errors = validator.validate_erd_schema(schema_data)

        if errors:
            return JSONResponse(
                status_code=400,
                content={
                    "valid": False,
                    "errors": errors
                }
            )

        return {
            "valid": True,
            "message": "Schema validation passed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post("/convert-to-database-schema", include_in_schema=False)
async def convert_to_database_schema(
    erd_schema: ERDSchema,
    service = Depends(get_optional_erd_service)
):
    """
    Convert ERD schema to database schema format
    """
    try:
        db_schema = service.convert_to_database_schema(erd_schema)
        return {
            "success": True,
            "database_schema": db_schema,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting schema: {str(e)}")

@router.post("/convert-to-fastapi-schema", include_in_schema=False)
async def convert_to_fastapi_schema(
    erd_schema: ERDSchema,
    service = Depends(get_optional_erd_service)
):
    """
    Convert ERD schema to FastAPI application schema
    """
    try:
        fastapi_schema = service.convert_to_fastapi_schema(erd_schema)
        return {
            "success": True,
            "fastapi_schema": fastapi_schema,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting schema: {str(e)}")

@router.post("/generate-comprehensive-schema", include_in_schema=False)
async def generate_comprehensive_schema(
    erd_schema: ERDSchema,
    service = Depends(get_optional_erd_service)
):
    """
    Generate comprehensive schema with all formats (database, Pydantic, FastAPI)
    """
    try:
        comprehensive_schema = service.generate_comprehensive_schema(erd_schema)
        return {
            "success": True,
            "comprehensive_schema": comprehensive_schema,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comprehensive schema: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "ERD Processing Service",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/agent-process", response_model=ERDProcessingResponse)
async def agent_process_erd(
    file: UploadFile = File(..., description="ERD image file"),
    additional_context: Optional[str] = None,
    service = Depends(get_required_erd_service)
):
    """
    🤖 AI Agent: Process ERD with intelligent analysis
    
    This endpoint uses AI to analyze your ERD and generate a complete Node.js backend.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Convert to base64
        import base64
        image_data = base64.b64encode(content).decode('utf-8')
        
        # Create request
        request = ERDProcessingRequest(
            image_data=image_data,
            additional_context=additional_context
        )
        
        # Process with service
        result = await service.process_erd(request)
        
        # Add agentic response
        if result.success:
            result.error_message = "🤖 AI Agent: ERD processed successfully! Ready for backend generation."
        else:
            result.error_message = f"🤖 AI Agent: {result.error_message}. Please try a clearer ERD image."
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🤖 AI Agent Error: {str(e)}")

@router.post("/process-with-prompt", response_model=ERDProcessingResponse, include_in_schema=False)
async def process_erd_with_prompt(
    file: UploadFile = File(..., description="ERD image file"),
    additional_context: Optional[str] = None,
    role_prompt: Optional[str] = None,
    service = Depends(get_required_erd_service)
):
    """
    🤖 AI Agent: Process ERD with role-based access and business rules prompt
    
    This endpoint processes your ERD and applies role-based access control and business rules
    specified in the prompt. Perfect for generating secure, role-aware backends.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Convert to base64
        import base64
        image_data = base64.b64encode(content).decode('utf-8')
        
        # Create request with prompt context
        request = ERDProcessingRequest(
            image_data=image_data,
            additional_context=additional_context
        )
        
        # Process with service
        result = await service.process_erd(request)
        
        # If we have a role prompt, analyze it
        if result.success and role_prompt:
            try:
                from backend_generator.PromptAnalysis.services import PromptAnalysisService
                prompt_service = PromptAnalysisService()
                
                # Analyze the role prompt
                from backend_generator.PromptAnalysis.models import PromptAnalysisRequest
                prompt_request = PromptAnalysisRequest(
                    prompt=role_prompt,
                    erd_schema=result.erd_schema.dict() if result.erd_schema else None
                )
                
                prompt_result = await prompt_service.analyze_prompt(prompt_request)
                
                # Add prompt analysis to processing metadata
                result.processing_metadata = {
                    **result.processing_metadata,
                    "role_analysis": {
                        "roles_found": len(prompt_result.roles),
                        "business_rules_found": len(prompt_result.business_rules),
                        "user_access_found": len(prompt_result.user_access),
                        "has_generated_code": prompt_result.generated_code is not None
                    }
                }
                
                result.error_message = f"🤖 AI Agent: ERD processed with role-based access control! Found {len(prompt_result.roles)} roles and {len(prompt_result.business_rules)} business rules."
                
            except Exception as prompt_error:
                result.error_message = f"🤖 AI Agent: ERD processed successfully, but role analysis failed: {str(prompt_error)}"
        elif result.success:
            result.error_message = "🤖 AI Agent: ERD processed successfully! Ready for backend generation."
        else:
            result.error_message = f"🤖 AI Agent: {result.error_message}. Please try a clearer ERD image."
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🤖 AI Agent Error: {str(e)}")
