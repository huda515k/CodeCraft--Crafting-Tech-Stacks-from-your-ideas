from typing import Dict, Any, Optional
import os
from ..ERD.services import ERDProcessingService
from ..NodeGen.generator import NodeProjectGenerator

class SimpleCodeCraftAgent:
    """Simplified AI Agent for CodeCraft Backend Generator"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.erd_service = ERDProcessingService(gemini_api_key)
        self.nodegen_service = NodeProjectGenerator()
    
    async def process_request(self, user_request: str, uploaded_file: bytes = None) -> Dict[str, Any]:
        """Process user request with simplified workflow"""
        try:
            # Step 1: Analyze request
            if uploaded_file:
                # Process ERD image
                result = await self._process_erd_image(uploaded_file, user_request)
            else:
                # Process text request
                result = await self._process_text_request(user_request)
            
            if not result["success"]:
                return {
                    "success": False,
                    "response": f"❌ **Error in CodeCraft Processing**\n\n**Error:** {result['error']}\n\nPlease try again or contact support.",
                    "error": result["error"]
                }
            
            # Step 2: Generate backend
            backend_result = await self._generate_backend(result["schema"])
            
            if not backend_result["success"]:
                return {
                    "success": False,
                    "response": f"❌ **Backend Generation Failed**\n\n**Error:** {backend_result['error']}\n\nPlease check your schema and try again.",
                    "error": backend_result["error"]
                }
            
            # Step 3: Create response
            response = f"""
🎉 **CodeCraft Backend Generated Successfully!**

**Project Details:**
- Entities: {len(result['schema'].get('entities', []))}
- Relationships: {len(result['schema'].get('relationships', []))}
- Generated Files: {len(backend_result['files'])} files

**Available API Endpoints:**
"""
            
            # Add endpoint information
            for entity in result["schema"].get("entities", []):
                table_name = entity.get("table_name", entity["name"].lower())
                response += f"- GET/POST /api/{table_name}\n"
            
            response += f"""
**Next Steps:**
1. Extract the generated project
2. Run `npm install` to install dependencies
3. Run `npm run dev` to start the server
4. Configure your database in .env file

Your AI-powered backend is ready! 🚀
"""
            
            return {
                "success": True,
                "response": response,
                "backend_data": backend_result,
                "agent_type": "Simple AI Agent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"❌ **Unexpected Error**\n\n**Error:** {str(e)}\n\nPlease try again or contact support.",
                "error": str(e)
            }
    
    async def _process_erd_image(self, image_data: bytes, context: str) -> Dict[str, Any]:
        """Process ERD image"""
        try:
            # Save image to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name
            
            # Process with ERD service
            result = self.erd_service.process_erd_from_file(tmp_path, context)
            
            # Cleanup
            os.unlink(tmp_path)
            
            if result.success:
                return {"success": True, "schema": result.erd_schema}
            else:
                return {"success": False, "error": result.error_message}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_text_request(self, request: str) -> Dict[str, Any]:
        """Process text request (placeholder for future implementation)"""
        return {
            "success": False,
            "error": "Text processing not implemented yet. Please upload an ERD image."
        }
    
    async def _generate_backend(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Node.js backend"""
        try:
            # Convert dict to ERDSchema object
            from ..ERD.models import ERDSchema
            schema_obj = ERDSchema(**schema)
            
            # Generate backend
            project = self.nodegen_service.generate(schema_obj)
            
            return {
                "success": True,
                "project_path": project.output_dir,
                "files": getattr(project, 'files', []),
                "metadata": {
                    "entities_count": len(schema.get("entities", [])),
                    "relationships_count": len(schema.get("relationships", []))
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
