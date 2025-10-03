from typing import Dict, Any, Optional
import os
import tempfile
from ..ERD.services import ERDProcessingService
from ..NodeGen.generator import NodeProjectGenerator

class CodeCraftAgent:
    """AI Agent for CodeCraft Backend Generator - Simple but Agentic"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.erd_service = ERDProcessingService(gemini_api_key)
        self.nodegen_service = NodeProjectGenerator()
    
    async def process_request(self, user_request: str, uploaded_file: bytes = None) -> Dict[str, Any]:
        """Process user request with agentic workflow"""
        try:
            # Agent Step 1: Analyze request and decide action
            if uploaded_file:
                # Agent decision: Process ERD image
                result = await self._process_erd_image(uploaded_file, user_request)
            else:
                # Agent decision: Handle text request
                result = await self._process_text_request(user_request)
            
            if not result["success"]:
                return {
                    "success": False,
                    "response": f"❌ **Agent Error**\n\n**Error:** {result['error']}\n\n**Agent Suggestion:** Please check your ERD image or try a different format.",
                    "error": result["error"]
                }
            
            # Agent Step 2: Generate backend with intelligence
            backend_result = await self._generate_backend(result["schema"])
            
            if not backend_result["success"]:
                return {
                    "success": False,
                    "response": f"❌ **Agent Backend Generation Failed**\n\n**Error:** {backend_result['error']}\n\n**Agent Suggestion:** Please verify your ERD schema is complete.",
                    "error": backend_result["error"]
                }
            
            # Agent Step 3: Create intelligent response
            response = self._create_agent_response(result["schema"], backend_result)
            
            return {
                "success": True,
                "response": response,
                "backend_data": backend_result,
                "agent_type": "CodeCraft AI Agent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"❌ **Agent System Error**\n\n**Error:** {str(e)}\n\n**Agent Status:** Recovering...",
                "error": str(e)
            }
    
    async def _process_erd_image(self, image_data: bytes, context: str) -> Dict[str, Any]:
        """Agent processes ERD image intelligently"""
        try:
            # Save image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name
            
            # Use existing ERD service (same as before)
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
        """Agent handles text requests"""
        return {
            "success": False,
            "error": "Agent requires ERD image for processing. Please upload an ERD diagram."
        }
    
    async def _generate_backend(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Agent generates backend intelligently"""
        try:
            # Convert dict to ERDSchema object (same as before)
            from ..ERD.models import ERDSchema
            schema_obj = ERDSchema(**schema)
            
            # Use existing NodeJS generator (same as before)
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
    
    def _create_agent_response(self, schema: Dict[str, Any], backend_result: Dict[str, Any]) -> str:
        """Agent creates intelligent response"""
        entities = schema.get("entities", [])
        relationships = schema.get("relationships", [])
        
        response = f"""
🤖 **CodeCraft AI Agent - Mission Accomplished!**

**Agent Analysis:**
✅ ERD processed successfully
✅ Schema validated ({len(entities)} entities, {len(relationships)} relationships)
✅ Node.js backend generated
✅ All systems operational

**Generated Backend:**
- **Files Created:** {len(backend_result.get('files', []))} files
- **Entities Mapped:** {len(entities)} database models
- **API Endpoints:** {len(entities)} REST endpoints

**Available Endpoints:**
"""
        
        # Add endpoint information
        for entity in entities:
            table_name = entity.get("table_name", entity["name"].lower())
            response += f"- GET/POST /api/{table_name}\n"
        
        response += f"""
**Agent Instructions:**
1. Extract the generated project
2. Run `npm install` to install dependencies  
3. Run `npm run dev` to start the server
4. Configure your database in .env file

**Agent Status:** ✅ Mission Complete
**Next Action:** Your AI-powered backend is ready for deployment! 🚀
"""
        
        return response