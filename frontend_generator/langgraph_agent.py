"""
LangGraph AI Agent for Frontend Generation
Uses AI to generate structured, UI-matching React code
"""

from typing import Dict, Any, Optional, List
import os
import tempfile
import zipfile
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .ui_parser import UIParser
from .ai_code_generator import AIReactCodeGenerator
from .models import UIAnalysis, UIProcessingRequest


class LangGraphFrontendAgent:
    """LangGraph-powered AI Agent for UI to React generation"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=gemini_api_key,
            temperature=0.1
        )
        self.ui_parser = UIParser(gemini_api_key)
        self.ai_code_generator = AIReactCodeGenerator(gemini_api_key)
        
        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for UI to React generation"""
        
        # Define the state
        from typing import TypedDict
        
        class AgentState(TypedDict):
            messages: List[Any]
            image_data: Optional[str]
            additional_context: Optional[str]
            ui_analysis: Optional[UIAnalysis]
            project_files: Optional[Dict[str, str]]
            project_name: str
            include_typescript: bool
            styling_approach: str
            status: str
            error_message: Optional[str]
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_ui", self._analyze_ui_node)
        workflow.add_node("generate_code", self._generate_code_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Add edges with conditional routing to handle errors
        workflow.set_entry_point("analyze_ui")
        
        # Route from analyze_ui: continue to generate_code or END on error
        def route_after_analyze(state: Dict[str, Any]) -> str:
            if state.get("status") == "error":
                return END
            return "generate_code"
        
        workflow.add_conditional_edges("analyze_ui", route_after_analyze, {
            "generate_code": "generate_code",
            END: END
        })
        
        # Route from generate_code: continue to finalize or END on error
        def route_after_generate(state: Dict[str, Any]) -> str:
            if state.get("status") == "error":
                return END
            # Also check if project_files exists
            if not state.get("project_files"):
                return END
            return "finalize"
        
        workflow.add_conditional_edges("generate_code", route_after_generate, {
            "finalize": "finalize",
            END: END
        })
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _analyze_ui_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the uploaded UI image"""
        try:
            print(f"🔍 Analyze UI Node: Starting...")
            image_data = state.get("image_data")
            additional_context = state.get("additional_context")
            
            if not image_data:
                print("❌ No image_data in state")
                return {
                    **state,
                    "status": "error",
                    "error_message": "No UI image provided"
                }
            
            print(f"   Image data length: {len(image_data) if image_data else 0}")
            print(f"   Additional context: {additional_context}")
            
            # Process UI with parser
            print("   Calling UI parser...")
            ui_analysis = await self.ui_parser.parse_ui_image(
                image_data=image_data,
                additional_context=additional_context
            )
            
            if not ui_analysis:
                print("❌ UI parser returned None")
                return {
                    **state,
                    "status": "error",
                    "error_message": "Failed to analyze UI image"
                }
            
            print(f"✅ UI analysis complete: {len(ui_analysis.components) if hasattr(ui_analysis, 'components') else 0} components")
            
            return {
                **state,
                "ui_analysis": ui_analysis,
                "status": "ui_analyzed",
                "messages": state.get("messages", []) + [
                    AIMessage(content="✅ UI analyzed successfully! Component structure extracted.")
                ]
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ UI analysis node error: {str(e)}")
            print(f"Traceback: {error_trace}")
            return {
                **state,
                "status": "error",
                "error_message": f"UI analysis error: {str(e)}"
            }
    
    async def _generate_code_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate React code using AI"""
        try:
            ui_analysis = state.get("ui_analysis")
            if not ui_analysis:
                return {
                    **state,
                    "status": "error",
                    "error_message": "No UI analysis available for code generation"
                }
            
            project_name = state.get("project_name", ui_analysis.project_name if hasattr(ui_analysis, 'project_name') else "react-app")
            include_typescript = state.get("include_typescript", True)
            styling_approach = state.get("styling_approach", "css-modules")
            
            print(f"🔧 Generating React code for project: {project_name}")
            print(f"   - TypeScript: {include_typescript}")
            print(f"   - Styling: {styling_approach}")
            print(f"   - Components: {len(ui_analysis.components) if hasattr(ui_analysis, 'components') else 0}")
            
            # Generate project using AI
            try:
                project_files = await self.ai_code_generator.generate_project_structure(
                    ui_analysis=ui_analysis,
                    project_name=project_name,
                    include_typescript=include_typescript,
                    styling_approach=styling_approach
                )
            except Exception as gen_error:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ AI code generation error: {str(gen_error)}")
                print(f"Traceback: {error_trace}")
                return {
                    **state,
                    "status": "error",
                    "error_message": f"AI code generation failed: {str(gen_error)}"
                }
            
            if not project_files:
                print("⚠️  Warning: generate_project_structure returned empty dict")
                return {
                    **state,
                    "status": "error",
                    "error_message": "Failed to generate React code - no files were created"
                }
            
            print(f"✅ Generated {len(project_files)} project files")
            print(f"   Files: {list(project_files.keys())[:5]}...")  # Show first 5 files
            
            return {
                **state,
                "project_files": project_files,
                "status": "code_generated",
                "messages": state.get("messages", []) + [
                    AIMessage(content=f"✅ React code generated successfully! {len(project_files)} files created.")
                ]
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Code generation node error: {str(e)}")
            print(f"Traceback: {error_trace}")
            return {
                **state,
                "status": "error",
                "error_message": f"Code generation error: {str(e)}"
            }
    
    async def _finalize_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the project generation"""
        try:
            project_files = state.get("project_files")
            if not project_files:
                # Debug: check what's in state
                print(f"⚠️  Finalize node: project_files is {project_files}")
                print(f"   State keys: {list(state.keys())}")
                print(f"   Status: {state.get('status')}")
                print(f"   Error message: {state.get('error_message')}")
                
                return {
                    **state,
                    "status": "error",
                    "error_message": f"No project files to finalize. Previous status: {state.get('status')}, Error: {state.get('error_message', 'None')}"
                }
            
            print(f"✅ Finalizing project with {len(project_files)} files")
            
            return {
                **state,
                "status": "completed",
                "messages": state.get("messages", []) + [
                    AIMessage(content="✅ Frontend project generation completed!")
                ]
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Finalization error: {str(e)}")
            print(f"Traceback: {error_trace}")
            return {
                **state,
                "status": "error",
                "error_message": f"Finalization error: {str(e)}"
            }
    
    async def process_ui_to_react(
        self,
        image_data: str,
        project_name: str = "react-app",
        additional_context: Optional[str] = None,
        include_typescript: bool = True,
        styling_approach: str = "css-modules"
    ) -> Dict[str, Any]:
        """
        Process UI image and generate React project using LangGraph workflow
        
        Args:
            image_data: Base64 encoded image data
            project_name: Name of the project
            additional_context: Additional context for UI analysis
            include_typescript: Whether to use TypeScript
            styling_approach: CSS modules or tailwind
        
        Returns:
            Dictionary with success status and project files
        """
        try:
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content="Generate React app from UI design")],
                "image_data": image_data,
                "additional_context": additional_context,
                "project_name": project_name,
                "include_typescript": include_typescript,
                "styling_approach": styling_approach,
                "ui_analysis": None,
                "project_files": None,
                "status": "initialized",
                "error_message": None
            }
            
            # Run workflow
            print(f"🚀 Starting LangGraph workflow...")
            print(f"   Initial state keys: {list(initial_state.keys())}")
            print(f"   Image data present: {bool(initial_state.get('image_data'))}")
            
            result = await self.workflow.ainvoke(initial_state)
            
            print(f"📊 Workflow completed")
            print(f"   Final status: {result.get('status')}")
            print(f"   Result keys: {list(result.keys())}")
            print(f"   Project files count: {len(result.get('project_files', {})) if result.get('project_files') else 0}")
            print(f"   Error message: {result.get('error_message', 'None')}")
            
            if result["status"] == "completed":
                return {
                    "success": True,
                    "project_files": result["project_files"],
                    "ui_analysis": result["ui_analysis"],
                    "project_name": result["project_name"],
                    "files_count": len(result["project_files"]) if result["project_files"] else 0
                }
            else:
                return {
                    "success": False,
                    "error_message": result.get("error_message", "Unknown error")
                }
                
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"LangGraph agent error: {error_trace}")
            return {
                "success": False,
                "error_message": f"Agent error: {str(e)}"
            }

