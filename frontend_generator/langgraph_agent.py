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
from .ai_multi_screen_code_generator import AIMultiScreenCodeGenerator
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
        self.ai_multi_screen_generator = AIMultiScreenCodeGenerator(gemini_api_key)
        
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
    
    async def process_multi_ui_to_react(
        self,
        screen_images: List[str],
        screen_names: Optional[List[str]] = None,
        screen_routes: Optional[List[str]] = None,
        project_name: str = "multi-screen-app",
        additional_context: Optional[str] = None,
        include_typescript: bool = True,
        styling_approach: str = "css-modules"
    ) -> Dict[str, Any]:
        """
        Process multiple UI images and generate a multi-screen React project with React Router
        Uses AI-powered multi-screen code generator for better quality
        
        Args:
            screen_images: List of base64 encoded image data strings (one per screen)
            screen_names: Optional list of screen names (defaults to Screen1, Screen2, etc.)
            screen_routes: Optional list of routes (defaults to /screen1, /screen2, etc.)
            project_name: Name of the project
            additional_context: Additional context for all screens
            include_typescript: Whether to use TypeScript
            styling_approach: CSS modules or tailwind
        
        Returns:
            Dictionary with success status and project files
        """
        try:
            print(f"🚀 Starting AI-powered multi-screen React generation...")
            print(f"   Screens: {len(screen_images)}")
            print(f"   Project: {project_name}")
            
            # Step 1: Analyze all UI images using LangGraph workflow
            screen_analyses = []
            
            for idx, image_data in enumerate(screen_images):
                screen_num = idx + 1
                current_screen_name = screen_names[idx] if screen_names and idx < len(screen_names) else f"Screen{screen_num}"
                current_screen_route = screen_routes[idx] if screen_routes and idx < len(screen_routes) else f"/screen{screen_num}"
                
                print(f"📱 Analyzing screen {screen_num}/{len(screen_images)}: {current_screen_name}")
                
                # Add screen-specific context
                screen_context = f"{additional_context or ''}\n\nThis is the {current_screen_name} screen. Analyze this UI design completely."
                
                # Analyze UI directly using the UI parser (same as single screen workflow)
                try:
                    ui_analysis = await self.ui_parser.parse_ui_image(
                        image_data=image_data,
                        additional_context=screen_context
                    )
                    
                    if not ui_analysis:
                        print(f"⚠️  Warning: Failed to analyze screen {current_screen_name}")
                        continue
                    
                    screen_analyses.append({
                        "ui_analysis": ui_analysis,
                        "screen_name": current_screen_name,
                        "screen_route": current_screen_route
                    })
                    
                    print(f"✅ Analyzed screen {current_screen_name}: {len(ui_analysis.components) if hasattr(ui_analysis, 'components') else 0} components")
                    
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"❌ Error analyzing screen {current_screen_name}: {str(e)}")
                    print(f"Traceback: {error_trace}")
                    continue
            
            if not screen_analyses:
                return {
                    "success": False,
                    "error_message": "No screens were successfully analyzed"
                }
            
            # Step 2: Generate complete multi-screen project using AI
            print(f"\n🤖 Generating complete multi-screen React project using AI...")
            print(f"   Screens to generate: {len(screen_analyses)}")
            
            try:
                all_project_files = await self.ai_multi_screen_generator.generate_multi_screen_project(
                    screen_analyses=screen_analyses,
                    project_name=project_name,
                    include_typescript=include_typescript,
                    styling_approach=styling_approach
                )
            except Exception as gen_error:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ AI multi-screen generation error: {str(gen_error)}")
                print(f"Traceback: {error_trace}")
                return {
                    "success": False,
                    "error_message": f"AI multi-screen generation failed: {str(gen_error)}"
                }
            
            if not all_project_files:
                return {
                    "success": False,
                    "error_message": "AI multi-screen generation returned no files"
                }
            
            print(f"✅ Multi-screen project generated successfully!")
            print(f"   - Screens: {len(screen_analyses)}")
            print(f"   - Total files: {len(all_project_files)}")
            
            screen_results = [
                {
                    "screen_name": sa["screen_name"],
                    "screen_route": sa["screen_route"],
                    "components_count": len(sa["ui_analysis"].components) if hasattr(sa["ui_analysis"], 'components') else 0
                }
                for sa in screen_analyses
            ]
            
            return {
                "success": True,
                "project_files": all_project_files,
                "project_name": project_name,
                "files_count": len(all_project_files),
                "screens_count": len(screen_analyses),
                "screen_results": screen_results
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Multi-screen agent error: {error_trace}")
            return {
                "success": False,
                "error_message": f"Multi-screen agent error: {str(e)}"
            }
    
    def _generate_multi_screen_app_file(
        self,
        screen_component_map: Dict[str, Any],
        project_name: str,
        include_typescript: bool,
        styling_approach: str
    ) -> str:
        """Generate the main App.tsx/jsx file for a multi-screen application with React Router"""
        file_ext = "tsx" if include_typescript else "jsx"
        imports = [
            "import React from 'react';",
            "import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';"
        ]
        routes = []
        nav_links = []
        
        for screen_name, details in screen_component_map.items():
            comp_name = details["component_name"]
            route_path = details["route"]
            # Import screen component
            imports.append(f"import {comp_name} from './screens/{screen_name}/{comp_name}';")
            # Add route
            routes.append(f"            <Route path=\"{route_path}\" element={{<{comp_name} />}} />")
            # Add nav link
            nav_links.append(f"            <Link to=\"{route_path}\">{screen_name}</Link>")
        
        imports_str = "\n".join(imports)
        routes_str = "\n".join(routes)
        nav_links_str = "\n".join(nav_links)
        
        return f"""{imports_str}
import './index.css';

const App: React.FC = () => {{
  return (
    <BrowserRouter>
      <nav style={{{{ padding: '20px', borderBottom: '1px solid #ddd' }}}}>
        <div style={{{{ display: 'flex', gap: '20px' }}}}>
{nav_links_str}
        </div>
      </nav>
      <Routes>
{routes_str}
      </Routes>
    </BrowserRouter>
  );
}};

export default App;
"""
    
    def _generate_package_json(
        self,
        project_name: str,
        include_typescript: bool,
        styling_approach: str
    ) -> str:
        """Generate package.json for multi-screen React app"""
        deps = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.20.0"
        }
        
        dev_deps = {
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
            "@vitejs/plugin-react": "^4.2.0",
            "vite": "^5.0.0"
        }
        
        if include_typescript:
            dev_deps["typescript"] = "^5.2.0"
            dev_deps["@types/node"] = "^20.10.0"
        
        deps_str = ",\n".join([f'    "{k}": "{v}"' for k, v in deps.items()])
        dev_deps_str = ",\n".join([f'    "{k}": "{v}"' for k, v in dev_deps.items()])
        
        return f"""{{
  "name": "{project_name.lower().replace(' ', '-')}",
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
{deps_str}
  }},
  "devDependencies": {{
{dev_deps_str}
  }}
}}
"""
    
    def _generate_index_file(self, include_typescript: bool) -> str:
        """Generate src/index.tsx/jsx file"""
        file_ext = "tsx" if include_typescript else "jsx"
        return f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    
    def _generate_index_html(self, project_name: str) -> str:
        """Generate index.html file"""
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.tsx"></script>
  </body>
</html>
"""
    
    def _generate_vite_config(self, include_typescript: bool) -> str:
        """Generate vite.config.ts/js file"""
        if include_typescript:
            return """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
"""
        else:
            return """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
"""

