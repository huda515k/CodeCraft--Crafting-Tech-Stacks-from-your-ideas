from typing import Dict, Any, Optional, List
import os
import tempfile
import zipfile
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from ..ERD.services import ERDProcessingService
from ..NodeGen.generator import NodeProjectGenerator
from ..ERD.models import ERDProcessingRequest, ERDSchema


class LangGraphCodeCraftAgent:
    """LangGraph-powered AI Agent for seamless ERD to Backend generation"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=gemini_api_key,
            temperature=0.1
        )
        self.erd_service = ERDProcessingService(gemini_api_key)
        self.nodegen_service = NodeProjectGenerator()
        
        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for ERD to Backend generation"""
        
        # Define the state
        from typing import TypedDict
        
        class AgentState(TypedDict):
            messages: List[Any]
            erd_schema: Optional[ERDSchema]
            backend_zip_path: Optional[str]
            status: str
            error_message: Optional[str]
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_erd", self._analyze_erd_node)
        workflow.add_node("generate_schema", self._generate_schema_node)
        workflow.add_node("create_backend", self._create_backend_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Add edges
        workflow.set_entry_point("analyze_erd")
        workflow.add_edge("analyze_erd", "generate_schema")
        workflow.add_edge("generate_schema", "create_backend")
        workflow.add_edge("create_backend", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _analyze_erd_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the uploaded ERD image"""
        try:
            messages = state.get("messages", [])
            if not messages:
                return {
                    **state,
                    "status": "error",
                    "error_message": "No ERD image provided"
                }
            
            # Get the last message (should contain ERD data)
            last_message = messages[-1]
            if hasattr(last_message, 'content') and isinstance(last_message.content, list):
                # Extract image data from message
                image_data = None
                for content_item in last_message.content:
                    if hasattr(content_item, 'type') and content_item.type == 'image_url':
                        image_data = content_item.image_url.url.split(',')[1]  # Remove data:image/... prefix
                        break
                
                if not image_data:
                    return {
                        **state,
                        "status": "error", 
                        "error_message": "No image data found in message"
                    }
                
                # Process ERD with our service
                request = ERDProcessingRequest(image_data=image_data)
                result = await self.erd_service.process_erd(request)
                
                if result.success:
                    return {
                        **state,
                        "erd_schema": result.erd_schema,
                        "status": "schema_generated",
                        "messages": messages + [AIMessage(content="✅ ERD analyzed successfully! Schema generated.")]
                    }
                else:
                    return {
                        **state,
                        "status": "error",
                        "error_message": f"ERD analysis failed: {result.error_message}"
                    }
            else:
                return {
                    **state,
                    "status": "error",
                    "error_message": "Invalid message format"
                }
                
        except Exception as e:
            return {
                **state,
                "status": "error",
                "error_message": f"ERD analysis error: {str(e)}"
            }
    
    async def _generate_schema_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON schema from ERD"""
        try:
            erd_schema = state.get("erd_schema")
            if not erd_schema:
                return {
                    **state,
                    "status": "error",
                    "error_message": "No ERD schema available"
                }
            
            # Schema is already generated in the previous step
            return {
                **state,
                "status": "schema_ready",
                "messages": state.get("messages", []) + [
                    AIMessage(content="✅ JSON Schema generated! Proceeding to backend generation...")
                ]
            }
            
        except Exception as e:
            return {
                **state,
                "status": "error",
                "error_message": f"Schema generation error: {str(e)}"
            }
    
    async def _create_backend_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Node.js backend from schema"""
        try:
            erd_schema = state.get("erd_schema")
            if not erd_schema:
                return {
                    **state,
                    "status": "error",
                    "error_message": "No ERD schema available for backend generation"
                }
            
            # Generate the Node.js project
            project = self.nodegen_service.generate(erd_schema)
            
            # Create zip file
            zip_path = os.path.join(tempfile.gettempdir(), "langgraph_agent_backend.zip")
            if os.path.exists(zip_path):
                os.remove(zip_path)
                
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(project.output_dir):
                    for f in files:
                        abs_path = os.path.join(root, f)
                        rel_path = os.path.relpath(abs_path, project.output_dir)
                        zf.write(abs_path, rel_path)
            
            return {
                **state,
                "backend_zip_path": zip_path,
                "status": "backend_ready",
                "messages": state.get("messages", []) + [
                    AIMessage(content="✅ Node.js Backend generated successfully!")
                ]
            }
            
        except Exception as e:
            return {
                **state,
                "status": "error",
                "error_message": f"Backend generation error: {str(e)}"
            }
    
    async def _finalize_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the workflow"""
        return {
            **state,
            "status": "completed",
            "messages": state.get("messages", []) + [
                AIMessage(content="🎉 Complete! Your ERD has been converted to a full Node.js backend. Download ready!")
            ]
        }
    
    async def process_erd_to_backend(self, image_data: str, additional_context: str = None) -> Dict[str, Any]:
        """Main entry point: Process ERD image and generate complete backend"""
        try:
            # Process ERD directly with our service
            from ..ERD.models import ERDProcessingRequest
            request = ERDProcessingRequest(image_data=image_data, additional_context=additional_context)
            erd_result = await self.erd_service.process_erd(request)
            
            if not erd_result.success:
                return {
                    "success": False,
                    "erd_schema": None,
                    "backend_zip_path": None,
                    "status": "error",
                    "error_message": f"🤖 AI Agent: ERD processing failed - {erd_result.error_message}. Please try with a clearer ERD image or check if the image contains a valid ERD.",
                    "messages": []
                }
            
            # Generate intelligent project name from ERD content
            project_name = self._generate_project_name(erd_result.erd_schema, additional_context)
            
            # Generate backend from schema
            project = self.nodegen_service.generate(erd_result.erd_schema)
            
            # Create zip file with intelligent naming
            import tempfile
            import zipfile
            safe_name = self._sanitize_filename(project_name)
            zip_path = os.path.join(tempfile.gettempdir(), f"{safe_name}_backend.zip")
            if os.path.exists(zip_path):
                os.remove(zip_path)
                
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(project.output_dir):
                    for f in files:
                        abs_path = os.path.join(root, f)
                        rel_path = os.path.relpath(abs_path, project.output_dir)
                        zf.write(abs_path, rel_path)
            
            return {
                "success": True,
                "erd_schema": erd_result.erd_schema,
                "backend_zip_path": zip_path,
                "status": "completed",
                "error_message": None,
                "messages": []
            }
            
        except Exception as e:
            return {
                "success": False,
                "erd_schema": None,
                "backend_zip_path": None,
                "status": "error",
                "error_message": f"Processing error: {str(e)}",
                "messages": []
            }
    
    def _generate_project_name(self, erd_schema, additional_context: str = None) -> str:
        """Generate intelligent project name based on ERD content"""
        try:
            # Get project name from schema if available
            if erd_schema.project_name:
                return erd_schema.project_name.lower().replace(" ", "_")
            
            # Analyze entity names to determine domain
            entity_names = [entity.name.lower() for entity in erd_schema.entities]
            
            # Domain detection based on common patterns
            domain_keywords = {
                "ecommerce": ["product", "order", "customer", "cart", "payment", "shipping", "inventory"],
                "hr": ["employee", "department", "salary", "position", "manager", "hr"],
                "education": ["student", "course", "teacher", "class", "grade", "school", "university"],
                "healthcare": ["patient", "doctor", "appointment", "medical", "hospital", "clinic"],
                "banking": ["account", "transaction", "customer", "loan", "card", "bank"],
                "real_estate": ["property", "house", "apartment", "rent", "lease", "owner"],
                "library": ["book", "member", "borrow", "return", "author", "publisher"],
                "restaurant": ["menu", "order", "customer", "table", "reservation", "food"],
                "hotel": ["room", "guest", "booking", "reservation", "service"],
                "transport": ["vehicle", "route", "ticket", "passenger", "station", "train", "bus"],
                "sales": ["sales", "lead", "opportunity", "deal", "client", "prospect"],
                "inventory": ["product", "stock", "warehouse", "supplier", "item"],
                "social": ["user", "post", "comment", "friend", "message", "profile"],
                "crm": ["contact", "lead", "opportunity", "deal", "client", "company"]
            }
            
            # Find matching domain
            detected_domain = "general"
            max_matches = 0
            
            for domain, keywords in domain_keywords.items():
                matches = sum(1 for keyword in keywords if any(keyword in name for name in entity_names))
                if matches > max_matches:
                    max_matches = matches
                    detected_domain = domain
            
            # Use additional context if provided
            if additional_context:
                context_lower = additional_context.lower()
                for domain, keywords in domain_keywords.items():
                    if any(keyword in context_lower for keyword in keywords):
                        detected_domain = domain
                        break
            
            # Generate final name
            if detected_domain != "general":
                return f"{detected_domain}_management_system"
            else:
                # Fallback to first entity name or generic name
                if entity_names:
                    return f"{entity_names[0]}_management_system"
                else:
                    return "database_backend"
                    
        except Exception:
            return "generated_backend"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        import re
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        # Limit length
        if len(filename) > 50:
            filename = filename[:50]
        return filename or "generated_backend"
