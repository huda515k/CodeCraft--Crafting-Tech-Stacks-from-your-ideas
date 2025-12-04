from typing import Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import os
import tempfile
import zipfile
import io

# Import existing services
from ..ERD.services import ERDProcessingService
from ..NodeGen.generator import NodeProjectGenerator

class ERDTools:
    """Tools for ERD processing and analysis"""
    
    def __init__(self, gemini_api_key: str):
        self.erd_service = ERDProcessingService(gemini_api_key)
    def analyze_erd_image(self, image_data: bytes, context: str = "") -> Dict[str, Any]:
        """Analyze ERD image and extract schema"""
        try:
            # Save image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name
            
            # Process with existing ERD service
            result = self.erd_service.process_erd_from_file(tmp_path, context)
            
            # Cleanup
            os.unlink(tmp_path)
            
            return {
                "success": result.success,
                "schema": result.erd_schema,
                "error": result.error_message
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_erd_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ERD schema structure"""
        try:
            # Use existing validator
            is_valid = self.erd_service.validator.validate_schema(schema)
            return {
                "valid": is_valid,
                "errors": [] if is_valid else ["Schema validation failed"]
            }
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}

class NodeGenTools:
    """Tools for Node.js backend generation"""
    
    def __init__(self):
        self.generator = NodeProjectGenerator()
    
    def generate_backend(self, erd_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Node.js backend from ERD schema"""
        try:
            # Convert dict to ERDSchema object
            from ..ERD.models import ERDSchema
            schema_obj = ERDSchema(**erd_schema)
            
            # Generate backend
            project = self.generator.generate(schema_obj)
            
            return {
                "success": True,
                "project_path": project.output_dir,
                "files": project.files,
                "metadata": {
                    "entities_count": len(erd_schema.get("entities", [])),
                    "relationships_count": len(erd_schema.get("relationships", []))
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_zip_archive(self, project_path: str) -> bytes:
        """Create zip archive of generated project"""
        try:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(project_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_path)
                        zf.write(file_path, arcname)
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
        except Exception as e:
            raise Exception(f"Failed to create zip archive: {str(e)}")

class CodeCraftTool(BaseTool):
    """Main CodeCraft tool for LangChain integration"""
    
    name: str = "codecraft_backend_generator"
    description: str = "Generate Node.js backend from ERD schema or image"
    
    def __init__(self, gemini_api_key: str):
        super().__init__()
        self.erd_tools = ERDTools(gemini_api_key)
        self.nodegen_tools = NodeGenTools()
    
    def _run(self, query: str, **kwargs) -> str:
        """Execute CodeCraft workflow"""
        try:
            # This would be called by the LangGraph agent
            return "CodeCraft tool executed successfully"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _arun(self, query: str, **kwargs) -> str:
        """Async execution"""
        return self._run(query, **kwargs)
