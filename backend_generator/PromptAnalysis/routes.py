# backend_generator/PromptAnalysis/routes.py

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from typing import Optional, List
import os
import zipfile
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import io

from .models import (
    PromptAnalysisRequest, PromptAnalysisResponse,
    BackendModificationRequest, BackendModificationResponse,
    Role, BusinessRule, UserAccess
)
from .services import PromptAnalysisService

router = APIRouter(prefix="/prompt-analysis", tags=["Prompt Analysis"])

# Dependency injection for prompt analysis service
def get_prompt_analysis_service():
    """Get prompt analysis service instance with AI capabilities."""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    return PromptAnalysisService(gemini_api_key)

@router.post("/analyze", response_model=PromptAnalysisResponse)
async def analyze_prompt(
    request: PromptAnalysisRequest,
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    🤖 AI Agent: Analyze user prompt for role-based access and business rules
    
    This endpoint analyzes user prompts to extract:
    - Role definitions and permissions
    - Business rules and constraints
    - User access patterns
    - Generate authorization code for Node.js backend
    """
    try:
        result = await service.analyze_prompt(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing prompt: {str(e)}")

@router.post("/modify-backend")
async def modify_backend(
    backend_zip: UploadFile = File(..., description="Backend zip file"),
    prompt: Optional[str] = Form(None, description="Desired changes prompt"),
    business_rules: Optional[str] = Form(None, description="Business rules to add"),
    role_based_access: Optional[str] = Form(None, description="Role-based access rules"),
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    🤖 AI Agent: Modify existing backend based on prompt and rules
    
    Upload a backend zip file and specify desired changes:
    - Prompt: Natural language description of changes
    - Business Rules: Specific business rules to implement
    - Role-based Access: Access control rules to add
    
    Returns modified backend zip file with all changes applied.
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded zip file
            zip_path = temp_path / "backend.zip"
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(backend_zip.file, buffer)
            
            # Extract zip file
            extract_path = temp_path / "extracted"
            extract_path.mkdir()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Process modifications
            result = await service.modify_backend_with_files(
                str(extract_path),
                prompt,
                business_rules,
                role_based_access
            )
            
            if result['success']:
                # Create zip content in memory
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in extract_path.rglob('*'):
                        if file_path.is_file():
                            # Use relative path from extract_path
                            arcname = file_path.relative_to(extract_path)
                            zipf.write(file_path, arcname)
                
                # Reset buffer position
                zip_buffer.seek(0)
                
                # Return as streaming response
                return StreamingResponse(
                    io.BytesIO(zip_buffer.getvalue()),
                    media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=modified_backend.zip"}
                )
            else:
                raise HTTPException(status_code=400, detail=result.get('error_message', 'Modification failed'))
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error modifying backend: {str(e)}")

@router.post("/validate")
async def validate_roles_and_rules(
    roles: List[Role],
    business_rules: List[BusinessRule],
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    Validate extracted roles and business rules
    """
    try:
        validation_results = await service.validate_roles_and_rules(roles, business_rules)
        return validation_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating roles and rules: {str(e)}")

@router.post("/generate-hierarchy")
async def generate_role_hierarchy(
    backend_zip: UploadFile = File(..., description="Backend zip file"),
    business_rules: Optional[str] = Form(None, description="Business rules to add"),
    role_based_access: Optional[str] = Form(None, description="Role-based access rules"),
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    🤖 AI Agent: Generate role hierarchy and apply business rules
    
    Upload a backend zip file and specify:
    - Business Rules: Rules to implement
    - Role-based Access: Access control rules
    
    Returns updated backend code with hierarchy applied and summary of changes.
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded zip file
            zip_path = temp_path / "backend.zip"
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(backend_zip.file, buffer)
            
            # Extract zip file
            extract_path = temp_path / "extracted"
            extract_path.mkdir()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Process hierarchy generation
            result = await service.generate_hierarchy_with_files(
                str(extract_path),
                business_rules,
                role_based_access
            )
            
            if result['success']:
                # Create zip content in memory
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in extract_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(extract_path)
                            zipf.write(file_path, arcname)
                
                # Reset buffer position
                zip_buffer.seek(0)
                
                # Return as streaming response
                return StreamingResponse(
                    io.BytesIO(zip_buffer.getvalue()),
                    media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=hierarchy_backend.zip"}
                )
            else:
                raise HTTPException(status_code=400, detail=result.get('error_message', 'Hierarchy generation failed'))
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating hierarchy: {str(e)}")

@router.post("/generate-permission-matrix")
async def generate_permission_matrix(
    roles: List[Role],
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    Generate permission matrix for all roles
    """
    try:
        matrix = await service.generate_permission_matrix(roles)
        return {
            "success": True,
            "permission_matrix": matrix,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating permission matrix: {str(e)}")

@router.post("/security-suggestions")
async def get_security_suggestions(
    backend_zip: UploadFile = File(..., description="Backend zip file"),
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    🤖 AI Agent: Analyze backend and provide security suggestions
    
    Upload a backend zip file to get comprehensive security analysis and suggestions.
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded zip file
            zip_path = temp_path / "backend.zip"
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(backend_zip.file, buffer)
            
            # Extract zip file
            extract_path = temp_path / "extracted"
            extract_path.mkdir()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Analyze security
            result = await service.analyze_security_with_files(str(extract_path))
            
            return {
                "success": True,
                "suggestions": result.get('suggestions', []),
                "security_issues": result.get('issues', []),
                "recommendations": result.get('recommendations', []),
                "generated_at": datetime.utcnow().isoformat()
            }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing security: {str(e)}")

@router.post("/generate-authorization-code")
async def generate_authorization_code(
    backend_zip: UploadFile = File(..., description="Backend zip file"),
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    🤖 AI Agent: Generate authorization code for existing backend
    
    Upload a backend zip file to generate complete authorization code and middleware.
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded zip file
            zip_path = temp_path / "backend.zip"
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(backend_zip.file, buffer)
            
            # Extract zip file
            extract_path = temp_path / "extracted"
            extract_path.mkdir()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Generate authorization code
            result = await service.generate_authorization_code_with_files(str(extract_path))
            
            if result['success']:
                # Create zip content in memory
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in extract_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(extract_path)
                            zipf.write(file_path, arcname)
                
                # Reset buffer position
                zip_buffer.seek(0)
                
                # Return as streaming response
                return StreamingResponse(
                    io.BytesIO(zip_buffer.getvalue()),
                    media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=authorized_backend.zip"}
                )
            else:
                raise HTTPException(status_code=400, detail=result.get('error_message', 'Authorization code generation failed'))
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating authorization code: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for prompt analysis service
    """
    return {
        "status": "healthy",
        "service": "Prompt Analysis Service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Role-based access control",
            "Business rules extraction",
            "Authorization code generation",
            "Backend modification",
            "Security suggestions"
        ]
    }

@router.post("/analyze-with-erd")
async def analyze_prompt_with_erd(
    erd_image: UploadFile = File(..., description="ERD image file"),
    prompt: Optional[str] = Form(None, description="Prompt for analysis"),
    business_rules: Optional[str] = Form(None, description="Business rules to add"),
    role_based_access: Optional[str] = Form(None, description="Role-based access rules"),
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    🤖 AI Agent: Analyze ERD with prompt and generate backend
    
    Upload an ERD image and specify:
    - Prompt: Analysis requirements
    - Business Rules: Rules to implement
    - Role-based Access: Access control rules
    
    Returns a complete backend zip file with all specifications applied.
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save ERD image
            erd_path = temp_path / "erd.png"
            with open(erd_path, "wb") as buffer:
                shutil.copyfileobj(erd_image.file, buffer)
            
            # Process ERD with prompt analysis
            result = await service.analyze_erd_with_prompt(
                str(erd_path),
                prompt,
                business_rules,
                role_based_access
            )
            
            if result['success']:
                # Create zip content in memory
                zip_buffer = io.BytesIO()
                backend_path_obj = Path(result['backend_path'])
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in backend_path_obj.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(backend_path_obj)
                            zipf.write(file_path, arcname)
                
                # Reset buffer position
                zip_buffer.seek(0)
                
                # Return as streaming response
                return StreamingResponse(
                    io.BytesIO(zip_buffer.getvalue()),
                    media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=generated_backend.zip"}
                )
            else:
                raise HTTPException(status_code=400, detail=result.get('error_message', 'ERD analysis failed'))
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing ERD with prompt: {str(e)}")

@router.post("/quick-analysis")
async def quick_analysis(
    prompt: str,
    service: PromptAnalysisService = Depends(get_prompt_analysis_service)
):
    """
    🤖 AI Agent: Quick analysis of prompt without full code generation
    
    This endpoint provides a fast analysis of user prompts to extract:
    - Roles and permissions
    - Business rules
    - User access patterns
    
    Perfect for quick validation and testing of prompt analysis capabilities.
    """
    try:
        request = PromptAnalysisRequest(prompt=prompt)
        result = await service.analyze_prompt(request)
        
        # Return simplified response
        return {
            "success": result.success,
            "roles_found": len(result.roles),
            "rules_found": len(result.business_rules),
            "user_access_found": len(result.user_access),
            "roles": [{"name": role.name, "permissions": [p.value for p in role.permissions]} for role in result.roles],
            "business_rules": [{"name": rule.name, "type": rule.rule_type.value, "description": rule.description} for rule in result.business_rules],
            "error_message": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in quick analysis: {str(e)}")
