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
from .langgraph_agent import LangGraphFrontendAgent
from .ai_code_generator import AIReactCodeGenerator

class FrontendGenerationService:
    """Main service class for frontend generation operations"""
    
    def __init__(self, gemini_api_key: str, use_ai_generator: bool = False):
        self.gemini_api_key = gemini_api_key
        self.parser = UIParser(gemini_api_key)
        self.code_generator = None  # Will be initialized per request
        self.use_ai_generator = use_ai_generator
        self.ai_code_generator = None
        self.langgraph_agent = None
        # Initialize AI components lazily when needed
    
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
            import traceback
            error_trace = traceback.format_exc()
            print(f"Code generation error details: {error_trace}")
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
        include_typescript: bool = True,
        use_ai: bool = False
    ) -> Dict[str, Any]:
        """
        Process UI image and generate complete React project in one call
        
        Args:
            use_ai: If True, use AI-powered code generator (LangGraph agent)
                    If False, use template-based generator (faster, less flexible)
        """
        try:
            # Use AI generator if requested
            if use_ai or self.use_ai_generator:
                # Initialize AI components if not already initialized
                if not self.langgraph_agent:
                    self.langgraph_agent = LangGraphFrontendAgent(self.gemini_api_key)
                
                return await self._process_and_generate_with_ai(
                    image_data=image_data,
                    image_url=image_url,
                    additional_context=additional_context,
                    framework=framework,
                    styling_approach=styling_approach,
                    include_typescript=include_typescript
                )
            
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
    
    async def _process_and_generate_with_ai(
        self,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        additional_context: Optional[str] = None,
        framework: str = "react",
        styling_approach: str = "css-modules",
        include_typescript: bool = True
    ) -> Dict[str, Any]:
        """Process UI and generate React code using AI (LangGraph agent)"""
        try:
            # Use LangGraph agent for AI-powered generation
            result = await self.langgraph_agent.process_ui_to_react(
                image_data=image_data,
                project_name="react-app",
                additional_context=additional_context,
                include_typescript=include_typescript,
                styling_approach=styling_approach
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error_message": result.get("error_message", "AI generation failed")
                }
            
            # Convert to GeneratedProject format
            from .models import GeneratedProject
            project = GeneratedProject(
                project_name=result.get("project_name", "react-app"),
                files=result["project_files"],
                metadata={
                    "framework": framework,
                    "styling_approach": styling_approach,
                    "typescript": include_typescript,
                    "generation_method": "ai_langgraph",
                    "components_count": len(result.get("ui_analysis", {}).get("components", [])) if result.get("ui_analysis") else 0
                }
            )
            
            return {
                "success": True,
                "project": project,
                "ui_analysis": result.get("ui_analysis"),
                "files_count": result.get("files_count", 0)
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"AI generation error: {error_trace}")
            return {
                "success": False,
                "error_message": f"AI generation error: {str(e)}"
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
    
    async def generate_multi_screen_project(
        self,
        screen_images: list,
        screen_names: Optional[list] = None,
        screen_routes: Optional[list] = None,
        project_name: str = "multi-screen-app",
        additional_context: Optional[str] = None,
        framework: str = "react",
        styling_approach: str = "css-modules",
        include_typescript: bool = True,
        use_ai: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a complete React project with multiple screens connected via React Router
        
        Args:
            screen_images: List of base64 image data strings
            screen_names: Optional list of screen names (defaults to Screen1, Screen2, etc.)
            screen_routes: Optional list of routes (defaults to /screen1, /screen2, etc.)
            project_name: Name of the project
            additional_context: Additional context for all screens
            framework: Target framework
            styling_approach: Styling approach
            include_typescript: Include TypeScript
        
        Returns:
            Dictionary with success status and project files
        """
        try:
            import json
            from pathlib import Path
            
            screen_results = []
            all_components = {}
            screen_components_map = {}
            
            # Process each screen
            for idx, image_data in enumerate(screen_images):
                screen_num = idx + 1
                screen_name = screen_names[idx] if screen_names and idx < len(screen_names) else f"Screen{screen_num}"
                screen_route = screen_routes[idx] if screen_routes and idx < len(screen_routes) else f"/screen{screen_num}"
                
                print(f"Processing screen {screen_num}/{len(screen_images)}: {screen_name}")
                
                # Process UI for this screen
                screen_context = f"{additional_context or ''}\n\nThis is the {screen_name} screen. Generate a complete React component for this screen."
                
                request = UIProcessingRequest(
                    image_data=image_data,
                    additional_context=screen_context,
                    framework=framework,
                    styling_approach=styling_approach
                )
                
                processing_result = await self.process_ui(request)
                
                if not processing_result.success:
                    print(f"Warning: Failed to process screen {screen_name}: {processing_result.error_message}")
                    continue
                
                # Generate code for this screen
                code_request = CodeGenerationRequest(
                    ui_analysis=processing_result.ui_analysis,
                    framework=framework,
                    styling_approach=styling_approach,
                    include_typescript=include_typescript
                )
                
                generation_result = await self.generate_code(code_request)
                
                if not generation_result["success"]:
                    print(f"Warning: Failed to generate code for screen {screen_name}")
                    continue
                
                # Extract components from generated project
                screen_project = generation_result["project"]
                
                # Find the main component (root component used in App.tsx)
                main_component = None
                main_component_path = None
                
                # Read App.tsx/jsx to find which component is imported and used
                app_file_path = None
                for file_path in screen_project.files.keys():
                    if 'App.tsx' in file_path or 'App.jsx' in file_path:
                        app_file_path = file_path
                        break
                
                if app_file_path:
                    app_content = screen_project.files[app_file_path]
                    # Extract import statements to find main component
                    import re
                    import_pattern = r"import\s+(\w+)\s+from\s+['\"].*components/(\w+)"
                    matches = re.findall(import_pattern, app_content)
                    if matches:
                        # Prioritize components that match root/container patterns
                        prioritized_matches = []
                        for match in matches:
                            comp_name = match[0]
                            file_name = match[1]
                            # Check if it's a root/container component
                            is_root = any(keyword in comp_name.lower() or keyword in file_name.lower() 
                                        for keyword in ['app', 'root', 'container', 'layout', 'main', 'screen'])
                            prioritized_matches.append((is_root, match))
                        
                        # Sort: root components first
                        prioritized_matches.sort(key=lambda x: (not x[0], x[1][0]))
                        
                        # Get the first (highest priority) component
                        main_component = prioritized_matches[0][1][0]  # Component name used in code
                        component_file_name = prioritized_matches[0][1][1]  # File name
                        
                        # Find the component file
                        file_ext = "tsx" if include_typescript else "jsx"
                        main_component_path = f"src/components/{component_file_name}.{file_ext}"
                        
                        # Verify the file exists in the project
                        if main_component_path not in screen_project.files:
                            # Try alternative naming
                            for comp_path in screen_project.files.keys():
                                if component_file_name in comp_path and ('components/' in comp_path):
                                    main_component_path = comp_path
                                    break
                
                # If still not found, use first root component from UI analysis
                # Prioritize components that match root/container patterns
                if not main_component or not main_component_path:
                    root_components = [c for c in processing_result.ui_analysis.components if c.parent_id is None or c.parent_id == ""]
                    if root_components:
                        # Sort root components by priority (container/app/root/main first)
                        root_components = sorted(root_components, key=lambda c: (
                            any(keyword in c.name.lower() for keyword in ['app', 'root', 'container', 'layout', 'main', 'screen']),
                            len(c.children) if c.children else 0
                        ), reverse=True)
                        
                        # Try to find the highest priority root component
                        for root_comp in root_components:
                            main_component = self._sanitize_component_name(root_comp.name)
                            file_ext = "tsx" if include_typescript else "jsx"
                            main_component_path = f"src/components/{main_component}.{file_ext}"
                            
                            # Verify it exists
                            if main_component_path in screen_project.files:
                                break
                            else:
                                # Find any component file with this name
                                for comp_path in screen_project.files.keys():
                                    if main_component.lower() in comp_path.lower() and ('components/' in comp_path):
                                        main_component_path = comp_path
                                        # Extract actual component name from path
                                        path_parts = comp_path.split('/')
                                        if path_parts:
                                            file_name = path_parts[-1].replace('.tsx', '').replace('.jsx', '')
                                            main_component = file_name
                                        break
                                if main_component_path in screen_project.files:
                                    break
                
                # Collect all components from this screen (merge into shared components)
                for file_path, file_content in screen_project.files.items():
                    # Skip App.tsx/jsx and index files - we'll create our own
                    if 'App.' in file_path or ('index.' in file_path and ('tsx' in file_path or 'jsx' in file_path)):
                        continue
                    # Skip config files (vite.config, tsconfig, package.json) - we'll create our own
                    if 'vite.config' in file_path or 'tsconfig' in file_path or 'package.json' in file_path:
                        continue
                    # Skip index.html - we'll create our own
                    if 'index.html' in file_path:
                        continue
                    
                    # Handle component files - merge into shared components directory
                    if 'components/' in file_path:
                        # Use the file path as-is (components are shared across screens)
                        # If there's a conflict, we'll handle it by checking if it already exists
                        if file_path not in all_components:
                            all_components[file_path] = file_content
                        else:
                            # Component already exists from another screen - this is fine, they can share
                            pass
                    elif 'src/' in file_path and file_path not in ['src/index.css']:
                        # Other src files (keep them)
                        all_components[file_path] = file_content
                    elif file_path == 'src/index.css':
                        # Merge global styles (we'll create our own, but keep for reference)
                        pass
                
                if main_component and main_component_path:
                    screen_components_map[screen_name] = {
                        'component_name': main_component,
                        'component_path': main_component_path,
                        'route': screen_route,
                        'display_name': screen_name,
                        'all_files': screen_project.files
                    }
                    screen_results.append({
                        'screen_name': screen_name,
                        'screen_route': screen_route,
                        'main_component': main_component,
                        'main_component_path': main_component_path
                    })
            
            if not screen_components_map:
                return {
                    "success": False,
                    "error_message": "No screens were successfully processed"
                }
            
            # Generate multi-screen project with React Router
            project_files = self._generate_multi_screen_project_files(
                screen_components_map=screen_components_map,
                all_components=all_components,
                project_name=project_name,
                include_typescript=include_typescript
            )
            
            # Create project structure
            project = GeneratedProject(
                project_name=project_name,
                files=project_files,
                metadata={
                    "framework": framework,
                    "styling_approach": styling_approach,
                    "typescript": include_typescript,
                    "screens_count": len(screen_components_map),
                    "multi_screen": True
                }
            )
            
            return {
                "success": True,
                "project": project,
                "files_count": len(project_files),
                "screens_count": len(screen_components_map)
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Multi-screen generation error: {error_trace}")
            return {
                "success": False,
                "error_message": f"Multi-screen generation error: {str(e)}"
            }
    
    def _sanitize_component_name(self, name: str) -> str:
        """Sanitize component name for use in code"""
        import re
        name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        words = name.split()
        return ''.join(word.capitalize() for word in words) if words else "Component"
    
    def _generate_multi_screen_project_files(
        self,
        screen_components_map: Dict[str, Any],
        all_components: Dict[str, str],
        project_name: str,
        include_typescript: bool
    ) -> Dict[str, str]:
        """Generate project files for multi-screen application with React Router"""
        import json
        from pathlib import Path
        
        project_files = {}
        file_ext = "tsx" if include_typescript else "jsx"
        
        # 1. package.json with React Router
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.0.0",
                "vite": "^4.4.0"
            }
        }
        
        if include_typescript:
            package_json["devDependencies"].update({
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "typescript": "^5.0.0"
            })
        
        project_files["package.json"] = json.dumps(package_json, indent=2)
        
        # 2. vite.config.ts
        if include_typescript:
            project_files["vite.config.ts"] = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
"""
        else:
            project_files["vite.config.js"] = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
"""
        
        # 3. tsconfig.json (if TypeScript)
        if include_typescript:
            project_files["tsconfig.json"] = json.dumps({
                "compilerOptions": {
                    "target": "ES2020",
                    "useDefineForClassFields": True,
                    "lib": ["ES2020", "DOM", "DOM.Iterable"],
                    "module": "ESNext",
                    "skipLibCheck": True,
                    "moduleResolution": "bundler",
                    "allowImportingTsExtensions": True,
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "noEmit": True,
                    "jsx": "react-jsx",
                    "strict": True
                },
                "include": ["src"]
            }, indent=2)
        
        # 4. index.html
        project_files["index.html"] = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.{file_ext}"></script>
  </body>
</html>
"""
        
        # 5. Add all extracted components
        project_files.update(all_components)
        
        # 6. Create screen wrapper components and routes
        screen_imports = []
        screen_routes = []
        
        for screen_name, screen_data in screen_components_map.items():
            comp_name = screen_data['component_name']
            comp_path = screen_data['component_path']
            route = screen_data['route']
            
            # Import path (relative from screens directory)
            if 'src/components/' in comp_path:
                import_path = comp_path.replace('src/components/', '../components/').replace('.tsx', '').replace('.jsx', '')
            else:
                import_path = f"../components/{comp_name}"
            
            # Sanitize screen name for component name (must be valid JS identifier)
            screen_component_name = self._sanitize_component_name(screen_name)
            # Ensure it doesn't start with a number (invalid JS identifier)
            if screen_component_name and screen_component_name[0].isdigit():
                screen_component_name = "Screen" + screen_component_name
            # Remove any remaining invalid characters (hyphens, etc.) from component name
            screen_component_name = screen_component_name.replace('-', '').replace('_', '')
            # Ensure it starts with a letter
            if not screen_component_name or not screen_component_name[0].isalpha():
                screen_component_name = "Screen" + screen_component_name
            
            # Create screen wrapper
            screen_imports.append(f"import {comp_name} from '{import_path}';")
            screen_routes.append(f'          <Route path="{route}" element={{<{screen_component_name} />}} />')
            
            # Find the ROOT container component - prioritize components that contain the full screen
            # Look for: AppContainer, AppRoot, RootContainer, ScreenContainer, or the largest root component
            root_container_name = None
            root_container_path = None
            
            # Priority order for root container names
            root_container_patterns = [
                'appcontainer', 'app-container', 'approot', 'app-root',
                'rootcontainer', 'root-container', 'screencontainer', 'screen-container',
                'maincontainer', 'main-container', 'layoutcontainer', 'layout-container'
            ]
            
            # First, try to find by name patterns
            for comp_file_path in all_components.keys():
                file_name_lower = comp_file_path.lower()
                if comp_file_path.endswith(f'.{file_ext}'):
                    for pattern in root_container_patterns:
                        if pattern in file_name_lower:
                            root_container_path = comp_file_path
                            path_parts = comp_file_path.split('/')
                            if path_parts:
                                file_name = path_parts[-1].replace(f'.{file_ext}', '')
                                root_container_name = self._sanitize_component_name(file_name)
                            break
                    if root_container_name:
                        break
            
            # If not found by pattern, find the largest root component (most children)
            if not root_container_name:
                # Check the screen's all_files to find the root component
                screen_files = screen_data.get('all_files', {})
                root_components = []
                for file_path, file_content in screen_files.items():
                    if 'components/' in file_path and file_path.endswith(f'.{file_ext}'):
                        # Count imports to estimate component size
                        import_count = file_content.count('import')
                        root_components.append((import_count, file_path))
                
                if root_components:
                    # Sort by import count (more imports = more likely to be root)
                    root_components.sort(reverse=True)
                    root_container_path = root_components[0][1]
                    path_parts = root_container_path.split('/')
                    if path_parts:
                        file_name = path_parts[-1].replace(f'.{file_ext}', '')
                        root_container_name = self._sanitize_component_name(file_name)
            
            # Use root container if found, otherwise use the selected component
            component_to_use = root_container_name if root_container_name else comp_name
            import_path_to_use = None
            
            if root_container_name and root_container_path:
                import_path_to_use = root_container_path.replace('src/components/', '../components/').replace(f'.{file_ext}', '')
            else:
                import_path_to_use = import_path
            
            # Generate screen file - render the root component exactly as designed
            project_files[f"src/screens/{screen_name}.{file_ext}"] = f"""import React from 'react';
import {component_to_use} from '{import_path_to_use}';

const {screen_component_name}: React.FC = () => {{
  return <{component_to_use} />;
}};

export default {screen_component_name};
"""
        
        # 7. Create App.tsx with React Router
        screen_imports_for_app = []
        screen_component_names_map = {}  # Map screen_name to sanitized component name
        for screen_name, screen_data in screen_components_map.items():
            screen_component_name = self._sanitize_component_name(screen_name)
            # Ensure it doesn't start with a number (invalid JS identifier)
            if screen_component_name and screen_component_name[0].isdigit():
                screen_component_name = "Screen" + screen_component_name
            # Remove any remaining invalid characters (hyphens, etc.) from component name
            screen_component_name = screen_component_name.replace('-', '').replace('_', '')
            # Ensure it starts with a letter
            if not screen_component_name or not screen_component_name[0].isalpha():
                screen_component_name = "Screen" + screen_component_name
            screen_component_names_map[screen_name] = screen_component_name
            screen_imports_for_app.append(f"import {screen_component_name} from './screens/{screen_name}';")
        
        # Generate routes with proper component names
        route_elements = []
        for screen_name, screen_data in screen_components_map.items():
            screen_component_name = screen_component_names_map.get(screen_name, self._sanitize_component_name(screen_name))
            route_elements.append(f'          <Route path="{screen_data["route"]}" element={{<{screen_component_name} />}} />')
        
        # Generate App.tsx WITHOUT navigation bar - screens should render exactly as designed
        # Only add React Router for navigation between screens, but don't add UI elements
        project_files[f"src/App.{file_ext}"] = f"""import React from 'react';
import {{ BrowserRouter, Routes, Route }} from 'react-router-dom';
{chr(10).join(screen_imports_for_app)}
import './index.css';

const App: React.FC = () => {{
  return (
    <BrowserRouter>
      <Routes>
{chr(10).join(route_elements)}
      </Routes>
    </BrowserRouter>
  );
}};

export default App;
"""
        
        # 8. index.tsx/jsx
        project_files[f"src/index.{file_ext}"] = f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        
        # 9. Clean index.css - NO navigation styles, just base reset
        project_files["src/index.css"] = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
}

#root {
  width: 100%;
  min-width: 100vw;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  overflow-x: hidden;
}
"""
        
        # 10. README
        screens_list = "\n".join([
            f"- **{screen_name}**: `{screen_data['route']}`"
            for screen_name, screen_data in screen_components_map.items()
        ])
        
        project_files["README.md"] = f"""# {project_name}

Complete React application with {len(screen_components_map)} connected screens.

## 🚀 Getting Started

```bash
npm install
npm run dev
```

Then open http://localhost:3000 in your browser.

## 📱 Available Screens

{screens_list}

## 🧭 Navigation

Navigate directly using the routes above. Screens are connected via React Router.

## 🏗️ Project Structure

```
src/
├── App.{file_ext}              # Main app with React Router
├── index.{file_ext}            # Entry point
├── index.css                   # Global styles
├── screens/                    # Screen wrappers
│   ├── {list(screen_components_map.keys())[0] if screen_components_map else 'Screen1'}.{file_ext}
│   └── ...
└── components/                 # Reusable components
    ├── [Component].{file_ext}
    └── [Component].module.css
```

## 📦 Build

```bash
npm run build
```

Generated by CodeCraft Frontend Generator.
"""
        
        return project_files

