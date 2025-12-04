# frontend_generator/services.py

import os
import zipfile
import io
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from .models import (
    UIProcessingRequest, UIProcessingResponse, UIAnalysis,
    CodeGenerationRequest, GeneratedProject
)
from .ui_parser import UIParser
from .code_generator import ReactCodeGenerator

class FrontendGenerationService:
    """Main service class for frontend generation operations"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.parser = UIParser(gemini_api_key)
        self.code_generator = None  # Will be initialized per request
    
    async def process_ui(
        self, 
        request: UIProcessingRequest
    ) -> UIProcessingResponse:
        """
        Process UI image and extract structured analysis
        """
        try:
            # Parse the UI image
            ui_analysis = await self.parser.parse_ui_image(
                image_data=request.image_data,
                image_url=request.image_url,
                additional_context=request.additional_context
            )
            
            if not ui_analysis:
                return UIProcessingResponse(
                    success=False,
                    error_message="Failed to parse UI image"
                )
            
            return UIProcessingResponse(
                success=True,
                ui_analysis=ui_analysis,
                processing_metadata={
                    "components_count": len(ui_analysis.components),
                    "framework": request.framework,
                    "styling_approach": request.styling_approach
                }
            )
            
        except Exception as e:
            import traceback
            error_details = str(e)
            traceback_str = traceback.format_exc()
            print(f"Frontend service error: {error_details}")
            print(f"Traceback: {traceback_str}")
            return UIProcessingResponse(
                success=False,
                error_message=f"Processing error: {error_details}"
            )
    
    async def generate_code(
        self,
        request: CodeGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate React code from UI analysis
        Returns dictionary with success status and project files
        """
        try:
            # Initialize code generator
            self.code_generator = ReactCodeGenerator(
                include_typescript=request.include_typescript,
                styling_approach=request.styling_approach
            )
            
            # Generate project files
            project_name = request.ui_analysis.project_name or "react-app"
            files = self.code_generator.generate_project(
                request.ui_analysis,
                project_name
            )
            
            # Create project structure
            project = GeneratedProject(
                project_name=project_name,
                files=files,
                metadata={
                    "framework": request.framework,
                    "styling_approach": request.styling_approach,
                    "typescript": request.include_typescript,
                    "components_count": len(request.ui_analysis.components)
                }
            )
            
            return {
                "success": True,
                "project": project,
                "files_count": len(files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": f"Code generation error: {str(e)}"
            }
    
    async def process_and_generate(
        self,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        additional_context: Optional[str] = None,
        framework: str = "react",
        styling_approach: str = "css-modules",
        include_typescript: bool = True
    ) -> Dict[str, Any]:
        """
        Process UI image and generate complete React project in one call
        """
        try:
            # Step 1: Process UI
            request = UIProcessingRequest(
                image_data=image_data,
                image_url=image_url,
                additional_context=additional_context,
                framework=framework,
                styling_approach=styling_approach
            )
            
            processing_result = await self.process_ui(request)
            
            if not processing_result.success:
                return {
                    "success": False,
                    "error_message": processing_result.error_message
                }
            
            # Step 2: Generate code
            code_request = CodeGenerationRequest(
                ui_analysis=processing_result.ui_analysis,
                framework=framework,
                styling_approach=styling_approach,
                include_typescript=include_typescript
            )
            
            generation_result = await self.generate_code(code_request)
            
            if not generation_result["success"]:
                return {
                    "success": False,
                    "error_message": generation_result.get("error_message", "Code generation failed")
                }
            
            return {
                "success": True,
                "project": generation_result["project"],
                "ui_analysis": processing_result.ui_analysis,
                "files_count": generation_result["files_count"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": f"Processing and generation error: {str(e)}"
            }
    
    def create_zip_from_project(self, project: GeneratedProject) -> io.BytesIO:
        """
        Create a ZIP file from generated project
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, file_content in project.files.items():
                zipf.writestr(file_path, file_content)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def create_project_directory(self, project: GeneratedProject, output_dir: str) -> str:
        """
        Create project files in a directory
        Returns the path to the created directory
        """
        project_path = Path(output_dir) / project.project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        for file_path, file_content in project.files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(file_content, encoding='utf-8')
        
        return str(project_path)

