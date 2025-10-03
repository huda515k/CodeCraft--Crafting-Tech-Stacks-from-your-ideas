from typing import Dict, Any, Optional
import os
import tempfile
from ..ERD.services import ERDProcessingService
from ..NodeGen.generator import NodeProjectGenerator

class FastCodeCraftAgent:
    """Fast AI Agent for CodeCraft - No Heavy Dependencies"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.erd_service = ERDProcessingService(gemini_api_key)
        self.nodegen_service = NodeProjectGenerator()
    
    async def process_request(self, user_request: str, uploaded_file: bytes = None) -> Dict[str, Any]:
        """Fast agent processing"""
        try:
            # Step 1: Process ERD if provided
            if uploaded_file:
                result = await self._process_erd_image(uploaded_file, user_request)
            else:
                return {
                    "success": False,
                    "response": "🤖 Fast Agent: Please upload an ERD image for processing.",
                    "error": "No image provided"
                }
            
            if not result["success"]:
                return {
                    "success": False,
                    "response": f"🤖 Fast Agent Error: {result['error']}",
                    "error": result["error"]
                }
            
            # Step 2: Generate backend
            backend_result = await self._generate_backend(result["schema"])
            
            if not backend_result["success"]:
                return {
                    "success": False,
                    "response": f"🤖 Fast Agent Backend Error: {backend_result['error']}",
                    "error": backend_result["error"]
                }
            
            # Step 3: Create response
            response = self._create_fast_response(result["schema"], backend_result)
            
            return {
                "success": True,
                "response": response,
                "backend_data": backend_result,
                "agent_type": "Fast CodeCraft Agent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"🤖 Fast Agent System Error: {str(e)}",
                "error": str(e)
            }
    
    async def _process_erd_image(self, image_data: bytes, context: str) -> Dict[str, Any]:
        """Fast ERD processing"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name
            
            result = self.erd_service.process_erd_from_file(tmp_path, context)
            os.unlink(tmp_path)
            
            if result.success:
                return {"success": True, "schema": result.erd_schema}
            else:
                return {"success": False, "error": result.error_message}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_backend(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Fast backend generation"""
        try:
            from ..ERD.models import ERDSchema
            schema_obj = ERDSchema(**schema)
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
    
    def _create_fast_response(self, schema: Dict[str, Any], backend_result: Dict[str, Any]) -> str:
        """Create fast agent response"""
        entities = schema.get("entities", [])
        relationships = schema.get("relationships", [])
        
        return f"""
🚀 **Fast CodeCraft Agent - Mission Complete!**

**Agent Analysis:**
✅ ERD processed in {len(entities)} entities
✅ {len(relationships)} relationships mapped
✅ Node.js backend generated
✅ All systems operational

**Generated Backend:**
- **Files:** {len(backend_result.get('files', []))} files created
- **API Endpoints:** {len(entities)} REST endpoints ready

**Available Endpoints:**
{chr(10).join([f"- GET/POST /api/{entity.get('table_name', entity['name'].lower())}" for entity in entities])}

**Fast Agent Instructions:**
1. Extract the generated project
2. Run `npm install` 
3. Run `npm run dev`
4. Configure database in .env

**Agent Status:** ✅ Mission Complete - Ready for deployment! 🚀
"""
